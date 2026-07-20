"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import {
  Archive,
  CalendarDays,
  CheckCircle2,
  Copy,
  Eye,
  FileText,
  Filter,
  ListChecks,
  RefreshCw,
  RotateCcw,
  Save,
  Send,
  Settings,
  XCircle,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import {
  approvePublishingDraft,
  archivePublishingDraft,
  cancelPublishingJob,
  createPublishingDraft,
  duplicatePublishingDraft,
  enqueuePublishingDraft,
  getBrands,
  getPublishingDrafts,
  getPublishingJobs,
  getPublishingReviewHistory,
  getPublishingVersions,
  processPublishingJob,
  processPublishingQueue,
  rejectPublishingDraft,
  requestPublishingRevision,
  restorePublishingDraft,
  retryPublishingJob,
  schedulePublishingDraft,
  submitPublishingDraft,
  updatePublishingDraft,
} from "@/lib/api";
import { PLATFORM_OPTIONS, PUBLISHING_STATUS_OPTIONS } from "@/lib/constants";
import { canAdminWorkspace, canEditWorkspace, isWorkspaceOwner } from "@/lib/permissions";
import type { BrandBrain } from "@/types/brand";
import type { Platform } from "@/types/content";
import type { AuthSession, WorkspaceRole } from "@/types/auth";
import type {
  DraftFormValues,
  DraftStatus,
  DraftVersion,
  PublishingDraft,
  PublishingJob,
  ReviewHistory,
} from "@/types/publishing";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { SelectField } from "@/components/ui/SelectField";
import { TextAreaField } from "@/components/ui/TextAreaField";

type PublishingEngineProps = {
  role: WorkspaceRole;
  session: AuthSession;
};

type Tab = "library" | "editor" | "review" | "calendar" | "queue" | "settings";
type LoadState = "loading" | "ready" | "error";

const emptyDraft: DraftFormValues = {
  title: "",
  body: "",
  platform: "LinkedIn",
  hashtags: [],
  brand_id: null,
  source_research_run_id: null,
};

