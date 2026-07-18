import type { Dispatch, FormEvent, SetStateAction } from "react";
import { Sparkles } from "lucide-react";
import {
  AUDIENCE_OPTIONS,
  GOAL_OPTIONS,
  PLATFORM_OPTIONS,
  TONE_OPTIONS,
} from "@/lib/constants";
import type { ContentFormValues } from "@/types/content";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { SelectField } from "@/components/ui/SelectField";
import { TextAreaField } from "@/components/ui/TextAreaField";
import { GenerationStatus } from "./GenerationStatus";

type ContentFormProps = {
  canSubmit: boolean;
  error: string;
  formValues: ContentFormValues;
  isLoading: boolean;
  onChange: Dispatch<SetStateAction<ContentFormValues>>;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  setTopicTouched: (value: boolean) => void;
  topicError: string;
};

export function ContentForm({
  canSubmit,
  error,
  formValues,
  isLoading,
  onChange,
  onSubmit,
  setTopicTouched,
  topicError,
}: ContentFormProps) {
  const updateField =
    (field: keyof ContentFormValues) =>
    (value: string) => {
      onChange((current) => ({ ...current, [field]: value }));
    };

  return (
    <Card className="mt-5">
      <form className="space-y-5" onSubmit={onSubmit}>
        <Field
          error={topicError}
          id="topic"
          label="Topic"
          onBlur={() => setTopicTouched(true)}
          onChange={updateField("topic")}
          placeholder="Example: AI automation for small businesses"
          required
          value={formValues.topic}
        />

        <div className="grid gap-4 md:grid-cols-2">
          <SelectField
            id="platform"
            label="Platform"
            onChange={updateField("platform")}
            options={PLATFORM_OPTIONS}
            value={formValues.platform}
          />
          <SelectField
            id="audience"
            label="Audience"
            onChange={updateField("audience")}
            options={AUDIENCE_OPTIONS}
            value={formValues.audience}
          />
          <SelectField
            id="goal"
            label="Goal"
            onChange={updateField("goal")}
            options={GOAL_OPTIONS}
            value={formValues.goal}
          />
          <SelectField
            id="tone"
            label="Tone"
            onChange={updateField("tone")}
            options={TONE_OPTIONS}
            value={formValues.tone}
          />
        </div>

        <TextAreaField
          id="instructions"
          label="Additional instructions"
          maxLength={2000}
          onChange={updateField("instructions")}
          placeholder="Add brand voice, CTA, keywords, audience context, or formatting notes."
          value={formValues.instructions}
        />

        <GenerationStatus error={error} isLoading={isLoading} />

        <Button disabled={!canSubmit} icon={Sparkles} type="submit">
          {isLoading ? "Generating content..." : "Generate Content"}
        </Button>
      </form>
    </Card>
  );
}
