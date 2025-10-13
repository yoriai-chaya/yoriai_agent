import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

from config import get_settings

PLAYWRIGHT_CONFIG_TS = "playwright.config.ts"


def save_result_json(
    result_file: Path,
    backup_file: Path,
    command: list[str],
    output_dir: Path,
    timestamp: str,
    message: str,
    success: bool,
):
    data = {
        "timestamp": timestamp,
        "command": " ".join(command),
        "cwd": str(output_dir),
        "message": message,
        "success": success,
    }
    for path in [result_file, backup_file]:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        print(f"[INFO] Saved result to: {path}")


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
    base_filename = Path(__file__).stem
    result_file = results_dir / f"{base_filename}.json"

    backup_dir = results_dir / "backup"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_file = backup_dir / f"{timestamp}_{base_filename}.json"

    command = [
        "npx",
        "playwright",
        "test",
        test_file,
    ]

    try:
        process = subprocess.Popen(
            command,
            cwd=output_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        error_detected = None

        if process.stdout is None:
            raise RuntimeError("Failed to capture Playwright stdout")

        for line in process.stdout:
            print(line, end="")

            if '"status":404' in line:
                error_detected = "Detected 404 in test output"
                break
            if "Error:" in line and "already used" in line:
                error_detected = "Playwright server port already in use"
                break
        if error_detected:
            print(f"error detected : {error_detected}")
            save_result_json(
                result_file=result_file,
                backup_file=backup_file,
                command=command,
                output_dir=output_dir,
                timestamp=timestamp,
                message=error_detected,
                success=False,
            )
            sys.exit(1)

        process.wait()
        return_code = process.returncode
        print(f"Playwright exited with return_code: {return_code}")
        if return_code != 0:
            save_result_json(
                result_file=result_file,
                backup_file=backup_file,
                command=command,
                output_dir=output_dir,
                timestamp=timestamp,
                message=f"Exit code: {return_code}",
                success=False,
            )
            sys.exit(return_code)

        save_result_json(
            result_file=result_file,
            backup_file=backup_file,
            command=command,
            output_dir=output_dir,
            timestamp=timestamp,
            message="Completed successfully",
            success=True,
        )
        sys.exit(0)

    except Exception as e:
        save_result_json(
            result_file=result_file,
            backup_file=backup_file,
            command=command,
            output_dir=output_dir,
            timestamp=timestamp,
            message=str(e),
            success=False,
        )
        print(f"[ERROR] Failed to run playwright: {e}")
        sys.exit(1)


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
