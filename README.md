# NOAVIA AI Support Ticket Pipeline

This repository contains a local-first support ticket system using FastAPI, n8n, OpenAI, and Qdrant.

- Intake endpoint: `/webhook/support-ticket` (served by `src/app.py`)
- Main workflow file: `support_ticket_pipline_main.json`
- Knowledge base docs: `data/knowledge_base/*.md`

![Support Ticket Flow](docs/ticket-flow.png)

## Architecture

1. **FastAPI portal/proxy (`src/app.py`)**
   - Serves the form UI at `/`
   - Proxies multipart ticket payloads to n8n at `${N8N_BASE_URL}/webhook/support-ticket`
   - Runs knowledge-base ingestion on startup
2. **n8n workflow orchestration (`support_ticket_pipline_main.json`)**
   - Validation -> PDF extraction (optional) -> classification -> RAG draft -> routing -> logging
3. **Qdrant vector store**
   - Stores embeddings for markdown knowledge base chunks in collection `knowledge_base`

### Key architecture decisions (and why)

- **FastAPI in front of n8n (`src/app.py`)**: keeps intake/web UX and orchestration concerns separated, while preserving multipart payload forwarding for optional PDF handling.
- **Single orchestrated workflow (`support_ticket_pipline_main.json`)**: keeps validation, AI processing, routing, and logging visible in one execution graph for debugging and interview walkthroughs.
- **Startup ingestion in app lifecycle**: ensures the KB is present before ticket processing, reducing first-run retrieval failures in local environments.
- **Containerized local stack (`docker-compose.yml`)**: reproducible setup for `portal` + `n8n` + `qdrant`, with env-based secret wiring instead of hardcoded keys.

## Local Development Quick Start

### 1) Prerequisites

- Docker + Docker Compose
- OpenAI API key

### 2) Configure environment

```zsh
cp .env.example .env
```

Set at minimum in `.env`:

- `OPENAI_API_KEY=...`
- `QDRANT_API_KEY=...` (optional but recommended; compose passes it to both services)

### 3) Start services

```zsh
docker compose up -d --build
```

Local endpoints:

- Portal: `http://localhost:8080`
- n8n UI: `http://localhost:5678`
- Qdrant: `http://localhost:6333`

### 4) Import workflow in n8n

1. Open `http://localhost:5678`
2. Import `support_ticket_pipline_main.json`
3. Verify webhook node path is `support-ticket`

### 5) Configure n8n credentials (required)

Set credentials used by nodes in `support_ticket_pipline_main.json`:

- `OpenAI account` (`openAiApi`)
- `Qdrant account` (`qdrantApi`)
- Gmail OAuth2 credential (for urgent/medium email branches)
- Google Sheets OAuth2 credential (for ticket logging)

After credentials are set, open each integration node once and confirm credential binding is valid.

### 6) Activate and test

Activate the workflow, then submit from UI or send a test payload:

```zsh
curl -X POST "http://localhost:8080/webhook/support-ticket" \
  -F "Name=Jane Doe" \
  -F "Email=jane@example.com" \
  -F "Subject=Refund request" \
  -F "Message=I was charged twice for my subscription."
```

## Current AI + RAG Behavior

### AI output validation

- `Step 1 - Classification & Analysis` enforces structured output via `Structured Output Parser`
- Required fields: `Category`, `Urgency`, `Sentiment`, `Confidence`, `Summary`
- Status is set to `needs-manual-review` when classification confidence is `< 0.6`

**Approach and why**

- **Approach**: force strict, machine-parseable classification JSON before routing logic executes.
- **Why**: prevents downstream branch failures caused by free-form LLM output (for example, malformed urgency labels that would break `Switch`/`IF` logic).
- **Approach**: apply a confidence gate (`< 0.6`) to override normal processing status.
- **Why**: low-certainty classifications are explicitly surfaced for human review instead of silently auto-resolving.

### RAG ingestion details (`src/ingest_to_qdrant.py`)

- Source files: `data/knowledge_base/*.md`
- Split strategy:
  - `MarkdownHeaderTextSplitter` on `#`, `##`, `###`
  - `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)`
- Embedding model: `text-embedding-3-small` (1536 dimensions)
- Collection name: `knowledge_base`
- Metadata added per chunk: `source`, `filename`

**Why this chunking/embedding setup**

- Header-aware splitting preserves document structure (policy section context), then recursive splitting keeps chunk size stable for embedding/search efficiency.
- `text-embedding-3-small` is used as a practical quality/cost tradeoff for local interview-scale retrieval.

### RAG retrieval details (workflow)

- `Qdrant Vector Store` node uses top `3` chunks (`topK: 3`)
- Step 2 prompt instructs fallback note when retrieval is low-confidence or empty:
  - `Note: No specific policy found - this response is based on general knowledge.`

**Retrieval approach and why**

- Top-3 retrieval keeps prompt context focused while still giving enough evidence for policy-grounded responses.
- Source citation format (`[Source: filename.md]`) is required in the draft so reviewers can verify grounding quickly.
- Fallback note is explicitly required when retrieval quality is weak, so generated replies stay transparent about uncertainty.

## Routing and Storage

From `Urgency Router` in `support_ticket_pipline_main.json`:

- `critical/high` -> detailed Gmail + Google Sheets
- `medium` -> brief Gmail + Google Sheets
- `low` -> Google Sheets only

Google Sheets row includes ticket info, AI fields, draft response, status, knowledge sources, and processing log.

## Useful Commands

Re-run ingestion manually from the running `portal` container:

```zsh
docker compose exec portal uv run python -m src.ingest_to_qdrant
```

Stop all services:

```zsh
docker compose down
```

## What I Would Improve With More Time

- Add a normalization node before final status calculation to standardize retrieval score shape from vector output payloads.
- Add replayable regression fixtures (sample ticket payloads + expected route/status) for workflow-level smoke tests.
- Add a dedicated human-review queue destination (separate sheet tab or Slack channel) for `needs-manual-review` tickets.
- Add OCR coverage for scanned/image-only PDFs to improve attachment reliability.

