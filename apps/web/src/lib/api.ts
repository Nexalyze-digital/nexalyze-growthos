import type { ContentFormValues, GeneratedContent } from "@/types/content";

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
