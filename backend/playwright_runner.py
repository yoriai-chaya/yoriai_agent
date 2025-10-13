import subprocess
from pathlib import Path

from agents import RunContextWrapper

from base import FunctionResult
from logger import logger


def run_playwright(
    ctx: RunContextWrapper, test_dir: str, test_file: str
) -> FunctionResult:
    logger.debug("run_playwright called")

    output_dir: Path = ctx.context.output_dir
    logger.debug(f"output_dir: {str(output_dir)}")
    results_dir: Path = ctx.context.results_dir
    logger.debug(f"results_dir: {str(results_dir)}")
    logger.debug(f"test_dir: {test_dir}")
    logger.debug(f"test_file: {test_file}")

    ctx.context.test_file = test_file

    test_path = output_dir / test_dir / test_file
    logger.debug(f"test_path: {str(test_path)}")
    command = ["npx", "playwright", "test", str(test_path)]
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
            logger.debug(f"process.stdout line: {line}")
            if '"status":404' in line:
                error_detected = "Detected 404 in test output"
                break
            if "Error:" in line and "already used" in line:
                error_detected = "Playwright server port already in use"
                break
        if error_detected:
            logger.debug(f"error detectd : {error_detected}")
            func_result = FunctionResult(result=False, detail=error_detected)
            return func_result
    except Exception as e:
        err_msg = f"Error running Playwright tests: {e}"
        logger.error(err_msg)
        func_result = FunctionResult(result=False, detail=err_msg)
        return func_result

    process.wait()
    return_code = process.returncode
    err_msg = f"Playwright exited with return code: {return_code}"
    logger.debug(err_msg)
    if return_code != 0:
        func_result = FunctionResult(result=False, detail=err_msg)
        return func_result
    logger.debug("run_playwright return")
    func_result = FunctionResult(result=True)
    return func_result
