import json
from typing import AsyncIterator

from base import (
    BuildErrorAnalyzerResult,
    EventType,
    FunctionResult,
    LocalContext,
    SSEPayload,
    SystemError,
)
from build_error_analysis import analyze_build_error
from logger import logger


async def run_rebuild_step(
    context: LocalContext, build_result: FunctionResult
) -> AsyncIterator[SSEPayload]:
    logger.debug("run_rebuild_step called")

    try:
        # SubStep-1: Build Error Analysis
        analyzer_result: BuildErrorAnalyzerResult | None = None
        logger.debug("[gen_code] Call gen_code()")
        async for line in analyze_build_error(
            context=context, build_result=build_result
        ):
            # Events: AGENT_UPDATE, ANALYZER_RESULT
            data = json.loads(line)
            yield SSEPayload(
                event=EventType(data["event"]), payload=data.get("payload", {})
            )
            if data["event"] == EventType.ANALYZER_RESULT:
                analyzer_result = BuildErrorAnalyzerResult(**data["payload"])

        # SubStep-2: Fix Code
        logger.debug(f"analyzer_result: {analyzer_result}")

        # SubStep-3: Validate Code

    except Exception as e:
        logger.error(f"Exception: {e}")
        yield SSEPayload(
            event=EventType.SYSTEM_ERROR,
            payload=SystemError(error="Unexpected Error", detail=str(e)).model_dump(),
        )
