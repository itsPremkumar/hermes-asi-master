package store

import (
	"context"
	"database/sql"
	"time"
)

// Config holds PostgreSQL connection parameters.
type Config struct {
	Host     string
	Port     string
	User     string
	Password string
	DBName   string
}

// Store persists integration events and their processing state.
type Store struct {
	db *sql.DB
}

// NewStore creates a new Store with a PostgreSQL connection.
func NewStore(ctx context.Context, cfg Config) (*Store, error) {
	connStr := "host=" + cfg.Host + " port=" + cfg.Port + " user=" + cfg.User +
		" password=" + cfg.Password + " dbname=" + cfg.DBName + " sslmode=disable"
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, err
	}
	if err := db.PingContext(ctx); err != nil {
		return nil, err
	}
	s := &Store{db: db}
	if err := s.initSchema(ctx); err != nil {
		return nil, err
	}
	return s, nil
}

// Event represents a persisted integration event.
type Event struct {
	ID             string
	EventType      string
	Payload        []byte
	Status         string
	IdempotencyKey string
	ProcessedAt    *time.Time
	CreatedAt      time.Time
}

// Close releases database resources.
func (s *Store) Close() error {
	return s.db.Close()
}

// initSchema creates the events table with idempotency constraint.
func (s *Store) initSchema(ctx context.Context) error {
	query := `
	CREATE TABLE IF NOT EXISTS events (
		id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
		event_id        TEXT NOT NULL,
		event_type      TEXT NOT NULL,
		payload         BYTEA,
		status          TEXT NOT NULL DEFAULT 'pending',
		idempotency_key TEXT,
		processed_at    TIMESTAMPTZ,
		created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
		UNIQUE(event_type, event_id)
	);
	CREATE INDEX IF NOT EXISTS idx_events_idempotency ON events(idempotency_key);
	CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);
	`
	_, err := s.db.ExecContext(ctx, query)
	return err
}

// SaveEvent inserts or updates an event (idempotent via upsert).
func (s *Store) SaveEvent(ctx context.Context, evt Event) error {
	query := `
	INSERT INTO events (event_id, event_type, payload, status, idempotency_key, processed_at, created_at)
	VALUES ($1, $2, $3, $4, $5, $6, $7)
	ON CONFLICT (event_type, event_id) DO UPDATE
		SET status = EXCLUDED.status, processed_at = EXCLUDED.processed_at
	`
	_, err := s.db.ExecContext(ctx, query, evt.ID, evt.EventType, evt.Payload,
		evt.Status, evt.IdempotencyKey, evt.ProcessedAt, evt.CreatedAt)
	return err
}

// GetEvent retrieves an event by event_id.
func (s *Store) GetEvent(ctx context.Context, eventID string) (*Event, error) {
	query := `SELECT id, event_id, event_type, payload, status, idempotency_key, processed_at, created_at FROM events WHERE event_id = $1`
	row := s.db.QueryRowContext(ctx, query, eventID)
	evt := &Event{}
	var processedAt sql.NullTime
	if err := row.Scan(&evt.ID, &evt.EventType, &evt.Payload, &evt.Status,
		&evt.IdempotencyKey, &processedAt, &evt.CreatedAt); err != nil {
		return nil, err
	}
	if processedAt.Valid {
		evt.ProcessedAt = &processedAt.Time
	}
	return evt, nil
}
