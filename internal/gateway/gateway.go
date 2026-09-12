package gateway

import (
	"context"
	"encoding/json"
	"net/http"
	"sync"
	"time"

	"enterprise-integration/internal/pipeline"
)

// Response is the unified API response envelope.
type Response struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
}

// Handler adapts an endpoint function to http.HandlerFunc with JSON.
type Handler func(ctx context.Context, w http.ResponseWriter, r *http.Request) error

func (h Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	if err := h(r.Context(), w, r); err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		_ = json.NewEncoder(w).Encode(Response{Success: false, Error: err.Error()})
		return
	}
}

// Router groups endpoints under a prefix.
type Router struct {
	prefix   string
	handlers map[string]Handler
	mu       sync.RWMutex
}

// NewRouter creates a new Router.
func NewRouter(prefix string) *Router {
	return &Router{
		prefix:   prefix,
		handlers: make(map[string]Handler),
	}
}

// Register adds an endpoint handler.
func (r *Router) Register(method, path string, h Handler) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.handlers[method+":"+path] = h
}

// ServeHTTP dispatches to registered handlers.
func (r *Router) ServeHTTP(w http.ResponseWriter, req *http.Request) {
	key := req.Method + ":" + req.URL.Path
	// Strip prefix if the registered path includes it.
	r.mu.RLock()
	h, ok := r.handlers[key]
	if !ok {
		// Fallback: try matching registered paths that end with req.URL.Path.
		for k, v := range r.handlers {
			if len(k) > len(req.Method) && k[len(req.Method)+1:] == req.URL.Path {
				h = v
				ok = true
				break
			}
		}
	}
	r.mu.RUnlock()
	if !ok {
		w.WriteHeader(http.StatusNotFound)
		_ = json.NewEncoder(w).Encode(Response{Success: false, Error: "not found"})
		return
	}
	if err := h(req.Context(), w, req); err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		_ = json.NewEncoder(w).Encode(Response{Success: false, Error: err.Error()})
	}
}

// EventBus bridges HTTP to the pipeline.
type EventBus struct {
	pipeline *pipeline.Pipeline
	mu       sync.RWMutex
	events   map[string]pipeline.Event
}

// NewEventBus creates an EventBus.
func NewEventBus(pl *pipeline.Pipeline) *EventBus {
	return &EventBus{
		pipeline: pl,
		events:   make(map[string]pipeline.Event),
	}
}

// Publish forwards an event to the pipeline.
func (eb *EventBus) Publish(ctx context.Context, evt pipeline.Event) error {
	eb.mu.Lock()
	eb.events[evt.ID] = evt
	eb.mu.Unlock()
	return eb.pipeline.Publish(ctx, evt)
}

// GetEvent retrieves an event by ID.
func (eb *EventBus) GetEvent(eventID string) (pipeline.Event, bool) {
	eb.mu.RLock()
	defer eb.mu.RUnlock()
	evt, ok := eb.events[eventID]
	return evt, ok
}

// HealthResponse represents the health check response.
type HealthResponse struct {
	Status    string    `json:"status"`
	Timestamp time.Time `json:"timestamp"`
	Uptime    float64 `json:"uptime_seconds"`
}

// StartServer launches the HTTP gateway.
func StartServer(ctx context.Context, addr string, router *Router) error {
	srv := &http.Server{
		Addr:         addr,
		Handler:      router,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
	}
	go func() {
		<-ctx.Done()
		srv.Shutdown(context.Background())
	}()
	return srv.ListenAndServe()
}
