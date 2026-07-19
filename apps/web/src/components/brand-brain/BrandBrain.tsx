"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { Brain, Save } from "lucide-react";
import { getBrands, saveBrand } from "@/lib/api";
import type { BrandBrain, BrandBrainFormValues } from "@/types/brand";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { TextAreaField } from "@/components/ui/TextAreaField";

const emptyBrand: BrandBrainFormValues = {
  company_profile: "",
  brand_name: "Nexalyze",
  mission: "",
  vision: "",
  core_values: [],
  products_and_services: [],
  industry: "",
  target_audience: "",
  icp: "",
  buyer_personas: [],
  competitors: [],
  brand_voice: "",
  tone_guidelines: "",
  writing_style: "",
  value_propositions: [],
  proof_points: [],
  case_studies: [],
  website_urls: [],
  social_media_urls: [],
  preferred_ctas: [],
  preferred_hashtags: [],
  forbidden_phrases: [],
  preferred_terminology: [],
  languages: ["English"],
  regional_preferences: [],
};

type SaveState = "idle" | "loading" | "saved" | "error";
type LoadState = "loading" | "ready" | "error";

export function BrandBrain() {
  const [brandId, setBrandId] = useState<string | undefined>();
  const [formValues, setFormValues] = useState<BrandBrainFormValues>(emptyBrand);
  const [loadStatus, setLoadStatus] = useState<LoadState>("loading");
  const [status, setStatus] = useState<SaveState>("idle");
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    getBrands()
      .then((brands) => {
        if (!active || brands.length === 0) {
          if (active) {
            setLoadStatus("ready");
          }
          return;
        }
        const [brand] = brands;
        setBrandId(brand.id);
        setFormValues(toFormValues(brand));
        setLoadStatus("ready");
      })
      .catch(() => {
        if (active) {
          setLoadStatus("error");
          setError("Brand Brain is unavailable until the API is running.");
        }
      });

    return () => {
      active = false;
    };
  }, []);

  const readiness = useMemo(() => {
    const signals = [
      formValues.company_profile,
      formValues.mission,
      formValues.brand_voice,
      formValues.target_audience,
      formValues.icp,
      formValues.products_and_services.length ? "Products" : "",
    ].filter((value) => value.trim().length > 0);
    return Math.round((signals.length / 6) * 100);
  }, [formValues]);

  function update<K extends keyof BrandBrainFormValues>(
    key: K,
    value: BrandBrainFormValues[K],
  ) {
    setFormValues((current) => ({ ...current, [key]: value }));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("loading");
    setError("");

    try {
      const saved = await saveBrand(normalizeBrand(formValues), brandId);
      setBrandId(saved.id);
      setFormValues(toFormValues(saved));
      setStatus("saved");
    } catch (saveError) {
      setStatus("error");
      setError(
        saveError instanceof Error
          ? saveError.message
          : "Unable to save Brand Brain.",
      );
    }
  }

  return (
    <section
      aria-labelledby="brand-brain-title"
      className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]"
    >
      <div>
        <p className="text-sm font-medium text-emerald-300">Brand Brain</p>
        <h2
          id="brand-brain-title"
          className="mt-2 text-2xl font-semibold tracking-tight text-white"
        >
          Persistent brand memory
        </h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
          Store the strategic context GrowthOS should apply to future content
          generation, proposals, research, and automation workflows.
        </p>

        <form className="mt-6 space-y-5" onSubmit={submit}>
          {loadStatus === "loading" ? (
            <p className="rounded-lg border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-slate-300">
              Loading Brand Brain...
            </p>
          ) : null}

          <Card className="grid gap-4 md:grid-cols-2">
            <Field
              id="brand-name"
              label="Brand name"
              onChange={(value) => update("brand_name", value)}
              required
              value={formValues.brand_name}
            />
            <Field
              id="industry"
              label="Industry"
              onChange={(value) => update("industry", value)}
              value={formValues.industry}
            />
            <div className="md:col-span-2">
              <TextAreaField
                id="company-profile"
                label="Company profile"
                maxLength={3000}
                onChange={(value) => update("company_profile", value)}
                value={formValues.company_profile}
              />
            </div>
            <TextAreaField
              id="mission"
              label="Mission"
              maxLength={1000}
              onChange={(value) => update("mission", value)}
              value={formValues.mission}
            />
            <TextAreaField
              id="vision"
              label="Vision"
              maxLength={1000}
              onChange={(value) => update("vision", value)}
              value={formValues.vision}
            />
          </Card>

          <Card className="grid gap-4 md:grid-cols-2">
            <TextAreaField
              id="brand-voice"
              label="Brand voice"
              maxLength={1000}
              onChange={(value) => update("brand_voice", value)}
              value={formValues.brand_voice}
            />
            <TextAreaField
              id="tone-guidelines"
              label="Tone guidelines"
              maxLength={1000}
              onChange={(value) => update("tone_guidelines", value)}
              value={formValues.tone_guidelines}
            />
            <TextAreaField
              id="writing-style"
              label="Writing style"
              maxLength={1000}
              onChange={(value) => update("writing_style", value)}
              value={formValues.writing_style}
            />
            <ListField
              label="Forbidden phrases"
              value={formValues.forbidden_phrases}
              onChange={(value) => update("forbidden_phrases", value)}
            />
            <ListField
              label="Preferred terminology"
              value={formValues.preferred_terminology}
              onChange={(value) => update("preferred_terminology", value)}
            />
            <ListField
              label="Preferred hashtags"
              value={formValues.preferred_hashtags}
              onChange={(value) => update("preferred_hashtags", value)}
            />
          </Card>

          <Card className="grid gap-4 md:grid-cols-2">
            <TextAreaField
              id="target-audience"
              label="Target audience"
              maxLength={1000}
              onChange={(value) => update("target_audience", value)}
              value={formValues.target_audience}
            />
            <TextAreaField
              id="icp"
              label="Ideal customer profile"
              maxLength={1500}
              onChange={(value) => update("icp", value)}
              value={formValues.icp}
            />
            <ListField
              label="Core values"
              value={formValues.core_values}
              onChange={(value) => update("core_values", value)}
            />
            <ListField
              label="Value propositions"
              value={formValues.value_propositions}
              onChange={(value) => update("value_propositions", value)}
            />
            <ListField
              label="Proof points"
              value={formValues.proof_points}
              onChange={(value) => update("proof_points", value)}
            />
            <ListField
              label="Preferred CTAs"
              value={formValues.preferred_ctas}
              onChange={(value) => update("preferred_ctas", value)}
            />
          </Card>

          <Card className="grid gap-4 md:grid-cols-3">
            <CollectionField
              label="Products and services"
              rows={formValues.products_and_services.map((item) =>
                [item.name, item.description, item.audience, item.value].join(" | "),
              )}
              placeholder="Name | Description | Audience | Value"
              onChange={(rows) =>
                update(
                  "products_and_services",
                  rows.map((row) => {
                    const [name = "", description = "", audience = "", value = ""] =
                      row.split("|").map((part) => part.trim());
                    return { name, description, audience, value };
                  }),
                )
              }
            />
            <CollectionField
              label="Buyer personas"
              rows={formValues.buyer_personas.map((item) =>
                [item.name, item.role, item.goals.join(", ")].join(" | "),
              )}
              placeholder="Name | Role | Goals"
              onChange={(rows) =>
                update(
                  "buyer_personas",
                  rows.map((row) => {
                    const [name = "", role = "", goals = ""] = row
                      .split("|")
                      .map((part) => part.trim());
                    return {
                      name,
                      role,
                      goals: splitList(goals),
                      pain_points: [],
                      buying_triggers: [],
                    };
                  }),
                )
              }
            />
            <CollectionField
              label="Competitors"
              rows={formValues.competitors.map((item) =>
                [item.name, item.website || "", item.positioning_notes].join(" | "),
              )}
              placeholder="Name | Website | Positioning notes"
              onChange={(rows) =>
                update(
                  "competitors",
                  rows.map((row) => {
                    const [name = "", website = "", positioning_notes = ""] = row
                      .split("|")
                      .map((part) => part.trim());
                    return {
                      name,
                      website: website || null,
                      positioning_notes,
                    };
                  }),
                )
              }
            />
          </Card>

          <Card className="grid gap-4 md:grid-cols-2">
            <CollectionField
              label="Case studies"
              rows={formValues.case_studies.map((item) =>
                [item.title, item.summary, item.outcome].join(" | "),
              )}
              placeholder="Title | Summary | Outcome"
              onChange={(rows) =>
                update(
                  "case_studies",
                  rows.map((row) => {
                    const [title = "", summary = "", outcome = ""] = row
                      .split("|")
                      .map((part) => part.trim());
                    return { title, summary, outcome };
                  }),
                )
              }
            />
            <ListField
              label="Website URLs"
              value={formValues.website_urls}
              onChange={(value) => update("website_urls", value)}
            />
            <ListField
              label="Social media URLs"
              value={formValues.social_media_urls}
              onChange={(value) => update("social_media_urls", value)}
            />
            <ListField
              label="Languages"
              value={formValues.languages}
              onChange={(value) => update("languages", value)}
            />
            <ListField
              label="Regional preferences"
              value={formValues.regional_preferences}
              onChange={(value) => update("regional_preferences", value)}
            />
          </Card>

          {error ? (
            <p className="rounded-lg border border-red-400/25 bg-red-500/10 px-4 py-3 text-sm text-red-100">
              {error}
            </p>
          ) : null}

          <Button
            className="sm:w-auto"
            disabled={status === "loading"}
            icon={Save}
            type="submit"
          >
            {status === "loading"
              ? "Saving"
              : status === "saved"
                ? "Saved"
                : "Save Brand Brain"}
          </Button>
        </form>
      </div>

      <Card className="h-fit">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-400/10 text-emerald-200">
            <Brain className="h-5 w-5" aria-hidden="true" />
          </span>
          <div>
            <p className="text-sm font-medium text-emerald-300">Preview</p>
            <h3 className="text-lg font-semibold text-white">
              {formValues.brand_name || "Untitled brand"}
            </h3>
          </div>
        </div>

        <div className="mt-6">
          <div
            aria-label="Brand Brain context readiness"
            aria-valuemax={100}
            aria-valuemin={0}
            aria-valuenow={readiness}
            className="h-2 overflow-hidden rounded-full bg-white/10"
            role="progressbar"
          >
            <div
              className="h-full rounded-full bg-emerald-300"
              style={{ width: `${readiness}%` }}
            />
          </div>
          <p className="mt-2 text-xs text-slate-400">
            {readiness}% context readiness
          </p>
        </div>

        <div className="mt-6 space-y-4 text-sm leading-6 text-slate-300">
          <PreviewItem label="Voice" value={formValues.brand_voice} />
          <PreviewItem label="Audience" value={formValues.target_audience} />
          <PreviewItem label="ICP" value={formValues.icp} />
          <PreviewItem
            label="Preferred CTAs"
            value={formValues.preferred_ctas.join(", ")}
          />
          <PreviewItem
            label="Forbidden"
            value={formValues.forbidden_phrases.join(", ")}
          />
        </div>
      </Card>
    </section>
  );
}

