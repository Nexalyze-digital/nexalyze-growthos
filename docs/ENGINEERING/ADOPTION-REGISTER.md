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