export function PublishingEngine({ role, session }: PublishingEngineProps) {
  const canEdit = canEditWorkspace(role);
  const canAdmin = canAdminWorkspace(role);
  const owner = isWorkspaceOwner(role);
  const activeWorkspace = session.workspaces.find(
    (workspace) => workspace.id === session.active_workspace_id,
  );

  const [activeTab, setActiveTab] = useState<Tab>("library");
  const [drafts, setDrafts] = useState<PublishingDraft[]>([]);
  const [jobs, setJobs] = useState<PublishingJob[]>([]);
  const [brands, setBrands] = useState<BrandBrain[]>([]);
  const [selectedDraft, setSelectedDraft] = useState<PublishingDraft | null>(null);
  const [versions, setVersions] = useState<DraftVersion[]>([]);
  const [reviewHistory, setReviewHistory] = useState<ReviewHistory>({ approvals: [] });
  const [formValues, setFormValues] = useState<DraftFormValues>(emptyDraft);
  const [initialFormSnapshot, setInitialFormSnapshot] = useState(JSON.stringify(emptyDraft));
  const [searchValue, setSearchValue] = useState("");
  const [platformFilter, setPlatformFilter] = useState<Platform | "">("");
  const [statusFilter, setStatusFilter] = useState<DraftStatus | "">("");
  const [showArchived, setShowArchived] = useState(false);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [status, setStatus] = useState<LoadState>("loading");
  const [message, setMessage] = useState("");
  const [reviewComment, setReviewComment] = useState("");
  const [scheduleDate, setScheduleDate] = useState("");
  const [scheduleTimezone, setScheduleTimezone] = useState("UTC");

  const unsaved = JSON.stringify(formValues) !== initialFormSnapshot;
  const pageSize = 8;

  const refreshAll = useCallback(async () => {
    setStatus("loading");
    setMessage("");
    try {
      const [draftPayload, brandPayload, jobPayload] = await Promise.all([
        getPublishingDrafts({
          archived: showArchived,
          page,
          page_size: pageSize,
          platform: platformFilter,
          search: searchValue,
          status: statusFilter,
        }),
        getBrands(),
        getPublishingJobs(),
      ]);
      setDrafts(draftPayload.drafts);
      setTotal(draftPayload.total);
      setBrands(brandPayload);
      setJobs(jobPayload);
      if (!selectedDraft && draftPayload.drafts[0]) {
        selectDraft(draftPayload.drafts[0], false);
      }
      setStatus("ready");
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "Publishing is unavailable.");
    }
  }, [page, platformFilter, searchValue, selectedDraft, showArchived, statusFilter]);

  useEffect(() => {
    window.setTimeout(() => {
      void refreshAll();
    }, 0);
  }, [refreshAll, session.active_workspace_id]);

  useEffect(() => {
    const warning = (event: BeforeUnloadEvent) => {
      if (!unsaved) {
        return;
      }
      event.preventDefault();
    };
    window.addEventListener("beforeunload", warning);
    return () => window.removeEventListener("beforeunload", warning);
  }, [unsaved]);

  async function applyFilters(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    setPage(1);
    await refreshAll();
  }

  async function selectDraft(draft: PublishingDraft, switchTab = true) {
    setSelectedDraft(draft);
    setFormValues(toFormValues(draft));
    setInitialFormSnapshot(JSON.stringify(toFormValues(draft)));
    setMessage("");
    try {
      const [versionPayload, historyPayload] = await Promise.all([
        getPublishingVersions(draft.id),
        getPublishingReviewHistory(draft.id),
      ]);
      setVersions(versionPayload);
      setReviewHistory(historyPayload);
    } catch {
      setVersions([]);
      setReviewHistory({ approvals: [] });
    }
    if (switchTab) {
      setActiveTab("editor");
    }
  }

  function startNewDraft() {
    if (!canEdit) {
      return;
    }
    setSelectedDraft(null);
    setVersions([]);
    setReviewHistory({ approvals: [] });
    setFormValues(emptyDraft);
    setInitialFormSnapshot(JSON.stringify(emptyDraft));
    setActiveTab("editor");
  }

  async function saveDraft(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    if (!canEdit || formValues.title.trim().length < 2 || formValues.body.trim().length < 1) {
      setMessage("Title and body are required before saving a draft.");
      return;
    }
    setMessage("");
    try {
      const saved = selectedDraft
        ? await updatePublishingDraft(selectedDraft.id, {
            ...normalizeDraft(formValues),
            expected_revision: selectedDraft.revision,
          })
        : await createPublishingDraft(normalizeDraft(formValues));
      setSelectedDraft(saved);
      setFormValues(toFormValues(saved));
      setInitialFormSnapshot(JSON.stringify(toFormValues(saved)));
      setMessage("Draft saved as a new version.");
      await refreshAll();
      await selectDraft(saved, false);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to save draft.");
    }
  }

  async function runDraftAction(action: "duplicate" | "archive" | "restore" | "submit") {
    if (!selectedDraft) {
      return;
    }
    try {
      if (action === "duplicate") {
        const duplicate = await duplicatePublishingDraft(selectedDraft.id);
        await refreshAll();
        await selectDraft(duplicate);
        setMessage("Draft duplicated.");
      }
      if (action === "archive") {
        const archived = await archivePublishingDraft(selectedDraft.id);
        await refreshAll();
        await selectDraft(archived, false);
        setMessage("Draft archived.");
      }
      if (action === "restore") {
        const restored = await restorePublishingDraft(selectedDraft.id);
        await refreshAll();
        await selectDraft(restored, false);
        setMessage("Draft restored.");
      }
      if (action === "submit") {
        await submitPublishingDraft(selectedDraft.id);
        await refreshAll();
        setActiveTab("review");
        setMessage("Draft submitted for review.");
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Draft action failed.");
    }
  }

  async function review(action: "approve" | "reject" | "revision") {
    if (!selectedDraft || !canAdmin) {
      return;
    }
    try {
      if (action === "approve") {
        await approvePublishingDraft(selectedDraft.id, reviewComment || "Approved.");
      }
      if (action === "reject") {
        await rejectPublishingDraft(selectedDraft.id, reviewComment || "Rejected.");
      }
      if (action === "revision") {
        await requestPublishingRevision(selectedDraft.id, reviewComment || "Please revise this draft.");
      }
      setReviewComment("");
      await refreshAll();
      const updated = (await getPublishingDrafts({ page_size: 100 })).drafts.find(
        (draft) => draft.id === selectedDraft.id,
      );
      if (updated) {
        await selectDraft(updated, false);
      }
      setMessage("Review updated.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to update review.");
    }
  }

  async function scheduleSelected() {
    if (!selectedDraft || !canAdmin || !scheduleDate) {
      setMessage("Choose an approved draft and future schedule date.");
      return;
    }
    try {
      await schedulePublishingDraft(
        selectedDraft.id,
        new Date(scheduleDate).toISOString(),
        scheduleTimezone,
      );
      await refreshAll();
      setMessage("Draft scheduled.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to schedule draft.");
    }
  }

  async function enqueueSelected() {
    if (!selectedDraft || !canAdmin) {
      return;
    }
    try {
      await enqueuePublishingDraft(selectedDraft.id);
      setJobs(await getPublishingJobs());
      setActiveTab("queue");
      setMessage("Draft added to the publishing queue.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to enqueue draft.");
    }
  }

  async function processNextJob() {
    try {
      const processed = await processPublishingQueue();
      setJobs(await getPublishingJobs());
      setMessage(processed.length ? "Publishing queue processed." : "No processable jobs are ready.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to process publishing queue.");
    }
  }

  async function runJobAction(jobId: string, action: "retry" | "cancel" | "process") {
    try {
      if (action === "retry") {
        await retryPublishingJob(jobId);
      } else if (action === "cancel") {
        await cancelPublishingJob(jobId);
      } else {
        await processPublishingJob(jobId);
      }
      setJobs(await getPublishingJobs());
      setMessage(action === "retry" ? "Retry queued." : action === "cancel" ? "Job cancelled." : "Publishing job processed.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Queue action failed.");
    }
  }

  const brandNameById = useMemo(
    () => Object.fromEntries(brands.map((brand) => [brand.id, brand.brand_name])),
    [brands],
  );
  const reviewDrafts = drafts.filter((draft) => draft.status === "ready_for_review");
  const approvedDrafts = drafts.filter((draft) => draft.status === "approved" || draft.status === "scheduled");
  const calendarDrafts = drafts.filter((draft) => draft.status === "scheduled");

  return (
    <section aria-labelledby="publishing-title" className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm font-medium text-sky-300">Publishing Engine</p>
          <h2 id="publishing-title" className="mt-2 text-2xl font-semibold tracking-tight text-white">
            Govern drafts, reviews, schedules, and queue readiness
          </h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
            Workspace-scoped publishing workflows for {activeWorkspace?.name || "the active workspace"}.
          </p>
        </div>
        {canEdit ? (
          <Button className="sm:w-auto" icon={FileText} onClick={startNewDraft} type="button">
            New draft
          </Button>
        ) : null}
      </div>

      <div className="flex gap-2 overflow-x-auto pb-1" role="tablist" aria-label="Publishing sections">
        {publishingTabs.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            aria-selected={activeTab === key}
            className={
              activeTab === key
                ? "inline-flex min-h-10 items-center gap-2 rounded-lg bg-sky-300 px-4 text-sm font-semibold text-slate-950"
                : "inline-flex min-h-10 items-center gap-2 rounded-lg border border-white/10 bg-white/[0.03] px-4 text-sm font-semibold text-slate-300 hover:bg-white/[0.07] focus:outline-none focus:ring-2 focus:ring-sky-300"
            }
            onClick={() => setActiveTab(key)}
            role="tab"
            type="button"
          >
            <Icon className="h-4 w-4" aria-hidden="true" />
            {label}
          </button>
        ))}
      </div>

      {message ? (
        <p className="rounded-lg border border-sky-300/20 bg-sky-300/10 px-4 py-3 text-sm text-sky-100" role="status">
          {message}
        </p>
      ) : null}

      {status === "loading" ? <Skeleton /> : null}
      {status === "error" ? (
        <Card>
          <p className="font-medium text-red-100">Publishing API unavailable</p>
          <p className="mt-2 text-sm text-red-200/85">{message}</p>
          <Button className="mt-4 sm:w-auto" icon={RefreshCw} onClick={refreshAll} type="button" variant="secondary">
            Retry
          </Button>
        </Card>
      ) : null}

      {status !== "error" && activeTab === "library" ? (
        <Library
          brandNameById={brandNameById}
          canEdit={canEdit}
          drafts={drafts}
          onAction={runDraftAction}
          onFilter={applyFilters}
          onRefresh={refreshAll}
          onSelect={selectDraft}
          page={page}
          pageSize={pageSize}
          platformFilter={platformFilter}
          searchValue={searchValue}
          selectedDraft={selectedDraft}
          setPage={setPage}
          setPlatformFilter={setPlatformFilter}
          setSearchValue={setSearchValue}
          setShowArchived={setShowArchived}
          setStatusFilter={setStatusFilter}
          showArchived={showArchived}
          statusFilter={statusFilter}
          total={total}
        />
      ) : null}

      {status !== "error" && activeTab === "editor" ? (
        <Editor
          brandNameById={brandNameById}
          brands={brands}
          canAdmin={canAdmin}
          canEdit={canEdit}
          formValues={formValues}
          onChange={setFormValues}
          onDraftAction={runDraftAction}
          onEnqueue={enqueueSelected}
          onSave={saveDraft}
          onSchedule={scheduleSelected}
          scheduleDate={scheduleDate}
          scheduleTimezone={scheduleTimezone}
          selectedDraft={selectedDraft}
          setScheduleDate={setScheduleDate}
          setScheduleTimezone={setScheduleTimezone}
          unsaved={unsaved}
          versions={versions}
        />
      ) : null}

      {status !== "error" && activeTab === "review" ? (
        <ReviewQueue
          canAdmin={canAdmin}
          canEdit={canEdit}
          drafts={reviewDrafts}
          onReview={review}
          onSelect={selectDraft}
          reviewComment={reviewComment}
          reviewHistory={reviewHistory}
          selectedDraft={selectedDraft}
          setReviewComment={setReviewComment}
        />
      ) : null}

      {status !== "error" && activeTab === "calendar" ? (
        <CalendarView
          canAdmin={canAdmin}
          drafts={calendarDrafts.length ? calendarDrafts : approvedDrafts}
          onSchedule={scheduleSelected}
          onSelect={selectDraft}
          scheduleDate={scheduleDate}
          scheduleTimezone={scheduleTimezone}
          selectedDraft={selectedDraft}
          setScheduleDate={setScheduleDate}
          setScheduleTimezone={setScheduleTimezone}
        />
      ) : null}

      {status !== "error" && activeTab === "queue" ? (
        <QueueView canAdmin={canAdmin} jobs={jobs} onJobAction={runJobAction} onProcessNext={processNextJob} />
      ) : null}

      {status !== "error" && activeTab === "settings" ? (
        <SettingsView owner={owner} role={role} workspaceName={activeWorkspace?.name || "Active workspace"} />
      ) : null}
    </section>
  );
}

