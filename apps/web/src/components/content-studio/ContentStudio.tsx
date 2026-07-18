"use client";

import { FormEvent, useMemo, useState } from "react";
import { generateContent } from "@/lib/api";
import { DEFAULT_FORM_VALUES } from "@/lib/constants";
import type { ContentFormValues, GeneratedContent } from "@/types/content";
import { ContentForm } from "./ContentForm";
import { GeneratedOutput } from "./GeneratedOutput";

type GenerationState = "empty" | "loading" | "success" | "error";

export function ContentStudio() {
  const [formValues, setFormValues] =
    useState<ContentFormValues>(DEFAULT_FORM_VALUES);
  const [output, setOutput] = useState<GeneratedContent | null>(null);
  const [status, setStatus] = useState<GenerationState>("empty");
  const [error, setError] = useState("");
  const [topicTouched, setTopicTouched] = useState(false);

  const topicError = useMemo(() => {
    const topic = formValues.topic.trim();
    if (!topicTouched && topic.length === 0) {
      return "";
    }
    if (topic.length < 3) {
      return "Topic must contain at least 3 characters.";
    }
    return "";
  }, [formValues.topic, topicTouched]);

  const canSubmit = formValues.topic.trim().length >= 3 && status !== "loading";

  async function submitCurrentValues(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    setTopicTouched(true);

    if (!canSubmit) {
      return;
    }

    setStatus("loading");
    setError("");

    try {
      const generated = await generateContent({
        ...formValues,
        topic: formValues.topic.trim(),
        instructions: formValues.instructions.trim(),
      });
      setOutput(generated);
      setStatus("success");
    } catch (requestError) {
      const message =
        requestError instanceof Error
          ? requestError.message
          : "Unable to connect to the GrowthOS API.";
      setError(message);
      setStatus("error");
    }
  }

  return (
    <section
      aria-labelledby="content-studio-title"
      className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(360px,0.9fr)]"
    >
      <div>
        <p className="text-sm font-medium text-cyan-300">AI Content Studio</p>
        <h2
          id="content-studio-title"
          className="mt-2 text-2xl font-semibold tracking-tight text-white"
        >
          Generate platform-ready content
        </h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
          Shape a topic into a structured social post with a deterministic mock
          provider while the live AI provider layer remains future-ready.
        </p>

        <ContentForm
          canSubmit={canSubmit}
          error={error}
          formValues={formValues}
          isLoading={status === "loading"}
          onChange={setFormValues}
          onSubmit={submitCurrentValues}
          setTopicTouched={setTopicTouched}
          topicError={topicError}
        />
      </div>

      <GeneratedOutput
        error={error}
        generatedContent={output}
        isLoading={status === "loading"}
        onRegenerate={() => submitCurrentValues()}
        status={status}
      />
    </section>
  );
}
