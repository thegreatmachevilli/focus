#!/bin/bash

# Focus AI Engine launcher for repo workflows.
# Supports both repository connector tasks and bid-editing workspace setup.

set -euo pipefail

ACTION="${1:-open}"
shift || true

GITHUB_USER="${GITHUB_USER:-thegreatmachevilli}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
BASE_PATH="${BASE_PATH:-.github_repos}"
BRANCH="${BRANCH:-main}"
MIRROR_PATH="${MIRROR_PATH:-}"
BID_ROOT="${BID_ROOT:-projects}"

TOKEN_ARGS=()
if [ -n "$GITHUB_TOKEN" ]; then
    TOKEN_ARGS=(--token "$GITHUB_TOKEN")
fi

show_banner() {
    echo "🧠 Focus AI Engine"
    echo "=================="
    echo "User: $GITHUB_USER"
    echo "Base Path: $BASE_PATH"
    echo "Bid Root: $BID_ROOT"
    echo "Branch: $BRANCH"
    if [ -n "$GITHUB_TOKEN" ]; then
        echo "Auth: token provided"
    else
        echo "Auth: public-access mode"
    fi
    echo ""
}

show_help() {
    show_banner
    cat <<'EOF'
Usage:
  ./focus_engine.sh [action]

Bid workflow actions:
  open        Show engine status and the bid workflow location
  bid-open    Show the current bid workspace instructions
  bid-init    Create a bid-editing workspace in the repo
  bid-pdfs    Export current bid workspace artifacts to PDFs
  drive-save  Save last workflow/task artifacts to Google Drive

Repository connector actions:
  clone       Clone or refresh the configured GitHub user's repositories
  sync        Fetch and pull all locally cloned repositories
  push        Push local repositories to origin using $BRANCH
  list        List locally cloned repositories
  report      Generate a repository report
  mirror      Create or refresh the unified mirror remote
  setup       Run the full setup flow (clone + mirror + report)
  task        Run a shell task through codex_task.js
  help        Show this help text

Examples:
  ./focus_engine.sh open
  ./focus_engine.sh bid-open
  ./focus_engine.sh bid-init quincy-office-remodel "Quincy Office Remodel"
  ./focus_engine.sh bid-pdfs quincy-office-remodel
  ./focus_engine.sh drive-save
  ./focus_engine.sh clone
  ./focus_engine.sh task "git status"
EOF
}

run_connector() {
    local action="$1"
    local extra_args=()

    if [ "$action" = "push" ]; then
        extra_args+=(--branch "$BRANCH")
    fi

    if [ "$action" = "mirror" ] && [ -n "$MIRROR_PATH" ]; then
        extra_args+=(--mirror-path "$MIRROR_PATH")
    fi

    python3 github_remote_connector.py \
        --user "$GITHUB_USER" \
        "${TOKEN_ARGS[@]}" \
        --path "$BASE_PATH" \
        --action "$action" \
        "${extra_args[@]}"
}

show_bid_workspace() {
    show_banner
    echo "Bid workflow is stored under: $BID_ROOT"
    echo ""
    echo "If the project workspace exists, put these files in its input folder:"
    echo "  - current bid PDF or editable source"
    echo "  - gold-line RLC template"
    echo "  - original/highest-quality logo file"
    echo ""
    echo "Current instruction: leave out the floor plans from the revised package."
}


export_bid_pdfs() {
    local slug="${1:-}"

    if [ -z "$slug" ]; then
        echo "❌ Usage: ./focus_engine.sh bid-pdfs <project-slug>"
        exit 1
    fi

    python3 focus_bid_workflow.py export-pdfs "$slug" \
        --root "$BID_ROOT"
}

init_bid_workspace() {
    local slug="${1:-}"
    local project_name="${2:-}"

    if [ -z "$slug" ] || [ -z "$project_name" ]; then
        echo "❌ Usage: ./focus_engine.sh bid-init <project-slug> \"<Project Name>\""
        exit 1
    fi

    python3 focus_bid_workflow.py init "$slug" \
        --project-name "$project_name" \
        --root "$BID_ROOT"
}

case "$ACTION" in
    open)
        show_banner
        echo "The engine is loaded in this repo."
        echo ""
        echo "Use the bid workflow for office-remodel package updates:"
        echo "  ./focus_engine.sh bid-open"
        echo "  ./focus_engine.sh bid-init <project-slug> \"<Project Name>\""
        echo "  ./focus_engine.sh bid-pdfs <project-slug>"
        echo ""
        echo "Repository connector actions are still available:"
        echo "  ./focus_engine.sh clone"
        echo "  ./focus_engine.sh report"
        echo "  ./focus_engine.sh mirror"
        echo "  ./focus_engine.sh list"
        ;;
    bid-open)
        show_bid_workspace
        ;;
    bid-init)
        init_bid_workspace "$@"
        ;;
    bid-pdfs)
        export_bid_pdfs "$@"
        ;;
    drive-save)
        python3 focus_drive_sync.py --root "$BID_ROOT" "$@"
        ;;
    clone|sync|push|list|report|mirror)
        show_banner
        run_connector "$ACTION" "$@"
        ;;
    setup)
        show_banner
        bash setup.sh
        ;;
    task)
        show_banner
        if [ "$#" -eq 0 ]; then
            echo "❌ Provide a command to run, for example:"
            echo "   ./focus_engine.sh task \"git status\""
            exit 1
        fi
        node codex_task.js "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown action: $ACTION"
        echo ""
        show_help
        exit 1
        ;;
esac
