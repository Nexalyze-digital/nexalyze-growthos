export type ResearchType =
  | "Market Opportunity"
  | "Competitor Analysis"
  | "Content Opportunity"
  | "Industry Trends"
  | "Customer Pain Points"
  | "Strategic Research";

export type ResearchDepth = "Quick" | "Standard" | "Deep";

export type ResearchFinding = {
  title: string;
  detail: string;
  importance: "high" | "medium" | "low";
};

export type SourceNote = {
  label: string;
  url: string | null;
  note: string;
};

export type ResearchRunFormValues = {
  topic: string;
  objective: string;
  audience: string;
  industry: string;
  geography: string;
  research_type: ResearchType;
  depth: ResearchDepth;
  instructions: string;
  brand_id?: string | null;
  source_urls: string[];
};

export type ResearchRun = ResearchRunFormValues & {
  id: string;
  summary: string;
  key_findings: ResearchFinding[];
  opportunities: string[];
  risks: string[];
  recommendations: string[];
  follow_up_questions: string[];
  source_notes: SourceNote[];
  provider: "ollama" | "mock" | "mock-fallback" | string;
  brand_context_used: boolean;
  created_at: string;
  updated_at: string;
};
