package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"enterprise-integration/internal/gateway"
	"enterprise-integration/internal/pipeline"
)

// cmdHandler creates an HTTP handler that returns a JSON response.
func cmdHandler(message string) gateway.Handler {
	return func(ctx context.Context, w http.ResponseWriter, r *http.Request) error {
		resp := map[string]interface{}{
			"message": message,
			"uptime":  time.Since(startTime).Seconds(),
		}
		w.Header().Set("Content-Type", "application/json")
		return json.NewEncoder(w).Encode(resp)
	}
}

var startTime = time.Now()

func main() {
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	// Initialize the event pipeline.
	pl := pipeline.NewPipeline("integration.events", nil)
	if err := pl.Start(ctx); err != nil {
		fmt.Fprintf(os.Stderr, "failed to start pipeline: %v\n", err)
		os.Exit(1)
	}
	defer pl.Stop()

	// Set up the API gateway router.
	router := gateway.NewRouter("/api/v1")
	router.Register("GET", "/health", func(ctx context.Context, w http.ResponseWriter, r *http.Request) error {
		w.Header().Set("Content-Type", "application/json")
		return json.NewEncoder(w).Encode(gateway.HealthResponse{
			Status:    "ok",
			Timestamp: time.Now(),
			Uptime:    time.Since(startTime).Seconds(),
		})
	})
	router.Register("POST", "/events", func(ctx context.Context, w http.ResponseWriter, r *http.Request) error {
		var evt pipeline.Event
		if err := json.NewDecoder(r.Body).Decode(&evt); err != nil {
			return fmt.Errorf("decode event: %w", err)
		}
		evt.CreatedAt = time.Now()
		if err := pl.Publish(ctx, evt); err != nil {
			return fmt.Errorf("publish event: %w", err)
		}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusAccepted)
		return json.NewEncoder(w).Encode(map[string]string{"status": "accepted", "event_id": evt.ID})
	})

	addr := ":8080"
	fmt.Printf("Enterprise Integration Gateway starting on %s\n", addr)
	if err := gateway.StartServer(ctx, addr, router); err != nil && err != http.ErrServerClosed {
		fmt.Fprintf(os.Stderr, "server error: %v\n", err)
		os.Exit(1)
	}
}
