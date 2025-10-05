import json
import re
from pathlib import Path
from typing import Callable, List

from base import FunctionResult, LoadPlaywrightReport, PlaywrightSpecs, PlaywrightSuites


def _strip_ansi_codes(text: str | None) -> str | None:
    if text is None:
        return None
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


def _extract_error_summary(error_message: str | None) -> str | None:
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


def _extract_waiting_for_message(errors: list[dict]) -> str | None:
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
                return _strip_ansi_codes(extracted)
    return None


def load_playwright_report(
    report_path: str,
    log_func: Callable[[str], None] = print,
) -> LoadPlaywrightReport:
    log_func(f"load_playwright_report called  report_path: {report_path}")
    path = Path(report_path)
    if not path.exists():
        result = LoadPlaywrightReport(
            result=False, detail=f"File not found: {report_path}"
        )
        return result
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except OSError as e:
        result = LoadPlaywrightReport(
            result=False, detail=f"Failed to open file: {report_path}: {e}"
        )
        return result
    except json.JSONDecodeError as e:
        result = LoadPlaywrightReport(
            result=False, detail=f"Failed to parse JSON in {report_path}: {e}"
        )
        return result

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
                    error_message = _strip_ansi_codes(
                        first_result["error"].get("message")
                    )
                    error_summary = _extract_error_summary(error_message)
                    error_stack = _strip_ansi_codes(first_result["error"].get("stack"))

                    if error_message and error_message.startswith("Test timeout"):
                        extracted = _extract_waiting_for_message(
                            first_result.get("errors", [])
                        )
                        if extracted:
                            error_message = extracted

            except Exception as e:
                log_func(f"Unexpected error: {e}")
                result = LoadPlaywrightReport(
                    result=False, detail=f"Unexpected error: {e}"
                )
                return result

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

    playwright_suites = PlaywrightSuites(
        name=suite["title"],
        file=suite["file"],
        result=suite_result,
        total=len(specs),
        ok=ok_count,
        ng=ng_count,
        specs=specs,
    )
    result = LoadPlaywrightReport(result=True, suites=playwright_suites)
    return result


def create_summary_report_file(
    suites: PlaywrightSuites,
    report_file_path: Path,
    log_func: Callable[[str], None] = print,
) -> FunctionResult:
    log_func(f"create_summary_report_file called  report_file_path: {report_file_path}")
    output_file = report_file_path.with_name(
        f"{report_file_path.stem}_summary{report_file_path.suffix}"
    )
    try:
        output_file.write_text(
            json.dumps(suites.model_dump(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        result = FunctionResult(result=True)
        return result
    except Exception as e:
        result = FunctionResult(result=False, detail=str(e))
        return result
