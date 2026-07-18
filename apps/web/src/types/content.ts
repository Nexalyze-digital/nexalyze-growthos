export type Platform = "LinkedIn" | "X" | "Instagram" | "Facebook";

export type Audience =
  | "CEOs"
  | "Founders"
  | "Marketing Leaders"
  | "SMEs"
  | "General Business Audience";

export type Goal =
  | "Lead Generation"
  | "Brand Awareness"
  | "Thought Leadership"
  | "Engagement"
  | "Education";

export type Tone =
  | "Professional"
  | "Executive"
  | "Conversational"
  | "Bold"
  | "Educational";

export type ContentFormValues = {
  topic: string;
  platform: Platform;
  audience: Audience;
  goal: Goal;
  tone: Tone;
  instructions: string;
};

export type GeneratedContent = {
  title: string;
  content: string;
  hashtags: string[];
  platform: Platform;
  tone: Tone;
  provider: "mock" | string;
};