function Library(props: {
  brandNameById: Record<string, string>;
  canEdit: boolean;
  drafts: PublishingDraft[];
  onAction: (action: "duplicate" | "archive" | "restore" | "submit") => void;
  onFilter: (event?: FormEvent<HTMLFormElement>) => void;
  onRefresh: () => void;
  onSelect: (draft: PublishingDraft) => void;
  page: number;
  pageSize: number;
  platformFilter: Platform | "";
  searchValue: string;
  selectedDraft: PublishingDraft | null;
  setPage: (page: number) => void;
  setPlatformFilter: (value: Platform | "") => void;
  setSearchValue: (value: string) => void;
  setShowArchived: (value: boolean) => void;
  setStatusFilter: (value: DraftStatus | "") => void;
  showArchived: boolean;
  statusFilter: DraftStatus | "";
  total: number;
}) {
  const pageCount = Math.max(1, Math.ceil(props.total / props.pageSize));
  return (
    <div className="space-y-4">
      <Card>
        <form className="grid gap-3 md:grid-cols-[1fr_180px_180px_auto]" onSubmit={props.onFilter}>
          <Field id="publishing-search" label="Search" onChange={props.setSearchValue} value={props.searchValue} />
          <SelectField
            id="publishing-platform-filter"
            label="Platform"
            onChange={props.setPlatformFilter}
            options={["", ...PLATFORM_OPTIONS]}
            value={props.platformFilter}
          />
          <SelectField
            id="publishing-status-filter"
            label="Status"
            onChange={props.setStatusFilter}
            options={["", ...PUBLISHING_STATUS_OPTIONS]}
            value={props.statusFilter}
          />
          <div className="flex items-end gap-2">
            <Button icon={Filter} type="submit" variant="secondary">Filter</Button>
            <button
              className="min-h-11 rounded-lg border border-white/10 px-3 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-300"
              onClick={() => props.setShowArchived(!props.showArchived)}
              type="button"
            >
              {props.showArchived ? "Active" : "Archived"}
            </button>
          </div>
        </form>
      </Card>
      <div className="overflow-hidden rounded-lg border border-white/10">
        <div className="hidden grid-cols-[1.4fr_0.7fr_0.9fr_0.7fr_0.9fr_0.7fr_1fr] bg-white/[0.04] px-4 py-3 text-xs font-semibold uppercase text-slate-400 md:grid">
          <span>Draft</span><span>Platform</span><span>Brand</span><span>Status</span><span>Workspace</span><span>Version</span><span>Actions</span>
        </div>
        {props.drafts.length === 0 ? (
          <div className="p-6 text-sm text-slate-400">No publishing drafts match the current filters.</div>
        ) : null}
        {props.drafts.map((draft) => (
          <div
            key={draft.id}
            className="grid gap-3 border-t border-white/10 px-4 py-4 text-sm text-slate-300 md:grid-cols-[1.4fr_0.7fr_0.9fr_0.7fr_0.9fr_0.7fr_1fr]"
          >
            <button className="text-left font-medium text-white focus:outline-none focus:ring-2 focus:ring-sky-300" onClick={() => props.onSelect(draft)} type="button">
              {draft.title}
              <span className="block text-xs font-normal text-slate-500">Modified {formatDate(draft.updated_at)}</span>
            </button>
            <span>{draft.platform}</span>
            <span>{draft.brand_id ? props.brandNameById[draft.brand_id] || "Linked brand" : "No brand"}</span>
            <StatusBadge status={draft.status} />
            <span>{draft.workspace_id.slice(0, 8)}</span>
            <span>v{draft.current_version_number}</span>
            <div className="flex flex-wrap gap-2">
              <IconButton label="View" icon={Eye} onClick={() => props.onSelect(draft)} />
              {props.canEdit ? <IconButton label="Duplicate" icon={Copy} onClick={() => { props.onSelect(draft); props.onAction("duplicate"); }} /> : null}
              {props.canEdit && draft.archived_at ? <IconButton label="Restore" icon={RotateCcw} onClick={() => { props.onSelect(draft); props.onAction("restore"); }} /> : null}
              {props.canEdit && !draft.archived_at ? <IconButton label="Archive" icon={Archive} onClick={() => { props.onSelect(draft); props.onAction("archive"); }} /> : null}
              {props.canEdit ? <IconButton label="Submit" icon={Send} onClick={() => { props.onSelect(draft); props.onAction("submit"); }} /> : null}
            </div>
          </div>
        ))}
      </div>
      <div className="flex items-center justify-between text-sm text-slate-400">
        <span>Page {props.page} of {pageCount}</span>
        <div className="flex gap-2">
          <Button className="w-auto" disabled={props.page <= 1} onClick={() => { props.setPage(props.page - 1); props.onRefresh(); }} type="button" variant="secondary">Previous</Button>
          <Button className="w-auto" disabled={props.page >= pageCount} onClick={() => { props.setPage(props.page + 1); props.onRefresh(); }} type="button" variant="secondary">Next</Button>
        </div>
      </div>
    </div>
  );
}

