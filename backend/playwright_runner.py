import subprocess
from pathlib import Path

from agents import RunContextWrapper

from base import FunctionResult
from common import archive
from logger import logger

SNAPSHOT_ERROR_MESSAGE_PREF = "Error: A snapshot doesn't exist at"


def run_playwright(
    ctx: RunContextWrapper,
    test_dir: str,
    test_file: str,
    project: str,
    update_snapshots: bool = False,
    allow_snapshot_retry: bool = True,
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
    if not test_path.is_file():
        err_msg = f"{test_path} not found"
        func_result = FunctionResult(result=False, abort_flg=True, detail=err_msg)
        return func_result

    playwright_report_file = ctx.context.playwright_report_file
    logger.debug(f"playwright_report_file: {playwright_report_file}")
    playwright_report_file_path: Path = (
        output_dir / results_dir / playwright_report_file
    )
    if playwright_report_file_path.exists():
        ctx.context.before_mtime = playwright_report_file_path.stat().st_mtime
    logger.debug(f"ctx.context.before_mtime: {ctx.context.before_mtime}")

    # Execute npx playwright command
    command = ["npx", "playwright", "test"]
    if update_snapshots:
        command.append("--update-snapshots")
    if project:
        # prj_option = f"--project={project}"
        # command.extend([prj_option])
        command.append("--project={project}")

    command.append(str(test_path))
    logger.debug(f"command: {command}")

    flg_404 = False
    detected_snapshot_missing = False
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
                return FunctionResult(result=False, detail=error_detected)
            if "Error:" in line and "already used" in line:
                error_detected = "Playwright server port already in use"
                return FunctionResult(result=False, detail=error_detected)
        if SNAPSHOT_ERROR_MESSAGE_PREF in line:
            detected_snapshot_missing = True
    except Exception as e:
        err_msg = f"Error running Playwright tests: {e}"
        logger.error(err_msg)
        func_result = FunctionResult(result=False, detail=err_msg)
        return func_result

    process.wait()
    return_code = process.returncode
    err_msg = f"Playwright exited with return code: {return_code}"
    logger.debug(err_msg)

    # for snapshot error (re-run once)
    if (
        return_code != 0
        and detected_snapshot_missing
        and (not update_snapshots)
        and allow_snapshot_retry
    ):
        logger.warning(
            "Snapshot missing detected. Re-running once with --update-snapshots ..."
        )
        return run_playwright(
            ctx=ctx,
            test_dir=test_dir,
            test_file=test_file,
            project=project,
            update_snapshots=True,
            allow_snapshot_retry=False,
        )

    # Backup
    if not flg_404:
        logger.debug("not flg_404 : backup info/report file")
        src_dir = output_dir / results_dir
        info_file = ctx.context.playwright_info_file
        report_file = ctx.context.playwright_report_file
        logger.debug(f"dir: {dir}")
        logger.debug(f"info_file: {info_file}")
        logger.debug(f"report_file: {report_file}")
        try:
            archive(
                src_dir=src_dir,
                src_file=info_file,
                stepid_dir=ctx.context.stepid_dir,
                dir=Path("./playwright"),
            )
            archive(
                src_dir=src_dir,
                src_file=report_file,
                stepid_dir=ctx.context.stepid_dir,
                dir=Path("./playwright"),
            )
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
