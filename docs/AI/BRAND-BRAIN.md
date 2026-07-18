# Brand Brain

Status: v0.3.0 core implementation

Brand Brain is the persistent brand memory layer for GrowthOS. It stores reusable company, audience, voice, offer, proof, and preference data so AI generation no longer depends only on a one-off user prompt.

## Architecture

The initial implementation uses the existing FastAPI layering:

- Schemas: `app/schemas/brand.py`
- Repository: `app/repositories/brand_repository.py`
- Service: `app/services/brand_service.py`
- API routes: `app/api/routes/brands.py`
- Prompt integration: `app/services/content_service.py`

The repository is intentionally small and file-backed. It can be replaced by a database repository without changing route contracts.

## Data Model

Brand Brain stores:

- Company profile, brand name, mission, vision, values, and industry.
- Products and services.
- Target audience, ICP, and buyer personas.
- Competitors.
- Brand voice, tone guidelines, and writing style.
- Value propositions, proof points, and case studies.
- Website and social URLs.
- Preferred CTAs, hashtags, terminology, languages, and regional preferences.
- Forbidden phrases.

## Prompt Injection Strategy

When a Brand Brain profile exists, the content service loads the active brand context and enriches every AI content generation request before invoking the selected provider.

The provider receives:

1. The user's topic, platform, audience, goal, tone, and instructions.
2. Saved Brand Brain context.
3. Instructions to prefer saved terminology, CTAs, hashtags, language, and regional preferences.
4. Instructions to avoid forbidden phrases.

Responses include:

- `brand_context_applied`
- `brand_name`

This makes prompt injection observable for tests and frontend validation.

## Future Memory Evolution

The current Brand Brain is a single active JSON-backed profile. Future versions should add:

- Workspace-scoped brand profiles.
- Versioned brand memory.
- Source attribution for brand facts.
- Approval workflow for AI-suggested brand updates.
- Retrieval over documents, website pages, campaigns, and customer research.
- Provider-specific prompt adapters.
- Audit logs for generated content and injected context.

## Migration Path From JSON To Database

1. Keep the API schemas stable.
2. Add a database-backed repository that implements the same repository methods.
3. Add migration scripts for brand profiles, personas, competitors, products, and case studies.
4. Add workspace and user ownership columns before multi-user release.
5. Run dual-read validation between JSON and database stores in development.
6. Switch `get_brand_repository` to the database implementation once migration validation passes.
7. Keep JSON export/import for backup and portability.
