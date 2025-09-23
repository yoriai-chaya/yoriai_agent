import datetime
import json
import subprocess
import sys
from pathlib import Path


def run_playwright_tests():
    print("run_playwright_tests() called")
    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / "output"
    config_file = output_dir / "playwright.config.ts"
    test_file = "home.spec.ts"
    #test_file = "booking_step1.spec.ts"
    results_dir = output_dir / "results"
    results_dir.mkdir(exist_ok=True)
    print(f"project_root: {project_root}")
    print(f"results_dir: {results_dir}")
    print(f"config_file: {config_file}")
    print(f"test_file: {test_file}")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_report_file = results_dir / f"playwright_report_{timestamp}.json"
    meta_file = results_dir / f"playwright_meta_{timestamp}.json"
    # summary_file = results_dir / f"playwright_summary_{timestamp}.md"

    command = [
        "npx",
        "playwright",
        "test",
        test_file,
    ]

    # start_time = datetime.datetime.now()
    try:
        result = subprocess.run(
            command, cwd=output_dir, capture_output=True, text=True, check=False
        )
        end_time = datetime.datetime.now()
        print(f"result: {result}")
        print("----------")
        print(f"result.stdout: {result.stdout}")
        print("----------")
        print(f"result.stderr: {result.stderr}")
    except Exception as e:
        meta_file.write_text(
            json.dumps(
                {
                    "timestamp": timestamp,
                    "command": " ".join(command),
                    "cwd": str(output_dir),
                    "error": str(e),
                    "success": False,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        print(f"[ERROR] Failed to run playwright: {e}")


if __name__ == "__main__":
    run_playwright_tests()
