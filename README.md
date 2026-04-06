# Noavia AI Ticketing System

An automated Support Ticket System built with [n8n](https://n8n.io/), [Qdrant](https://qdrant.tech/), and OpenAI. This project demonstrates how to answer support inquiries automatically using Retrieval-Augmented Generation (RAG) over a standard markdown knowledge base.

[![Submit a Ticket](https://img.shields.io/badge/Submit-Ticket-6366f1?style=for-the-badge)](https://noavia.alielite.dev)
[![View Logs](https://img.shields.io/badge/View-Google%20Sheets-4ade80?style=for-the-badge)](https://docs.google.com/spreadsheets/d/1hkOV9jvLJG7HPW6lyuJuMY9ju-9P_QgMzrLYV6ENaSE/edit?gid=0#gid=0)

---

## Architecture Overview

The system is designed for high performance, reliability, and ease of deployment.

![Support Ticket Flow](./docs/ticket-flow.png)

1. **Self-Hosted n8n Orchestration**: Acts as the central brain, coordinating between the vector store, AI agents, and communication channels (Gmail, Google Sheets).
2. **FastAPI Webhook Proxy**: A high-performance Python bridge that handles incoming ticket submissions (including PDF metadata) and proxies them into n8n's event-driven pipeline.
3. **Traefik Ingress**: Automates SSL/TLS certificates via Let's Encrypt for securely exposing the portal, n8n, and Qdrant under professional subdomains.
4. **Qdrant Vector DB**: A production-ready vector database used for context-aware retrieval.

---

## AI Output Validation

To ensure the AI categorizes and summarizes tickets with 100% reliability for downstream processing, we implement:

- **Structured Output Parser Node**: We enforce a strict JSON schema at the orchestration level. The n8n Classification Agent is required to output:
  - `Category`: (String)
  - `Urgency`: (critical, high, medium, low)
  - `Sentiment`: (String)
  - `Confidence`: (Float 0-1)
  - `Summary`: (String)
- **Schema Enforcement**: This guarantees that n8n's logic (like `Switch` nodes for urgent routing) never fails due to malformed or conversational "garbage" output from the LLM. If confidence is `< 0.6`, the system automatically flags the ticket for manual human review.

---

## RAG Implementation

Our Retrieval-Augmented Generation strategy focuses on grounding the AI in company-specific ground truth documents.

1. **Chunking Strategy**: We use `RecursiveCharacterTextSplitter` with a chunk size of 1000 and an overlap of 150. This balance allows the system to retain enough context (like specific policy headers) while ensuring the AI can focus on relevant paragraphs for specific questions.
2. **Embedding Model**: We use OpenAI's `text-embedding-3-small` model (1536 dimensions) for its high-performance retrieval-accuracy-to-cost ratio.
3. **Retrieval Approach**: We implement nearest-neighbor search via **Qdrant**. The RAG Agent node in n8n uses a `VectorStoreTool` to pull exactly the top-3 most similar chunks before drafting a response.
4. **Low-Similarity Guardrail**: When retrieval quality is low (top similarity score below `0.45`, or no relevant chunk is returned), the draft explicitly includes: `Note: No specific policy found — this response is based on general knowledge.`

---

## Future Improvements

With more time, the following features would enhance the system:
- **Hybrid Search**: Combining semantic search with BM25 keyword matching for better handling of technical product codes.
- **Caching Layer**: Implementing Redis to cache common FAQ responses, reducing LLM calls and latency.
- **Multimodal Support**: Enabling the AI to perform OCR on PDF attachments natively to extract even more contextual data.
- **A/B Prompt Testing**: An automated framework to test different system prompts against historical "perfect" human answers to measure response quality drifts.

---

## Quick Start

1. Copy `.env.example` to `.env` and add your `OPENAI_API_KEY`.
2. Run `docker-compose up -d --build`.
3. The system will automatically ingest documents from `data/knowledge_base` into Qdrant on startup.
