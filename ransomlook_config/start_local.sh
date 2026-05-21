#!/bin/bash
set -e

echo "Patching RansomLook to use TCP Redis..."
python3 /ransomlook/config/patch_redis.py

echo "Patching RansomLook API..."
python3 /ransomlook/config/patch_api.py

echo "Starting RansomLook scrapper in background..."
cd /ransomlook
poetry run scrape &

echo "Starting RansomLook website..."
poetry run start_website
