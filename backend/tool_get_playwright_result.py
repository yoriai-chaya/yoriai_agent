import argparse
import json
import sys
from pathlib import Path

from base import LoadPlaywrightReport
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
            result_dict = result.suites.model_dump()
            print(json.dumps(result_dict, indent=2, ensure_ascii=False))

            input_path = Path(args.file)
            create_summary_report_file(result.suites, input_path)