function Editor(props: {
  brandNameById: Record<string, string>;
  brands: BrandBrain[];
  canAdmin: boolean;
  canEdit: boolean;
  formValues: DraftFormValues;
  onChange: (value: DraftFormValues) => void;
  onDraftAction: (action: "duplicate" | "archive" | "restore" | "submit") => void;
  onEnqueue: () => void;
  onSave: (event?: FormEvent<HTMLFormElement>) => void;
  onSchedule: () => void;
  scheduleDate: string;
  scheduleTimezone: string;
  selectedDraft: PublishingDraft | null;
  setScheduleDate: (value: string) => void;
  setScheduleTimezone: (value: string) => void;
  unsaved: boolean;
  versions: DraftVersion[];
}) {
  const value = props.formValues;
  const characters = value.body.length;
  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_380px]">
      <form className="space-y-4" onSubmit={props.onSave}>
        <Card className="grid gap-4 md:grid-cols-2">
          <Field id="publishing-title-field" label="Title" onChange={(title) => props.onChange({ ...value, title })} required value={value.title} />
          <SelectField id="publishing-platform" label="Platform" onChange={(platform) => props.onChange({ ...value, platform })} options={PLATFORM_OPTIONS} value={value.platform} />
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-200" htmlFor="publishing-brand">Brand</label>
            <select
              className="w-full rounded-lg border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white outline-none focus:border-sky-300 focus:ring-2 focus:ring-sky-300/25"
              id="publishing-brand"
              onChange={(event) => props.onChange({ ...value, brand_id: event.target.value || null })}
              value={value.brand_id || ""}
            >
              <option value="">No Brand Brain</option>
              {props.brands.map((brand) => <option key={brand.id} value={brand.id}>{brand.brand_name}</option>)}
            </select>
          </div>
          <Field id="publishing-hashtags" label="Hashtags" onChange={(text) => props.onChange({ ...value, hashtags: splitTags(text) })} value={value.hashtags.join(" ")} />
          <div className="md:col-span-2">
            <TextAreaField id="publishing-body" label="Rich text draft body" maxLength={10000} onChange={(body) => props.onChange({ ...value, body })} value={value.body} />
          </div>
        </Card>
        <div className="flex flex-wrap gap-3">
          {props.canEdit ? <Button className="w-auto" icon={Save} type="submit">{props.selectedDraft ? "Save new version" : "Create draft"}</Button> : null}
          {props.canEdit && props.selectedDraft ? <Button className="w-auto" icon={Send} onClick={() => props.onDraftAction("submit")} type="button" variant="secondary">Submit</Button> : null}
          {props.canEdit && props.selectedDraft ? <Button className="w-auto" icon={Copy} onClick={() => props.onDraftAction("duplicate")} type="button" variant="secondary">Duplicate</Button> : null}
        </div>
      </form>
      <div className="space-y-4">
        <Card>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Preview</h3>
            {props.unsaved ? <span className="text-xs text-amber-200">Unsaved changes</span> : null}
          </div>
          <p className="mt-3 text-xs text-slate-500">{characters} characters · {value.platform}</p>
          <div className="mt-4 rounded-lg border border-white/10 bg-slate-950/60 p-4">
            <p className="font-semibold text-white">{value.title || "Untitled draft"}</p>
            <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-300">{value.body || "Draft copy preview appears here."}</p>
            <p className="mt-3 text-sm text-sky-300">{value.hashtags.join(" ")}</p>
          </div>
        </Card>
        <Card>
          <h3 className="text-lg font-semibold text-white">Version history</h3>
          <div className="mt-3 space-y-2">
            {props.versions.length === 0 ? <p className="text-sm text-slate-400">No versions yet.</p> : null}
            {props.versions.map((version) => (
              <details key={version.id} className="rounded-lg border border-white/10 p-3 text-sm text-slate-300">
                <summary className="cursor-pointer font-medium text-white">Version {version.version_number} · {formatDate(version.created_at)}</summary>
                <p className="mt-2">{version.title}</p>
              </details>
            ))}
          </div>
        </Card>
        <Card>
          <h3 className="text-lg font-semibold text-white">Schedule and queue</h3>
          <div className="mt-3 grid gap-3">
            <input className="rounded-lg border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white" onChange={(event) => props.setScheduleDate(event.target.value)} type="datetime-local" value={props.scheduleDate} />
            <Field id="publishing-timezone" label="Timezone" onChange={props.setScheduleTimezone} value={props.scheduleTimezone} />
            {props.canAdmin ? <Button icon={CalendarDays} onClick={props.onSchedule} type="button" variant="secondary">Schedule approved draft</Button> : null}
            {props.canAdmin ? <Button icon={Send} onClick={props.onEnqueue} type="button" variant="secondary">Enqueue draft</Button> : null}
          </div>
        </Card>
      </div>
    </div>
  );
}

