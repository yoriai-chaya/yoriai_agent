import subprocess
from pathlib import Path

from agents import RunContextWrapper

from base import PlaywrightSpecs, RunTestsResultPayload
from logger import logger


def run_playwright(
    ctx: RunContextWrapper, test_dir: str, test_file: str
) -> RunTestsResultPayload:
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
        cmd_result = subprocess.run(
            command, cwd=output_dir, capture_output=True, text=True, check=False
        )
        logger.debug(f"cmd_result.stdout: {cmd_result.stdout}")
        logger.debug(f"cmd_result.stderr: {cmd_result.stderr}")
    except Exception as e:
        test_result = RunTestsResultPayload(result=False, detail=str(e))
        return test_result

    test_result = RunTestsResultPayload(result=True, detail="xxx")
    return test_result
