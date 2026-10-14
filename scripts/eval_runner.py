#!/usr/bin/env python3
"""
Simplifeyn Feynman Index Evals & Benchmark Leaderboard Harness

Computes the objective Feynman Index (0-100 Scorecard) across 5 pedagogical pillars:
1. Mechanism Purity (25 pts)
2. Honest Limits & Metaphor (25 pts)
3. Audience Calibration (20 pts)
4. Empirical Verifiability (15 pts)
5. Brevity & Density (15 pts)
"""

import argparse
import json
import os
import re
import sys

# Ensure scripts directory is in sys.path
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import audit_debrief


def score_debrief(text: str) -> dict:
    """Evaluates an explanation text and computes the Feynman Index (0-100)."""
    audit_res = audit_debrief.audit_text(text)
    missing = audit_res["missing_sections"]
    banned = audit_res["banned_words_found"]
    prose_words = audit_res["prose_word_count"]
    total_words = audit_res["total_word_count"]

    # 1. Mechanism Purity (max 25 pts)
    purity_pts = 0
    if "In One Sentence" not in missing:
        purity_pts += 15
        sentence_errors = [e for e in audit_res["errors"] if "'In One Sentence'" in e]
        if not sentence_errors:
            purity_pts += 5
        if not banned:
            purity_pts += 5
        else:
            # Penalty for banned buzzwords
            penalty = len(banned) * 5
            purity_pts = max(0, purity_pts - penalty)

    # 2. Honest Limits & Metaphor (max 25 pts)
    limits_pts = 0
    if "The Picture" not in missing:
        limits_pts += 10
        diagram_errors = [e for e in audit_res["errors"] if "Missing ASCII mechanism flow diagram" in e]
        if not diagram_errors:
            limits_pts += 5
    if "Where the Picture Breaks" not in missing:
        limits_pts += 10

    # 3. Audience Calibration (max 20 pts)
    audience_pts = 0
    if "The Ladder" not in missing:
        audience_pts += 10
        ladder_errors = [e for e in audit_res["errors"] if "The Ladder" in e]
        if not ladder_errors:
            audience_pts += 10

    # 4. Empirical Verifiability & Stress Limits (max 15 pts)
    empirical_pts = 0
    if "The Ice-Water Test" not in missing:
        empirical_pts += 8
    if "Where the Machine Snaps" not in missing:
        empirical_pts += 7

    # 5. Brevity & Density (max 15 pts)
    brevity_pts = 0
    if "What Was Left Out" not in missing:
        brevity_pts += 5

    # Word count scoring curve
    if 80 <= prose_words <= 160:
        brevity_pts += 10
    elif 161 <= prose_words <= 170:
        brevity_pts += 7
    elif 50 <= prose_words < 80:
        brevity_pts += 7
    elif 171 <= prose_words <= 200:
        brevity_pts += 3
    else:
        brevity_pts += 0

    total_score = purity_pts + limits_pts + audience_pts + empirical_pts + brevity_pts
    total_score = max(0, min(100, total_score))

    if total_score >= 90:
        grade = "A+"
    elif total_score >= 80:
        grade = "A"
    elif total_score >= 70:
        grade = "B"
    elif total_score >= 60:
        grade = "C"
    else:
        grade = "F"

    passed = audit_res["passed"] and total_score >= 80

    return {
        "score": total_score,
        "grade": grade,
        "passed": passed,
        "breakdown": {
            "mechanism_purity": purity_pts,
            "honest_limits": limits_pts,
            "audience_calibration": audience_pts,
            "empirical_verification": empirical_pts,
            "brevity_density": brevity_pts,
        },
        "prose_word_count": prose_words,
        "total_word_count": total_words,
        "banned_words_found": banned,
        "missing_sections": missing,
        "errors": audit_res["errors"],
    }


