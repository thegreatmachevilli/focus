#!/bin/bash

# GitHub Remote Connector - Codex Deployment Setup
# This script sets up the connector and initializes remotes for all repos

set -e

GITHUB_USER="thegreatmachevilli"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
BASE_PATH="${BASE_PATH:-.github_repos}"

echo "🚀 GitHub Remote Connector - Codex Deployment"
echo "=============================================="
echo "User: $GITHUB_USER"
echo "Base Path: $BASE_PATH"
echo ""

TOKEN_ARGS=()
if [ -n "$GITHUB_TOKEN" ]; then
    TOKEN_ARGS=(--token "$GITHUB_TOKEN")
else
    echo "⚠️  GITHUB_TOKEN not set; continuing in public-access mode."
fi

# Run the connector
echo "🔗 Initializing GitHub remote connector..."
python3 github_remote_connector.py \
    --user "$GITHUB_USER" \
    "${TOKEN_ARGS[@]}" \
    --path "$BASE_PATH" \
    --action clone

echo ""
echo "🪞 Creating unified mirror..."
python3 github_remote_connector.py \
    --user "$GITHUB_USER" \
    "${TOKEN_ARGS[@]}" \
    --path "$BASE_PATH" \
    --action mirror

echo ""
echo "📋 Generating repository report..."
python3 github_remote_connector.py \
    --user "$GITHUB_USER" \
    "${TOKEN_ARGS[@]}" \
    --path "$BASE_PATH" \
    --action report

echo ""
echo "✅ Deployment complete!"
echo "Repository remotes are now connected and ready for operations."
echo "All repos cloned to: $BASE_PATH"
echo "Check $BASE_PATH/connector_log.txt for detailed logs"
