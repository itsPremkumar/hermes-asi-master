/**
 * Core types for the Deep Research engine.
 */

export interface EvidenceNode {
  id: string;
  type: 'source' | 'claim' | 'reasoning' | 'context' | 'hypothesis' | 'counter';
  content: string;
  source?: string;
  confidence: number;        // 0.0 - 1.0
  metadata: Record<string, unknown>;
  createdAt: number;
}

export interface EvidenceEdge {
  id: string;
  from: string;              // EvidenceNode id
  to: string;                // EvidenceNode id
  type: 'supports' | 'contradicts' | 'elaborates' | 'cites' | 'derives';
  strength: number;          // 0.0 - 1.0
}

export interface EvidenceGraph {
  nodes: Map<string, EvidenceNode>;
  edges: EvidenceEdge[];
}

export interface ResearchPass {
  id: string;
  query: string;
  queries: string[];         // Expanded search queries
  results: SearchResult[];
  extractions: Extraction[];
  synthesis: string;
  confidence: number;
  startedAt: number;
  completedAt: number;
}

export interface SearchResult {
  id: string;
  title: string;
  url?: string;
  snippet: string;
  content?: string;
  relevance: number;
  source: string;
  timestamp: number;
}

export interface Extraction {
  id: string;
  fact: string;
  sourceResult: string;
  confidence: number;
  entities: string[];
}

export interface ResearchReport {
  query: string;
  passes: ResearchPass[];
  evidenceGraph: EvidenceGraph;
  conclusions: string[];
  openQuestions: string[];
  confidence: number;
  generatedAt: number;
}
