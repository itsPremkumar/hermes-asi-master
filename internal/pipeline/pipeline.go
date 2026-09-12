package pipeline

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"
)

// Event represents a message in the data pipeline.
type Event struct {
	ID            string                 `json:"id"`
	Type          string                 `json:"type"`
	Source        string                 `json:"source"`
	Target        string                 `json:"target"`
	Payload       map[string]interface{} `json:"payload"`
	IdempotencyKey string                `json:"idempotency_key"`
	CreatedAt     time.Time              `json:"created_at"`
}

// Processor handles incoming pipeline events.
type Processor interface {
	Process(ctx context.Context, evt Event) error
}

// Pipeline is the event-driven data pipeline backed by NATS.
type Pipeline struct {
	subject  string
	processor Processor
	clients   map[string]context.CancelFunc
	mu        sync.Mutex
	running   bool
}

// NewPipeline creates a new event-driven pipeline.
func NewPipeline(subject string, p Processor) *Pipeline {
	return &Pipeline{
		subject:  subject,
		processor: p,
		clients:  make(map[string]context.CancelFunc),
	}
}

// Start subscribes to the NATS subject and begins processing.
func (pl *Pipeline) Start(ctx context.Context) error {
	pl.mu.Lock()
	defer pl.mu.Unlock()
	if pl.running {
		return fmt.Errorf("pipeline already running")
	}
	pl.running = true
	go pl.run(ctx)
	return nil
}

// Stop gracefully shuts down the pipeline.
func (pl *Pipeline) Stop() {
	pl.mu.Lock()
	defer pl.mu.Unlock()
	for id, cancel := range pl.clients {
		cancel()
		delete(pl.clients, id)
	}
	pl.running = false
}

// Publish publishes an event to the pipeline (simulated NATS publish).
func (pl *Pipeline) Publish(ctx context.Context, evt Event) error {
	data, err := json.Marshal(evt)
	if err != nil {
		return fmt.Errorf("marshal event: %w", err)
	}
	// In production this would be: nc.Publish(pl.subject, data)
	_ = data
	return pl.processor.Process(ctx, evt)
}

func (pl *Pipeline) run(ctx context.Context) {
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			if !pl.running {
				return
			}
		}
	}
}

// Transform applies a transformation function to event payload.
func (pl *Pipeline) Transform(evt Event, fn func(map[string]interface{}) map[string]interface{}) Event {
	if fn != nil {
		evt.Payload = fn(evt.Payload)
	}
	return evt
}
