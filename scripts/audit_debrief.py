#!/usr/bin/env python3
"""
Validator and linter for Feynman Debrief explanations.
Audits text against Feynman principles:
1. Ban on lazy filler words and downplaying jargon ('basically', 'obviously', 'trivial', etc.)
2. Mandatory structural sections (Mechanism, Master Analogy, Ladder, Breaking Points, What was left out)
3. Sensory/physical mechanism check.
"""
import os
import re
import sys
from typing import Dict, List, Any

BANNED_WORDS = [
    r"\bbasically\b",
    r"\bobviously\b",
    r"\bsimply\b",
    r"\bjust\b",
    r"\btrivial\b",
    r"\babstracted away\b",
    r"\bunder the hood\b",  # often used as hand-waving instead of actually explaining
    r"\bself-explanatory\b",
    r"\boptimized\b",
    r"\boptimizing\b",
    r"\bstreamline\b",
    r"\bstreamlined\b",
    r"\bstreamlining\b",
    r"\bseamless\b",
    r"\bseamlessly\b",
]

# Load centralized banned words file if present
_banned_ref = os.path.join(os.path.dirname(__file__), "..", "references", "banned-words.txt")
if os.path.isfile(_banned_ref):
    try:
        with open(_banned_ref, "r", encoding="utf-8") as _f:
            _words = [rf"\b{line.strip()}\b" for line in _f if line.strip() and not line.startswith("#")]
            if _words:
                BANNED_WORDS = _words
    except Exception:
        pass

BANNED_PREAMBLES = [
    r"(?i)(?:^|\n)\s*(?:Sure[!,.]?|Certainly[!,.]?|Great question[!,.]?|Here is|Here's|I have (?:implemented|completed|updated|fixed)|Looking at the)",
    r"(?i)(?:Hope this helps|Let me know if you (?:need|have)|Feel free to ask|Happy to clarify)",
]

REQUIRED_SECTIONS = [
    (r"(?i)#{1,3}\s+(?:\d+\.\s+)?In One Sentence", "In One Sentence"),
    (r"(?i)#{1,3}\s+(?:\d+\.\s+)?The (?:Tangible\s+|Physical\s+)?Picture", "The Picture"),
    (r"(?i)#{1,3}\s+(?:\d+\.\s+)?The Ladder", "The Ladder"),
    (r"(?i)(?:#{1,3}\s+(?:\d+\.\s+)?Where the Picture Breaks|\bWhere the (?:Picture|Analogy) Breaks\b|\bbreaks\s+if\b|\bbreaking\s+point\b)", "Where the Picture Breaks"),
    (r"(?i)#{1,3}\s+(?:\d+\.\s+)?(?:What Was )?Left Out", "What Was Left Out"),
]

MAX_PROSE_WORDS = 150
MAX_TOTAL_WORDS = 220

