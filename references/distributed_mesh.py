"""Distributed Mesh — P2P agent mesh across multiple machines.

Implements a peer-to-peer network where agents discover, communicate,
coordinate, and share tasks without central control.

Usage:
    from advanced.distributed_mesh import AgentMesh, MeshNode
    mesh = AgentMesh(node_id="node-1")
    mesh.start()
    mesh.broadcast("hello", {"msg": "world"})
"""
from __future__ import annotations

import hashlib
import json
import queue
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4


class MessageType(Enum):
    PING = "ping"
    PONG = "pong"
    BROADCAST = "broadcast"
    DIRECT = "direct"
    TASK_OFFER = "task_offer"
    TASK_ACCEPT = "task_accept"
    TASK_RESULT = "task_result"
    DISCOVERY = "discovery"
    GOSSIP = "gossip"
    CONSENSUS_PROPOSE = "consensus_propose"
    CONSENSUS_VOTE = "consensus_vote"


class NodeState(Enum):
    JOINING = "joining"
    ACTIVE = "active"
    BUSY = "busy"
    LEAVING = "leaving"
    OFFLINE = "offline"


@dataclass
class MeshMessage:
    msg_type: MessageType
    sender: str
    target: Optional[str] = None  # None = broadcast
    payload: dict[str, Any] = field(default_factory=dict)
    msg_id: str = field(default_factory=lambda: str(uuid4()))
    ttl: int = 10
    timestamp: float = field(default_factory=time.time)
    trace: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "msg_type": self.msg_type.value,
            "sender": self.sender,
            "target": self.target,
            "payload": self.payload,
            "msg_id": self.msg_id,
            "ttl": self.ttl,
            "timestamp": self.timestamp,
            "trace": self.trace,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "MeshMessage":
        return cls(
            msg_type=MessageType(d["msg_type"]),
            sender=d["sender"],
            target=d.get("target"),
            payload=d.get("payload", {}),
            msg_id=d.get("msg_id", str(uuid4())),
            ttl=d.get("ttl", 10),
            timestamp=d.get("timestamp", time.time()),
            trace=d.get("trace", []),
        )

    @property
    def id(self) -> str:
        return self.msg_id

    def reply(self, msg_type: MessageType, payload: dict[str, Any]) -> "MeshMessage":
        return MeshMessage(
            msg_type=msg_type,
            sender=self.target if self.target else "",
            target=self.sender,
            payload=payload,
            trace=self.trace + [self.sender],
        )


@dataclass
class MeshNode:
    node_id: str
    address: str = "localhost:0"
    state: NodeState = NodeState.JOINING
    capabilities: list[str] = field(default_factory=list)
    peers: dict[str, "MeshNode"] = field(default_factory=dict)
    reputation: float = 1.0
    last_seen: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "address": self.address,
            "state": self.state.value,
            "capabilities": self.capabilities,
            "reputation": self.reputation,
            "last_seen": self.last_seen,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "MeshNode":
        return cls(
            node_id=d["node_id"],
            address=d.get("address", "localhost:0"),
            state=NodeState(d.get("state", "joining")),
            capabilities=d.get("capabilities", []),
            reputation=d.get("reputation", 1.0),
            last_seen=d.get("last_seen", time.time()),
            metadata=d.get("metadata", {}),
        )

    def is_active(self) -> bool:
        return self.state in (NodeState.ACTIVE, NodeState.BUSY)

    def age(self) -> float:
        return time.time() - self.last_seen


