#!/usr/bin/env bash
# Helper script to retrieve git diff and change summaries for Simplifeyn debriefing.
set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: Not inside a git repository." >&2
  exit 1
fi

detect_project_surface() {
  local toplevel
  toplevel="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

  local has_ui=0
  local has_backend=0
  local has_cli=0
  local details=""

  # Check for frontend / UI indicators
  if [ -f "$toplevel/index.html" ] || [ -d "$toplevel/src/components" ] || [ -d "$toplevel/ui" ]; then
    has_ui=1
    details="HTML/UI components"
  fi
  if [ -f "$toplevel/package.json" ]; then
    if grep -iqE '"(react|vue|svelte|next|nuxt|solid-js|angular|electron)"' "$toplevel/package.json" 2>/dev/null; then
      has_ui=1
      details="Web UI"
    fi
  fi
  if [ "$has_ui" -eq 0 ]; then
    if (set +o pipefail; git ls-files "$toplevel" 2>/dev/null | grep -qE '\.(html|jsx|tsx|vue|svelte)$'); then
      has_ui=1
      details="UI templates/components"
    fi
  fi

  # Check for backend indicators
  if [ -f "$toplevel/pom.xml" ] || [ -f "$toplevel/build.gradle" ] || [ -f "$toplevel/build.gradle.kts" ]; then
    has_backend=1
    details="${details:-Spring Boot / JVM service}"
  elif [ -f "$toplevel/go.mod" ]; then
    has_backend=1
    details="${details:-Go service}"
  elif [ -f "$toplevel/Cargo.toml" ]; then
    has_backend=1
    details="${details:-Rust crate}"
  elif [ -f "$toplevel/requirements.txt" ] || [ -f "$toplevel/pyproject.toml" ]; then
    has_backend=1
    details="${details:-Python backend}"
  fi

  # Check for CLI indicators
  if [ -d "$toplevel/cmd" ] || [ -d "$toplevel/bin" ] || [ -f "$toplevel/cli.py" ]; then
    has_cli=1
    details="${details:-CLI entrypoint}"
  fi

  # Check for project memory (AGENTS.md / GEMINI.md / CLAUDE.md)
  local memory_note=""
  for memfile in "$toplevel/AGENTS.md" "$toplevel/GEMINI.md" "$toplevel/CLAUDE.md"; do
    if [ -f "$memfile" ]; then
      if grep -iqE '((dashboard|ui|frontend)[^.]*defer|defer[^.]*(dashboard|ui|frontend))' "$memfile" 2>/dev/null; then
        memory_note=" [Note: UI/dashboards marked as deferred in project memory]"
        break
      fi
    fi
  done

  echo "=== Project Context ==="
  if [ "$has_ui" -eq 1 ]; then
    echo "Surface: Web/UI App ($details)$memory_note"
  elif [ "$has_backend" -eq 1 ]; then
    echo "Surface: Headless Backend ($details | No UI detected)$memory_note"
  elif [ "$has_cli" -eq 1 ]; then
    echo "Surface: CLI Tool ($details)$memory_note"
  else
    echo "Surface: Generic Repository$memory_note"
  fi
  echo ""
}

run_git_diff() {
  detect_project_surface
  echo "=== Files Changed ==="
  git diff --stat "$@"
  echo ""
  echo "=== Diff Content ==="
  git diff "$@"
}

run_git_show() {
  local ref="$1"
  detect_project_surface
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
