#!/bin/bash

# Set working directory
cd /home/sathyan/slr_mvp_build/slr_backend_apis

# Initialize conda for this shell
eval "$(conda shell.bash hook)"

# Activate conda environment
conda activate slr_ai

# Set Python path
export PYTHONPATH="/home/sathyan/slr_mvp_build/slr_backend_apis"

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the API
exec uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1
