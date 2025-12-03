import json

from agents.exceptions import AgentsException, ModelBehaviorError

from base import (
    DebugMode,
    DonePayload,
    DoneStatus,
    EventType,
    PromptRequest,
    SystemError,
)
from check_code import check_gen_code
from create_code import gen_code
from create_prompt import create_prompt_for_builderror
from logger import logger
from run_build_cmd import run_build


async def handle_gen_code(
    prompt: str, context, settings, sse_event, wait_for_console_input
):
    category = context.category
    logger.info(f"[{category}]: Start Code Generation")
    # Make Payload (for Completed)
    final_payload = DonePayload(
        status=DoneStatus.COMPLETED, message="All Tasks Completed"
    )

    # Code Gen Loop
    debug_mode = DebugMode.CONTINUE
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
                logger.debug("[debug] wait (before gen_code)")
                debug_mode = await wait_for_console_input()
                if debug_mode == DebugMode.END:
                    logger.debug("[debug] end")
                    break
                logger.debug("[debug] continue or skip_agent")

            if not debug_mode == DebugMode.SKIP_AGENT:
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
            logger.debug("[debug] wait (before check_gen_code)")
            debug_mode = await wait_for_console_input()
            if debug_mode == DebugMode.END:
                logger.debug("[debug] end")
                break
            logger.debug("[debug] continue or skip_agent")

        # Check Code
        if not debug_mode == DebugMode.SKIP_AGENT:
            try:
                async for line in check_gen_code(
                    request=PromptRequest(prompt=prompt), context=context
                ):
                    try:
                        data = json.loads(line)
                        yield await sse_event(data["event"], data.get("payload", {}))
                    except Exception as e:
                        logger.debug(f"Invalid JSON from check_gen_code: {e}")

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                error_payload = SystemError(error="Unexpected error", detail=str(e))
                yield await sse_event(
                    EventType.SYSTEM_ERROR, error_payload.model_dump()
                )
                final_payload = DonePayload(
                    status=DoneStatus.FAILED, message="check_gen_code error occurred"
                )
                break

        # Wait for console input (for debug)
        if settings.debug:
            logger.debug("[debug] wait (before is_retry_gen_code)")
            debug_mode = await wait_for_console_input()
            if debug_mode == DebugMode.END:
                logger.debug("[debug] end")
                break
            logger.debug("[debug] continue or skip_agent or bypass")

        # Loop Judge
        logger.debug(f"debug_mode: {debug_mode}")
        if context.is_retry_gen_code:
            if not debug_mode == DebugMode.BYPASS:
                continue

        # Build
        build_result = await run_build(context, settings)
        logger.debug(f"build_result: {build_result}")
        if not build_result.result:
            if build_result.abort_flg:
                logger.error(f"Build failed: {build_result.detail}")
                final_payload = DonePayload(
                    status=DoneStatus.FAILED, message="Build failed"
                )
                break
            else:
                build_check_payload = {
                    "checker": "Build",
                    "result": False,
                    "rule_id": "",
                    "detail": "",
                }
                yield await sse_event(EventType.CHECK_RESULT, build_check_payload)
                re_prompt = create_prompt_for_builderror()
                logger.debug(f"re_prompt: {re_prompt}")
        else:
            build_check_payload = {
                "checker": "Build",
                "result": True,
                "rule_id": "",
                "detail": "",
            }
            yield await sse_event(EventType.CHECK_RESULT, build_check_payload)
            break

        # Retry Limit Check
        if i == settings.code_gen_retry - 1:
            final_payload = DonePayload(
                status=DoneStatus.FAILED, message="Retry Limit exceeded"
            )

    # Done
    logger.info(f"[{category}]: All Tasks Completed")
    yield await sse_event(EventType.DONE, final_payload.model_dump())
