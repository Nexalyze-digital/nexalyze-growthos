import type { ContentFormValues, GeneratedContent } from "@/types/content";
import type { BrandBrain, BrandBrainFormValues } from "@/types/brand";
import type { ResearchRun, ResearchRunFormValues } from "@/types/research";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ||
  "http://localhost:8000";

async function parseApiError(response: Response) {
  try {
    const payload = await response.json();
    if (typeof payload?.detail === "string") {
      return payload.detail;
    }
    if (Array.isArray(payload?.detail)) {
      return payload.detail
        .map((item: { msg?: string }) => item.msg)
        .filter(Boolean)
        .join(" ");
    }
  } catch {
    return "";
  }
  return "";
}

export async function getHealth() {
  const response = await fetch(`${API_BASE_URL}/health`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("The GrowthOS API health check failed.");
  }
  return response.json() as Promise<{
    status: string;
    service: string;
    version: string;
  }>;
}

export async function generateContent(
  values: ContentFormValues,
): Promise<GeneratedContent> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}/api/v1/content/generate`, {
      body: JSON.stringify(values),
      headers: { "Content-Type": "application/json" },
      method: "POST",
    });
  } catch {
    throw new Error(
      "GrowthOS API is offline. Start FastAPI on http://localhost:8000 and try again.",
    );
  }

  if (!response.ok) {
    const apiMessage = await parseApiError(response);
    throw new Error(apiMessage || `The API returned status ${response.status}.`);
  }

  return response.json() as Promise<GeneratedContent>;
}

export async function getBrands(): Promise<BrandBrain[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/brands`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("Unable to load Brand Brain.");
  }
  const payload = (await response.json()) as { brands: BrandBrain[] };
  return payload.brands;
}

export async function saveBrand(
  values: BrandBrainFormValues,
  brandId?: string,
): Promise<BrandBrain> {
  const response = await fetch(
    brandId ? `${API_BASE_URL}/api/v1/brands/${brandId}` : `${API_BASE_URL}/api/v1/brands`,
    {
      body: JSON.stringify(values),
      headers: { "Content-Type": "application/json" },
      method: brandId ? "PUT" : "POST",
    },
  );

  if (!response.ok) {
    const apiMessage = await parseApiError(response);
    throw new Error(apiMessage || "Unable to save Brand Brain.");
  }

  return response.json() as Promise<BrandBrain>;
}

export async function getResearchRuns(): Promise<ResearchRun[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/research/runs`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("Unable to load Research Hub history.");
  }
  const payload = (await response.json()) as { runs: ResearchRun[] };
  return payload.runs;
}

export async function createResearchRun(
  values: ResearchRunFormValues,
): Promise<ResearchRun> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/research/runs`, {
      body: JSON.stringify(values),
      headers: { "Content-Type": "application/json" },
      method: "POST",
    });
  } catch {
    throw new Error(
      "GrowthOS API is offline. Start FastAPI on http://localhost:8000 and try again.",
    );
  }
  if (!response.ok) {
    const apiMessage = await parseApiError(response);
    throw new Error(apiMessage || "Unable to run Research Hub.");
  }
  return response.json() as Promise<ResearchRun>;
}

export async function regenerateResearchRun(runId: string): Promise<ResearchRun> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/research/runs/${runId}/regenerate`,
    { method: "POST" },
  );
  if (!response.ok) {
    const apiMessage = await parseApiError(response);
    throw new Error(apiMessage || "Unable to regenerate research.");
  }
  return response.json() as Promise<ResearchRun>;
}

export async function deleteResearchRun(runId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/research/runs/${runId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    const apiMessage = await parseApiError(response);
    throw new Error(apiMessage || "Unable to delete research.");
  }
}
