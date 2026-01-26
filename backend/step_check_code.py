import json

from base import (
    EventType,
    IsCodeCheckError,
    LocalContext,
    LoopAction,
    PromptRequest,
    SSEPayload,
    StepResult,
)
from check_code import check_gen_code
from logger import logger


async def check_code_step(prompt: str, context: LocalContext) -> StepResult:
    logger.debug("[check_gen_code] Call check_gen_code()")
    sse_events: list[SSEPayload] = []

    async for line in check_gen_code(
        request=PromptRequest(prompt=prompt),
        context=context,
    ):
        try:
            data = json.loads(line)
            sse_events.append(
                SSEPayload(
                    event=EventType(data["event"]),
                    payload=data.get("payload", {}),
                )
            )
        except Exception as e:
            logger.error(f"[check_gen_code] Invalid JSON: {e}")

    if context.is_code_check_error == IsCodeCheckError.ESLINT_ERROR:
        return StepResult(
            action=LoopAction.CONTINUE,
            sse_events=sse_events,
        )

    return StepResult(
        action=LoopAction.BREAK,
        sse_events=sse_events,
    )
