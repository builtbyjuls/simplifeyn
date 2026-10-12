#!/usr/bin/env bash
# Universal installer for simplifeyn across Claude Code, Antigravity, OpenAI Codex, and Cursor
set -euo pipefail
SCRIPT_DIR=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

CLEANUP_TMP=0
TMP_CLONE_DIR=""
if [ -z "$SCRIPT_DIR" ] || [ ! -f "$SCRIPT_DIR/SKILL.md" ]; then
  TMP_CLONE_DIR="$(mktemp -d)"
  CLEANUP_TMP=1
  cleanup() {
    if [ "$CLEANUP_TMP" -eq 1 ] && [ -n "$TMP_CLONE_DIR" ] && [ -d "$TMP_CLONE_DIR" ]; then
      rm -rf "$TMP_CLONE_DIR"
    fi
  }
  trap cleanup EXIT INT TERM
  if command -v git >/dev/null 2>&1; then
    git clone --depth 1 https://github.com/builtbyjuls/simplifeyn.git "$TMP_CLONE_DIR" >/dev/null 2>&1
    SCRIPT_DIR="$TMP_CLONE_DIR"
  elif command -v curl >/dev/null 2>&1 && command -v tar >/dev/null 2>&1; then
    curl -fsSL https://github.com/builtbyjuls/simplifeyn/archive/refs/heads/main.tar.gz | tar -xz -C "$TMP_CLONE_DIR" --strip-components=1
    SCRIPT_DIR="$TMP_CLONE_DIR"
  else
    echo "Error: git or (curl + tar) is required to download simplifeyn." >&2
    exit 1
  fi
fi

SKILL_NAME="simplifeyn"

usage() {
  cat << 'EOF'
Usage: ./install.sh [OPTIONS]

Install simplifeyn skill to one or more AI coding assistants.

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
      local src_file
      for src_file in "$SCRIPT_DIR/$subdir"/*; do
        if [ -f "$src_file" ]; then
          local rel_name
          rel_name="$(basename "$src_file")"
          local target_file="$dest/$subdir/$rel_name"
          if [ ! -f "$target_file" ] || ! cmp -s "$src_file" "$target_file"; then
            echo "[FAIL] $dest/$subdir/$rel_name is missing or modified"
            return 1
          fi
        fi
      done
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
