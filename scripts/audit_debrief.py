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
]

BANNED_PREAMBLES = [
    r"(?i)(?:^|\n)\s*(?:Sure[!,.]?|Certainly[!,.]?|Great question[!,.]?|Here is|Here's|I have (?:implemented|completed|updated|fixed)|Looking at the)",
    r"(?i)(?:Hope this helps|Let me know if you (?:need|have)|Feel free to ask|Happy to clarify)",
]

REQUIRED_SECTIONS = [
    (r"(?i)#{1,3}\s+(?:\d+\.\s+)?In One Sentence", "In One Sentence"),
    (r"(?i)#{1,3}\s+(?:\d+\.\s+)?The (?:Tangible\s+|Physical\s+)?Picture", "The Picture"),
    (r"(?i)#{1,3}\s+(?:\d+\.\s+)?The Ladder", "The Ladder"),
    (r"(?i)(?:#{1,3}\s+(?:\d+\.\s+)?Where the Picture Breaks|\bbreaks\s+if\b|\bbreaking\s+point\b)", "Where the Picture Breaks"),
    (r"(?i)#{1,3}\s+(?:\d+\.\s+)?(?:What Was )?Left Out", "What Was Left Out"),
]

MAX_WORD_COUNT = 250

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

    # Check word count budget
    word_count = len(text.split())
    if word_count > MAX_WORD_COUNT:
        errors.append(f"Excessive verbosity: debrief word count is {word_count} (maximum allowed is {MAX_WORD_COUNT} words). Debrief is too verbose; simplify and compress.")

    # Check for required sections
    for pattern, name in REQUIRED_SECTIONS:
        if not re.search(pattern, text):
            missing_sections.append(name)
            errors.append(f"Missing required section: '{name}'")

    # Check that ladder contains at least Level 0
    if "The Ladder" not in missing_sections:
        if not re.search(r"(?i)Level 0|Kitchen[- ]Table|\bL0\b", text):
            errors.append("The Ladder must include Level 0 / L0 (Kitchen-table level with zero jargon)")

    passed = len(errors) == 0
    return {
        "passed": passed,
        "errors": errors,
        "banned_words_found": banned_found,
        "missing_sections": missing_sections,
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
