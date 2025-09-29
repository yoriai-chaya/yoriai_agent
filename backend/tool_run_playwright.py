import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

from config import get_settings

PLAYWRIGHT_CONFIG_TS = "playwright.config.ts"


def run_playwright_tests(test_file: str, output_dir: Path, results: Path):
    print("run_playwright_tests() called")
    project_root = Path(__file__).resolve().parent
    config_file = output_dir / PLAYWRIGHT_CONFIG_TS
    results_dir = output_dir / results
    results_dir.mkdir(exist_ok=True)
    print(f"project_root: {project_root}")
    print(f"results_dir: {results_dir}")
    print(f"config_file: {config_file}")
    print(f"test_file: {test_file}")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    meta_file = results_dir / f"playwright_meta_{timestamp}.json"

    command = [
        "npx",
        "playwright",
        "test",
        test_file,
    ]

    try:
        result = subprocess.run(
            command, cwd=output_dir, capture_output=True, text=True, check=False
        )
        print(f"result.stdout: {result.stdout}")
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
    parser = argparse.ArgumentParser(description="Run Playwright Tool")
    parser.add_argument("-f", "--file", required=True, help="Run Playwright Tool")
    args = parser.parse_args()
    if not args.file:
        parser.print_usage()
        sys.exit(1)

    settings = get_settings()
    output_dir = settings.output_dir
    results = settings.test_results_dir
    print(f"file: {args.file}, output_dir: {output_dir}, results: {results}")
    run_playwright_tests(args.file, output_dir, results)
