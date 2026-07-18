# Ollama Integration

## Purpose

GrowthOS can use a local Ollama model for AI Content Studio generation while keeping the deterministic mock provider as a safe fallback.

## Installation Prerequisite

Install Ollama locally from the official project site or package manager for your operating system. This repository does not download Ollama or model weights automatically.

Check installation:

```powershell
where.exe ollama
Get-Command ollama -ErrorAction SilentlyContinue
ollama --version
ollama list
```

## Recommended Model

Current local default:

```text
llama3.2:latest
```

This model is a practical starting point for the current validation machine because it is already installed, content-capable, and smaller than the larger local models available on the same host.

Do not download large models without confirming available disk space and runtime memory.

## Environment Variables

Create `apps/api/.env` locally if needed. Do not commit it.

```text
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
AI_FALLBACK_PROVIDER=mock
OLLAMA_TIMEOUT_SECONDS=90
```

Use mock-only mode:

```text
AI_PROVIDER=mock
```

## Startup Commands

Start Ollama separately using the local Ollama application or service.

Start the API:

```powershell
.\scripts\run-api.ps1
```

Start the frontend:

```powershell
.\scripts\run-web.ps1
```

## Fallback Behavior

If `AI_PROVIDER=ollama` and Ollama is unavailable, times out, or returns malformed JSON, GrowthOS uses the deterministic mock provider when `AI_FALLBACK_PROVIDER=mock`.

Fallback responses return:

```json
{
  "provider": "mock-fallback"
}
```

The frontend shows:

```text
Local AI was unavailable, so GrowthOS used the offline fallback.
```

## Troubleshooting

- Confirm Ollama is running at `OLLAMA_BASE_URL`.
- Confirm the configured model appears in `ollama list`.
- Increase `OLLAMA_TIMEOUT_SECONDS` if local inference is slow.
- Use `AI_PROVIDER=mock` for offline development or automated testing.
- Check `GET http://localhost:8000/health` for non-sensitive provider status.

## Privacy

Ollama inference runs locally on your machine. Prompts are sent to the local Ollama HTTP API, not a cloud AI provider. Generated content quality depends on the installed local model.
