"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { Clipboard, RefreshCw, Search, Trash2 } from "lucide-react";
import {
  createResearchRun,
  deleteResearchRun,
  getBrands,
  getResearchRuns,
  regenerateResearchRun,
} from "@/lib/api";
import {
  DEFAULT_RESEARCH_VALUES,
  RESEARCH_DEPTH_OPTIONS,
  RESEARCH_TYPE_OPTIONS,
} from "@/lib/constants";
import type { BrandBrain } from "@/types/brand";
import type { ResearchRun, ResearchRunFormValues } from "@/types/research";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { SelectField } from "@/components/ui/SelectField";
import { TextAreaField } from "@/components/ui/TextAreaField";

type Status = "empty" | "loading" | "success" | "error";

export function ResearchHub() {
  const [brands, setBrands] = useState<BrandBrain[]>([]);
  const [history, setHistory] = useState<ResearchRun[]>([]);
  const [formValues, setFormValues] =
    useState<ResearchRunFormValues>(DEFAULT_RESEARCH_VALUES);
  const [activeRun, setActiveRun] = useState<ResearchRun | null>(null);
  const [status, setStatus] = useState<Status>("empty");
  const [error, setError] = useState("");
  const [copyStatus, setCopyStatus] = useState<"idle" | "copied" | "failed">(
    "idle",
  );
  const [topicTouched, setTopicTouched] = useState(false);

  useEffect(() => {
    let active = true;
    Promise.all([getBrands(), getResearchRuns()])
      .then(([brandList, runs]) => {
        if (!active) {
          return;
        }
        setBrands(brandList);
        setHistory(runs);
        if (brandList[0]) {
          setFormValues((current) => ({ ...current, brand_id: brandList[0].id }));
        }
        if (runs[0]) {
          setActiveRun(runs[0]);
          setStatus("success");
        }
      })
      .catch(() => setError("Research Hub is unavailable until the API is running."));
    return () => {
      active = false;
    };
  }, []);

  const topicError = useMemo(() => {
    if (!topicTouched && formValues.topic.trim().length === 0) {
      return "";
    }
    return formValues.topic.trim().length < 3
      ? "Topic must contain at least 3 characters."
      : "";
  }, [formValues.topic, topicTouched]);

  const canSubmit =
    formValues.topic.trim().length >= 3 &&
    formValues.objective.trim().length >= 3 &&
    status !== "loading";

  function update<K extends keyof ResearchRunFormValues>(
    key: K,
    value: ResearchRunFormValues[K],
  ) {
    setFormValues((current) => ({ ...current, [key]: value }));
  }

  async function submit(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    setTopicTouched(true);
    if (!canSubmit) {
      return;
    }
    setStatus("loading");
    setError("");
    try {
      const run = await createResearchRun(normalizeResearch(formValues));
      setActiveRun(run);
      setHistory((current) => [run, ...current.filter((item) => item.id !== run.id)]);
      setStatus("success");
    } catch (requestError) {
      setStatus("error");
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to run Research Hub.",
      );
    }
  }

  async function regenerate() {
    if (!activeRun) {
      return;
    }
    setStatus("loading");
    setError("");
    try {
      const run = await regenerateResearchRun(activeRun.id);
      setActiveRun(run);
      setHistory((current) => [run, ...current.filter((item) => item.id !== run.id)]);
      setStatus("success");
    } catch (requestError) {
      setStatus("error");
      setError(requestError instanceof Error ? requestError.message : "Unable to regenerate.");
    }
  }

  async function removeRun(runId: string) {
    setError("");
    try {
      await deleteResearchRun(runId);
      setHistory((current) => current.filter((item) => item.id !== runId));
      if (activeRun?.id === runId) {
        setActiveRun(null);
        setStatus("empty");
      }
    } catch (requestError) {
      setStatus("error");
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to delete research.",
      );
    }
  }

  async function copyReport() {
    if (!activeRun) {
      return;
    }
    const text = [
      activeRun.topic,
      "",
      activeRun.summary,
      "",
      "Key findings",
      ...activeRun.key_findings.map((item) => `- ${item.title}: ${item.detail}`),
      "",
      "Recommendations",
      ...activeRun.recommendations.map((item) => `- ${item}`),
      "",
      "Source notes",
      ...activeRun.source_notes.map((item) => `- ${item.label}: ${item.note}`),
    ].join("\n");
    try {
      await navigator.clipboard.writeText(text);
      setCopyStatus("copied");
    } catch {
      setCopyStatus("failed");
    }
  }

  const providerLabel =
    activeRun?.provider === "ollama"
      ? "Ollama"
      : activeRun?.provider === "mock-fallback"
        ? "Mock fallback"
        : "Mock";

  return (
    <section
      aria-labelledby="research-hub-title"
      className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(360px,0.9fr)]"
    >
      <div>
        <p className="text-sm font-medium text-violet-300">Research Hub</p>
        <h2
          id="research-hub-title"
          className="mt-2 text-2xl font-semibold tracking-tight text-white"
        >
          Generate structured market intelligence
        </h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
          Create AI-generated synthesis from your brief and Brand Brain. GrowthOS
          does not browse the live web or verify sources in this release.
        </p>

        <form className="mt-6 space-y-5" onSubmit={submit}>
          <Card className="grid gap-4 md:grid-cols-2">
            <Field
              error={topicError}
              id="research-topic"
              label="Topic"
              onBlur={() => setTopicTouched(true)}
              onChange={(value) => update("topic", value)}
              required
              value={formValues.topic}
            />
            <SelectField
              id="research-type"
              label="Research type"
              onChange={(value) => update("research_type", value)}
              options={RESEARCH_TYPE_OPTIONS}
              value={formValues.research_type}
            />
            <SelectField
              id="research-depth"
              label="Depth"
              onChange={(value) => update("depth", value)}
              options={RESEARCH_DEPTH_OPTIONS}
              value={formValues.depth}
            />
            <div className="space-y-2">
              <label
                className="block text-sm font-medium text-slate-200"
                htmlFor="research-brand"
              >
                Brand Brain
              </label>
              <select
                className="w-full rounded-lg border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none transition focus:border-violet-300 focus:ring-2 focus:ring-violet-300/30"
                id="research-brand"
                onChange={(event) =>
                  update("brand_id", event.target.value || null)
                }
                value={formValues.brand_id || ""}
              >
                <option value="">No Brand Brain</option>
                {brands.map((brand) => (
                  <option key={brand.id} value={brand.id}>
                    {brand.brand_name}
                  </option>
                ))}
              </select>
            </div>
            <Field
              id="research-audience"
              label="Audience"
              onChange={(value) => update("audience", value)}
              value={formValues.audience}
            />
            <Field
              id="research-industry"
              label="Industry"
              onChange={(value) => update("industry", value)}
              value={formValues.industry}
            />
            <Field
              id="research-geography"
              label="Geography"
              onChange={(value) => update("geography", value)}
              value={formValues.geography}
            />
            <div className="md:col-span-2">
              <TextAreaField
                id="research-objective"
                label="Objective"
                maxLength={1000}
                onChange={(value) => update("objective", value)}
                value={formValues.objective}
              />
            </div>
            <TextAreaField
              id="research-instructions"
              label="Additional instructions"
              maxLength={2000}
              onChange={(value) => update("instructions", value)}
              value={formValues.instructions}
            />
            <TextAreaField
              id="research-source-urls"
              label="Source URLs"
              onChange={(value) => update("source_urls", splitLines(value))}
              placeholder="Optional, one URL per line"
              value={formValues.source_urls.join("\n")}
            />
          </Card>

          {error ? (
            <p className="rounded-lg border border-red-400/25 bg-red-500/10 px-4 py-3 text-sm text-red-100">
              {error}
            </p>
          ) : null}

          <Button
            className="sm:w-auto"
            disabled={!canSubmit}
            icon={Search}
            type="submit"
          >
            {status === "loading" ? "Running research" : "Run Research"}
          </Button>
        </form>

        <Card className="mt-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-medium text-violet-300">History</p>
              <h3 className="mt-1 text-lg font-semibold text-white">
                Saved research runs
              </h3>
            </div>
            <span className="text-xs text-slate-500">{history.length} saved</span>
          </div>
          <div className="mt-4 space-y-2">
            {history.length === 0 ? (
              <p className="rounded-lg border border-dashed border-white/15 bg-slate-950/50 p-4 text-sm text-slate-400">
                Research history will appear here after the first run.
              </p>
            ) : null}
            {history.map((run) => (
              <button
                key={run.id}
                className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-4 py-3 text-left text-sm text-slate-300 transition hover:bg-white/[0.06] focus:outline-none focus:ring-2 focus:ring-violet-300"
                onClick={() => {
                  setActiveRun(run);
                  setStatus("success");
                }}
                type="button"
              >
                <span className="block font-medium text-white">{run.topic}</span>
                <span className="mt-1 block text-xs text-slate-500">
                  {run.research_type} - {run.provider}
                </span>
              </button>
            ))}
          </div>
        </Card>
      </div>

      <Card className="min-h-[620px]">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-violet-300">Results</p>
            <h3 className="mt-2 text-2xl font-semibold text-white">
              Research brief
            </h3>
          </div>
          <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-medium text-slate-300">
            {status === "loading" ? "Working" : status === "success" ? "Saved" : "Ready"}
          </span>
        </div>

        {status === "loading" ? <LoadingPanel /> : null}
        {status === "empty" ? (
          <div className="mt-8 rounded-lg border border-dashed border-white/15 bg-slate-950/50 p-6 text-sm leading-6 text-slate-400">
            Run a research request to generate findings, opportunities, risks,
            recommendations, follow-up questions, and source notes.
          </div>
        ) : null}
        {status === "error" ? (
          <div className="mt-8 rounded-lg border border-red-400/25 bg-red-500/10 p-5 text-sm text-red-100">
            {error || "Research Hub could not complete the request."}
          </div>
        ) : null}
        {status === "success" && activeRun ? (
          <div className="mt-7 space-y-5">
            <div className="flex flex-wrap gap-2">
              <Badge>{activeRun.research_type}</Badge>
              <Badge>{activeRun.depth}</Badge>
              <Badge>{providerLabel}</Badge>
              {activeRun.brand_context_used ? <Badge>Brand Brain</Badge> : null}
            </div>
            {activeRun.provider === "mock-fallback" ? (
              <Notice>
                Local AI was unavailable, so GrowthOS used deterministic mock
                research fallback.
              </Notice>
            ) : null}
            <Notice>
              AI-generated synthesis. No live web research or source verification
              was performed.
            </Notice>

            <ResultSection title="Executive summary">
              <p>{activeRun.summary}</p>
            </ResultSection>
            <ResultSection title="Key findings">
              {activeRun.key_findings.map((finding) => (
                <div key={finding.title} className="rounded-lg bg-white/[0.03] p-3">
                  <p className="font-medium text-white">
                    {finding.title}{" "}
                    <span className="text-xs text-violet-300">
                      {finding.importance}
                    </span>
                  </p>
                  <p className="mt-1 text-slate-300">{finding.detail}</p>
                </div>
              ))}
            </ResultSection>
            <ListSection title="Opportunities" items={activeRun.opportunities} />
            <ListSection title="Risks" items={activeRun.risks} />
            <ListSection title="Recommendations" items={activeRun.recommendations} />
            <ListSection
              title="Follow-up questions"
              items={activeRun.follow_up_questions}
            />
            <ResultSection title="Source notes">
              {activeRun.source_notes.map((note) => (
                <p key={note.label}>
                  <span className="font-medium text-white">{note.label}:</span>{" "}
                  {note.note}
                  {note.url ? ` (${note.url})` : ""}
                </p>
              ))}
            </ResultSection>

            <div className="grid gap-3 sm:grid-cols-3">
              <Button icon={Clipboard} onClick={copyReport} type="button" variant="secondary">
                {copyStatus === "copied"
                  ? "Copied"
                  : copyStatus === "failed"
                    ? "Copy failed"
                    : "Copy report"}
              </Button>
              <Button icon={RefreshCw} onClick={regenerate} type="button" variant="secondary">
                Regenerate
              </Button>
              <Button
                icon={Trash2}
                onClick={() => removeRun(activeRun.id)}
                type="button"
                variant="secondary"
              >
                Delete
              </Button>
            </div>
          </div>
        ) : null}
      </Card>
    </section>
  );
}

