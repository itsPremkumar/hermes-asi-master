/**
 * Plugin Registry — extensible provider system for search, extraction, and synthesis.
 *
 * The research-analyst profile lacks filesystem tools, so all data
 * flows through in-memory plugins. New providers can be registered
 * at runtime without modifying the engine core.
 */
import { SearchResult, Extraction, ResearchPass } from '../types.js';

export interface SearchPlugin {
  name: string;
  description: string;
  search(query: string, limit: number): Promise<SearchResult[]>;
}

export interface ExtractionPlugin {
  name: string;
  description: string;
  extract(content: string): Promise<Extraction[]>;
}

export interface SynthesisPlugin {
  name: string;
  description: string;
  synthesize(pass: ResearchPass): Promise<string>;
}

export interface PluginRegistry {
  registerSearch(plugin: SearchPlugin): void;
  registerExtraction(plugin: ExtractionPlugin): void;
  registerSynthesis(plugin: SynthesisPlugin): void;

  getSearch(name: string): SearchPlugin | undefined;
  getExtraction(name: string): ExtractionPlugin | undefined;
  getSynthesis(name: string): SynthesisPlugin | undefined;

  listSearch(): SearchPlugin[];
  listExtraction(): ExtractionPlugin[];
  listSynthesis(): SynthesisPlugin[];
}

export class PluginRegistryImpl implements PluginRegistry {
  private searchPlugins: Map<string, SearchPlugin> = new Map();
  private extractionPlugins: Map<string, ExtractionPlugin> = new Map();
  private synthesisPlugins: Map<string, SynthesisPlugin> = new Map();

  registerSearch(plugin: SearchPlugin): void {
    this.searchPlugins.set(plugin.name, plugin);
  }

  registerExtraction(plugin: ExtractionPlugin): void {
    this.extractionPlugins.set(plugin.name, plugin);
  }

  registerSynthesis(plugin: SynthesisPlugin): void {
    this.synthesisPlugins.set(plugin.name, plugin);
  }

  getSearch(name: string): SearchPlugin | undefined {
    return this.searchPlugins.get(name);
  }

  getExtraction(name: string): ExtractionPlugin | undefined {
    return this.extractionPlugins.get(name);
  }

  getSynthesis(name: string): SynthesisPlugin | undefined {
    return this.synthesisPlugins.get(name);
  }

  listSearch(): SearchPlugin[] {
    return Array.from(this.searchPlugins.values());
  }

  listExtraction(): ExtractionPlugin[] {
    return Array.from(this.extractionPlugins.values());
  }

  listSynthesis(): SynthesisPlugin[] {
    return Array.from(this.synthesisPlugins.values());
  }
}

/**
 * Built-in search plugin that uses a mock knowledge base for testing.
 * In production, this would connect to web search APIs, academic
 * databases, or internal knowledge stores.
 */
export class MockSearchPlugin implements SearchPlugin {
  name = 'mock-search';
  description = 'In-memory mock search for testing';

  constructor(private knowledgeBase: Map<string, SearchResult[]>) {}

  async search(query: string, limit: number = 5): Promise<SearchResult[]> {
    const results: SearchResult[] = [];
    for (const [key, values] of this.knowledgeBase) {
      if (query.toLowerCase().includes(key.toLowerCase()) || key.toLowerCase().includes(query.toLowerCase())) {
        results.push(...values);
      }
    }
    return results.slice(0, limit);
  }
}

/**
 * Built-in extraction plugin that extracts entities and facts from content.
 */
export class RegexExtractionPlugin implements ExtractionPlugin {
  name = 'regex-extraction';
  description = 'Extract facts using regex patterns';

  async extract(content: string): Promise<Extraction[]> {
    const extractions: Extraction[] = [];
    const sentences = content.split(/[.!?]+/).filter((s) => s.trim().length > 10);

    for (let i = 0; i < sentences.length; i++) {
      const sentence = sentences[i].trim();
      if (sentence.length < 5) continue;

      extractions.push({
        id: `ext_${i}`,
        fact: sentence,
        sourceResult: 'unknown',
        confidence: Math.min(0.9, sentence.length / 100),
        entities: this.extractEntities(sentence),
      });
    }

    return extractions;
  }

  private extractEntities(text: string): string[] {
    const entities: string[] = [];
    const capitalWords = text.match(/[A-Z][a-z]+(?:\s[A-Z][a-z]+)*/g);
    if (capitalWords) {
      entities.push(...capitalWords.slice(0, 5));
    }
    return entities;
  }
}

/**
 * Built-in synthesis plugin that summarizes research passes.
 */
export class TemplateSynthesisPlugin implements SynthesisPlugin {
  name = 'template-synthesis';
  description = 'Template-based synthesis from research pass results';

  async synthesize(pass: ResearchPass): Promise<string> {
    const resultCount = pass.results.length;
    const extractionCount = pass.extractions.length;
    const avgConfidence = pass.extractions.reduce((acc, e) => acc + e.confidence, 0) / Math.max(extractionCount, 1);

    return `Research on "${pass.query}" yielded ${resultCount} results and ${extractionCount} extractions. ` +
      `Average confidence: ${avgConfidence.toFixed(2)}. ` +
      `Key findings: ${pass.extractions.slice(0, 3).map((e) => e.fact).join('; ')}`;
  }
}
