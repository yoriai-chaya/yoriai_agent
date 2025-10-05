import json
from pathlib import Path

from agents import ItemHelpers, Runner

from base import DonePayload, DoneStatus, EventType, RunTestsResultPayload
from custom_agents import run_tests_agent
from logger import logger


async def handler_run_tests(
    prompt: str, context, settings, sse_event, wait_for_console_input
):
    logger.info("RunTests handler called")

    final_payload = DonePayload(
        status=DoneStatus.COMPLETED, message="RunTests completed"
    )

    result = Runner.run_streamed(
        starting_agent=run_tests_agent,
        input=prompt,
        context=context,
        max_turns=context.max_turns,
    )
    logger.debug(f"result: {result}")

    json_path = Path("./output/results/playwright_report_summary.json")
    try:
        with json_path.open("r", encoding="utf-8") as f:
            report_summary = json.load(f)
        test_result_payload = RunTestsResultPayload(**report_summary)
    except Exception as e:
        logger.error(f"Failed to load report summary: {e}")
        test_result_payload = RunTestsResultPayload(result=False, detail=str(e))
    yield await sse_event(EventType.TEST_RESULT, test_result_payload.model_dump())

    yield await sse_event(EventType.DONE, final_payload.model_dump())
