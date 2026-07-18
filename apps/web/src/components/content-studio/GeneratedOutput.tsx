"use client";

import { useEffect, useState } from "react";
import { Clipboard, RefreshCw } from "lucide-react";
import type { GeneratedContent } from "@/types/content";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

type GeneratedOutputProps = {
  error: string;
  generatedContent: GeneratedContent | null;
  isLoading: boolean;
  onRegenerate: () => void;
  status: "empty" | "loading" | "success" | "error";
};

export function GeneratedOutput({
  error,
  generatedContent,
  isLoading,
  onRegenerate,
  status,
}: GeneratedOutputProps) {
  const [copyStatus, setCopyStatus] = useState<"idle" | "copied" | "failed">(
    "idle",
  );

  useEffect(() => {
    if (copyStatus === "idle") {
      return;
    }
    const timer = window.setTimeout(() => setCopyStatus("idle"), 2200);
    return () => window.clearTimeout(timer);
  }, [copyStatus]);

  async function copyPost() {
    if (!generatedContent) {
      return;
    }

    const text = [
      generatedContent.title,
      "",
      generatedContent.content,
      "",
      generatedContent.hashtags.join(" "),
    ]
      .join("\n")
      .trim();

    try {
      await navigator.clipboard.writeText(text);
      setCopyStatus("copied");
    } catch {
      setCopyStatus("failed");
    }
  }

  return (
    <Card className="min-h-[520px]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-cyan-300">
            Generated Output
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-white">
            Ready-to-use post
          </h2>
        </div>
        <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-medium text-slate-300">
          {status === "success" ? "Success" : status === "loading" ? "Working" : "Ready"}
        </span>
      </div>

      {status === "loading" ? <LoadingPanel /> : null}

      {status === "empty" ? (
        <div className="mt-8 rounded-lg border border-dashed border-white/15 bg-slate-950/50 p-6 text-sm leading-6 text-slate-400">
          Generated content will appear here after you submit a valid topic.
          The response will include a title, post body, hashtags, platform, and
          tone.
        </div>
      ) : null}

      {status === "error" ? (
        <div className="mt-8 rounded-lg border border-red-400/25 bg-red-500/10 p-5">
          <p className="font-medium text-red-100">API request failed</p>
          <p className="mt-2 text-sm leading-6 text-red-200/85">
            {error || "Confirm the FastAPI backend is running on port 8000."}
          </p>
          <Button
            className="mt-5 w-auto"
            icon={RefreshCw}
            onClick={onRegenerate}
            type="button"
            variant="secondary"
          >
            Retry
          </Button>
        </div>
      ) : null}

      {status === "success" && generatedContent ? (
        <div className="mt-7 space-y-5">
          <div className="flex flex-wrap gap-2">
            <span className="rounded-full bg-cyan-400/10 px-3 py-1 text-xs font-medium text-cyan-200">
              {generatedContent.platform}
            </span>
            <span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-200">
              {generatedContent.tone}
            </span>
          </div>

          <div className="rounded-lg border border-white/10 bg-slate-950/60 p-5">
            <h3 className="text-xl font-semibold text-white">
              {generatedContent.title}
            </h3>
            <div className="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-300">
              {generatedContent.content}
            </div>
            <div className="mt-5 flex flex-wrap gap-2">
              {generatedContent.hashtags.map((hashtag) => (
                <span key={hashtag} className="text-sm text-cyan-300">
                  {hashtag}
                </span>
              ))}
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <Button
              disabled={isLoading}
              icon={Clipboard}
              onClick={copyPost}
              type="button"
              variant="secondary"
            >
              {copyStatus === "copied"
                ? "Copied"
                : copyStatus === "failed"
                  ? "Copy failed"
                  : "Copy full post"}
            </Button>
            <Button
              disabled={isLoading}
              icon={RefreshCw}
              onClick={onRegenerate}
              type="button"
              variant="secondary"
            >
              Regenerate
            </Button>
          </div>
        </div>
      ) : null}
    </Card>
  );
}

function LoadingPanel() {
  return (
    <div className="mt-8 space-y-4 rounded-lg border border-white/10 bg-slate-950/60 p-5">
      <div className="h-4 w-32 animate-pulse rounded bg-white/10" />
      <div className="h-7 w-3/4 animate-pulse rounded bg-white/10" />
      <div className="space-y-2">
        <div className="h-3 animate-pulse rounded bg-white/10" />
        <div className="h-3 w-11/12 animate-pulse rounded bg-white/10" />
        <div className="h-3 w-10/12 animate-pulse rounded bg-white/10" />
      </div>
    </div>
  );
}
