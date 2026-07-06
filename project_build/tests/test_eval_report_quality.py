from pathlib import Path

import yaml


def test_generated_reports_quality():
    eval_dir = Path(__file__).parent / "eval"
    if not eval_dir.exists():
        # fallback path
        eval_dir = Path(__file__).parent.parent / "tests" / "eval"

    with open(eval_dir / "eval_cases.yaml", "r") as f:
        config = yaml.safe_load(f)

    reports_dir = eval_dir / "eval_results" / "reports"

    for case in config["cases"]:
        case_id = case["id"]
        expected = case["expected"]
        if expected.get("validation_status") == "pass":
            report_file = reports_dir / f"portfolio_review_{case_id}.md"
            assert report_file.exists(), f"Missing expected report: {report_file}"

            with open(report_file, "r") as f:
                content = f.read()

            if case_id == "EVAL-002":
                assert "85.0%" in content or "85%" in content
                assert "50.0%" in content or "50%" in content
                assert "NY" in content
            elif case_id == "EVAL-003":
                assert "60,000" in content or "60000" in content
                assert "100,000" in content or "100000" in content
                assert "NY" in content
            elif case_id == "EVAL-004":
                assert "0.75" in content

            # Ensure no developer placeholders exist in compiled report
            assert "TODO" not in content
            assert "[Insert" not in content