def audit_text(text: str) -> Dict[str, Any]:
    errors: List[str] = []
    banned_found: List[str] = []
    missing_sections: List[str] = []

    # Check for banned words
    for pattern in BANNED_WORDS:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        if matches:
            clean_word = pattern.replace(r"\b", "")
            banned_found.extend(matches)
            errors.append(f"Forbidden buzzword/hand-waving detected: '{clean_word}'")

    # Check for banned conversational preambles and postambles
    for pattern in BANNED_PREAMBLES:
        if re.search(pattern, text):
            errors.append("Conversational preamble or pleasantry detected. Start directly at the first heading and end when the debrief is complete.")

    # Check word count budgets (prose words vs total words)
    prose = re.sub(r"```[\s\S]*?```", "", text)
    prose = re.sub(r"^#{1,6}\s+.*$", "", prose, flags=re.MULTILINE)
    prose = re.sub(r"^---+$", "", prose, flags=re.MULTILINE)
    prose_words = len(prose.split())
    total_words = len(text.split())

    if prose_words > MAX_PROSE_WORDS:
        errors.append(f"Excessive verbosity (word count limit exceeded): debrief has {prose_words} prose words (budget is < {MAX_PROSE_WORDS} words). Simplify and compress prose.")
    if total_words > MAX_TOTAL_WORDS:
        errors.append(f"Excessive total length (word count limit exceeded): debrief has {total_words} total words (hard ceiling is {MAX_TOTAL_WORDS} words).")

    # Check for required sections
    for pattern, name in REQUIRED_SECTIONS:
        if not re.search(pattern, text):
            missing_sections.append(name)
            errors.append(f"Missing required section: '{name}'")

    # Check that "In One Sentence" is truly a single sentence
    if "In One Sentence" not in missing_sections:
        sentence_sec_match = re.search(r"(?i)#{1,3}\s+(?:\d+\.\s+)?In One Sentence\s*\n+([\s\S]*?)(?=\n+#{1,3}|\Z)", text)
        if sentence_sec_match:
            sec_text = sentence_sec_match.group(1).strip()
            clean_sec = re.sub(r"\[.*?\]\(.*?\)", "", sec_text)
            clean_sec = re.sub(r"[*_`]", "", clean_sec)
            clean_sec = re.sub(r"\b(?:e\.g\.|i\.e\.|vs\.|etc\.)", "", clean_sec)
            sentences = [s.strip() for s in re.split(r"[.!?]+(?:\s+|\Z)", clean_sec) if s.strip()]
            if len(sentences) > 1:
                errors.append(f"'In One Sentence' section must be exactly one sentence (found {len(sentences)}).")

    # Check that ASCII mechanism diagram is present in Section 2
    if "The Picture" not in missing_sections:
        has_diagram = bool(re.search(r"```(?:text)?\s*\n[\s\S]*?\[[\s\S]*?\][\s\S]*?--+>[\s\S]*?```", text))
        if not has_diagram:
            errors.append("Missing ASCII mechanism flow diagram in 'The Tangible Picture' (must include fenced block with [ Node ] ---> [ Node ])")

    # Check that Ladder contains all 3 levels (Level 0, Level 1, Level 2) and 3 rungs
    if "The Ladder" not in missing_sections:
        ladder_match = re.search(r"(?i)#{1,3}\s+(?:\d+\.\s+)?The Ladder\s*\n+([\s\S]*?)(?=\n+#{1,3}|\Z)", text)
        ladder_text = ladder_match.group(1).strip() if ladder_match else text

        has_l0 = bool(re.search(r"(?i)Level 0|Kitchen[- ]Table|\bL0\b", ladder_text))
        has_l1 = bool(re.search(r"(?i)Level 1|Practitioner|\bL1\b", ladder_text))
        has_l2 = bool(re.search(r"(?i)Level 2|Maintainer|\bL2\b", ladder_text))

        if not has_l0:
            errors.append("The Ladder must include Level 0 (Kitchen-table level with zero jargon)")
        if not has_l1:
            errors.append("The Ladder must include Level 1 (Practitioner level with code mechanisms and trade-offs)")
        if not has_l2:
            errors.append("The Ladder must include Level 2 (Maintainer level with failure modes and scale ceilings)")

        bullets = [line for line in ladder_text.splitlines() if re.match(r"^\s*[-*]\s+", line)]
        if len(bullets) != 3:
            errors.append(f"The Ladder must have exactly 3 rungs (found {len(bullets)} bullets).")

    passed = len(errors) == 0
    return {
        "passed": passed,
        "errors": errors,
        "banned_words_found": banned_found,
        "missing_sections": missing_sections,
        "prose_word_count": prose_words,
        "total_word_count": total_words,
    }

DOCS_EXTS = {".md", ".markdown", ".txt", ".rst", ".adoc"}
LOCKFILES_AND_IGNORES = {
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "cargo.lock",
    "gemfile.lock", "composer.lock", "poetry.lock",
    ".gitignore", ".gitattributes", ".editorconfig",
    ".npmignore", ".dockerignore", "license", "notice", "authors",
}
CONFIG_OR_CI_EXTS = {".json", ".yml", ".yaml", ".toml", ".ini", ".env", ".conf"}

