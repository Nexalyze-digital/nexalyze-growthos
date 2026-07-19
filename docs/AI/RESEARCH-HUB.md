# Research Hub

Status: v0.4.0 core implementation

Research Hub creates structured AI-generated research synthesis from a user brief and optional Brand Brain context. It is local-first and does not browse the live web in v0.4.0.

## Architecture

- Schemas: `app/schemas/research.py`
- Routes: `app/api/routes/research.py`
- Service: `app/services/research_service.py`
- Repository: `app/repositories/research_repository.py`
- Providers: `app/providers/research_mock.py`, `app/providers/research_ollama.py`

The module follows the Brand Brain pattern: Pydantic contracts, service orchestration, provider abstraction, and JSON persistence behind a repository boundary.

## Data Model

Each research run stores:

- Topic, objective, audience, industry, geography, research type, depth, instructions, optional Brand Brain ID, and optional source URLs.
- Summary.
- Key findings with importance.
- Opportunities.
- Risks.
- Recommendations.
- Follow-up questions.
- Source notes.
- Provider metadata.
- Brand context usage.
- Created and updated timestamps.

## Research Integrity

GrowthOS v0.4.0 does not perform live browsing, crawling, external search, or source verification.

Rules:

- Do not claim live web research was performed.
- Do not fabricate citations, statistics, named reports, studies, or URLs.
- Source URLs are returned only when supplied by the user.
- Source notes disclose whether a source was supplied or whether the output is AI-generated synthesis.
- Findings and recommendations should remain appropriately qualified.

## Brand Brain Integration

When a Brand Brain profile is selected, Research Hub injects protected brand context before provider execution. This context includes company, industry, audience, offer, competitor, terminology, and regional signals when available.

Protected Brand Brain context takes priority over conflicting user instructions. Empty fields are ignored and context size is bounded by `RESEARCH_CONTEXT_MAX_CHARACTERS`.

## Providers

### Mock

The mock provider is deterministic and useful for tests, offline demos, and fallback. It returns structured synthesis that clearly states no live research was performed.

### Ollama

The Ollama provider uses the existing local HTTP pattern:

- `AI_PROVIDER=ollama`
- `OLLAMA_BASE_URL=http://localhost:11434`
- `OLLAMA_MODEL=<installed model>`

It requests structured JSON, parses safely, and falls back to mock output on connection failure, timeout, malformed JSON, or invalid schema.

## Persistence

Research runs are stored as JSON at `RESEARCH_STORE_PATH`, defaulting to `data/research-runs.json`.

Current safeguards:

- Atomic writes through temporary files and `os.replace`.
- Controlled corruption errors.
- Stable IDs.
- Created and updated timestamps.
- Safe deletion.

Known limitation: JSON persistence is suitable for local/single-user use only and does not provide cross-process locking or multi-user ownership.

## Future Roadmap

- Crawl4AI or equivalent controlled crawler integration.
- Playwright-based source inspection.
- RSS and sitemap ingestion.
- External search API connectors.
- File ingestion through a MarkItDown-style conversion path.
- Vector search and retrieval memory.
- Database-backed persistence with workspace ownership.