function ReviewQueue(props: {
  canAdmin: boolean;
  canEdit: boolean;
  drafts: PublishingDraft[];
  onReview: (action: "approve" | "reject" | "revision") => void;
  onSelect: (draft: PublishingDraft) => void;
  reviewComment: string;
  reviewHistory: ReviewHistory;
  selectedDraft: PublishingDraft | null;
  setReviewComment: (value: string) => void;
}) {
  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,0.9fr)_minmax(360px,1fr)]">
      <Card>
        <h3 className="text-lg font-semibold text-white">Review queue</h3>
        <div className="mt-4 space-y-3">
          {props.drafts.length === 0 ? <p className="text-sm text-slate-400">No drafts are waiting for review.</p> : null}
          {props.drafts.map((draft) => (
            <button key={draft.id} className="w-full rounded-lg border border-white/10 p-4 text-left text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-sky-300" onClick={() => props.onSelect(draft)} type="button">
              <span className="block font-medium text-white">{draft.title}</span>
              <span className="mt-1 block text-xs text-slate-500">{draft.platform} · version {draft.current_version_number}</span>
            </button>
          ))}
        </div>
      </Card>
      <Card>
        <h3 className="text-lg font-semibold text-white">{props.selectedDraft?.title || "Select a draft"}</h3>
        <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-300">{props.selectedDraft?.body || "Review comments and actions appear after selecting a draft."}</p>
        <TextAreaField id="review-comment" label="Review comment" onChange={props.setReviewComment} value={props.reviewComment} />
        {props.canAdmin ? (
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <Button icon={CheckCircle2} onClick={() => props.onReview("approve")} type="button" variant="secondary">Approve</Button>
            <Button icon={XCircle} onClick={() => props.onReview("reject")} type="button" variant="secondary">Reject</Button>
            <Button icon={RefreshCw} onClick={() => props.onReview("revision")} type="button" variant="secondary">Revision</Button>
          </div>
        ) : props.canEdit ? <p className="mt-4 text-sm text-slate-400">Editors can submit and view comments. Admin or owner approval is required.</p> : null}
        <div className="mt-5 space-y-2">
          {props.reviewHistory.approvals.map((approval) => (
            <div key={approval.id} className="rounded-lg border border-white/10 p-3 text-sm text-slate-300">
              <p className="font-medium text-white">{approval.status}</p>
              {approval.comments.map((comment) => <p key={comment.id} className="mt-2">{comment.comment_type}: {comment.body}</p>)}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

function CalendarView(props: {
  canAdmin: boolean;
  drafts: PublishingDraft[];
  onSchedule: () => void;
  onSelect: (draft: PublishingDraft) => void;
  scheduleDate: string;
  scheduleTimezone: string;
  selectedDraft: PublishingDraft | null;
  setScheduleDate: (value: string) => void;
  setScheduleTimezone: (value: string) => void;
}) {
  const [view, setView] = useState<"month" | "week" | "day">("month");
  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
      <Card>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h3 className="text-lg font-semibold text-white">Publishing calendar</h3>
          <div className="flex gap-2">
            {(["month", "week", "day"] as const).map((item) => (
              <button key={item} className={view === item ? "rounded-lg bg-sky-300 px-3 py-2 text-sm font-semibold text-slate-950" : "rounded-lg border border-white/10 px-3 py-2 text-sm text-slate-300"} onClick={() => setView(item)} type="button">
                {item}
              </button>
            ))}
          </div>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-3">
          {Array.from({ length: view === "day" ? 1 : view === "week" ? 7 : 12 }).map((_, index) => (
            <div key={index} className="min-h-28 rounded-lg border border-white/10 bg-slate-950/50 p-3">
              <p className="text-xs font-medium text-slate-500">{view} slot {index + 1}</p>
              {props.drafts[index] ? (
                <button className="mt-3 w-full rounded-lg bg-white/[0.04] p-3 text-left text-sm text-white focus:outline-none focus:ring-2 focus:ring-sky-300" draggable onClick={() => props.onSelect(props.drafts[index])} type="button">
                  {props.drafts[index].title}
                </button>
              ) : null}
            </div>
          ))}
        </div>
      </Card>
      <Card>
        <h3 className="text-lg font-semibold text-white">Schedule draft</h3>
        <p className="mt-2 text-sm text-slate-400">{props.selectedDraft ? props.selectedDraft.title : "Select an approved draft to schedule."}</p>
        <div className="mt-4 grid gap-3">
          <input className="rounded-lg border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white" onChange={(event) => props.setScheduleDate(event.target.value)} type="datetime-local" value={props.scheduleDate} />
          <Field id="calendar-timezone" label="Timezone" onChange={props.setScheduleTimezone} value={props.scheduleTimezone} />
          {props.canAdmin ? <Button icon={CalendarDays} onClick={props.onSchedule} type="button">Schedule</Button> : null}
          <p className="text-xs leading-5 text-slate-500">Conflict warnings come from the backend as `409 Conflict` responses.</p>
        </div>
      </Card>
    </div>
  );
}

function QueueView({
  canAdmin,
  jobs,
  onJobAction,
  onProcessNext,
}: {
  canAdmin: boolean;
  jobs: PublishingJob[];
  onJobAction: (jobId: string, action: "retry" | "cancel" | "process") => void;
  onProcessNext: () => void;
}) {
  return (
    <Card>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h3 className="text-lg font-semibold text-white">Publishing queue</h3>
        {canAdmin ? (
          <Button className="sm:w-auto" icon={Send} onClick={onProcessNext} type="button" variant="secondary">
            Process next
          </Button>
        ) : null}
      </div>
      <div className="mt-4 space-y-3">
        {jobs.length === 0 ? <p className="text-sm text-slate-400">No publishing jobs are queued yet.</p> : null}
        {jobs.map((job) => (
          <details key={job.id} className="rounded-lg border border-white/10 p-4 text-sm text-slate-300">
            <summary className="cursor-pointer font-medium text-white">{job.platform} · {job.status} · retries {job.retry_count}</summary>
            <p className="mt-2 text-xs text-slate-500">Idempotency: {job.idempotency_key}</p>
            {job.provider_response_summary ? <p className="mt-2 text-xs text-slate-400">{job.provider_response_summary}</p> : null}
            <div className="mt-3 flex flex-wrap gap-2">
              {canAdmin ? <IconButton label="Process" icon={Send} onClick={() => onJobAction(job.id, "process")} /> : null}
              {canAdmin ? <IconButton label="Retry" icon={RefreshCw} onClick={() => onJobAction(job.id, "retry")} /> : null}
              {canAdmin ? <IconButton label="Cancel" icon={XCircle} onClick={() => onJobAction(job.id, "cancel")} /> : null}
            </div>
            <div className="mt-3 space-y-2">
              {job.attempts.map((attempt) => (
                <p key={attempt.id} className="rounded bg-white/[0.03] p-2">Attempt {attempt.attempt_number}: {attempt.status} {attempt.provider_response_summary || ""}</p>
              ))}
            </div>
          </details>
        ))}
      </div>
    </Card>
  );
}

function SettingsView({ owner, role, workspaceName }: { owner: boolean; role: WorkspaceRole; workspaceName: string }) {
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <h3 className="text-lg font-semibold text-white">Publishing settings</h3>
        <div className="mt-4 space-y-4 text-sm text-slate-300">
          <p>Workspace: {workspaceName}</p>
          <p>Current role: {role}</p>
          <p>Default timezone: UTC</p>
          <p>Approval required: enabled</p>
          <p>Self-approval prevention: enabled by default</p>
          {owner ? <p className="text-sky-200">Owner setting edits are planned for the settings API package.</p> : <p className="text-slate-500">Only owners will edit publishing settings.</p>}
        </div>
      </Card>
      <Card>
        <h3 className="text-lg font-semibold text-white">Social connection status</h3>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          {PLATFORM_OPTIONS.map((platform) => (
            <div key={platform} className="rounded-lg border border-white/10 p-4">
              <p className="font-medium text-white">{platform}</p>
              <p className="mt-1 text-sm text-slate-400">Mock/not connected</p>
            </div>
          ))}
        </div>
        <p className="mt-4 text-sm text-slate-500">Real OAuth and external provider adapters are outside Package 2.</p>
      </Card>
    </div>
  );
}

function Skeleton() {
  return (
    <Card>
      <div className="space-y-3">
        <div className="h-4 w-36 animate-pulse rounded bg-white/10" />
        <div className="h-8 w-2/3 animate-pulse rounded bg-white/10" />
        <div className="h-20 animate-pulse rounded bg-white/10" />
      </div>
    </Card>
  );
}

const publishingTabs: { key: Tab; label: string; icon: LucideIcon }[] = [
  { key: "library", label: "Library", icon: FileText },
  { key: "editor", label: "Editor", icon: Save },
  { key: "review", label: "Review", icon: ListChecks },
  { key: "calendar", label: "Calendar", icon: CalendarDays },
  { key: "queue", label: "Queue", icon: Send },
  { key: "settings", label: "Settings", icon: Settings },
];

function StatusBadge({ status }: { status: string }) {
  return <span className="rounded-full border border-white/10 px-2 py-1 text-xs text-slate-300">{status.replaceAll("_", " ")}</span>;
}

function IconButton({ icon: Icon, label, onClick }: { icon: LucideIcon; label: string; onClick: () => void }) {
  return (
    <button aria-label={label} className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-white/10 text-slate-300 hover:bg-white/[0.06] focus:outline-none focus:ring-2 focus:ring-sky-300" onClick={onClick} title={label} type="button">
      <Icon className="h-4 w-4" aria-hidden="true" />
    </button>
  );
}

function toFormValues(draft: PublishingDraft): DraftFormValues {
  return {
    title: draft.title,
    body: draft.body,
    platform: draft.platform,
    hashtags: draft.hashtags,
    brand_id: draft.brand_id,
    source_research_run_id: draft.source_research_run_id,
  };
}

function normalizeDraft(values: DraftFormValues): DraftFormValues {
  return {
    ...values,
    title: values.title.trim(),
    body: values.body.trim(),
    hashtags: values.hashtags.map((tag) => tag.trim()).filter(Boolean),
    brand_id: values.brand_id || null,
    source_research_run_id: values.source_research_run_id || null,
  };
}

function splitTags(value: string) {
  return value.split(/[\s,]+/).map((tag) => tag.trim()).filter(Boolean);
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
