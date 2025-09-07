import json

from agents.exceptions import AgentsException, ModelBehaviorError

from base import DonePayload, DoneStatus, EventType, PromptRequest, SystemError
from check_code import check_gen_code
from create_code import gen_code
from logger import logger


async def handle_gen_code(
    prompt: str, context, settings, sse_event, wait_for_console_input
):
    # Make Payload (for Completed)
    final_payload = DonePayload(
        status=DoneStatus.COMPLETED, message="All Tasks Completed"
    )

    # Code Gen Loop
    for i in range(settings.code_gen_retry):
        logger.debug(f"Code Gen Loop [{i}]")

        try:
            # Create Code
            final_prompt = prompt
            add_prompts_len = len(context.add_prompts)
            logger.debug(f"add_prompts_len: {add_prompts_len}")
            if not add_prompts_len == 0:
                # extend prompt
                for add_prompt in context.add_prompts:
                    logger.debug(f"add_prompt : {add_prompt}")
                    prefix = "- "
                    final_prompt = f"{final_prompt}\n{prefix}{add_prompt}\n"
                    logger.debug(f"final_prompt: {final_prompt}")

            # Wait for console input (for debug)
            if settings.debug:
                logger.debug("[debug] stop")
                should_continue = await wait_for_console_input()
                if not should_continue:
                    logger.debug("[debug] user stop")
                    break
                logger.debug("[debug] continue")

            async for line in gen_code(
                request=PromptRequest(prompt=final_prompt), context=context
            ):
                try:
                    data = json.loads(line)
                    yield await sse_event(data["event"], data.get("payload", {}))
                except Exception as e:
                    logger.debug(f"Invalid JSON from gen_code: {e}")
        except ModelBehaviorError as e:
            logger.warning(f"ModelBehaviorError detected: {e}")
            error_payload = SystemError(error="ModelBehaviorError", detail=str(e))
            yield await sse_event(EventType.SYSTEM_ERROR, error_payload.model_dump())
            if i == settings.code_gen_retry - 1:
                final_payload = DonePayload(
                    status=DoneStatus.FAILED, message="Retry Limit exceeded"
                )
            else:
                continue
        except AgentsException as e:
            logger.error(f"AgentsException detected: {e}")
            error_payload = SystemError(error="AgentsException", detail=str(e))
            yield await sse_event(EventType.SYSTEM_ERROR, error_payload.model_dump())
            final_payload = DonePayload(
                status=DoneStatus.FAILED, message="Internal error occurred"
            )
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            error_payload = SystemError(error="Unexpected error", detail=str(e))
            yield await sse_event(EventType.SYSTEM_ERROR, error_payload.model_dump())
            final_payload = DonePayload(
                status=DoneStatus.FAILED, message="Internal error occurred"
            )
            break

        # Wait for console input (for debug)
        if settings.debug:
            logger.debug("[debug] stop")
            should_continue = await wait_for_console_input()
            if not should_continue:
                logger.debug("[debug] user stop")
                break
            logger.debug("[debug] continue")

        # Check Code
        async for line in check_gen_code(
            request=PromptRequest(prompt=prompt), context=context
        ):
            try:
                data = json.loads(line)
                yield await sse_event(data["event"], data.get("payload", {}))
            except Exception as e:
                logger.debug(f"Invalid JSON from check_gen_code: {e}")

        # Loop Judge
        if context.code_check_result:
            break

        # Retry Limit Check
        if i == settings.code_gen_retry - 1:
            final_payload = DonePayload(
                status=DoneStatus.FAILED, message="Retry Limit exceeded"
            )

    # Done
    # yield await sse_event(EventType.DONE, {"message": "All Tasks Completed"})
    yield await sse_event(EventType.DONE, final_payload.model_dump())

    logger.debug("All Tasks Completed")
