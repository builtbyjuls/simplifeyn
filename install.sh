#!/usr/bin/env bash
# Universal installer for feynman-debrief across Claude Code, Antigravity, OpenAI Codex, and Cursor
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="feynman-debrief"

usage() {
  cat << 'EOF'
Usage: ./install.sh [OPTIONS]

Install feynman-debrief skill to one or more AI coding assistants.

Options:
  --claude         Install to ~/.claude/skills/ (Claude Code)
  --antigravity    Install to ~/.gemini/skills/ (Antigravity CLI)
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
      TARGETS+=("$HOME/.gemini/skills")
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
      [ -d "$HOME/.gemini" ] && TARGETS+=("$HOME/.gemini/skills")
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
  if [ -d "$HOME/.gemini" ]; then TARGETS+=("$HOME/.gemini/skills"); fi
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
    mkdir -p "$dest/references"
    cp -r "$SCRIPT_DIR/references/"* "$dest/references/"
  fi
  if [ -d "$SCRIPT_DIR/assets" ]; then
    mkdir -p "$dest/assets"
    cp -r "$SCRIPT_DIR/assets/"* "$dest/assets/"
  fi
  if [ -d "$SCRIPT_DIR/scripts" ]; then
    mkdir -p "$dest/scripts"
    cp -r "$SCRIPT_DIR/scripts/"* "$dest/scripts/"
  fi
  echo "✓ Installed $SKILL_NAME to $dest"
}

check_in() {
  local dest_base="$1"
  local dest="$dest_base/$SKILL_NAME"
  if [ ! -d "$dest" ]; then
    echo "✗ Not installed in $dest"
    return 1
  fi
  if cmp -s "$SCRIPT_DIR/SKILL.md" "$dest/SKILL.md"; then
    echo "✓ $dest is up to date"
    return 0
  else
    echo "! $dest differs from source (run install.sh to update)"
    return 1
  fi
}

for target in "${TARGETS[@]}"; do
  if [ "$CHECK_MODE" -eq 1 ]; then
    check_in "$target" || true
  else
    install_to "$target"
  fi
done
