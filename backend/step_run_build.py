from base import (
    DonePayload,
    DoneStatus,
    EventType,
    LocalContext,
    SSEPayload,
    StepResult,
)
from config import Settings
from logger import logger
from run_build_cmd import run_build


async def run_build_step(
    context: LocalContext,
    settings: Settings,
) -> StepResult:
    sse_events: list[SSEPayload] = []

    logger.debug("[run_build] Call run_build()")
    build_result = await run_build(context, settings)

    if not build_result.result:
        # Case-1: The build command could not be executed due to a system-level error.
        # Case-2: The build command completed, but the build output contains errors.
        logger.error(f"[run_build] Build failed: {build_result.detail}")
        sse_events.append(
            SSEPayload(
                event=EventType.CHECK_RESULT,
                payload={
                    "checker": "Build",
                    "result": False,
                    "rule_id": "npm run build",
                    "detail": build_result.detail,
                },
            )
        )
        return StepResult(
            result=build_result,
            sse_events=sse_events,
            final_payload=DonePayload(
                status=DoneStatus.FAILED,
                message="Build failed",
            ),
        )

    # Case-3: The build command completed successfully with no errors detected.
    sse_events.append(
        SSEPayload(
            event=EventType.CHECK_RESULT,
            payload={
                "checker": "Build",
                "result": True,
                "rule_id": "",
                "detail": "",
            },
        )
    )
    return StepResult(result=build_result, sse_events=sse_events)
