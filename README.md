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
*(To be filled in later)*

### AI Output Validation
*(To be filled in later)*

### RAG Implementation Details
*(To be filled in later)*
