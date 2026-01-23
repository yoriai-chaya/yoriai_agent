import json

from agents.exceptions import AgentsException, ModelBehaviorError

from base import (
    DonePayload,
    DoneStatus,
    EventType,
    LocalContext,
    LoopAction,
    PromptRequest,
    SSEPayload,
    StepResult,
    SystemError,
)
from create_code import gen_code
from logger import logger


async def gen_code_step(
    final_prompt: str,
    context: LocalContext,
    retry_index: int,
    retry_limit: int,
) -> StepResult:
    sse_events: list[SSEPayload] = []

    try:
        logger.debug("[gen_code] Call gen_code()")
        async for line in gen_code(
            request=PromptRequest(prompt=final_prompt),
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
                logger.error(f"[gen_code] Invalid JSON: {e}")

        logger.debug(f"action={LoopAction.NORMAL}, sse_events={sse_events}")
        return StepResult(action=LoopAction.NORMAL, sse_events=sse_events)

    except ModelBehaviorError as e:
        logger.warning(f"[gen_code] ModelBehaviorError: {e}")
        sse_events.append(
            SSEPayload(
                event=EventType.SYSTEM_ERROR,
                payload=SystemError(
                    error="ModelBehaviorError",
                    detail=str(e),
                ).model_dump(),
            )
        )

        if retry_index == retry_limit - 1:
            return StepResult(
                action=LoopAction.BREAK,
                sse_events=sse_events,
                final_payload=DonePayload(
                    status=DoneStatus.FAILED,
                    message="Retry Limit exceeded",
                ),
            )

        return StepResult(action=LoopAction.CONTINUE, sse_events=sse_events)

    except AgentsException as e:
        logger.error(f"[gen_code] AgentsException: {e}")
        sse_events.append(
            SSEPayload(
                event=EventType.SYSTEM_ERROR,
                payload=SystemError(
                    error="AgentsException",
                    detail=str(e),
                ).model_dump(),
            )
        )

        return StepResult(
            action=LoopAction.BREAK,
            sse_events=sse_events,
            final_payload=DonePayload(
                status=DoneStatus.FAILED,
                message="Internal error occurred",
            ),
        )
