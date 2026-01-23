from base import (
    DonePayload,
    DoneStatus,
    EventType,
    IsCodeCheckError,
    LocalContext,
    LoopAction,
    SSEPayload,
    StepResult,
)
from config import Settings
from create_prompt import create_prompt_for_builderror
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
        if build_result.abort_flg:
            logger.error(f"[run_build] Build failed: {build_result.detail}")
            return StepResult(
                action=LoopAction.BREAK,
                final_payload=DonePayload(
                    status=DoneStatus.FAILED,
                    message="Build failed",
                ),
            )

        context.is_code_check_error = IsCodeCheckError.BUILD_ERROR

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

        if context.response is None:
            logger.error("context.response is None at build error")
            return StepResult(
                action=LoopAction.BREAK,
                final_payload=DonePayload(
                    status=DoneStatus.FAILED,
                    message="Internal error occurred",
                ),
            )

        re_prompt = create_prompt_for_builderror(
            context.response.code,
            build_result.detail or "",
        )

        return StepResult(
            action=LoopAction.CONTINUE,
            sse_events=sse_events,
            next_prompt=re_prompt,
        )

    context.is_code_check_error = IsCodeCheckError.NO_ERROR
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

    return StepResult(action=LoopAction.BREAK, sse_events=sse_events)