class RoutingTable:
    """DHT-inspired routing table for the mesh."""

    def __init__(self, node_id: str, k: int = 20):
        self.node_id = node_id
        self.k = k
        self._buckets: dict[int, list[MeshNode]] = {}
        self._all_nodes: dict[str, MeshNode] = {}

    def _distance(self, a: str, b: str) -> int:
        """XOR distance between two node IDs."""
        ha = int(hashlib.sha256(a.encode()).hexdigest(), 16)
        hb = int(hashlib.sha256(b.encode()).hexdigest(), 16)
        return ha ^ hb

    def _bucket_id(self, node_id: str) -> int:
        dist = self._distance(self.node_id, node_id)
        if dist == 0:
            return -1  # self
        return dist.bit_length() - 1

    def add(self, node: MeshNode) -> None:
        if node.node_id == self.node_id:
            return
        bucket_id = self._bucket_id(node.node_id)
        if bucket_id < 0:
            return
        if bucket_id not in self._buckets:
            self._buckets[bucket_id] = []
        # If bucket has space, add
        existing = [n for n in self._buckets[bucket_id] if n.node_id == node.node_id]
        if existing:
            existing[0].last_seen = node.last_seen
            existing[0].state = node.state
        elif len(self._buckets[bucket_id]) < self.k:
            self._buckets[bucket_id].append(node)
        else:
            # Bucket full; replace oldest
            oldest = min(self._buckets[bucket_id], key=lambda n: n.last_seen)
            if oldest.age() > 60:  # stale after 60s
                self._buckets[bucket_id].remove(oldest)
                self._buckets[bucket_id].append(node)
        self._all_nodes[node.node_id] = node

    def remove(self, node_id: str) -> bool:
        if node_id in self._all_nodes:
            del self._all_nodes[node_id]
        for bucket in self._buckets.values():
            for n in bucket:
                if n.node_id == node_id:
                    bucket.remove(n)
                    return True
        return False

    def find_closest(self, target_id: str, n: int = 3) -> list[MeshNode]:
        """Find n closest nodes to target."""
        all_nodes = list(self._all_nodes.values())
        all_nodes.sort(key=lambda node: self._distance(node.node_id, target_id))
        return all_nodes[:n]

    def get_all(self) -> list[MeshNode]:
        return list(self._all_nodes.values())

    @property
    def size(self) -> int:
        return len(self._all_nodes)


class GossipProtocol:
    """Epidemic broadcast protocol."""

    def __init__(self, fanout: int = 3):
        self.fanout = fanout
        self._seen: set[str] = set()

    def should_process(self, msg_id: str) -> bool:
        """Check if message is new."""
        if msg_id in self._seen:
            return False
        self._seen.add(msg_id)
        return True

    def select_targets(self, peers: list[MeshNode],
                       exclude: set[str]) -> list[MeshNode]:
        """Select fanout peers to gossip to."""
        candidates = [p for p in peers if p.node_id not in exclude and p.is_active()]
        if len(candidates) <= self.fanout:
            return candidates
        import random
        return random.sample(candidates, self.fanout)

    @property
    def seen_count(self) -> int:
        return len(self._seen)