function normalizeResearch(values: ResearchRunFormValues): ResearchRunFormValues {
  return {
    ...values,
    topic: values.topic.trim(),
    objective: values.objective.trim(),
    audience: values.audience.trim(),
    industry: values.industry.trim(),
    geography: values.geography.trim(),
    instructions: values.instructions.trim(),
    brand_id: values.brand_id || null,
    source_urls: values.source_urls.map((url) => url.trim()).filter(Boolean),
  };
}

function splitLines(value: string): string[] {
  return value.split("\n").map((item) => item.trim()).filter(Boolean);
}

function Badge({ children }: { children: string }) {
  return (
    <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-medium text-slate-300">
      {children}
    </span>
  );
}

function Notice({ children }: { children: string }) {
  return (
    <div className="rounded-lg border border-amber-300/20 bg-amber-300/10 px-4 py-3 text-sm text-amber-100">
      {children}
    </div>
  );
}

function ResultSection({
  children,
  title,
}: {
  children: ReactNode;
  title: string;
}) {
  return (
    <section className="rounded-lg border border-white/10 bg-slate-950/60 p-4">
      <h4 className="text-sm font-semibold text-white">{title}</h4>
      <div className="mt-3 space-y-3 text-sm leading-6 text-slate-300">{children}</div>
    </section>
  );
}

function ListSection({ items, title }: { items: string[]; title: string }) {
  return (
    <ResultSection title={title}>
      <ul className="space-y-2">
        {items.map((item) => (
          <li key={item} className="rounded-lg bg-white/[0.03] p-3">
            {item}
          </li>
        ))}
      </ul>
    </ResultSection>
  );
}

function LoadingPanel() {
  return (
    <div className="mt-8 space-y-4 rounded-lg border border-white/10 bg-slate-950/60 p-5">
      <div className="h-4 w-40 animate-pulse rounded bg-white/10" />
      <div className="h-7 w-3/4 animate-pulse rounded bg-white/10" />
      <div className="space-y-2">
        <div className="h-3 animate-pulse rounded bg-white/10" />
        <div className="h-3 w-11/12 animate-pulse rounded bg-white/10" />
        <div className="h-3 w-10/12 animate-pulse rounded bg-white/10" />
      </div>
    </div>
  );
}
