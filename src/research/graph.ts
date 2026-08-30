/**
 * EvidenceGraph — core data structure for the research engine.
 *
 * Maintains a graph of evidence nodes and their relationships.
 * Supports confidence propagation, contradiction detection,
 * and evidence aggregation.
 */
import { EvidenceGraph, EvidenceNode, EvidenceEdge } from './types.js';

let idCounter = 0;
function genId(prefix: string): string {
  return `${prefix}_${++idCounter}`;
}

export class EvidenceGraphImpl implements EvidenceGraph {
  nodes: Map<string, EvidenceNode> = new Map();
  edges: EvidenceEdge[] = [];

  addNode(node: Omit<EvidenceNode, 'id' | 'createdAt'> & { id?: string | undefined }): EvidenceNode {
    const full: EvidenceNode = {
      ...node,
      id: node.id || genId('node'),
      createdAt: Date.now(),
    };
    this.nodes.set(full.id, full);
    return full;
  }

  addEdge(edge: Omit<EvidenceEdge, 'id'> & { id?: string | undefined }): EvidenceEdge {
    const full: EvidenceEdge = {
      ...edge,
      id: edge.id || genId('edge'),
    };
    this.edges.push(full);
    return full;
  }

  getNode(id: string): EvidenceNode | undefined {
    return this.nodes.get(id);
  }

  getEdgesFrom(nodeId: string): EvidenceEdge[] {
    return this.edges.filter((e) => e.from === nodeId);
  }

  getEdgesTo(nodeId: string): EvidenceEdge[] {
    return this.edges.filter((e) => e.to === nodeId);
  }

  getSupporting(nodeId: string): EvidenceNode[] {
    return this.getEdgesTo(nodeId)
      .filter((e) => e.type === 'supports')
      .map((e) => this.nodes.get(e.from))
      .filter((n): n is EvidenceNode => n !== undefined);
  }

  getContradicting(nodeId: string): EvidenceNode[] {
    return this.getEdgesTo(nodeId)
      .filter((e) => e.type === 'contradicts')
      .map((e) => this.nodes.get(e.from))
      .filter((n): n is EvidenceNode => n !== undefined);
  }

  /**
   * Propagate confidence through the graph using a simple
   * weighted propagation model.
   */
  propagateConfidence(): void {
    for (const [, node] of this.nodes) {
      const supporters = this.getSupporting(node.id);
      const contradictors = this.getContradicting(node.id);

      const supportScore = supporters.reduce(
        (acc, s) => acc + s.confidence * 0.2,
        0,
      );
      const contradictScore = contradictors.reduce(
        (acc, c) => acc + c.confidence * 0.3,
        0,
      );

      node.confidence = Math.max(0, Math.min(1,
        node.confidence + supportScore - contradictScore
      ));
    }
  }

  /**
   * Find contradictions in the graph: pairs of claims that
   * contradict each other with high confidence.
   */
  findContradictions(): Array<[EvidenceNode, EvidenceNode]> {
    const contradictions: Array<[EvidenceNode, EvidenceNode]> = [];
    for (const edge of this.edges) {
      if (edge.type === 'contradicts' && edge.strength > 0.5) {
        const from = this.nodes.get(edge.from);
        const to = this.nodes.get(edge.to);
        if (from && to) {
          contradictions.push([from, to]);
        }
      }
    }
    return contradictions;
  }

  /**
   * Get the top-N most confident nodes.
   */
  getTopNodes(n: number = 10): EvidenceNode[] {
    return Array.from(this.nodes.values())
      .sort((a, b) => b.confidence - a.confidence)
      .slice(0, n);
  }

  /**
   * Merge another graph into this one (deduplication by content hash).
   */
  merge(other: EvidenceGraphImpl): void {
    for (const [, node] of other.nodes) {
      const existing = Array.from(this.nodes.values()).find(
        (n) => n.content === node.content && n.source === node.source
      );
      if (!existing) {
        this.addNode({ ...node, id: undefined });
      }
    }
    for (const edge of other.edges) {
      this.addEdge({ ...edge, id: undefined });
    }
  }

  toJSON(): { nodes: EvidenceNode[]; edges: EvidenceEdge[] } {
    return {
      nodes: Array.from(this.nodes.values()),
      edges: this.edges,
    };
  }
}
