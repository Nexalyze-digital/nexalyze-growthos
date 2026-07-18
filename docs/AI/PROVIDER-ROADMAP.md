# AI Provider Roadmap

Status: v0.2.5 foundation roadmap

GrowthOS should keep provider integration behind the backend provider interface. Frontend code should consume provider metadata, fallback status, and generated content without depending on provider SDKs.

## Current Providers

| Provider | Status | Configuration | Cost Profile | Recommended Use |
| --- | --- | --- | --- | --- |
| Mock | Adopted | `AI_PROVIDER=mock` or automatic fallback | Free | Tests, demos, offline development, deterministic QA |
| Ollama | Adopted | `AI_PROVIDER=ollama`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL` | Free local runtime, hardware cost only | Local development, privacy-sensitive drafting, offline-first validation |

## Planned Providers

| Provider | Status | Configuration | Capabilities | Cost Profile | Recommended Use |
| --- | --- | --- | --- | --- | --- |
| OpenAI | Planned | `AI_PROVIDER=openai`, `OPENAI_API_KEY`, `OPENAI_MODEL` | Strong general writing, structured output, tool use, embeddings depending on model | Usage-based cloud | Production content, agents, research, proposals |
| Anthropic | Planned | `AI_PROVIDER=anthropic`, `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` | Long-form reasoning, drafting, analysis | Usage-based cloud | Research Hub, Proposal Generator, long context review |
| Google Gemini | Planned | `AI_PROVIDER=gemini`, `GEMINI_API_KEY`, `GEMINI_MODEL` | Multimodal and long-context workflows depending on model | Usage-based cloud | Website Intelligence, document and multimodal workflows |
| OpenRouter | Planned | `AI_PROVIDER=openrouter`, `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` | Unified routing across third-party models | Usage-based cloud aggregator | Provider experiments and model comparison |
| Groq | Planned | `AI_PROVIDER=groq`, `GROQ_API_KEY`, `GROQ_MODEL` | Low-latency inference for supported models | Usage-based cloud | Fast drafts, interactive UI loops |
| LM Studio | Planned | `AI_PROVIDER=lmstudio`, `LMSTUDIO_BASE_URL`, `LMSTUDIO_MODEL` | Local OpenAI-compatible inference | Free local runtime, hardware cost only | Local model experiments and offline development |

## Fallback Order

Recommended default order for development:

1. Configured primary provider.
2. Local compatible provider if configured and reachable.
3. Mock fallback.

Recommended default order for production:

1. Configured primary cloud provider.
2. Secondary cloud provider, if explicitly enabled for the workspace.
3. Mock fallback only for non-production demos or explicitly marked degraded mode.

## Provider Capabilities To Track

Each provider adapter should publish a small capabilities object:

- Text generation.
- Structured JSON generation.
- Streaming support.
- Embeddings.
- Tool/function calling.
- Vision or file support.
- Local/private runtime.
- Max context guidance.
- Cost category.
- Health check method.

## Configuration Rules

- Never expose provider API keys to the frontend.
- Keep provider selection server-side.
- Document each provider's required and optional environment variables.
- Preserve deterministic tests with mock provider fixtures.
- Separate live provider validation from normal unit tests.
- Log provider name, model, latency, fallback status, and error category without logging secrets.

## Recommended Sequence

1. Keep Mock and Ollama as stable local foundation.
2. Add OpenAI first for production-grade cloud generation.
3. Add Anthropic for long-form strategy and research quality.
4. Add Gemini where multimodal or long-context use cases are validated.
5. Add OpenRouter for provider experimentation after telemetry exists.
6. Add Groq for low-latency workflows.
7. Add LM Studio for local OpenAI-compatible model testing.

## Module Fit

| Module | Preferred Providers |
| --- | --- |
| AI Content Studio | Ollama, OpenAI, Groq, Mock |
| Brand Brain | OpenAI, Anthropic, Ollama |
| Research Hub | Anthropic, OpenAI, Gemini, Ollama |
| Publishing | OpenAI, Groq, Ollama |
| Website Intelligence | Gemini, OpenAI, Ollama |
| Lead Intelligence | OpenAI, Anthropic |
| Analytics | OpenAI, Mock |
| Proposal Generator | Anthropic, OpenAI, Ollama |
| Presentation Builder | Gemini, OpenAI, Anthropic |
| Workflow Automation | OpenAI, OpenRouter, Mock |
