#!/bin/bash
set -e

# Default to running the API if no command is specified
if [ "$1" = 'api' ]; then
    echo "Starting API..."
    exec fastapi run main.py --port $PORT
elif [ "$1" = 'worker-transcriber' ]; then
    echo "Starting Transcriber Worker..."
    exec python -m workers.transcriber
elif [ "$1" = 'worker-llm' ]; then
    echo "Starting LLM Worker..."
    exec python -m workers.llm_worker
elif [ "$1" = 'worker-vault' ]; then
    echo "Starting Vault Writer Worker..."
    exec python -m workers.vault_writer
else
    exec "$@"
fi