class ConsensusProtocol:
    """Simplified Raft-like consensus for mesh coordination."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.term = 0
        self.votes: dict[str, bool] = {}
        self.log: list[dict[str, Any]] = []
        self.pending_proposals: dict[str, dict[str, Any]] = {}

    def propose(self, value: Any) -> str:
        """Propose a value for consensus."""
        self.term += 1
        proposal_id = f"p-{self.term}-{self.node_id}"
        self.pending_proposals[proposal_id] = {
            "value": value,
            "term": self.term,
            "votes": {},
            "status": "pending",
        }
        return proposal_id

    def vote(self, proposal_id: str, voter: str, approve: bool) -> bool:
        """Record a vote. Returns True if proposal is accepted."""
        if proposal_id not in self.pending_proposals:
            return False
        proposal = self.pending_proposals[proposal_id]
        proposal["votes"][voter] = approve
        return len([v for v in proposal["votes"].values() if v]) > len(proposal["votes"]) / 2

    def finalize(self, proposal_id: str) -> Optional[dict[str, Any]]:
        """Finalize a proposal."""
        if proposal_id not in self.pending_proposals:
            return None
        proposal = self.pending_proposals[proposal_id]
        approve_count = sum(1 for v in proposal["votes"].values() if v)
        total = len(proposal["votes"])
        if total > 0 and approve_count > total / 2:
            proposal["status"] = "accepted"
            self.log.append(proposal)
            return proposal
        else:
            proposal["status"] = "rejected"
            return None


class TaskManager:
    """Distribute and track tasks across mesh nodes."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.tasks: dict[str, dict[str, Any]] = {}
        self.results: dict[str, Any] = {}
        self._lock = threading.Lock()

    def create_task(self, task_type: str, payload: dict[str, Any],
                    target: Optional[str] = None) -> str:
        """Create a new task."""
        task_id = str(uuid4())
        with self._lock:
            self.tasks[task_id] = {
                "task_id": task_id,
                "type": task_type,
                "payload": payload,
                "owner": self.node_id,
                "target": target,
                "status": "pending",
                "created_at": time.time(),
                "result": None,
            }
        return task_id

    def assign_task(self, task_id: str, node_id: str) -> bool:
        """Assign a task to a node."""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id]["target"] = node_id
                self.tasks[task_id]["status"] = "assigned"
                return True
        return False

    def complete_task(self, task_id: str, result: Any) -> bool:
        """Mark a task as complete."""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id]["status"] = "completed"
                self.tasks[task_id]["result"] = result
                self.results[task_id] = result
                return True
        return False

    def get_pending(self) -> list[dict[str, Any]]:
        """Get pending tasks."""
        with self._lock:
            return [t for t in self.tasks.values() if t["status"] == "pending"]

    def get_completed(self) -> list[dict[str, Any]]:
        """Get completed tasks."""
        with self._lock:
            return [t for t in self.tasks.values() if t["status"] == "completed"]


class AgentMesh:
    """Main mesh network interface."""

    def __init__(self, node_id: Optional[str] = None, address: str = "localhost:0"):
        self.node_id = node_id or str(uuid4())[:8]
        self.address = address
        self.state = NodeState.JOINING
        self.routing = RoutingTable(self.node_id)
        self.gossip = GossipProtocol()
        self.consensus = ConsensusProtocol(self.node_id)
        self.tasks = TaskManager(self.node_id)
        self._message_queue: queue.Queue[MeshMessage] = queue.Queue()
        self._handlers: dict[MessageType, list[Callable]] = {}
        self._transport: Optional[Any] = None  # injected transport
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._peers: dict[str, MeshNode] = {}
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start the mesh node."""
        self.state = NodeState.ACTIVE
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the mesh node."""
        self.state = NodeState.LEAVING
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _run(self) -> None:
        """Main loop processing messages."""
        while self._running:
            try:
                msg = self._message_queue.get(timeout=0.1)
                self._dispatch(msg)
            except queue.Empty:
                continue

    def _dispatch(self, msg: MeshMessage) -> None:
        """Route a message to registered handlers."""
        handlers = self._handlers.get(msg.msg_type, [])
        for h in handlers:
            try:
                h(msg)
            except Exception as e:
                pass  # log in real impl
        # Built-in handlers
        if msg.msg_type == MessageType.PING:
            if msg.target == self.node_id:
                self.send(msg.reply(MessageType.PONG, {"status": "alive"}))
        elif msg.msg_type == MessageType.DISCOVERY:
            self._handle_discovery(msg)

    def _handle_discovery(self, msg: MeshMessage) -> None:
        """Handle a discovery message."""
        peer_info = msg.payload.get("node")
        if peer_info:
            node = MeshNode.from_dict(peer_info)
            self.routing.add(node)
            with self._lock:
                self._peers[node.node_id] = node
        # Respond with our info
        if msg.target is None or msg.target == self.node_id:
            self.send(msg.reply(MessageType.DISCOVERY, {
                "node": MeshNode(
                    node_id=self.node_id,
                    address=self.address,
                    state=self.state,
                ).to_dict()
            }))

    def on(self, msg_type: MessageType, handler: Callable) -> None:
        """Register a message handler."""
        if msg_type not in self._handlers:
            self._handlers[msg_type] = []
        self._handlers[msg_type].append(handler)

    def send(self, msg: MeshMessage) -> None:
        """Send a message."""
        if self._transport:
            self._transport.send(msg)
        # In-process fallback for testing
        self._message_queue.put(msg)

    def broadcast(self, event: str, payload: dict[str, Any],
                  exclude: Optional[set[str]] = None) -> MeshMessage:
        """Broadcast to all peers via gossip."""
        msg = MeshMessage(
            msg_type=MessageType.BROADCAST,
            sender=self.node_id,
            payload={"event": event, **payload},
        )
        self.gossip.should_process(msg.msg_id)
        self.send(msg)
        return msg

    def send_to(self, target_id: str, event: str,
                payload: dict[str, Any]) -> MeshMessage:
        """Send directly to a peer."""
        msg = MeshMessage(
            msg_type=MessageType.DIRECT,
            sender=self.node_id,
            target=target_id,
            payload={"event": event, **payload},
        )
        self.send(msg)
        return msg

    def ping(self, target_id: str) -> MeshMessage:
        """Ping a specific node."""
        return self.send_to(target_id, "ping", {})

    def join(self, bootstrap_nodes: list[MeshNode]) -> None:
        """Join the mesh via bootstrap nodes."""
        for node in bootstrap_nodes:
            self.routing.add(node)
            with self._lock:
                self._peers[node.node_id] = node
            self.send_to(node.node_id, "discovery", {
                "node": MeshNode(
                    node_id=self.node_id,
                    address=self.address,
                    state=self.state,
                ).to_dict()
            })
        self.state = NodeState.ACTIVE

    def discover(self) -> list[MeshNode]:
        """Return all known peers."""
        return self.routing.get_all()

    def offer_task(self, task_type: str, payload: dict[str, Any]) -> str:
        """Offer a task to the mesh."""
        task_id = self.tasks.create_task(task_type, payload)
        self.broadcast("task_offer", {
            "task_id": task_id,
            "type": task_type,
            "payload": payload,
        })
        return task_id

    def propose_value(self, value: Any) -> str:
        """Propose a value for mesh consensus."""
        proposal_id = self.consensus.propose(value)
        self.broadcast("consensus_propose", {
            "proposal_id": proposal_id,
            "value": value,
            "term": self.consensus.term,
        })
        return proposal_id

    def get_stats(self) -> dict[str, Any]:
        """Get node statistics."""
        return {
            "node_id": self.node_id,
            "state": self.state.value,
            "peers": len(self._peers),
            "routing_table_size": self.routing.size,
            "pending_tasks": len(self.tasks.get_pending()),
            "completed_tasks": len(self.tasks.get_completed()),
            "messages_seen": self.gossip.seen_count,
            "consensus_term": self.consensus.term,
        }


