#!/usr/bin/env bash
# Universal installer for simplifeyn across Claude Code, Antigravity, OpenAI Codex, and Cursor
set -euo pipefail
SCRIPT_DIR=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
elif [ -f "./SKILL.md" ]; then
  SCRIPT_DIR="$(pwd)"
fi

if [ -z "$SCRIPT_DIR" ] || [ ! -f "$SCRIPT_DIR/SKILL.md" ]; then
  echo "Error: install.sh must be run from within the simplifeyn repository." >&2
  echo "To install, obtain a local copy of the repository first." >&2
  exit 1
fi

SKILL_NAME="simplifeyn"

usage() {
  cat << 'EOF'
Usage: ./install.sh [OPTIONS]

Install simplifeyn skill to one or more AI coding assistants.

Options:
  --claude         Install to ~/.claude/skills/ (Claude Code)
  --antigravity    Install to ~/.gemini/config/skills/ (Antigravity CLI)
  --codex          Install to ~/.agents/skills/ (OpenAI Codex / Agent Skills standard)
  --cursor         Install to ~/.cursor/skills/ (Cursor)
  --project        Install to current repository project (.agents/skills/)
  --all            Install to all detected client directories
  --target DIR     Install to a custom directory DIR
  --check          Verify whether installed copies are up to date
  -h, --help       Show this help message

Default:
  If no options are given, auto-detects installed CLI tools and prompts/installs.
EOF
}

TARGETS=()
CHECK_MODE=0
CUSTOM_TARGET=""

while [ $# -gt 0 ]; do
  case "$1" in
    --claude)
      TARGETS+=("$HOME/.claude/skills")
      shift
      ;;
    --antigravity)
      TARGETS+=("$HOME/.gemini/config/skills")
      shift
      ;;
    --codex)
      TARGETS+=("$HOME/.agents/skills")
      shift
      ;;
    --cursor)
      TARGETS+=("$HOME/.cursor/skills")
      shift
      ;;
    --project)
      TARGETS+=(".agents/skills")
      shift
      ;;
    --target)
      if [ -z "${2:-}" ]; then
        echo "Error: --target requires a directory argument." >&2
        exit 1
      fi
      CUSTOM_TARGET="$2"
      TARGETS+=("$2")
      shift 2
      ;;
    --all)
      [ -d "$HOME/.claude" ] && TARGETS+=("$HOME/.claude/skills")
      [ -d "$HOME/.gemini" ] && TARGETS+=("$HOME/.gemini/config/skills")
      [ -d "$HOME/.agents" ] && TARGETS+=("$HOME/.agents/skills")
      [ -d "$HOME/.cursor" ] && TARGETS+=("$HOME/.cursor/skills")
      shift
      ;;
    --check)
      CHECK_MODE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

# If no target specified, detect available clients
if [ ${#TARGETS[@]} -eq 0 ]; then
  if [ -d "$HOME/.gemini" ]; then TARGETS+=("$HOME/.gemini/config/skills"); fi
  if [ -d "$HOME/.claude" ]; then TARGETS+=("$HOME/.claude/skills"); fi
  if [ -d "$HOME/.agents" ]; then TARGETS+=("$HOME/.agents/skills"); fi
  if [ -d "$HOME/.cursor" ]; then TARGETS+=("$HOME/.cursor/skills"); fi
  if [ ${#TARGETS[@]} -eq 0 ]; then
    TARGETS+=("$HOME/.agents/skills")
  fi
fi

# Function to copy files for the skill
install_to() {
  local dest_base="$1"
  local dest="$dest_base/$SKILL_NAME"
  mkdir -p "$dest_base"
  mkdir -p "$dest"

  cp "$SCRIPT_DIR/SKILL.md" "$dest/"
  if [ -d "$SCRIPT_DIR/references" ]; then
    rm -rf "$dest/references"
    cp -R "$SCRIPT_DIR/references" "$dest/"
  fi
  if [ -d "$SCRIPT_DIR/assets" ]; then
    rm -rf "$dest/assets"
    cp -R "$SCRIPT_DIR/assets" "$dest/"
  fi
  if [ -d "$SCRIPT_DIR/scripts" ]; then
    rm -rf "$dest/scripts"
    cp -R "$SCRIPT_DIR/scripts" "$dest/"
    chmod +x "$dest/scripts/"*
  fi

  # Clean up byte-compiled python artifacts and cache folders
  find "$dest" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
  find "$dest" -type f -name "*.pyc" -delete 2>/dev/null || true

  echo "[OK] Installed $SKILL_NAME to $dest"
}

check_in() {
  local dest_base="$1"
  local dest="$dest_base/$SKILL_NAME"
  if [ ! -d "$dest" ]; then
    echo "[FAIL] Not installed in $dest"
    return 1
  fi

  if [ ! -f "$dest/SKILL.md" ] || ! cmp -s "$SCRIPT_DIR/SKILL.md" "$dest/SKILL.md"; then
    echo "[FAIL] $dest/SKILL.md is missing or modified"
    return 1
  fi

  local subdir
  for subdir in references assets scripts; do
    if [ -d "$SCRIPT_DIR/$subdir" ]; then
      if [ ! -d "$dest/$subdir" ]; then
        echo "[FAIL] $dest/$subdir directory is missing"
        return 1
      fi
      while IFS= read -r -d '' src_file; do
        local rel_path="${src_file#$SCRIPT_DIR/}"
        local target_file="$dest/$rel_path"
        if [ ! -f "$target_file" ] || ! cmp -s "$src_file" "$target_file"; then
          echo "[FAIL] $dest/$rel_path is missing or modified"
          return 1
        fi
      done < <(find "$SCRIPT_DIR/$subdir" -type f ! -name "*.pyc" ! -path "*/__pycache__/*" -print0)
    fi
  done

  echo "[OK] $dest is up to date"
  return 0
}

CHECK_FAILED=0
for target in "${TARGETS[@]}"; do
  if [ "$CHECK_MODE" -eq 1 ]; then
    if ! check_in "$target"; then
      CHECK_FAILED=1
    fi
  else
    install_to "$target"
  fi
done

if [ "$CHECK_MODE" -eq 1 ] && [ "$CHECK_FAILED" -ne 0 ]; then
  exit 1
fi
