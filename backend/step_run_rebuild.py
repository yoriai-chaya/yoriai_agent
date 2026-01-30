import json

from base import (
    BuildErrorAnalyzerResult,
    EventType,
    FunctionResult,
    LocalContext,
    SSEPayload,
    StepResult,
    SystemError,
)
from build_error_analysis import analyze_build_error
from code_fixer import fix_code
from config import Settings
from logger import logger
from run_build_cmd import run_build


async def run_rebuild_step(
    context: LocalContext, settings: Settings, build_result: FunctionResult
) -> StepResult:
    logger.debug("run_rebuild_step called")
    sse_events: list[SSEPayload] = []

    try:
        # ------------------------------
        # SubStep-1: Analyze build error
        # ------------------------------
        logger.debug("SubStep-1: Analyze build error")
        analyzer_result: BuildErrorAnalyzerResult | None = None
        async for line in analyze_build_error(
            context=context, build_result=build_result
        ):
            # Events: AGENT_UPDATE, ANALYZER_RESULT
            data = json.loads(line)
            sse_events.append(
                SSEPayload(
                    event=EventType(data["event"]),
                    payload=data.get("payload", {}),
                )
            )
            if data["event"] == EventType.ANALYZER_RESULT:
                analyzer_result = BuildErrorAnalyzerResult(**data["payload"])

        if analyzer_result is None:
            raise ValueError("analyzer_result is None")
        logger.debug(f"analyzer_result: {analyzer_result}")

        # -------------------
        # SubStep-2: Fix code
        # -------------------
        logger.debug("SubStep-2: Fix code")
        async for line in fix_code(context=context, analyzer_result=analyzer_result):
            # Events: AGENT_RESULT
            data = json.loads(line)
            sse_events.append(
                SSEPayload(
                    event=EventType(data["event"]),
                    payload=data.get("payload", {}),
                )
            )

        # -----------------------
        # SubStep-3: Re-run build
        # -----------------------
        logger.debug("SubStep-3: Re-run build")
        rebuild_result = await run_build(context, settings)
        sse_events.append(
            SSEPayload(
                event=EventType.CHECK_RESULT,
                payload={
                    "checker": "Build",
                    "result": rebuild_result.result,
                    "rule_id": "npm run build (rebuild)",
                    "detail": rebuild_result.detail,
                },
            )
        )

        return StepResult(result=rebuild_result, sse_events=sse_events)

    except Exception as e:
        logger.error(f"Exception: {e}")

        sse_events.append(
            SSEPayload(
                event=EventType.SYSTEM_ERROR,
                payload=SystemError(
                    error="Unexpected Error",
                    detail=str(e),
                ).model_dump(),
            )
        )

        return StepResult(
            result=FunctionResult(
                result=False,
                abort_flg=True,
                detail=str(e),
            ),
            sse_events=sse_events,
        )