def format_scorecard_ascii(res: dict) -> str:
    """Formats an evaluation result as an ASCII scorecard."""
    b = res["breakdown"]
    status_label = "PASSED" if res["passed"] else "FAILED"

    def bar(val, max_val):
        pct = val / max_val if max_val > 0 else 0
        filled = int(round(pct * 10))
        return "[" + "|" * filled + "." * (10 - filled) + "]"

    lines = [
        "+---------------------------------------------------------+",
        "|                    FEYNMAN SCORECARD                    |",
        "+---------------------------------------------------------+",
        f"| Final Score: {res['score']:>3} / 100 [Grade: {res['grade']:<2}]  Status: {status_label:<7} |",
        "+---------------------------------------------------------+",
        "| Category Breakdown:                                     |",
        f"|   1. Mechanism Purity:       {b['mechanism_purity']:>2} / 25 {bar(b['mechanism_purity'], 25)}           |",
        f"|   2. Honest Limits:          {b['honest_limits']:>2} / 25 {bar(b['honest_limits'], 25)}           |",
        f"|   3. Audience Calibration:   {b['audience_calibration']:>2} / 20 {bar(b['audience_calibration'], 20)}           |",
        f"|   4. Empirical Verification: {b['empirical_verification']:>2} / 15 {bar(b['empirical_verification'], 15)}           |",
        f"|   5. Brevity & Density:      {b['brevity_density']:>2} / 15 {bar(b['brevity_density'], 15)}           |",
        "+---------------------------------------------------------+",
        f"| Metrics: {res['prose_word_count']:>3} prose words | {res['total_word_count']:>3} total words | {len(res['banned_words_found']):>2} buzzwords |",
        "+---------------------------------------------------------+",
    ]
    if res["errors"]:
        lines.append("| Deficiencies:")
        for err in res["errors"]:
            lines.append(f"|   - {err}")
        lines.append("+---------------------------------------------------------+")
    return "\n".join(lines)


def format_score_markdown(res: dict) -> str:
    """Formats an evaluation result as a GitHub Flavored Markdown table."""
    b = res["breakdown"]
    status_emoji = "[PASS]" if res["passed"] else "[FAIL]"
    lines = [
        f"### Feynman Scorecard: {res['score']}/100 (Grade {res['grade']}) {status_emoji}",
        "",
        "| Category | Score | Max | Status |",
        "| :--- | :---: | :---: | :---: |",
        f"| **1. Mechanism Purity** | {b['mechanism_purity']} | 25 | {'PASS' if b['mechanism_purity'] >= 20 else 'WARN'} |",
        f"| **2. Honest Limits** | {b['honest_limits']} | 25 | {'PASS' if b['honest_limits'] >= 20 else 'WARN'} |",
        f"| **3. Audience Calibration** | {b['audience_calibration']} | 20 | {'PASS' if b['audience_calibration'] >= 15 else 'WARN'} |",
        f"| **4. Empirical Verification** | {b['empirical_verification']} | 15 | {'PASS' if b['empirical_verification'] >= 12 else 'WARN'} |",
        f"| **5. Brevity & Density** | {b['brevity_density']} | 15 | {'PASS' if b['brevity_density'] >= 10 else 'WARN'} |",
        f"| **Total Feynman Index** | **{res['score']}** | **100** | **{res['grade']}** |",
        "",
        f"*Prose Words: {res['prose_word_count']} (< 170) | Banned Buzzwords: {len(res['banned_words_found'])}*",
    ]
    return "\n".join(lines)


def format_score_json(res: dict) -> str:
    """Formats an evaluation result as structured JSON."""
    return json.dumps(res, indent=2)


