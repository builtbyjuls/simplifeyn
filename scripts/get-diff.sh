#!/usr/bin/env bash
# Helper script to retrieve git diff and change summaries for Feynman debriefing.
set -euo pipefail

TARGET="${1:-HEAD}"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: Not inside a git repository." >&2
  exit 1
fi

echo "=== Files Changed ==="
if [ "$TARGET" = "staged" ]; then
  git diff --cached --stat
  echo ""
  echo "=== Diff Content ==="
  git diff --cached
elif [ "$TARGET" = "unstaged" ]; then
  git diff --stat
  echo ""
  echo "=== Diff Content ==="
  git diff
else
  # Default: diff against specified target (or HEAD / working tree)
  if git rev-parse --verify "$TARGET" >/dev/null 2>&1; then
    git diff --stat "${TARGET}~1" "${TARGET}" 2>/dev/null || git diff --stat "${TARGET}"
    echo ""
    echo "=== Diff Content ==="
    git diff "${TARGET}~1" "${TARGET}" 2>/dev/null || git diff "${TARGET}"
  else
    git diff --stat
    echo ""
    echo "=== Diff Content ==="
    git diff
  fi
fi
