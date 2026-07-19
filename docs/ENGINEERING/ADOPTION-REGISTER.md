# Adoption Register

Status: Brand Brain v0.3.0 implementation

This register records patterns adopted from the local open-source catalog. No source code was copied.

| Source Repository | Purpose | License | What Was Adopted | Why It Was Adopted | Integration Approach |
| --- | --- | --- | --- | --- | --- |
| `vercel__next.js` | Next.js framework reference | MIT | App Router page composition and client component boundaries | Brand Brain needs interactive editing inside the existing Next.js shell | Used existing GrowthOS Next.js patterns; no external code copied |
| `facebook__react` | React UI framework reference | MIT | Controlled form state and derived preview state | The Brand Brain editor has many structured inputs and a live preview | Implemented with local components and `useState`/`useMemo` |
| `radix-ui__primitives` | Accessible UI primitive reference | MIT | Accessible form and panel composition concepts | The editor needs labeled controls and keyboard-friendly primitives without adding a dependency | Reused current GrowthOS field/card components with accessible labels |
| `openai__openai-agents-python` | Agent architecture patterns | MIT | Separation between memory/context assembly and provider execution | Brand Brain should enrich prompts without binding routes to a specific model provider | Added service-level context assembly before provider invocation |
| `run-llama__llama_index` | Retrieval and memory architecture reference | MIT | Treating durable brand facts as reusable context | Future Brand Brain memory can evolve from JSON facts to indexed retrieval | Started with JSON persistence and documented migration path |
| `modelcontextprotocol__python-sdk` | Tool/provider boundary reference | MIT | Explicit interface boundaries around future integrations | Brand Brain will later expose tools/connectors without route coupling | Kept repository and service abstractions separate from API routes |
| `run-llama__llama_index` | Retrieval and memory architecture reference | MIT | Research artifacts as reusable, structured knowledge records | Research Hub needs saved outputs that can later become indexed memory | Adopted result/memory structure concepts only; no code copied |
| `deepset-ai__haystack` | Retrieval pipeline reference | Apache-2.0 | Separation between source notes, findings, and synthesis | Research Hub must avoid blending unverified assumptions with source metadata | Adopted pipeline boundary concepts only; no code copied |
| `microsoft__markitdown` | Document conversion reference | MIT | Future file-to-text ingestion pathway | Research Hub will later ingest files without changing its result schema | Documented as future integration pattern only |
| `browser-use__browser-use` | Browser automation reference | MIT | Browser research as a future connector, not v0.4.0 core | Keeps live browsing out of the initial release while preserving expansion path | Documented future connector boundary only |
| `microsoft__playwright` | Browser automation and testing | Apache-2.0 | Smoke-test workflow for multi-module browser regression | Research Hub needs validation across Brand Brain, Content Studio, mobile navigation, copy, and offline states | Used for local smoke validation approach only |
| `modelcontextprotocol__python-sdk` | Tool boundary reference | MIT | Connector/tool interface separation for future research sources | Future Research Hub integrations should remain behind explicit connector boundaries | Reused architectural boundary concept only |
| `openai__openai-agents-python` | Agent responsibility patterns | MIT | Planner, source evaluator, synthesizer, and brand alignment agent responsibilities | Research Hub needs clear future agent roles without adding an agent framework now | Adopted responsibility separation concepts only |
| `vercel__next.js` | Next.js framework reference | MIT | Client-side protected shell composition | v0.5.0 needs login/register gating without replacing the existing dashboard | Used existing GrowthOS App Router/client component patterns; no external code copied |
| `facebook__react` | React UI framework reference | MIT | Controlled auth form state and session-derived rendering | Authentication requires ergonomic login/register state and workspace switching | Implemented with local components and React state; no external code copied |
| `microsoft__playwright` | Browser automation and testing | Apache-2.0 | Authenticated smoke-test flow before module regression checks | v0.5.0 protects the app, so browser tests must authenticate before validating released modules | Extended local smoke script only; no source copied |
