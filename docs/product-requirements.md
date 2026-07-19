# GrowthOS Product Bible

## Brand Brain Core

Brand Brain is the first enterprise capability after the v0.2.5 foundation. It provides persistent brand memory for all AI-assisted workflows.

### Requirements

- Store company profile, brand name, mission, vision, core values, products and services, industry, target audience, ICP, buyer personas, competitors, brand voice, tone guidelines, writing style, value propositions, proof points, case studies, website URLs, social URLs, preferred CTAs, preferred hashtags, forbidden phrases, preferred terminology, languages, and regional preferences.
- Provide CRUD APIs with validation.
- Persist data locally as JSON for the initial implementation.
- Keep repository and service boundaries ready for database migration.
- Provide a dashboard, editors, managers, and preview panel in the GrowthOS UI.
- Automatically apply active Brand Brain context to AI Content Studio generation.
- Expose response metadata so users and tests can confirm Brand Brain was applied.

### Acceptance Criteria

- Users can create, update, view, and delete a Brand Brain profile.
- Content generation includes Brand Brain context when a profile exists.
- Generated output identifies when Brand Brain was applied.
- Existing AI Content Studio generation, copy, regenerate, validation, and fallback workflows continue to work.
