"""STAGE 1 of 3: build the visual spec.

Runs the real pytest suite, offline evaluations, and a live (real Gemini API) vertical-slice
agent run, then renders all 7 segments' visuals into slides/rendered/slide_1.png ...
slide_7.png - segments 1/2/3/7 from hand-authored bullets (generate_video.SLIDES_DATA),
segments 4/5/6 from the real command output captured above ("Live Demo" evidence cards).

This is the slow, API-hitting stage. Run it when the narrative text changes or the agent
code changes and you need fresh "Live Demo" evidence. Review slides/rendered/ afterward -
assemble_video.py just reads whatever is currently there, so nothing gets baked into the
final video until you're happy with these images.
"""

import os
import sys
import re
import time
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import generate_video
from common import (
    SLIDES_DIR, PROJECT_BUILD_DIR, OUTPUTS_DIR, CARDS_DIR, VERIFICATION_RESULTS_PATH,
    run_command, redact_workspace_paths, ensure_persistent_dirs,
)

def draw_static_slides():
    print("Drawing standard conceptual slide images...")
    for slide in generate_video.SLIDES_DATA:
        slide_path = os.path.join(SLIDES_DIR, f"slide_{slide['segment_number']}.png")
        generate_video.draw_slide(slide["title"], slide["bullets"], slide_path, slide_number=slide["segment_number"])

