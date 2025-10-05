import shutil
from datetime import datetime
from pathlib import Path

from agents import RunContextWrapper

from logger import logger


def save_playwright_results(ctx: RunContextWrapper):
    logger.debug("save_playwright_results called")

    output_dir: Path = ctx.context.output_dir
    logger.debug(f"output_dir: {str(output_dir)}")
    results_dir: Path = ctx.context.results_dir
    logger.debug(f"results_dir: {str(results_dir)}")
    playwright_info_file = ctx.context.playwright_info_file
    logger.debug(f"playwright_info_file: {playwright_info_file}")
    playwright_report_file = ctx.context.playwright_report_file
    logger.debug(f"playwright_report_file: {playwright_report_file}")
    playwright_report_summary_file = ctx.context.playwright_report_summary_file
    logger.debug(f"playwright_report_summary_file: {playwright_report_summary_file}")
    test_file = ctx.context.test_file
    logger.debug(f"test_file: {test_file}")

    backup_targets = [
        playwright_info_file,
        playwright_report_file,
        playwright_report_summary_file,
    ]
    backup_dir: Path = output_dir / results_dir / test_file

    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"backup directory prepared: {backup_dir}")
    except Exception as e:
        logger.error(f"Failed to create backup directory: {backup_dir} : {e}")
        return

    for src_file in backup_targets:
        try:
            src_path: Path = output_dir / results_dir / src_file
            if not src_path.exists():
                logger.error(f"Backup source file does not exist: {src_path}")
                return
            stat = src_path.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)
            timestamp = mtime.strftime("%Y%m%d_%H%M%S")

            stem = src_path.stem
            ext = src_path.suffix
            backup_path = backup_dir / f"{stem}_{timestamp}{ext}"
            logger.debug(f"backup_path: {backup_path}")

            shutil.copy2(str(src_path), str(backup_path))
            logger.debug(f"backup: {src_path.name} -> {backup_path.name}")

        except Exception as e:
            logger.error(f"Failed to backup file {src_path}: {e}")
            return

    logger.debug("save_playwright_results completed successfully")
    return
