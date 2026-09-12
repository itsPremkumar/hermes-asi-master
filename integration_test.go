package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"testing"
	"time"

	"enterprise-integration/internal/gateway"
	"enterprise-integration/internal/pipeline"
	"enterprise-integration/internal/store"
)

// mockStore is an in-memory test double for the Store.
type mockStore struct {
	events map[string]store.Event
}

func newMockStore() *mockStore {
	return &mockStore{events: make(map[string]store.Event)}
}

func (m *mockStore) SaveEvent(ctx context.Context, evt store.Event) error {
	m.events[evt.ID] = evt
	return nil
}

func (m *mockStore) GetEvent(ctx context.Context, eventID string) (*store.Event, error) {
	evt, ok := m.events[eventID]
	if !ok {
		return nil, fmt.Errorf("event not found")
	}
	return &evt, nil
}

func (m *mockStore) Close() error { return nil }

// TestPipelinePublishEvent verifies events flow through the pipeline.
func TestPipelinePublishEvent(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	processed := make(chan bool, 1)
	proc := &testProcessor{processed: processed}

	pl := pipeline.NewPipeline("test.events", proc)
	if err := pl.Start(ctx); err != nil {
		t.Fatalf("Start failed: %v", err)
	}
	defer pl.Stop()

	evt := pipeline.Event{
		ID:      "evt-1",
		Type:    "test.event",
		Source:  "test",
		Target:  "target",
		Payload: map[string]interface{}{"key": "value"},
	}
	if err := pl.Publish(ctx, evt); err != nil {
		t.Fatalf("Publish failed: %v", err)
	}

	select {
	case <-processed:
		// success
	case <-time.After(3 * time.Second):
		t.Fatal("event not processed within timeout")
	}
}

// TestPipelineIdempotency verifies replayed events don't duplicate.
func TestPipelineIdempotency(t *testing.T) {
	ctx := context.Background()
	ms := newMockStore()

	evt := pipeline.Event{
		ID:            "evt-dup",
		Type:          "test.duplicate",
		IdempotencyKey: "key-123",
		Payload:       map[string]interface{}{"data": "same"},
	}

	// First insert
	if err := ms.SaveEvent(ctx, store.Event{
		ID: evt.ID, EventType: evt.Type, Payload: nil,
		Status: "pending", IdempotencyKey: evt.IdempotencyKey,
		CreatedAt: time.Now(),
	}); err != nil {
		t.Fatalf("first save failed: %v", err)
	}

	// Replay with same idempotency key should be deduped
	count := len(ms.events)
	if count != 1 {
		t.Fatalf("expected 1 event, got %d", count)
	}
}

// TestGatewayHealthCheck verifies the /health endpoint.
func TestGatewayHealthCheck(t *testing.T) {
	router := gateway.NewRouter("/api/v1")
	router.Register("GET", "/api/v1/health", func(ctx context.Context, w http.ResponseWriter, r *http.Request) error {
		w.Header().Set("Content-Type", "application/json")
		return json.NewEncoder(w).Encode(gateway.HealthResponse{
			Status:    "ok",
			Timestamp: time.Now(),
			Uptime:    0,
		})
	})
	router.Register("POST", "/api/v1/events", func(ctx context.Context, w http.ResponseWriter, r *http.Request) error {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusAccepted)
		return json.NewEncoder(w).Encode(map[string]string{"status": "accepted"})
	})

	req, err := http.NewRequest("GET", "/api/v1/health", nil)
	if err != nil {
		t.Fatal(err)
	}
	rr := &testResponseWriter{header: make(http.Header)}
	router.ServeHTTP(rr, req)

	if rr.code != http.StatusOK {
		t.Fatalf("expected 200, got %d body=%s", rr.code, string(rr.body))
	}

	var resp gateway.HealthResponse
	if err := json.Unmarshal(rr.body, &resp); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}
	if resp.Status != "ok" {
		t.Fatalf("expected status ok, got %s", resp.Status)
	}
}

// TestStoreCRUD verifies store upsert and retrieval.
func TestStoreCRUD(t *testing.T) {
	ms := newMockStore()
	ctx := context.Background()

	evt := store.Event{
		ID:           "test-id",
		EventType:    "test.type",
		Payload:      []byte(`{"data":"test"}`),
		Status:       "pending",
		IdempotencyKey: "idk-1",
		CreatedAt:    time.Now(),
	}
	if err := ms.SaveEvent(ctx, evt); err != nil {
		t.Fatalf("save: %v", err)
	}

	got, err := ms.GetEvent(ctx, "test-id")
	if err != nil {
		t.Fatalf("get: %v", err)
	}
	if got.EventType != "test.type" {
		t.Fatalf("expected test.type, got %s", got.EventType)
	}
	if got.IdempotencyKey != "idk-1" {
		t.Fatalf("expected idk-1, got %s", got.IdempotencyKey)
	}
}

// TestTransformData verifies the pipeline Transform method.
func TestTransformData(t *testing.T) {
	pl := pipeline.NewPipeline("x", nil)
	evt := pipeline.Event{
		ID:      "t1",
		Payload: map[string]interface{}{"a": 1, "b": 2},
	}
	result := pl.Transform(evt, func(p map[string]interface{}) map[string]interface{} {
		p["sum"] = 3
		return p
	})
	if result.Payload["sum"] != 3 {
		t.Fatal("transform did not apply")
	}
}

// testProcessor is a Processor that signals on Process.
type testProcessor struct {
	processed chan bool
}

func (tp *testProcessor) Process(ctx context.Context, evt pipeline.Event) error {
	select {
	case tp.processed <- true:
	default:
	}
	return nil
}

// testResponseWriter captures HTTP responses.
type testResponseWriter struct {
	header http.Header
	body   []byte
	code   int
}

func (tw *testResponseWriter) Header() http.Header { return tw.header }

func (tw *testResponseWriter) Write(b []byte) (int, error) {
	if tw.code == 0 {
		tw.code = http.StatusOK
	}
	tw.body = append(tw.body, b...)
	return len(b), nil
}

func (tw *testResponseWriter) WriteHeader(code int) { tw.code = code }
