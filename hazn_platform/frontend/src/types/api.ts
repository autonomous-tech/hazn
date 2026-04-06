/**
 * TypeScript types matching Django DRF serializer shapes.
 *
 * These types correspond to the workspace API serializers defined in
 * hazn_platform/workspace/serializers.py and the orchestrator
 * serializers used for nested workflow detail.
 *
 * All IDs are UUIDs (string). Timestamps are ISO 8601 strings.
 * Decimal fields (cost) are serialized as strings by DRF.
 */

// ----- Core Models -----

export interface Agency {
  id: string;
  name: string;
  slug: string;
  house_style: Record<string, unknown>;
  methodology: Record<string, unknown>;
  tool_preferences: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface EndClient {
  id: string;
  agency: string;
  name: string;
  slug: string;
  competitors: string[];
  created_at: string;
  updated_at: string;
}

export interface BrandVoice {
  id: string;
  end_client: string;
  content: string;
  version: number;
  is_active: boolean;
  created_at: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  name: string;
  agency: string | null;
  agency_role: "admin" | "member";
}

// ----- Workflow Models -----

export type WorkflowRunStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "timed_out"
  | "waiting_for_input";

export interface WorkflowRun {
  id: string;
  workflow_name: string;
  agency: string;
  end_client: string;
  status: WorkflowRunStatus;
  total_tokens: number;
  total_cost: string;
  started_at: string | null;
  ended_at: string | null;
  triggered_by: string;
  created_at: string;
}

export interface WorkflowRunDetail extends WorkflowRun {
  wall_clock_seconds: number;
  last_activity_at: string;
  error_details: Record<string, unknown>;
  celery_task_id: string;
  agents: WorkflowAgent[];
  tool_calls: WorkflowToolCall[];
  phase_outputs: WorkflowPhaseOutput[];
  chat_messages: ChatMessage[];
}

export interface WorkflowAgent {
  id: string;
  workflow_run: string;
  agent_id: string;
  agent_type: string;
  phase_id: string;
  total_tokens: number;
  total_cost: string;
  started_at: string | null;
  ended_at: string | null;
  created_at: string;
}

export interface WorkflowToolCall {
  id: string;
  workflow_run: string;
  tool_name: string;
  call_count: number;
  total_cost: string;
  avg_latency_ms: number;
  created_at: string;
}

export interface WorkflowPhaseOutput {
  id: string;
  workflow_run: string;
  phase_id: string;
  output_type: string;
  content: Record<string, unknown>;
  summary: string;
  created_at: string;
}

export interface WorkflowCatalogItem {
  name: string;
  description: string;
  phases: { id: string; name: string; agent: string | null }[];
  estimated_duration: string;
  parameters: unknown[];
  estimated_cost: number | null;
}

// ----- Chat Models -----

export interface ChatMessage {
  id: string;
  workflow_run: string;
  role: "user" | "agent" | "system";
  content: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

// ----- Deliverable Models -----

export interface Deliverable {
  id: string;
  workflow_run: string;
  phase_output: string;
  task_type: string;
  title: string;
  preview_url: string;
  html_content: string;
  markdown_source: string;
  created_at: string;
  updated_at: string;
}

// ----- Dashboard -----

export interface DashboardData {
  running_workflows: number;
  ready_deliverables: number;
  recent_activity: ActivityItem[];
}

export interface ActivityItem {
  type: string;
  title: string;
  timestamp: string;
  [key: string]: unknown;
}

// ----- Memory -----

export interface MemoryBlock {
  id: string;
  text: string;
  metadata: Record<string, unknown>;
  score?: number;
  created_at?: string;
}

export interface MemorySearchResult {
  results: MemoryBlock[];
  query: string;
  agent_type?: string;
}

// ----- API Response Wrappers -----

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface WorkflowTriggerResponse {
  run_id: string;
  celery_task_id: string;
  message: string;
}
