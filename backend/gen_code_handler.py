"""
A handler for code generation, ESLint checking, and build checking

Notes:
(1)error_payload
    In the following statement:
    error_payload = SystemError(error="Unexpected error", detail=str(e))
    The error value (e.g., "Unexpected error") is displayed in the frontend UI (Left-Panel)
    Keep this error message within 20 characters.
"""

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
    """
    Overview:
        A handler that performs code generation, ESLint checks, and build verification.

    Description:
        This handler executes the following steps:

        1. Generate code based on a given prompt.
           If necessary, additional text may be appended to the prompt
           (e.g., when ESLint errors occur, supplementary instructions are added
           to help avoid those errors).

        2. Perform static analysis on the generated code using ESLint.

        3. If the static check passes, run the build command to detect errors
           that ESLint cannot catch
           (e.g., when using useState, a build error occurs if "use client"
           is missing).

        4. If an error occurs in steps (2) or (3), retry the code generation
           process up to the maximum number of retry attempts.
    """
    try:
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

            # -------------------------------
            # 1. Create Code (prepare prompt)
            # -------------------------------
            final_prompt = prompt
            add_prompts_len = len(context.add_prompts)
            logger.debug(
                f"[Prompt] Base prompt len={len(prompt)}, number of additional prompts={add_prompts_len}"
            )
            if not add_prompts_len == 0:
                logger.debug("[Prompt] Extending prompt with additional messages")
                for add_prompt in context.add_prompts:
                    logger.debug(f"[Prompt] Additional prompt: {add_prompt}")
                    prefix = "- "
                    final_prompt = f"{final_prompt}\n{prefix}{add_prompt}\n"
                    logger.debug(f"final_prompt: {final_prompt}")

            # --------------------------------------------
            # 2. CP1: Debug Checkpoint - before gen_code()
            # --------------------------------------------
            logger.debug(f"[CP1] Current debug_mode: {debug_mode}")
            if settings.debug:
                logger.debug("[CP1] Waiting for input from the console")
                debug_mode = await wait_for_console_input()
                logger.debug(f"[CP1] Entered debug_mode: {debug_mode}")
                if debug_mode == DebugMode.END:
                    logger.debug("[CP1] Exiting loop")
                    break
                logger.debug("[CP1] Continuing to gen_code()")

            # ------------------
            # 3. Call gen_code()
            # ------------------
            try:
                if not debug_mode == DebugMode.SKIP_AGENT:
                    logger.debug("[gen_code] Call gen_code()")
                    async for line in gen_code(
                        request=PromptRequest(prompt=final_prompt), context=context
                    ):
                        try:
                            data = json.loads(line)
                            logger.debug(f"[gen_code] Received data: {data}")
                            yield await sse_event(
                                data["event"], data.get("payload", {})
                            )
                        except Exception as e:
                            logger.debug(f"[gen_code] Invalid JSON from gen_code: {e}")
                else:
                    logger.debug("[gen_code] Skipping gen_code()")

            except ModelBehaviorError as e:
                logger.warning(f"[gen_code] ModelBehaviorError detected: {e}")
                error_payload = SystemError(error="ModelBehaviorError", detail=str(e))
                yield await sse_event(
                    EventType.SYSTEM_ERROR, error_payload.model_dump()
                )
                if i == settings.code_gen_retry - 1:
                    final_payload = DonePayload(
                        status=DoneStatus.FAILED, message="Retry Limit exceeded"
                    )
                    logger.debug(
                        "[gen_code] Exiting loop due to ModelBehaviorError and reaching retry limit"
                    )
                    break
                else:
                    logger.debug(f"[gen_code] Retrying due to ModelBehaviorError i={i}")
                    continue
            except AgentsException as e:
                logger.error(f"[gen_code] AgentsException detected: {e}")
                error_payload = SystemError(error="AgentsException", detail=str(e))
                yield await sse_event(
                    EventType.SYSTEM_ERROR, error_payload.model_dump()
                )
                final_payload = DonePayload(
                    status=DoneStatus.FAILED, message="Internal error occurred"
                )
                break

            # --------------------------------------------------
            # 4. CP2: Debug Checkpoint - before check_gen_code()
            # --------------------------------------------------
            logger.debug(f"[CP2] Current debug_mode: {debug_mode}")
            if settings.debug:
                logger.debug("[CP2] Waiting for input from the console")
                debug_mode = await wait_for_console_input()
                logger.debug(f"[CP2] Entered debug_mode: {debug_mode}")
                if debug_mode == DebugMode.END:
                    logger.debug("[CP2] Exiting loop")
                    break
                logger.debug("[CP2] Continuing to check_gen_code()")

            # ------------------------
            # 5. Call check_gen_code()
            # ------------------------
            if not debug_mode == DebugMode.SKIP_AGENT:
                logger.debug("[check_gen_code] Call check_gen_code()")
                async for line in check_gen_code(
                    request=PromptRequest(prompt=prompt), context=context
                ):
                    try:
                        data = json.loads(line)
                        logger.debug(f"[check_gen_code] Received data: {data}")
                        yield await sse_event(data["event"], data.get("payload", {}))
                    except Exception as e:
                        logger.debug(
                            f"[check_gen_code] Invalid JSON from check_gen_code: {e}"
                        )
            else:
                logger.debug("[check_gen_code] Skipping check_gen_code()")

            # ---------------------------------------------
            # 6. CP3: Debug Checkpoint - before run_build()
            # ---------------------------------------------
            logger.debug(f"[CP3] Current debug_mode: {debug_mode}")
            if settings.debug:
                logger.debug("[CP3] Waiting for input from the console")
                debug_mode = await wait_for_console_input()
                logger.debug(f"[CP3] Entered debug_mode: {debug_mode}")
                if debug_mode == DebugMode.END:
                    logger.debug("[CP3] Exiting loop")
                    break
                logger.debug("[CP3] Continuing to run_build()")

            # ------------------------------
            # 7. Loop judge (Retry decision)
            # ------------------------------
            logger.debug(f"[Loop] Current debug_mode: {debug_mode}")
            logger.debug(
                f"[Loop] context.is_retry_gen_code: {context.is_retry_gen_code}"
            )
            if context.is_retry_gen_code:
                if not debug_mode == DebugMode.BYPASS:
                    logger.debug("[Loop] Retry code generation")
                    continue

            # -------------------
            # 8. Call run_build()
            # -------------------
            logger.debug("[run_build] Call run_build()")
            build_result = await run_build(context, settings)
            logger.debug(f"[run_build] build_result: {build_result}")
            if not build_result.result:
                if build_result.abort_flg:
                    logger.error(f"[run_build] Build failed: {build_result.detail}")
                    final_payload = DonePayload(
                        status=DoneStatus.FAILED, message="Build failed"
                    )
                    break
                else:
                    build_check_payload = {
                        "checker": "Build",
                        "result": False,
                        "rule_id": "npm run build",
                        "detail": build_result.detail,
                    }
                    yield await sse_event(EventType.CHECK_RESULT, build_check_payload)
                    logger.debug("[run_build] call create_prompt_for_builderror()")
                    re_prompt = create_prompt_for_builderror()
                    logger.debug(f"[run_build] re_prompt: {re_prompt}")
            else:
                build_check_payload = {
                    "checker": "Build",
                    "result": True,
                    "rule_id": "",
                    "detail": "",
                }
                logger.debug("[run_build] Build succeeded")
                yield await sse_event(EventType.CHECK_RESULT, build_check_payload)
                break

            # --------------------
            # 9. Retry limit check
            # --------------------
            logger.debug(
                f"[retry limit check] i={i} settings.code_gen_retry={settings.code_gen_retry}"
            )
            if i == settings.code_gen_retry - 1:
                logger.error("[retry limit check] Retry limit exceeded")
                final_payload = DonePayload(
                    status=DoneStatus.FAILED, message="Retry Limit exceeded"
                )

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        error_payload = SystemError(error="Unexpected error", detail=str(e))
        yield await sse_event(EventType.SYSTEM_ERROR, error_payload.model_dump())
        final_payload = DonePayload(
            status=DoneStatus.FAILED, message="unexpected error occurred"
        )

    # Done
    logger.info(f"[{category}]: All Tasks Completed")
    yield await sse_event(EventType.DONE, final_payload.model_dump())
