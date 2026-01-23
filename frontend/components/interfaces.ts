// Note: This file should be in a 'interfaces' or 'types' directory.

export interface Solution {
  title: string;
  explanation: string;
  code: string;
  confidence: number;
  source_urls?: string[];
}

export interface SearchResult {
  title: string;
  url: string;
  content: string;
  tags: string[];
  votes: number;
  distance: number;
}

export interface AnalysisResult {
  error_type: string;
  error_message: string;
  language: string;
  file_path: string;
  line_number: number;
  root_cause: string;
  reasoning: string;
  solutions: Solution[];
  sources_used: number;
  analysis_id: number;
  analysis_time_ms?: number;
}