def run_verification_commands():
    results = {}

    # 1. pytest run
    print("\nRunning pytest suite...")
    pytest_stdout, pytest_stderr, pytest_rc = run_command("uv run pytest")
    pytest_stdout = redact_workspace_paths(pytest_stdout)
    pytest_stderr = redact_workspace_paths(pytest_stderr)
    pytest_log_path = os.path.join(OUTPUTS_DIR, "pytest_output.txt")
    with open(pytest_log_path, "w", encoding="utf-8") as f:
        f.write(pytest_stdout + "\n" + pytest_stderr)
    print(f"Pytest output saved to: {pytest_log_path}")
    results["pytest_passed"] = (pytest_rc == 0)

    # Headline-first card: the summary line (e.g. "59 passed, 6 warnings in 0.75s"), not the
    # full verbose run - nobody can read a scrolling pytest log while narration plays. Not a
    # segment visual (no segment narrates raw pytest output) - stays in CARDS_DIR as bonus
    # proof, not part of the reviewable 7-slide deck.
    summary_match = re.search(r"={3,}\s*(.+?)\s*={3,}\s*$", pytest_stdout.strip())
    pytest_headline = summary_match.group(1) if summary_match else ("PASSED" if results["pytest_passed"] else "FAILED")
    generate_video.draw_stat_card(
        "Pytest Automated Verification Suite",
        pytest_headline,
        ["uv run pytest", f"Exit code: {pytest_rc}"],
        os.path.join(CARDS_DIR, "pytest_card.png"),
        border_color=(16, 185, 129) # green
    )
    results["pytest_headline"] = pytest_headline

    # 2. Offline evaluations run -> segment 6 ("Rigorous Safety & Verification")
    print("\nRunning offline evaluations...")
    eval_stdout, eval_stderr, eval_rc = run_command("FORCE_OFFLINE=1 uv run python3 -m tests.eval.run_eval")
    eval_stdout = redact_workspace_paths(eval_stdout)
    eval_stderr = redact_workspace_paths(eval_stderr)
    eval_log_path = os.path.join(OUTPUTS_DIR, "eval_output.txt")
    with open(eval_log_path, "w", encoding="utf-8") as f:
        f.write(eval_stdout + "\n" + eval_stderr)
    print(f"Eval scorecard output saved to: {eval_log_path}")
    results["eval_passed"] = (eval_rc == 0)

    # Headline-first card: total pass/fail count plus a compact per-case status grid (case ID
    # and PASS/FAIL only) - the raw scorecard lines are full sentences with report file paths
    # in them, which is both unreadable at a glance and (before redaction above) a path leak.
    eval_clean = re.sub(r'\x1b\[[0-9;]*m', '', eval_stdout)
    passed_match = re.search(r"Passed:\s*(\d+)/(\d+) cases", eval_clean)
    eval_headline = f"{passed_match.group(1)}/{passed_match.group(2)} evaluation cases passed" if passed_match else ("PASSED" if results["eval_passed"] else "FAILED")

    case_status = {}
    case_notes = []
    for cid, status, note in re.findall(r"^(EVAL-\d+)\s*:\s*(PASS|FAIL)\s*\|\s*(.+)$", eval_clean, re.MULTILINE):
        case_status[cid] = status
        if not note.startswith("All expectations met"):
            case_notes.append(f"{cid}: {note.split(' Report generated')[0].strip()}")

    grid_lines = []
    ids = sorted(case_status.keys(), key=lambda c: int(c.split("-")[1]))
    for i in range(0, len(ids), 4):
        row = "   ".join(f"{cid} {case_status[cid]}" for cid in ids[i:i + 4])
        grid_lines.append(row)

    generate_video.draw_stat_card(
        "Offline Evaluation Scorecard Results",
        eval_headline,
        grid_lines + [""] + case_notes[:3],
        os.path.join(SLIDES_DIR, "slide_6.png"),
        border_color=(139, 92, 246) # purple
    )
    results["eval_headline"] = eval_headline

    # 3. Vertical slice run - this deliberately hits the real Gemini API (no --force-offline)
    # so the "live demo" segments show genuine agent output, not an offline stub. That makes
    # it subject to transient upstream errors (observed: a 503 "high demand" from Gemini) that
    # have nothing to do with this code being broken. Retry a couple of times before giving
    # up, since a hard failure here would otherwise silently produce blank slides downstream
    # while still reporting overall pipeline success.
    print("\nRunning vertical-slice orchestrator...")
    run_cmd = "uv run python3 -m portfolio_agent.run --input \"tests/golden/loss_ratio_spike.csv\" --latest-month \"2026-06\""
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        run_stdout, run_stderr, run_rc = run_command(run_cmd)
        if run_rc == 0:
            break
        print(f"Warning: vertical-slice run failed on attempt {attempt}/{max_attempts} (likely a transient upstream API error) - {run_stderr.strip().splitlines()[-1] if run_stderr.strip() else 'no stderr'}")
        if attempt < max_attempts:
            time.sleep(5)
    run_stdout = redact_workspace_paths(run_stdout)
    run_stderr = redact_workspace_paths(run_stderr)
    run_log_path = os.path.join(OUTPUTS_DIR, "run_output.txt")
    with open(run_log_path, "w", encoding="utf-8") as f:
        f.write(run_stdout + "\n" + run_stderr)
    print(f"Vertical slice run output saved to: {run_log_path}")
    results["run_passed"] = (run_rc == 0)
    if not results["run_passed"]:
        print(f"\n{'!' * 60}\nERROR: vertical-slice run did not succeed after {max_attempts} attempts. Slides 4/5 ('Live Demo') will be blank placeholders, not real pipeline output. See {run_log_path} for the failure.\n{'!' * 60}\n")

    # Segment 4 ("Live Demo: Pipeline Execution")
    run_lines = run_stdout.splitlines()
    run_card_lines = []
    summary_block_started = False
    for line in run_lines:
        if "Run complete." in line or "===" in line:
            summary_block_started = True
        if summary_block_started or any(term in line for term in ["Starting Portfolio", "Loading data", "Validating", "Calculating", "Running anomaly", "Calling Gemini"]):
            run_card_lines.append(line)

    generate_video.draw_log_card(
        "Live Demo: Underwriting Review Pipeline",
        run_card_lines,
        os.path.join(SLIDES_DIR, "slide_4.png"),
        border_color=(245, 158, 11) # amber
    )

    # Parse report file and trace paths
    report_match = re.search(r"Report:\s*(outputs/reports/portfolio_review_\S+\.md)", run_stdout)
    trace_match = re.search(r"Trace:\s*(outputs/traces/run_trace_\S+\.json)", run_stdout)

    # Segment 5 ("Live Demo: Actuarial Memo Output")
    if report_match:
        actual_path = os.path.join(PROJECT_BUILD_DIR, report_match.group(1).strip())
        if not os.path.exists(actual_path):
            normalized_rel = report_match.group(1).strip().replace("/", os.sep)
            actual_path = os.path.join(PROJECT_BUILD_DIR, normalized_rel)

        print(f"Reading generated report: {actual_path}")
        try:
            with open(actual_path, "r", encoding="utf-8") as f:
                report_content = redact_workspace_paths(f.read())
            report_lines = report_content.splitlines()
            generate_video.draw_log_card(
                "Compiled Actuarial Memo Excerpt",
                report_lines[:25],
                os.path.join(SLIDES_DIR, "slide_5.png"),
                border_color=(16, 185, 129)
            )
            results["report_path"] = actual_path
        except Exception as e:
            print(f"Failed to read report: {e}")
            generate_video.draw_log_card(
                "Compiled Actuarial Memo Excerpt",
                ["[Error loading report file: " + str(e) + "]"],
                os.path.join(SLIDES_DIR, "slide_5.png")
            )
    else:
        print("Warning: Could not parse report path from run output.")
        generate_video.draw_log_card(
            "Compiled Actuarial Memo Excerpt",
            ["[Report generation output not found in log]"],
            os.path.join(SLIDES_DIR, "slide_5.png")
        )

    # Trace JSON - not a segment visual (no segment narrates raw trace JSON), stays in
    # CARDS_DIR as bonus proof, not part of the reviewable 7-slide deck.
    if trace_match:
        trace_path = os.path.join(PROJECT_BUILD_DIR, trace_match.group(1).strip())
        print(f"Reading generated trace JSON: {trace_path}")
        try:
            with open(trace_path, "r", encoding="utf-8") as f:
                trace_content = redact_workspace_paths(f.read())
            trace_lines = trace_content.splitlines()
            generate_video.draw_log_card(
                "Structured Observability Trace JSON",
                trace_lines[:25],
                os.path.join(CARDS_DIR, "trace_card.png"),
                border_color=(59, 130, 246)
            )
            results["trace_path"] = trace_path
        except Exception as e:
            print(f"Failed to read trace file: {e}")
            generate_video.draw_log_card(
                "Structured Observability Trace JSON",
                ["[Error loading trace file: " + str(e) + "]"],
                os.path.join(CARDS_DIR, "trace_card.png")
            )
    else:
        print("Warning: Could not parse trace path from run output.")
        generate_video.draw_log_card(
            "Structured Observability Trace JSON",
            ["[Trace JSON output not found in log]"],
            os.path.join(CARDS_DIR, "trace_card.png")
        )

    return results

def main():
    """Returns True if pytest/eval/the live-demo run all passed, False otherwise. Deliberately
    does not sys.exit() itself - generate_all.py's thin wrapper calls this directly and must
    still proceed to assemble_video.main() even when verification failed (matching the
    original single-script behavior: always assemble, report pass/fail status in the report).
    Only the __main__ block below turns a failure into a nonzero process exit code, for
    standalone runs of this script.
    """
    ensure_persistent_dirs()
    draw_static_slides()
    results = run_verification_commands()

    with open(VERIFICATION_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "pytest_passed": results.get("pytest_passed", False),
            "eval_passed": results.get("eval_passed", False),
            "run_passed": results.get("run_passed", False),
            "pytest_headline": results.get("pytest_headline", ""),
            "eval_headline": results.get("eval_headline", ""),
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }, f, indent=2)
    print(f"\nWrote verification results to: {VERIFICATION_RESULTS_PATH}")

    all_passed = bool(results.get("pytest_passed") and results.get("eval_passed") and results.get("run_passed"))
    print("\nAll 7 slides/rendered/slide_N.png are up to date - review them before running assemble_video.py.")
    return all_passed

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
