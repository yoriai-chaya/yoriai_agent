from pathlib import Path

from agents import RunContextWrapper

from base import FunctionResult, LoadPlaywrightReport, RunTestsResultPayload
from edit_playwright_report import create_summary_report_file, load_playwright_report
from logger import logger


def eval_test_results(ctx: RunContextWrapper) -> RunTestsResultPayload:
    logger.debug("eval_test_results called")

    output_dir: Path = ctx.context.output_dir
    logger.debug(f"output_dir: {str(output_dir)}")
    results_dir: Path = ctx.context.results_dir
    logger.debug(f"results_dir: {str(results_dir)}")
    playwright_report_file = ctx.context.playwright_report_file
    logger.debug(f"playwright_report_file: {playwright_report_file}")
    test_file = ctx.context.test_file
    logger.debug(f"test_file: {test_file}")

    report_file: Path = output_dir / results_dir / playwright_report_file
    logger.debug(f"report_file: {report_file}")
    result: LoadPlaywrightReport = load_playwright_report(
        str(report_file), logger.debug
    )
    if not result.result:
        test_results = RunTestsResultPayload(result=False, detail=result.detail)
        return test_results
    if result.suites:
        create_result: FunctionResult = create_summary_report_file(
            result.suites, report_file, logger.debug
        )
        if not create_result.result:
            test_results = RunTestsResultPayload(
                result=False, detail=create_result.detail
            )
            return test_results

        test_results = RunTestsResultPayload(
            result=result.suites.result,
            name=result.suites.name,
            file=result.suites.file,
            total=result.suites.total,
            ok=result.suites.ok,
            ng=result.suites.ng,
            specs=result.suites.specs.copy(),
        )

    logger.debug("return test_results")
    return test_results
