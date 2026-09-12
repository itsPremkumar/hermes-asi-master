# Enterprise System Integration Framework — Architecture

## Overview
Cross-system integration platform using gRPC for synchronous communication,
NATS for asynchronous event-driven messaging, PostgreSQL for state persistence,
and a Go-based MCP server for tool orchestration.

## Components
1. **MCP Server** (`cmd/mcp-server/`) — exposes integration tools via MCP protocol
2. **gRPC Services** (`internal/service/`) — sync request/response between systems
3. **Event Pipeline** (`internal/pipeline/`) — NATS-backed async event processing
4. **State Store** (`internal/store/`) — PostgreSQL persistence layer
5. **API Gateway** (`internal/gateway/`) — unified entry point

## Data Flow
- Sync: Client -> gRPC -> Service -> PostgreSQL
- Async: Producer -> NATS -> Consumer -> Processor -> PostgreSQL
- MCP: Tool call -> Handler -> gRPC/NATS -> downstream system

## Idempotency
All writes use idempotency keys (X-Idempotency-Key header). Replayed events
are deduplicated via a composite unique constraint on (event_type, event_id).

## Deployment
Docker Compose orchestrates: postgres, nats, nats-exec, mcp-server, grpc-gateway.
