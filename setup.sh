#!/bin/bash

# Improved setup script including better variable checks
set -euo pipefail

GITHUB_USER="${GITHUB_USER:-thegreatmachevilli}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
BASE_PATH="${BASE_PATH:-.github_repos}"

if [ -z "$GITHUB_USER" ]; then
    echo "❌ GITHUB_USER is not set. Aborting setup."
    exit 1
fi

echo "Setting up the repository deployment connector! Please ensure token is ready."