function toFormValues(brand: BrandBrain): BrandBrainFormValues {
  const { id, created_at, updated_at, ...values } = brand;
  void id;
  void created_at;
  void updated_at;
  return values;
}

function normalizeBrand(values: BrandBrainFormValues): BrandBrainFormValues {
  return {
    ...values,
    core_values: cleanList(values.core_values),
    value_propositions: cleanList(values.value_propositions),
    proof_points: cleanList(values.proof_points),
    website_urls: cleanList(values.website_urls),
    social_media_urls: cleanList(values.social_media_urls),
    preferred_ctas: cleanList(values.preferred_ctas),
    preferred_hashtags: cleanList(values.preferred_hashtags),
    forbidden_phrases: cleanList(values.forbidden_phrases),
    preferred_terminology: cleanList(values.preferred_terminology),
    languages: cleanList(values.languages),
    regional_preferences: cleanList(values.regional_preferences),
    products_and_services: values.products_and_services.filter((item) =>
      item.name.trim(),
    ),
    buyer_personas: values.buyer_personas.filter((item) => item.name.trim()),
    competitors: values.competitors.filter((item) => item.name.trim()),
    case_studies: values.case_studies.filter((item) => item.title.trim()),
  };
}

function ListField({
  label,
  onChange,
  value,
}: {
  label: string;
  onChange: (value: string[]) => void;
  value: string[];
}) {
  return (
    <TextAreaField
      id={label.toLowerCase().replaceAll(" ", "-")}
      label={label}
      onChange={(nextValue) => onChange(splitList(nextValue))}
      placeholder="One per line or comma separated"
      value={value.join("\n")}
    />
  );
}

function CollectionField({
  label,
  onChange,
  placeholder,
  rows,
}: {
  label: string;
  onChange: (rows: string[]) => void;
  placeholder: string;
  rows: string[];
}) {
  return (
    <TextAreaField
      id={label.toLowerCase().replaceAll(" ", "-")}
      label={label}
      onChange={(value) => onChange(value.split("\n").filter(Boolean))}
      placeholder={placeholder}
      value={rows.join("\n")}
    />
  );
}

function PreviewItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-medium uppercase text-slate-500">{label}</p>
      <p className="mt-1 text-slate-300">{value || "Not set yet"}</p>
    </div>
  );
}

function cleanList(values: string[]): string[] {
  return Array.from(new Set(values.map((value) => value.trim()).filter(Boolean)));
}

function splitList(value: string): string[] {
  return cleanList(value.split(/[\n,]/));
}
