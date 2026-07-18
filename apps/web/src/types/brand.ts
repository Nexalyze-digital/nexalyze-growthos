export type ProductService = {
  id?: string;
  name: string;
  description: string;
  audience: string;
  value: string;
};

export type BuyerPersona = {
  id?: string;
  name: string;
  role: string;
  goals: string[];
  pain_points: string[];
  buying_triggers: string[];
};

export type Competitor = {
  id?: string;
  name: string;
  website: string | null;
  positioning_notes: string;
};

export type CaseStudy = {
  id?: string;
  title: string;
  summary: string;
  outcome: string;
};

export type BrandBrain = {
  id: string;
  company_profile: string;
  brand_name: string;
  mission: string;
  vision: string;
  core_values: string[];
  products_and_services: ProductService[];
  industry: string;
  target_audience: string;
  icp: string;
  buyer_personas: BuyerPersona[];
  competitors: Competitor[];
  brand_voice: string;
  tone_guidelines: string;
  writing_style: string;
  value_propositions: string[];
  proof_points: string[];
  case_studies: CaseStudy[];
  website_urls: string[];
  social_media_urls: string[];
  preferred_ctas: string[];
  preferred_hashtags: string[];
  forbidden_phrases: string[];
  preferred_terminology: string[];
  languages: string[];
  regional_preferences: string[];
  created_at?: string;
  updated_at?: string;
};

export type BrandBrainFormValues = Omit<
  BrandBrain,
  "id" | "created_at" | "updated_at"
>;
