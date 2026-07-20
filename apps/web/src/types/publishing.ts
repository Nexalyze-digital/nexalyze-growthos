import type { Platform } from "./content";

export type DraftStatus =
  | "generated"
  | "edited"
  | "ready_for_review"
  | "approved"
  | "rejected"
  | "scheduled"
  | "publishing"
  | "published"
  | "failed"
  | "archived";

export type ApprovalStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "revision_requested";

export type PublishingJobStatus =
  | "pending"
  | "processing"
  | "retry_pending"
  | "published"
  | "succeeded"
  | "failed"
  | "dead_letter"
  | "cancelled";

export type DraftFormValues = {
  title: string;
  body: string;
  platform: Platform;
  hashtags: string[];
  brand_id: string | null;
  source_research_run_id: string | null;
};

export type DraftUpdateValues = DraftFormValues & {
  expected_revision: number;
};

export type DraftVersion = {
  id: string;
  draft_id: string;
  version_number: number;
  title: string;
  body: string;
  hashtags: string[];
  created_by_user_id: string;
  created_at: string;
};

export type PublishingDraft = DraftFormValues & {
  id: string;
  workspace_id: string;
  status: DraftStatus;
  current_version_number: number;
  revision: number;
  created_by_user_id: string;
  updated_by_user_id: string;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
  latest_version: DraftVersion | null;
};

export type DraftListResponse = {
  drafts: PublishingDraft[];
  page: number;
  page_size: number;
  total: number;
};

export type ApprovalComment = {
  id: string;
  approval_id: string;
  user_id: string;
  comment_type: "note" | "rejection_reason" | "revision_request";
  body: string;
  created_at: string;
};

export type Approval = {
  id: string;
  draft_id: string;
  submitted_by_user_id: string;
  reviewed_by_user_id: string | null;
  status: ApprovalStatus;
  submitted_at: string;
  reviewed_at: string | null;
  comments: ApprovalComment[];
};

export type Schedule = {
  id: string;
  draft_id: string;
  draft_version_id: string;
  workspace_id: string;
  platform: Platform;
  scheduled_at_utc: string;
  workspace_timezone: string;
  status: "scheduled" | "unscheduled" | "publishing" | "published" | "failed";
  created_by_user_id: string;
  updated_by_user_id: string;
  created_at: string;
  updated_at: string;
};

export type PublishingAttempt = {
  id: string;
  job_id: string;
  attempt_number: number;
  status: PublishingJobStatus;
  provider_post_id: string | null;
  error_category: string | null;
  provider_response_summary: string | null;
  published_at: string | null;
  created_at: string;
};

export type PublishingJob = {
  id: string;
  workspace_id: string;
  draft_id: string;
  draft_version_id: string;
  schedule_id: string | null;
  platform: Platform;
  status: PublishingJobStatus;
  retry_count: number;
  next_retry_at: string | null;
  idempotency_key: string;
  error_category: string | null;
  provider_response_summary: string | null;
  created_at: string;
  updated_at: string;
  attempts: PublishingAttempt[];
};

export type ReviewHistory = {
  approvals: Approval[];
};
