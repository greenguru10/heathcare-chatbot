export type RiskLevel = 'green' | 'yellow' | 'orange' | 'red' | 'blocked';
export type ResponseMode = 'grounded_answer' | 'emergency' | 'safety_refusal' | 'clarification' | 'insufficient_evidence';

export interface SourceCitation {
  citation_key: string;
  title: string;
  source_name: string;
  authority_tier: string;
  section?: string;
  publication_date?: string;
  last_updated?: string;
  url?: string;
  excerpt: string;
}

export interface ConfidenceInfo {
  score: number;
  label: 'high' | 'medium' | 'low' | 'insufficient';
  explanation: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  response_mode?: ResponseMode;
  risk_level?: RiskLevel;
  key_points?: string[];
  when_to_seek_care?: string;
  limitations?: string;
  confidence?: ConfidenceInfo;
  sources?: SourceCitation[];
  follow_up_suggestions?: string[];
  created_at?: string;
}

export interface SourceItem {
  id: string;
  name: string;
  base_url: string;
  authority_tier: string;
  authority_score: number;
  source_type: string;
  license_notes?: string;
  active: boolean;
}

export interface CategoryItem {
  id: number;
  slug: string;
  display_name: string;
  description?: string;
  active: boolean;
}

export interface DocumentItem {
  id: string;
  title: string;
  source_id: string;
  category_id: number;
  document_type: string;
  source_url?: string;
  language: string;
  publication_date?: string;
  last_updated?: string;
  status: string;
  source_name?: string;
  category_slug?: string;
  chunk_count?: number;
  created_at: string;
}

export interface SessionSummary {
  id: string;
  title: string;
  message_count: number;
  user_id?: string;
  created_at: string;
  updated_at: string;
  last_message_preview?: string;
  risk_level?: string;
}

export interface SessionDetail {
  id: string;
  title: string;
  user_id?: string;
  created_at: string;
  updated_at: string;
  state_json: Record<string, any>;
  messages: Array<{
    id: string;
    role: string;
    content: string;
    metadata_json: Record<string, any>;
    created_at: string;
  }>;
}
