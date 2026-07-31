// ==========================================
// DevShield Type Definitions
// ==========================================

export type SecurityLevel = 'low' | 'medium' | 'high' | 'critical';
export type Severity = 'Critical' | 'High' | 'Medium' | 'Low';
export type Language = 'python' | 'javascript' | 'typescript' | 'java' | 'cpp' | 'go' | 'rust';
export type AIProvider = 'gemini' | 'claude';
export type AIStatus = 'active' | 'fallback' | 'offline';
export type DocTab = 'readme' | 'api' | 'architecture' | 'security';
export type ExportFormat = 'pdf' | 'json' | 'csv' | 'markdown' | 'docx';

export interface Vulnerability {
  id: string;
  name: string;
  severity: Severity;
  cwe_id: string;
  owasp_category: string;
  line_number: number;
  description: string;
  fix_suggestion: string;
  confidence: number;
  fixed?: boolean;
}

export interface SecurityResult {
  overall_score: number;
  vulnerabilities: Vulnerability[];
  severity_distribution: Record<Severity, number>;
  owasp_heatmap: Record<string, number>;
  scan_duration_ms: number;
}

export interface GenerateCodeRequest {
  task: string;
  language: Language;
  security_level: SecurityLevel;
}

export interface GenerateCodeResponse {
  code: string;
  language: Language;
  confidence_score: number;
  token_count: number;
  estimated_cost: number;
  security_notes: string[];
  session_id: string;
}

export interface AutoFixRequest {
  code: string;
  vulnerabilities: Vulnerability[];
}

export interface AutoFixResponse {
  fixed_code: string;
  fixes_applied: FixApplied[];
  new_score: number;
}

export interface FixApplied {
  vulnerability_id: string;
  original_line: string;
  fixed_line: string;
  line_number: number;
  explanation: string;
}

export interface DocGenerationRequest {
  code: string;
  doc_type: DocTab;
}

export interface DocGenerationResponse {
  content: string;
  doc_type: DocTab;
  format: string;
}

export interface Session {
  id: string;
  task: string;
  language: Language;
  security_score: number;
  rating: number;
  created_at: string;
  status: 'completed' | 'failed' | 'in_progress';
  code_preview: string;
  vulnerabilities_found: number;
  vulnerabilities_fixed: number;
}

export interface HistoryFilters {
  search: string;
  language: Language | 'all';
  date_from: string;
  date_to: string;
  min_score: number;
  max_score: number;
  rating: number | null;
}

export interface FeedbackRequest {
  session_id: string;
  rating: number;
  text: string;
}

export interface DashboardMetrics {
  total_sessions: number;
  vulnerabilities_fixed: number;
  avg_security_score: number;
  lines_generated: number;
  recent_sessions: Session[];
  security_health: number;
}

export interface AnalyticsData {
  security_over_time: TimeSeriesPoint[];
  common_vulnerabilities: BarChartPoint[];
  language_distribution: PieChartPoint[];
  generation_volume: TimeSeriesPoint[];
  fix_acceptance_rate: number;
  weekly_activity: WeeklyActivity[];
}

export interface TimeSeriesPoint {
  date: string;
  value: number;
}

export interface BarChartPoint {
  name: string;
  count: number;
}

export interface PieChartPoint {
  name: string;
  value: number;
  color: string;
}

export interface WeeklyActivity {
  day: string;
  hour: number;
  count: number;
}

export interface UserPreferences {
  theme: 'dark' | 'light';
  default_language: Language;
  default_security_level: SecurityLevel;
  ai_provider: AIProvider;
  notifications_enabled: boolean;
  auto_scan: boolean;
  token_budget: number;
}
