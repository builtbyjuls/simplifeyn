#!/usr/bin/env bash
# Helper script to retrieve git diff and change summaries for Simplifeyn debriefing.
set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: Not inside a git repository." >&2
  exit 1
fi

print_diff() {
  local stat_cmd="$1"
  local diff_cmd="$2"
  echo "=== Files Changed ==="
  eval "$stat_cmd"
  echo ""
  echo "=== Diff Content ==="
  eval "$diff_cmd"
}

if [ $# -gt 0 ]; then
  TARGET="$1"

  if [ "$TARGET" = "staged" ]; then
    print_diff "git diff --cached --stat" "git diff --cached"
    exit 0
  fi

  if [ "$TARGET" = "unstaged" ]; then
    print_diff "git diff --stat" "git diff"
    exit 0
  fi

  # Check if target is a range (contains ..)
  if [[ "$TARGET" =~ \.\. ]]; then
    # Validate range
    if ! git rev-parse "$TARGET" >/dev/null 2>&1; then
      echo "Error: Invalid revision range: $TARGET" >&2
      exit 1
    fi
    print_diff "git diff --stat '$TARGET'" "git diff '$TARGET'"
    exit 0
  fi

  # Single commit or ref
  if ! git rev-parse --verify "$TARGET" >/dev/null 2>&1; then
    echo "Error: Invalid revision or ref: $TARGET" >&2
    exit 1
  fi

  if git rev-parse --verify "${TARGET}~1" >/dev/null 2>&1; then
    print_diff "git diff --stat '${TARGET}~1..${TARGET}'" "git diff '${TARGET}~1..${TARGET}'"
  else
    # Root commit
    print_diff "git show --stat --format='' '${TARGET}'" "git show '${TARGET}'"
  fi
  exit 0
fi

# Default mode (no arguments):
# 1. Check if uncommitted working tree changes exist
UNCOMMITTED=$(git status --porcelain 2>/dev/null || true)
if [ -n "$UNCOMMITTED" ]; then
  if git rev-parse --verify HEAD >/dev/null 2>&1; then
    print_diff "git diff --stat HEAD" "git diff HEAD"
  else
    print_diff "git diff --stat" "git diff"
  fi
  exit 0
fi

# 2. Clean working tree: show HEAD commit diff
if git rev-parse --verify HEAD >/dev/null 2>&1; then
  if git rev-parse --verify HEAD~1 >/dev/null 2>&1; then
    print_diff "git diff --stat HEAD~1..HEAD" "git diff HEAD~1..HEAD"
  else
    # Root commit
    print_diff "git show --stat --format='' HEAD" "git show HEAD"
  fi
else
  echo "Repository has no commits and working tree is clean."
fi
