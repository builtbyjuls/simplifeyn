#!/usr/bin/env bash
# Helper script to retrieve git diff and change summaries for Simplifeyn debriefing.
set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: Not inside a git repository." >&2
  exit 1
fi

run_git_diff() {
  echo "=== Files Changed ==="
  git diff --stat "$@"
  echo ""
  echo "=== Diff Content ==="
  git diff "$@"
}

run_git_show() {
  local ref="$1"
  echo "=== Files Changed ==="
  git show --stat --format='' "$ref"
  echo ""
  echo "=== Diff Content ==="
  git show "$ref"
}

if [ $# -gt 0 ]; then
  if [[ "$1" == -* ]]; then
    echo "Error: Options and flags are not supported: $1" >&2
    exit 1
  fi
  TARGET="$1"

  if [ "$TARGET" = "staged" ]; then
    run_git_diff --cached
    exit 0
  fi

  if [ "$TARGET" = "unstaged" ]; then
    run_git_diff
    exit 0
  fi

  # Check if target is a range (contains ..)
  if [[ "$TARGET" =~ \.\. ]]; then
    if ! git rev-parse "$TARGET" >/dev/null 2>&1; then
      echo "Error: Invalid revision range: $TARGET" >&2
      exit 1
    fi
    run_git_diff "$TARGET"
    exit 0
  fi

  # Single commit or ref
  if ! git rev-parse --verify "$TARGET" >/dev/null 2>&1; then
    echo "Error: Invalid revision or ref: $TARGET" >&2
    exit 1
  fi

  if git rev-parse --verify "${TARGET}~1" >/dev/null 2>&1; then
    run_git_diff "${TARGET}~1..${TARGET}"
  else
    run_git_show "$TARGET"
  fi
  exit 0
fi

# Default mode (no arguments):
# 1. Check if uncommitted working tree changes exist
UNCOMMITTED=$(git status --porcelain 2>/dev/null || true)
if [ -n "$UNCOMMITTED" ]; then
  if git rev-parse --verify HEAD >/dev/null 2>&1; then
    run_git_diff HEAD
  else
    run_git_diff
  fi
  exit 0
fi

# 2. Clean working tree: show HEAD commit diff
if git rev-parse --verify HEAD >/dev/null 2>&1; then
  if git rev-parse --verify HEAD~1 >/dev/null 2>&1; then
    run_git_diff "HEAD~1..HEAD"
  else
    run_git_show HEAD
  fi
else
  echo "Repository has no commits and working tree is clean."
fi
