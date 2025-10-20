import argparse
import subprocess
import sys
from pathlib import Path

from config import get_settings
from logger import logger


def run_playwright_tests(test_file: str, output_dir: Path, results: Path) -> int:
    logger.debug("run_playwright_tests() called")
    project_root = Path(__file__).resolve().parent
    results_dir = output_dir / results
    results_dir.mkdir(exist_ok=True)
    logger.debug(f"project_root: {project_root}")
    logger.debug(f"results_dir: {results_dir}")
    logger.debug(f"test_file: {test_file}")

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
            logger.debug(line, end="")

            if '"status":404' in line:
                error_detected = "Detected 404 in test output"
                break
            if "Error:" in line and "already used" in line:
                error_detected = "Playwright server port already in use"
                break
        if error_detected:
            logger.error(f"error detected : {error_detected}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Failed to run playwright: {e}")
        sys.exit(1)

    process.wait()
    return_code = process.returncode
    return return_code


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
    my_name = Path(__file__).name
    logger.info(f"{my_name} Started")
    logger.debug(f"file: {args.file}, output_dir: {output_dir}, results: {results}")
    return_code = run_playwright_tests(args.file, output_dir, results)
    logger.info(f"{my_name} Ended return_code: {return_code}")
