import argparse
import sys
from pathlib import Path

from base import FunctionResult, LoadPlaywrightReport
from edit_playwright_report import create_summary_report_file, load_playwright_report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Playwright Report Parser")
    parser.add_argument(
        "-f", "--file", required=True, help="Playwright report file (json-format)"
    )
    args = parser.parse_args()
    if not args.file:
        parser.print_usage()
        sys.exit(1)
    result: LoadPlaywrightReport = load_playwright_report(args.file)
    if result.result:
        if result.suites:
            input_path = Path(args.file)
            result_create: FunctionResult = create_summary_report_file(
                result.suites, input_path
            )
            if not result_create:
                print(f"Failed to write file: {result_create.detail}")
            else:
                print(f"Saved report: {input_path}")
