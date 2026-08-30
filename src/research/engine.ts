/**
 * Multi-Pass Research Engine.
 *
 * Runs multiple research passes, each building on the previous one:
 * Pass 1: Broad search — gather initial sources
 * Pass 2: Deep extraction — extract facts from sources
 * Pass 3: Synthesis — combine findings and identify gaps
 * Pass 4+: Targeted follow-up — fill gaps, resolve contradictions
 *
 * Each pass adds nodes and edges to the evidence graph.
 */
import { ResearchPass, SearchResult, Extraction, ResearchReport } from './types.js';
import { EvidenceGraphImpl } from './graph.js';
import { PluginRegistryImpl, SearchPlugin, ExtractionPlugin, SynthesisPlugin } from './plugins.js';

export interface MultiPassConfig {
  maxPasses: number;
  minConfidence: number;     // Stop if overall confidence exceeds this
  queriesPerPass: number;    // How many expanded queries to run per pass
  resultsPerQuery: number;   // Max results per query
  searchPlugin: string;      // Which search plugin to use
  extractionPlugin: string;  // Which extraction plugin to use
  synthesisPlugin: string;   // Which synthesis plugin to use
}

export class MultiPassResearchEngine {
  private graph: EvidenceGraphImpl;
  private registry: PluginRegistryImpl;
  private config: MultiPassConfig;
  private passes: ResearchPass[] = [];

  constructor(graph: EvidenceGraphImpl, registry: PluginRegistryImpl, config: Partial<MultiPassConfig> = {}) {
    this.graph = graph;
    this.registry = registry;
    this.config = {
      maxPasses: 4,
      minConfidence: 0.85,
      queriesPerPass: 3,
      resultsPerQuery: 5,
      searchPlugin: 'mock-search',
      extractionPlugin: 'regex-extraction',
      synthesisPlugin: 'template-synthesis',
      ...config,
    };
  }

  /**
   * Run the full multi-pass research pipeline.
   */
  async research(query: string): Promise<ResearchReport> {
    this.passes = [];
    let currentQuery = query;

    for (let passNum = 0; passNum < this.config.maxPasses; passNum++) {
      const pass = await this.runPass(passNum, currentQuery);
      this.passes.push(pass);

      // Add pass results to evidence graph
      this.addPassToGraph(pass);

      // Check if we've reached sufficient confidence
      if (pass.confidence >= this.config.minConfidence) {
        break;
      }

      // Generate follow-up query for next pass
      currentQuery = this.generateFollowUpQuery(pass, query);
    }

    // Final propagation
    this.graph.propagateConfidence();

    return this.buildReport(query);
  }

  /**
   * Run a single research pass.
   */
  private async runPass(passNum: number, query: string): Promise<ResearchPass> {
    const startedAt = Date.now();
    const queries = this.expandQuery(query, passNum);

    // Search
    const searchPlugin = this.registry.getSearch(this.config.searchPlugin);
    if (!searchPlugin) throw new Error(`Search plugin not found: ${this.config.searchPlugin}`);

    const allResults: SearchResult[] = [];
    for (const q of queries) {
      const results = await searchPlugin.search(q, this.config.resultsPerQuery);
      allResults.push(...results);
    }

    // Extract
    const extractionPlugin = this.registry.getExtraction(this.config.extractionPlugin);
    if (!extractionPlugin) throw new Error(`Extraction plugin not found: ${this.config.extractionPlugin}`);

    const allExtractions: Extraction[] = [];
    for (const result of allResults) {
      if (result.content) {
        const extractions = await extractionPlugin.extract(result.content);
        allExtractions.push(...extractions);
      }
    }

    // Synthesize
    const pass: ResearchPass = {
      id: `pass_${passNum}`,
      query,
      queries,
      results: allResults,
      extractions: allExtractions,
      synthesis: '',
      confidence: this.computePassConfidence(allExtractions),
      startedAt,
      completedAt: Date.now(),
    };

    const synthesisPlugin = this.registry.getSynthesis(this.config.synthesisPlugin);
    if (synthesisPlugin) {
      pass.synthesis = await synthesisPlugin.synthesize(pass);
    }

    return pass;
  }

  /**
   * Expand a query into multiple search queries for a pass.
   */
  private expandQuery(query: string, passNum: number): string[] {
    const expansions = [
      [query],
      [`${query} overview`, `${query} details`, `${query} examples`],
      [`${query} research`, `${query} analysis`, `${query} 2024`],
      [`${query} alternatives`, `${query} comparison`, `${query} review`],
    ];
    return expansions[Math.min(passNum, expansions.length - 1)];
  }

  /**
   * Generate a follow-up query based on gaps in the current pass.
   */
  private generateFollowUpQuery(pass: ResearchPass, originalQuery: string): string {
    if (pass.extractions.length === 0) {
      return `${originalQuery} introduction`;
    }
    const entities = pass.extractions.flatMap((e) => e.entities).slice(0, 3);
    if (entities.length > 0) {
      return `${originalQuery} ${entities.join(' ')}`;
    }
    return `${originalQuery} deep dive`;
  }

  /**
   * Compute overall confidence for a pass.
   */
  private computePassConfidence(extractions: Extraction[]): number {
    if (extractions.length === 0) return 0;
    const avgConfidence = extractions.reduce((acc, e) => acc + e.confidence, 0) / extractions.length;
    const coverage = Math.min(1, extractions.length / 10); // More extractions = more coverage
    return avgConfidence * 0.7 + coverage * 0.3;
  }

  /**
   * Add a research pass results to the evidence graph.
   */
  private addPassToGraph(pass: ResearchPass): void {
    // Add result nodes
    for (const result of pass.results) {
      const node = this.graph.addNode({
        type: 'source',
        content: result.snippet,
        source: result.url || result.source,
        confidence: result.relevance,
        metadata: { title: result.title, timestamp: result.timestamp },
      });

      // Add extraction nodes linked to source
      for (const extraction of pass.extractions.filter((e) => e.sourceResult === result.id || e.sourceResult === 'unknown')) {
        const extNode = this.graph.addNode({
          type: 'claim',
          content: extraction.fact,
          confidence: extraction.confidence,
          metadata: { entities: extraction.entities },
        });

        this.graph.addEdge({
          from: node.id,
          to: extNode.id,
          type: 'derives',
          strength: extraction.confidence,
        });
      }
    }
  }

  /**
   * Build the final research report.
   */
  private buildReport(query: string): ResearchReport {
    const topNodes = this.graph.getTopNodes(10);
    const contradictions = this.graph.findContradictions();

    const conclusions = topNodes
      .filter((n) => n.confidence > 0.5)
      .map((n) => n.content);

    const openQuestions: string[] = [];
    if (contradictions.length > 0) {
      openQuestions.push(`${contradictions.length} contradictions found that need resolution`);
    }
    if (this.passes.length >= this.config.maxPasses) {
      openQuestions.push(`Max passes reached — further research may be needed`);
    }

    const confidence = this.passes.length > 0
      ? this.passes[this.passes.length - 1].confidence
      : 0;

    return {
      query,
      passes: this.passes,
      evidenceGraph: this.graph,
      conclusions,
      openQuestions,
      confidence,
      generatedAt: Date.now(),
    };
  }

  getPasses(): ResearchPass[] {
    return this.passes;
  }
}
