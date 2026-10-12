export type VerificationStatus = 
  | 'VERIFIED'
  | 'VERIFIED WITH METADATA ISSUES'
  | 'POSSIBLE MATCH'
  | 'NOT FOUND'
  | 'DUPLICATE'
  | 'INVALID DOI';

export type IssueSeverity = 'CRITICAL' | 'WARNING' | 'INFO';

export type IssueType =
  | 'INVALID_DOI'
  | 'METADATA_MISMATCH'
  | 'POSSIBLE_UNMATCHED'
  | 'NOT_FOUND'
  | 'DUPLICATE_REFERENCE'
  | 'ORPHAN_CITATION'
  | 'UNUSED_REFERENCE'
  | 'POTENTIAL_MISSING_CITATION'
  | 'SEMANTIC_MISMATCH';

export type HealthRating = 'Excellent' | 'Good' | 'Needs Review' | 'Poor' | 'Pending' | 'Inconclusive';

export interface MetadataMismatch {
  field: string;
  reference_value: string;
  db_value: string;
  explanation: string;
}

export interface VerificationResult {
  id: string;
  reference_id: string;
  status: VerificationStatus;
  confidence: number;
  overall_score: number;
  title_similarity: number;
  author_similarity: number;
  year_match: boolean;
  year_difference: number;
  venue_similarity: number;
  doi_match: boolean;
  doi_status: string;
  matched_title?: string;
  matched_authors?: string[];
  matched_year?: string;
  matched_venue?: string;
  matched_publisher?: string;
  matched_doi?: string;
  matched_url?: string;
  matched_abstract?: string;
  citation_count?: number;
  verification_sources?: string[];
  openalex_match?: any;
  crossref_match?: any;
  semantic_scholar_match?: any;
  explanation?: string;
  metadata_mismatches?: MetadataMismatch[];
  created_at?: string;
}

export interface ReferenceDetail {
  id: string;
  paper_id: string;
  reference_number: number;
  raw_text: string;
  title?: string;
  authors: string[];
  year?: number;
  journal?: string;
  conference?: string;
  venue?: string;
  publisher?: string;
  volume?: string;
  issue?: string;
  pages?: string;
  doi?: string;
  url?: string;
  citation_format: string;
  created_at?: string;
  verification_result?: VerificationResult;
}

export interface CitationOccurrence {
  id: string;
  paper_id: string;
  reference_id?: string;
  reference_title?: string;
  reference_authors?: string[];
  reference_year?: number;
  citation_marker: string;
  page_number: number;
  sentence: string;
  section: string;
  claim_text?: string;
  semantic_relevance_score: number;
  semantic_status: 'STRONGLY RELATED' | 'RELATED' | 'WEAKLY RELATED' | 'LOW RELEVANCE' | 'INSUFFICIENT EVIDENCE';
  explanation?: string;
  created_at?: string;
}

export interface PaperIssue {
  id: string;
  paper_id: string;
  reference_id?: string;
  reference_number?: number;
  reference_title?: string;
  issue_type: IssueType;
  severity: IssueSeverity;
  title: string;
  description: string;
  details?: any;
  created_at?: string;
}

export interface PaperSection {
  title: string;
  start_page: number;
  raw_heading?: string;
}

export interface PaperStats {
  demo?: boolean;
  verification_limitations?: string[];
  verification_coverage_pct?: number;
  page_count: number;
  word_count: number;
  character_count: number;
  reading_time_minutes: number;
  figures_count: number;
  tables_count: number;
}

export interface ScoreBreakdown {
  verification_score: number;
  metadata_score: number;
  coverage_score: number;
  consistency_score: number;
  hygiene_score: number;
}

export interface PaperDetail {
  id: string;
  filename: string;
  file_size_bytes: number;
  page_count: number;
  title?: string;
  authors: string[];
  corresponding_author?: string;
  publication_date?: string;
  publication_year?: number;
  journal?: string;
  conference?: string;
  venue?: string;
  publisher?: string;
  doi?: string;
  url?: string;
  isbn_issn?: string;
  volume?: string;
  issue?: string;
  pages?: string;
  article_type?: string;
  open_access: boolean;
  citation_count: number;
  abstract?: string;
  ai_summary?: string;
  keywords: string[];
  sections: PaperSection[];
  paper_stats: PaperStats;
  health_score: number;
  health_rating: HealthRating;
  score_breakdown: ScoreBreakdown;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  progress_stage: string;
  error_message?: string;
  total_references?: number;
  verified_references?: number;
  created_at: string;
  updated_at: string;
}

export interface PaperSummary {
  id: string;
  filename: string;
  title?: string;
  authors: string[];
  publication_year?: number;
  journal?: string;
  conference?: string;
  doi?: string;
  health_score: number;
  health_rating: HealthRating;
  processing_status: string;
  progress_stage: string;
  total_references: number;
  verified_references: number;
  issue_count: number;
  created_at: string;
}

export interface PaperStatistics {
  total_references: number;
  verified_count: number;
  metadata_issues_count: number;
  possible_matches_count: number;
  not_found_count: number;
  duplicates_count: number;
  invalid_doi_count: number;
  citation_coverage_pct: number;
  semantic_relevance_pct: number;
  orphan_citations_count: number;
  unused_references_count: number;
  total_issues_count: number;
  critical_issues_count: number;
  warning_issues_count: number;
  info_issues_count: number;
  sources_distribution: Record<string, number>;
  confidence_distribution: Record<string, number>;
  health_score: number;
  health_rating: HealthRating;
  score_breakdown: ScoreBreakdown;
}
