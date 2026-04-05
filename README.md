# AI Support Ticket System

An automated Support Ticket System built with [n8n](https://n8n.io/), [Qdrant](https://qdrant.tech/), and OpenAI embeddings. This project demonstrates how to answer support inquiries automatically using Retrieval-Augmented Generation (RAG) over a standard markdown knowledge base.

## Project Overview

This repository contains the foundational structure to spin up n8n and Qdrant locally, along with a Python script to ingest markdown knowledge base files into the vector database using OpenAI's embeddings.

### Directory Structure
- `/data/knowledge_base`: Contains the markdown files acting as the system's ground truth.
- `/src`: Python source code utilities like data ingestion scripts.
- `/tests`: Testing directory.
- `/docker`: (Reserved for future Dockerfile extensions or setups).
- `docker-compose.yml`: For spinning up n8n and Qdrant locally.
- `requirements.txt`: Python package dependencies.

## Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose installed.
- [Python 3.9+](https://www.python.org/) installed.
- An [OpenAI API Key](https://platform.openai.com/api-keys)

## Setup Instructions

### 1. Configure Environment Variables
Copy `.env.example` to a new `.env` file and insert your OpenAI API key.
```bash
cp .env.example .env
```

### 2. Spin up Services with Docker Compose
Run the following command in the root directory to start n8n and Qdrant together in the background:
```bash
docker-compose up -d
```
- n8n will be accessible at: `http://localhost:5678`
- Qdrant will be accessible at: `http://localhost:6333`

### 3. Ingest Knowledge Base
To allow the AI to answer contextually, you need to embed the documentation into Qdrant.

1. Create and activate a Python virtual environment at the project root:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the ingestion script from the source directory:
   ```bash
   python src/ingest_to_qdrant.py
   ```
   *Note: This script will automatically load variables from the `.env` file in the root directory.*

---

## Technical Details

### Architecture Decisions
We chose an event-driven architecture using **n8n** for orchestrating the AI pipelining due to its powerful visual workflow design and robust `Langchain` nodes. 
The perfect production-ready workflow (`support_ticket_pipeline.json`) processes incoming webhooks (with rigorous field validation), uses an `IF` condition to smartly handle optional PDF attachments, extracts textual data safely (`continueOnFail`), and constructs a clean ticket log. From there, we perform a sequential AI analysis via Agent nodes:
1. **Classification Agent:** Determines Category, Urgency, Sentiment, Confidence, and Summary.
2. **RAG Agent:** Uses the embedded knowledge base via the `VectorStoreTool` to ground the draft response based strictly on company policies.

A `Switch` node routes logs to Google Sheets (including full pipeline logs and knowledge source tracking), and sends contextual HTML email notifications depending on whether the ticket is marked *Urgent* or *Medium*. Any ticket with Confidence < 0.6 is additionally flagged for manual review. We also implemented comprehensive error handling (e.g. `onError: 'continueErrorOutput'`) across the pipeline.

### AI Output Validation
To ensure perfectly reliable and parsable data from the Classification step, we use the `Structured Output Parser` node enforcing a strict programmatic JSON schema:
`"Category"`, `"Urgency" (critical, high, medium, low)`, `"Sentiment"`, `"Confidence" (0-1)`, and `"Summary"`.
Handling outputs as tightly coupled JSON guarantees the downstream `Switch` routing logic, Google Sheets ingestion, and RAG drafting never fail due to malformed conversational garbage.

### RAG Implementation Details
For knowledge retrieval, we provided 11 Markdown FAQ and policy documents inside the `/data/knowledge_base` folder. 
The RAG strategy uses:
- **Chunking:** `RecursiveCharacterTextSplitter` with balanced chunks to retain paragraph context.
- **Embedding:** `OpenAI embeddings` vectorizing raw strings to high-dimensional space.
- **Vector Store:** Local `Qdrant` instances run in Docker for fast and scalable nearest-neighbor/cosine similarity.
- **Retrieval & Drafting:** A Langchain Agent leverages an attached VectorStoreTool to pull the top-3 most similar chunks before drafting a response to the user. A strict fallback message is baked into the system prompt for low-confidence queries (`< 0.6`).
