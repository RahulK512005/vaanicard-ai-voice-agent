import { Product, ComparisonData } from './product';

export type VoiceState = 'IDLE' | 'LISTENING' | 'PROCESSING' | 'SPEAKING' | 'ERROR';

export interface SpokenOutput {
  text: string;
  ssml?: string;
  language_code: string;
  speech_rate: number;
}

export interface LatencyMetrics {
  intent_ms: number;
  retrieval_ms: number;
  pricing_ms: number;
  llm_ms: number;
  validation_ms: number;
  total_ms: number;
}

export interface DebugInfo {
  session_id: string;
  detected_intent: string;
  extracted_entities: Record<string, any>;
  detected_language: string;
  rag_used: boolean;
  rag_sources: string[];
  pricing_authoritative?: Record<string, any>;
  prompt_version: string;
  validation_passed: boolean;
  validation_notes: string[];
  latency: LatencyMetrics;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: Date;
  spokenOutput?: SpokenOutput;
  products?: Product[];
  comparison?: ComparisonData;
  debug?: DebugInfo;
  isVoiceInput?: boolean;
}

export interface ChatResponse {
  session_id: string;
  display_response: string;
  spoken_response: SpokenOutput;
  products: Product[];
  suggested_actions: string[];
  comparison?: ComparisonData;
  debug?: DebugInfo;
}
