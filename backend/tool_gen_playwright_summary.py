import json
import sys
from pathlib import Path

from base import FunctionResult, LoadPlaywrightReport
from common import resolve_path, save_backup
from config import get_settings
from edit_playwright_report import create_summary_report_file, load_playwright_report
from logger import logger

if __name__ == "__main__":
    # Get Settings / Config Data
    settings = get_settings()
    output_dir = resolve_path(settings.output_dir)
    logger.debug(f"output_dir: {output_dir}")
    custom_config_file = output_dir / settings.playwright_customconfig_file
    logger.debug(f"custom_config_file: {custom_config_file}")
    if not custom_config_file.exists():
        logger.error(f"{custom_config_file} not found")
        sys.exit(1)
    try:
        with open(custom_config_file, "r") as f:
            custom_config = json.load(f)
    except Exception as e:
        logger.error(f"{custom_config_file} open failed: {e}")
        sys.exit(1)

    results = custom_config["results"]
    logger.debug(f"results: {results}")
    playwright_report_file = custom_config["playwright_report_file"]
    logger.debug(f"playwright_report_file: {playwright_report_file}")
    playwright_report_summary_file = custom_config["playwright_report_summary_file"]
    logger.debug(f"playwright_report_summary_file: {playwright_report_summary_file}")
    playwright_report_path = output_dir / results / playwright_report_file
    playwright_report_summary_path = (
        output_dir / results / playwright_report_summary_file
    )

    # sys.exit(1)

    # Load Playwright Report File
    my_name = Path(__file__).name
    logger.info(f"{my_name} Started")
    result: LoadPlaywrightReport = load_playwright_report(playwright_report_path)
    if not result.result:
        logger.error(f"Playwright report file loading error: detail={result.detail}")
        sys.exit(1)

    if result.suites:
        dir = output_dir / results
        try:
            save_backup(dir=dir, src_file=playwright_report_file)
        except Exception as e:
            logger.error(f"Failed backup: {e}")
            sys.exit(1)
        input_path = Path(playwright_report_path)
        result_create: FunctionResult = create_summary_report_file(
            result.suites, input_path
        )
        if not result_create:
            logger.error(f"Failed to generate summary file: {result_create.detail}")
        else:
            save_backup(dir=dir, src_file=playwright_report_summary_file)
            logger.info(f"Saved summary file: {playwright_report_summary_path}")