def run_benchmark(transcripts_dir: str) -> dict:
    """Evaluates all transcript fixtures in the specified directory and computes leaderboard statistics."""
    if not os.path.isdir(transcripts_dir):
        raise ValueError(f"Directory not found: {transcripts_dir}")

    fixtures = [
        f for f in os.listdir(transcripts_dir)
        if f.endswith(".md") and f != "README.md"
    ]
    fixtures.sort()

    model_scores = {}
    total_evals = 0
    all_scores = []

    level_markers = [
        "## 3. Simplifeyn Output: Level (Vibe Coder - Default)",
        "## 4. Simplifeyn Output: Level (Junior Dev with Workshop Lens)",
        "## 4. Simplifeyn Output: Level (Junior Dev with Gaming Lens)",
        "## 4. Simplifeyn Output: Level (Junior Dev with Warehouse Lens)",
        "## 5. Simplifeyn Output: Level (Senior Dev with Transit Lens)",
        "## 5. Simplifeyn Output: Level (Senior Dev with Workshop Lens)",
        "## 6. Simplifeyn Output: Full 3-Rung Ladder (--full)",
    ]

    for fname in fixtures:
        fpath = os.path.join(transcripts_dir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse model name from header
        model_match = re.search(r"-\s+\*\*Model:\*\*\s+([^\n]+)", content)
        model_name = model_match.group(1).strip() if model_match else "Unknown Model"

        # Check for gated skip fixtures
        if "[Simplifeyn debrief skipped:" in content:
            # Gated skip fixtures test complexity gating rather than 6-section generation
            continue

        if model_name not in model_scores:
            model_scores[model_name] = {
                "scores": [],
                "prose_words": [],
                "passed_count": 0,
            }

        for marker in level_markers:
            if marker in content:
                section = content.split(marker, 1)[1].split("\n---\n")[0].strip()
                if "> **Prompt:**" in section:
                    section = section.split("\n\n", 1)[1].strip()
                if "\n### Audit Verification" in section:
                    section = section.split("\n### Audit Verification")[0].strip()

                eval_res = score_debrief(section)
                model_scores[model_name]["scores"].append(eval_res["score"])
                model_scores[model_name]["prose_words"].append(eval_res["prose_word_count"])
                if eval_res["passed"]:
                    model_scores[model_name]["passed_count"] += 1
                all_scores.append(eval_res["score"])
                total_evals += 1

    leaderboard_models = []
    for mname, data in model_scores.items():
        n = len(data["scores"])
        if n == 0:
            continue
        avg_score = round(sum(data["scores"]) / n, 1)
        avg_words = round(sum(data["prose_words"]) / n, 1)
        pass_rate = round((data["passed_count"] / n) * 100, 1)
        leaderboard_models.append({
            "model": mname,
            "evals_count": n,
            "avg_score": avg_score,
            "pass_rate": pass_rate,
            "avg_prose_words": avg_words,
            "min_score": min(data["scores"]),
            "max_score": max(data["scores"]),
        })

    leaderboard_models.sort(key=lambda x: x["avg_score"], reverse=True)

    overall_avg = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0.0

    return {
        "transcripts_directory": transcripts_dir,
        "total_fixtures": len(fixtures),
        "total_evals": total_evals,
        "overall_avg_score": overall_avg,
        "models": leaderboard_models,
    }


def format_leaderboard_ascii(leaderboard: dict) -> str:
    """Formats benchmark results as an ASCII leaderboard table."""
    lines = [
        "+-------------------------------------------------------------------------+",
        "|                       FEYNMAN INDEX LEADERBOARD                         |",
        "+------------------------------------+-----------+-----------+------------+",
        "| Model                              | Avg Score | Pass Rate | Avg Words  |",
        "+------------------------------------+-----------+-----------+------------+",
    ]
    for m in leaderboard["models"]:
        mname = m["model"][:34]
        lines.append(
            f"| {mname:<34} | {m['avg_score']:>5.1f}/100 | {m['pass_rate']:>8.1f}% | {m['avg_prose_words']:>7.1f} w  |"
        )
    lines.append("+------------------------------------+-----------+-----------+------------+")
    lines.append(
        f"| Overall Average: {leaderboard['overall_avg_score']:>5.1f}/100 across {leaderboard['total_evals']} evaluations            |"
    )
    lines.append("+-------------------------------------------------------------------------+")
    return "\n".join(lines)


def format_leaderboard_markdown(leaderboard: dict) -> str:
    """Formats benchmark results as a GitHub Flavored Markdown table."""
    lines = [
        "## Feynman Index Model Benchmark Leaderboard",
        "",
        f"*Evaluated across {leaderboard['total_evals']} scenario debriefs (Overall Average: **{leaderboard['overall_avg_score']}/100**)*",
        "",
        "| Rank | Model | Feynman Index (Avg) | Pass Rate | Avg Prose Words | Min / Max |",
        "| :---: | :--- | :---: | :---: | :---: | :---: |",
    ]
    for rank, m in enumerate(leaderboard["models"], 1):
        lines.append(
            f"| {rank} | **{m['model']}** | **{m['avg_score']} / 100** | {m['pass_rate']}% | {m['avg_prose_words']} w | {m['min_score']} / {m['max_score']} |"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Simplifeyn Feynman Index Evals & Benchmark Leaderboard Harness")
    parser.add_argument("file", nargs="?", help="Markdown file to score (or omit for benchmark mode)")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark across transcript fixtures")
    parser.add_argument("--transcripts-dir", default=os.path.join(os.path.dirname(SCRIPTS_DIR), "assets", "transcripts"), help="Transcripts directory for benchmark")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--markdown", action="store_true", help="Output results in Markdown format")

    args = parser.parse_args()

    if args.benchmark or not args.file:
        lb = run_benchmark(args.transcripts_dir)
        if args.json:
            print(json.dumps(lb, indent=2))
        elif args.markdown:
            print(format_leaderboard_markdown(lb))
        else:
            print(format_leaderboard_ascii(lb))
        sys.exit(0)

    # Single file evaluation
    if args.file == "-":
        content = sys.stdin.read()
    else:
        if not os.path.isfile(args.file):
            sys.stderr.write(f"File not found: {args.file}\n")
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()

    res = score_debrief(content)
    if args.json:
        print(format_score_json(res))
    elif args.markdown:
        print(format_score_markdown(res))
    else:
        print(format_scorecard_ascii(res))

    sys.exit(0 if res["passed"] else 1)


if __name__ == "__main__":
    main()