CONTROL_FLOW_INDICATORS = [
    r"\bdef\s+",
    r"\bclass\s+",
    r"\bfunction\b",
    r"\basync\s+",
    r"\bawait\b",
    r"\bif\b",
    r"\bfor\b",
    r"\bwhile\b",
    r"\btry\b",
    r"\bcatch\b",
    r"\bexcept\b",
    r"\bswitch\b",
    r"\bcase\b",
    r"\breturn\b",
    r"\bthrow\b",
    r"\braise\b",
]

SECURITY_AND_STATE_INDICATORS = [
    r"\b(true|false|True|False)\b",
    r"\bauth\b",
    r"\bssl\b",
    r"\btls\b",
    r"\btoken\b",
    r"\bsecret\b",
    r"\bpassword\b",
    r"\badmin\b",
    r"\bmutex\b",
    r"\block\b",
    r"\bcache\b",
    r"\bstate\b",
    r"\b[A-Z][A-Z0-9_]{2,}\s*=",
]

CONFIG_RISK_INDICATORS = [
    r"\b(true|false|True|False)\b",
    r"\bauth\b",
    r"\bssl\b",
    r"\btls\b",
    r"\btoken\b",
    r"\bsecret\b",
    r"\bpassword\b",
    r"\badmin\b",
    r"\btests?\b",
    r"\bscripts?\b",
    r"\brun\b",
    r"\bbuild\b",
    r"\bci\b",
    r"\bdeploy\b",
    r"\bexec\b",
    r"\bcmd\b",
    r"\bcommand\b",
    r"\bpreinstall\b",
    r"\bpostinstall\b",
    r"\bport\b",
    r"\bhost\b",
    r"\bendpoint\b",
    r"\burl\b",
    r"\benv\b",
    r"\bdependencies\b",
    r"\bdevdependencies\b",
    r"\b[A-Z][A-Z0-9_]{2,}\s*=",
]

