---
name: hermes-p2p-agent-mesh
description: Decentralized peer-to-peer agent mesh network with DID authentication and multi-machine workload offloading.
version: "1.0.0"
author: Hermes Advanced Team
license: MIT
metadata:
  hermes:
    tags: [hermes, p2p, agent-mesh, a2a, decentralized, swarm]
    category: hermes-advanced
---

# SKILL 15 — PEER-TO-PEER AGENT MESH & A2A

> **Load this skill when:** Delegating work across multiple physical machines, clusters, or independent agent nodes.

---

## 1. Mesh Topology

```
Primary Hermes (Local Laptop) <--- A2A Protocol ---> Worker Node (Remote GPU Server)
```

## 2. Security Protocol
- Ed25519 cryptographic handshake on node discovery.
- Scoped delegation tokens preventing unauthorized privilege escalation.