class MeshTransport:
    """Abstract transport layer. Subclass for TCP/UDP/WebSocket."""

    def send(self, msg: MeshMessage) -> None:
        raise NotImplementedError

    def receive(self) -> Optional[MeshMessage]:
        raise NotImplementedError


class InMemoryTransport(MeshTransport):
    """In-process transport for testing."""

    _channels: dict[str, queue.Queue[MeshMessage]] = {}
    _lock = threading.Lock()

    def __init__(self, node_id: str):
        self.node_id = node_id
        with self._lock:
            if node_id not in self._channels:
                self._channels[node_id] = queue.Queue()
            self._queue = self._channels[node_id]

    def send(self, msg: MeshMessage) -> None:
        """Route to target or broadcast."""
        with self._lock:
            if msg.target:
                if msg.target in self._channels:
                    self._channels[msg.target].put(msg)
            else:
                for nid, ch in self._channels.items():
                    if nid != self.node_id:
                        ch.put(msg)

    def receive(self, timeout: float = 1.0) -> Optional[MeshMessage]:
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None


def create_mesh(node_id: Optional[str] = None,
                peers: Optional[list[str]] = None) -> tuple[AgentMesh, InMemoryTransport]:
    """Factory: create a mesh node with in-memory transport."""
    nid = node_id or f"node-{uuid4().hex[:6]}"
    transport = InMemoryTransport(nid)
    mesh = AgentMesh(node_id=nid)
    mesh._transport = transport
    return mesh, transport
