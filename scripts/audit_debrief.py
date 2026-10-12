#!/usr/bin/env python3
"""
Validator and linter for Feynman Debrief explanations.
Audits text against Feynman principles:
1. Ban on lazy filler words and downplaying jargon ('basically', 'obviously', 'trivial', etc.)
2. Mandatory structural sections (Mechanism, Master Analogy, Ladder, Breaking Points, What was left out)
3. Sensory/physical mechanism check.
"""
import re
import sys
from typing import Dict, List, Any

BANNED_WORDS = [
    r"\bbasically\b",
    r"\bobviously\b",
    r"\bsimply\b",
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
        if len(bullets) < 3:
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

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: audit_debrief.py <file-to-audit | --stdin>")
        sys.exit(0)

    if sys.argv[1] == "--stdin":
        content = sys.stdin.read()
    else:
        try:
            with open(sys.argv[1], "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            sys.stderr.write(f"Error: File '{sys.argv[1]}' not found.\n")
            sys.exit(1)
        except Exception as e:
            sys.stderr.write(f"Error reading file '{sys.argv[1]}': {e}\n")
            sys.exit(1)

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
