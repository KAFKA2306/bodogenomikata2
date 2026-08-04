export type RuleSourceType =
  | 'OfficialRule'
  | 'ExtractedFact'
  | 'AIGeneratedSummary'
  | 'Translation'
  | 'HumanReview'
  | 'DatabaseObservation';

export interface RuleSource {
  id: string;
  title: string;
  url?: string | null;
  version?: string | null;
  page_or_section?: string | null;
  language?: string | null;
  source_type: RuleSourceType;
  review_status?: 'reviewed' | 'pending' | 'rejected';
}

export interface RuleAnswer {
  id: string;
  question_keywords: string[];
  answer: string;
  source_ids: string[];
  answer_type: 'OfficialRule' | 'ExtractedFact' | 'AIGeneratedSummary' | 'Translation';
  review_status: 'reviewed' | 'pending' | 'rejected';
  spoiler_level?: 'none' | 'minor' | 'major';
}

export interface Game {
  id: number;
  slug: string;
  title: string;
  title_ja?: string | null;
  description: string;
  image_url?: string | null;
  published_year: number;
  min_players: number;
  max_players: number;
  play_time: number;
  min_age: number;
  editions?: string[];
  structured_data?: {
    mechanics?: string[];
    source_documents?: RuleSource[];
    rule_answers?: RuleAnswer[];
  };
}
