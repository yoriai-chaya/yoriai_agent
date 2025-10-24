import subprocess
from pathlib import Path

from agents import RunContextWrapper

from base import FunctionResult
from common import save_backup
from logger import logger


def run_playwright(
    ctx: RunContextWrapper, test_dir: str, test_file: str, project: str
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

    playwright_report_file = ctx.context.playwright_report_file
    logger.debug(f"playwright_report_file: {playwright_report_file}")
    playwright_report_file_path: Path = (
        output_dir / results_dir / playwright_report_file
    )
    if playwright_report_file_path.exists():
        ctx.context.before_mtime = playwright_report_file_path.stat().st_mtime
    logger.debug(f"ctx.context.before_mtime: {ctx.context.before_mtime}")

    # Execute npx playwright command
    flg_404 = False
    command = ["npx", "playwright", "test"]
    if project:
        prj_option = f"--project={project}"
        command.extend([prj_option])
    command.append(str(test_path))
    logger.debug(f"command: {command}")
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
                flg_404 = True
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

    # Backup
    if not flg_404:
        logger.debug("not flg_404 : backup info/report file")
        dir = output_dir / results_dir
        info_file = ctx.context.playwright_info_file
        report_file = ctx.context.playwright_report_file
        logger.debug(f"dir: {dir}")
        logger.debug(f"info_file: {info_file}")
        logger.debug(f"report_file: {report_file}")
        try:
            save_backup(dir=dir, src_file=info_file)
            save_backup(dir=dir, src_file=report_file)
        except Exception as e:
            logger.error(f"Faild backup: {e}")
            func_result = FunctionResult(result=False, detail=err_msg)
            return func_result

    # Return
    if return_code != 0:
        func_result = FunctionResult(result=False, detail=err_msg)
        return func_result
    logger.debug("run_playwright return")
    func_result = FunctionResult(result=True)
    return func_result
