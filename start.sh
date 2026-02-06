#!/usr/bin/env bash

echo "Starting FastAPI app with Uvicorn..."

uvicorn main:app \
  --host 0.0.0.0 \
  --port ${PORT:-10000}
