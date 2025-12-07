# Pi-Hub Backend

A production-shaped backend service for ingesting audio notes, processing them (transcription + LLM summarization), and writing structured markdown files.

## Features

- **Audio Ingestion**: Upload audio files via API.
- **Async Processing**:
    - **Transcription**: Uses `faster-whisper` (or `whisper.cpp`) to transcribe audio.
    - **Summarization**: Uses `llama-cpp-python` to generate summaries, action items, and titles.
    - **Vault Writer**: Writes processed notes as Markdown files to a vault directory.
- **API**: FastAPI-based REST API.
- **Infrastructure**: Docker Compose, PostgreSQL, Caddy Reverse Proxy.

## Tech Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy ORM (Async)
- **AI Models**: `faster-whisper`, `llama-cpp-python`
- **Containerization**: Docker, Docker Compose

## Getting Started

### Prerequisites

- Docker & Docker Compose
- (Optional) GPU for faster inference (requires NVIDIA Container Toolkit)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repo-url>
    cd pi-hub-backend
    ```

2.  **Environment Setup**:
    Copy `.env.example` to `.env`:
    ```bash
    cp .env.example .env
    ```
    Adjust settings in `.env` if needed.

3.  **Download Models**:
    Create a `models` directory and download your GGUF models (e.g., Llama 2) and Whisper models if not auto-downloaded.
    *Note: `faster-whisper` auto-downloads models to cache, but you can map a volume to persist them.*

4.  **Run with Docker Compose**:
    ```bash
    docker-compose up --build
    ```

### Usage

**API Documentation**:
Once running, visit `http://localhost/docs` (via Caddy) or `http://localhost:8000/docs` (direct) to see the Swagger UI.

**Ingest Audio**:
```bash
curl -X POST "http://localhost/api/notes/audio" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/audio.wav"
```

**Check Status**:
The system will process the note through the pipeline: `UPLOADED` -> `TRANSCRIBED` -> `PROCESSED` -> `DONE`.
Check the `/data/vault` directory (mapped volume) for the final Markdown file.

## Development

- **Project Structure**:
    - `api/`: FastAPI routes and schemas.
    - `core/`: Configuration, models, logging.
    - `infra/`: Database and storage logic.
    - `workers/`: Background worker scripts.
    - `scripts/`: Utility scripts.

- **Run Locally (without Docker)**:
    1.  Install dependencies: `pip install -r requirements.txt`
    2.  Start DB (e.g., via Docker).
    3.  Run API: `uvicorn main:app --reload`
    4.  Run Workers: `python -m workers.transcriber`, etc.
