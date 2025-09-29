import argparse
import json
import re
import sys
from pathlib import Path
from typing import List

from pydantic import BaseModel


class PlaywrightSpecs(BaseModel):
    title: str
    result: bool
    error_summary: str | None = None
    error_message: str | None = None
    error_stack: str | None = None


class PlaywrightSuites(BaseModel):
    name: str
    file: str
    result: bool
    total: int
    ok: int
    ng: int
    specs: List[PlaywrightSpecs]


def strip_ansi_codes(text: str | None) -> str | None:
    if text is None:
        return None
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


def extract_error_summary(error_message: str | None) -> str | None:
    if not error_message:
        return None

    head_128 = error_message[:128]
    start_index = head_128.find("Error:")
    if start_index != -1:
        remainder = head_128[start_index:]
        newline_index = remainder.find("\n")
        if newline_index != -1:
            return remainder[:newline_index]

    return error_message[:40]


def extract_waiting_for_message(errors: list[dict]) -> str | None:
    for err in errors:
        msg = err.get("message")
        if msg and msg.startswith("Error:"):
            waiting_index = msg.find("waiting for")
            if waiting_index != -1:
                remainder = msg[waiting_index:]
                newline_index = remainder.find("\n")
                extracted = (
                    remainder if newline_index == -1 else remainder[:newline_index]
                )
                return strip_ansi_codes(extracted)
    return None


def load_playwright_report(report_path: str) -> PlaywrightSuites:
    path = Path(report_path)
    if not path.exists():
        print(f"Error: File not found: {report_path}")
        sys.exit(1)
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except OSError as e:
        print(f"Error: Failed to open file {report_path}: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON in {report_path}: {e}")
        sys.exit(1)

    suite = report["suites"][0]["suites"][0]
    specs_data = suite["specs"]

    specs: List[PlaywrightSpecs] = []
    for spec in specs_data:
        ok = spec["ok"]
        error_message = None
        error_stack = None
        error_summary = None

        if not ok:
            try:
                first_result = spec["tests"][0]["results"][0]
                if "error" in first_result:
                    error_message = strip_ansi_codes(
                        first_result["error"].get("message")
                    )
                    error_summary = extract_error_summary(error_message)
                    error_stack = strip_ansi_codes(first_result["error"].get("stack"))

                    if error_message and error_message.startswith("Test timeout"):
                        extracted = extract_waiting_for_message(
                            first_result.get("errors", [])
                        )
                        if extracted:
                            error_message = extracted

            except (KeyError, IndexError, TypeError):
                pass

        specs.append(
            PlaywrightSpecs(
                title=spec["title"],
                result=ok,
                error_summary=error_summary,
                error_message=error_message,
                error_stack=error_stack,
            )
        )

    ok_count = sum(1 for s in specs if s.result)
    ng_count = sum(1 for s in specs if not s.result)

    suite_result = all(s.result for s in specs)

    return PlaywrightSuites(
        name=suite["title"],
        file=suite["file"],
        result=suite_result,
        total=len(specs),
        ok=ok_count,
        ng=ng_count,
        specs=specs,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Playwright Report Parser")
    parser.add_argument(
        "-f", "--file", required=True, help="Playwright report file (json-format)"
    )
    args = parser.parse_args()
    if not args.file:
        parser.print_usage()
        sys.exit(1)
    result = load_playwright_report(args.file)
    result_dict = result.model_dump()

    print(json.dumps(result_dict, indent=2, ensure_ascii=False))

    input_path = Path(args.file)
    output_file = input_path.with_name(f"{input_path.stem}_summary{input_path.suffix}")
    try:
        output_file.write_text(
            json.dumps(result_dict, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"\nSaved report: {output_file}")
    except OSError as e:
        print(f"Error: Failed to write file {output_file}: {e}")
        sys.exit(1)