def check_diff_complexity(diff_text: str, commit_msg: str = "") -> Dict[str, Any]:
    # 1. Commit message convention heuristic
    if commit_msg:
        cm_lower = commit_msg.strip().lower()
        if re.match(r"^(docs|chore|style|ci|build)(\([a-z0-9_-]+\))?:\s*", cm_lower):
            prefix = cm_lower.split(":")[0]
            return {
                "should_debrief": False,
                "action": "skip",
                "reason": f"Commit message type '{prefix}' indicates non-behavioral or maintenance change.",
            }
        if re.match(r"^(feat|perf)(\([a-z0-9_-]+\))?:\s*", cm_lower):
            prefix = cm_lower.split(":")[0]
            return {
                "should_debrief": True,
                "action": "debrief",
                "reason": f"Commit message type '{prefix}' indicates behavioral or performance change.",
            }

    # 2. Extract changed files from diff headers
    files_changed = set()
    for line in diff_text.splitlines():
        if line.startswith("diff --git a/") or line.startswith("--- a/") or line.startswith("+++ b/"):
            parts = line.split()
            if len(parts) >= 2:
                raw_path = parts[-1]
                if raw_path.startswith("b/") or raw_path.startswith("a/"):
                    path = raw_path[2:]
                else:
                    path = raw_path
                if path and path != "/dev/null":
                    files_changed.add(path)

    has_config_or_ci = False
    has_dedicated_ci_pipeline = False
    if files_changed:
        all_docs_or_locks = True
        for path in files_changed:
            base = os.path.basename(path).lower()
            name, ext = os.path.splitext(base)
            if ext in DOCS_EXTS or base in LOCKFILES_AND_IGNORES or base.endswith(".lock"):
                continue
            all_docs_or_locks = False
            if ext in CONFIG_OR_CI_EXTS:
                has_config_or_ci = True
            if ".github" in path or ".circleci" in path:
                has_dedicated_ci_pipeline = True

        if all_docs_or_locks:
            return {
                "should_debrief": False,
                "action": "skip",
                "reason": "Only documentation, lockfiles, or repository metadata were modified.",
            }

    # 3. Analyze modified lines
    added_or_removed = []
    has_non_comment_content = False
    for line in diff_text.splitlines():
        if (line.startswith("+") and not line.startswith("+++")) or (line.startswith("-") and not line.startswith("---")):
            content_line = line[1:].strip()
            if content_line:
                added_or_removed.append(content_line)
                stripped = re.sub(r"^\s*(?://|#|/\*|\*).*$", "", content_line).strip()
                if stripped:
                    has_non_comment_content = True

    if not has_non_comment_content:
        return {
            "should_debrief": False,
            "action": "skip",
            "reason": "Diff contains only comments or whitespace changes.",
        }

    if has_dedicated_ci_pipeline:
        return {
            "should_debrief": True,
            "action": "debrief",
            "reason": "CI pipeline modification.",
        }

    if has_config_or_ci:
        for line in added_or_removed:
            stripped = re.sub(r"^\s*(?://|#|/\*|\*).*$", "", line).strip()
            if not stripped:
                continue
            for indicator in CONFIG_RISK_INDICATORS:
                if re.search(indicator, stripped, flags=re.IGNORECASE if not indicator.startswith(r"\b[A-Z]") else 0):
                    return {
                        "should_debrief": True,
                        "action": "debrief",
                        "reason": "Configuration, runtime settings, or dependency script modification.",
                    }
        if len(added_or_removed) <= 4:
            return {
                "should_debrief": False,
                "action": "skip",
                "reason": "Configuration metadata change with zero runtime or script logic shifts.",
            }

    has_logic = False
    for line in added_or_removed:
        stripped = re.sub(r"^\s*(?://|#|/\*|\*).*$", "", line).strip()
        if not stripped:
            continue
        # Security, state, boolean, or constant indicators
        for indicator in SECURITY_AND_STATE_INDICATORS:
            if re.search(indicator, stripped, flags=re.IGNORECASE if not indicator.startswith(r"\b[A-Z]") else 0):
                has_logic = True
                break
        if has_logic:
            break
        # Strip string literals so words inside quotes (e.g. "wait for it") don't match control flow keywords
        line_code_only = re.sub(r'"(?:\\.|[^"\\])*"', '""', stripped)
        line_code_only = re.sub(r"'(?:\\.|[^'\\])*'", "''", line_code_only)
        for indicator in CONTROL_FLOW_INDICATORS:
            if re.search(indicator, line_code_only, flags=re.IGNORECASE):
                has_logic = True
                break
        if has_logic:
            break

    if len(added_or_removed) <= 4 and not has_logic:
        return {
            "should_debrief": False,
            "action": "skip",
            "reason": "Diff is small (< 5 lines) with no structural logic or control flow shifts.",
        }

    return {
        "should_debrief": True,
        "action": "debrief",
        "reason": "Diff introduces non-trivial logic, state changes, or behavioral modifications.",
    }

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: audit_debrief.py [--check-diff] [--commit-msg <msg>] <file-to-audit | --stdin>")
        sys.exit(0)

    check_diff_mode = False
    commit_msg = ""
    args = sys.argv[1:]
    if "--check-diff" in args:
        check_diff_mode = True
        args.remove("--check-diff")

    if "--commit-msg" in args:
        idx = args.index("--commit-msg")
        if idx + 1 < len(args):
            commit_msg = args[idx + 1]
            del args[idx:idx + 2]
        else:
            sys.stderr.write("Error: --commit-msg requires a message string.\n")
            sys.exit(1)

    if not args or args[0] == "--stdin":
        content = sys.stdin.read()
    else:
        try:
            with open(args[0], "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            sys.stderr.write(f"Error: File '{args[0]}' not found.\n")
            sys.exit(1)
        except Exception as e:
            sys.stderr.write(f"Error reading file '{args[0]}': {e}\n")
            sys.exit(1)

    if check_diff_mode:
        res = check_diff_complexity(content, commit_msg=commit_msg)
        if res["should_debrief"]:
            print(f"[DEBRIEF] {res['reason']}")
            sys.exit(0)
        else:
            print(f"[SKIP] {res['reason']}")
            sys.exit(0)

    result = audit_text(content)
    if result["passed"]:
        print("[PASS] Simplifeyn Debrief Audit PASSED: Clear, mechanistic, and free of lazy jargon.")
        sys.exit(0)
    else:
        print("[FAIL] Simplifeyn Debrief Audit FAILED:")
        for err in result["errors"]:
            print(f"  - {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()
