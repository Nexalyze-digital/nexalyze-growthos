import type {
  Audience,
  ContentFormValues,
  Goal,
  Platform,
  Tone,
} from "@/types/content";

export const PLATFORM_OPTIONS = [
  "LinkedIn",
  "X",
  "Instagram",
  "Facebook",
] as const satisfies readonly Platform[];

export const AUDIENCE_OPTIONS = [
  "CEOs",
  "Founders",
  "Marketing Leaders",
  "SMEs",
  "General Business Audience",
] as const satisfies readonly Audience[];

export const GOAL_OPTIONS = [
  "Lead Generation",
  "Brand Awareness",
  "Thought Leadership",
  "Engagement",
  "Education",
] as const satisfies readonly Goal[];

export const TONE_OPTIONS = [
  "Professional",
  "Executive",
  "Conversational",
  "Bold",
  "Educational",
] as const satisfies readonly Tone[];

export const DEFAULT_FORM_VALUES: ContentFormValues = {
  topic: "",
  platform: "LinkedIn",
  audience: "CEOs",
  goal: "Lead Generation",
  tone: "Professional",
  instructions: "",
};

export const NAVIGATION_ITEMS = [
  { label: "Dashboard" },
  { label: "AI Content Studio" },
  { label: "Brand Brain" },
  { label: "Research Hub" },
  { label: "Publishing" },
  { label: "Drafts" },
  { label: "Analytics" },
  { label: "Settings" },
] as const;
