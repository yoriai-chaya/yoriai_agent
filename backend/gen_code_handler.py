"""
A handler for code generation, ESLint checking, and build checking

Notes:
(1)error_payload
    In the following statement:
    error_payload = SystemError(error="Unexpected error", detail=str(e))
    The error value (e.g., "Unexpected error") is displayed in the frontend UI (Left-Panel)
    Keep this error message within 20 characters.
"""

from typing import AsyncIterator, Awaitable, Callable

from base import (
    DebugMode,
    DonePayload,
    DoneStatus,
    EventType,
    LocalContext,
    LoopAction,
    SystemError,
)
from checkpoint import debug_checkpoint
from config import Settings
from logger import logger
from step_check_code import check_code_step
from step_gen_code import gen_code_step
from step_run_build import run_build_step
from step_run_rebuild import run_rebuild_step

SSEEventCallable = Callable[[str, dict], Awaitable[str]]


async def handle_gen_code(
    prompt: str,
    context: LocalContext,
    settings: Settings,
    sse_event: SSEEventCallable,
) -> AsyncIterator[str]:
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

        # Completed payload (may be overwritten)
        final_payload = DonePayload(
            status=DoneStatus.COMPLETED,
            message="All Tasks Completed",
        )

        debug_mode = DebugMode.CONTINUE
        next_prompt = prompt

        # =========================
        # Code Generation Loop
        # =========================
        success = False
        for i in range(settings.code_gen_retry):
            logger.debug(f"Code Gen Loop [{i}]")

            # -------------------------------
            # 1. Create Code (prepare prompt)
            # -------------------------------
            final_prompt = next_prompt
            add_prompts_len = len(context.add_prompts)

            logger.debug(
                f"[Prompt] Base prompt len={len(final_prompt)}, "
                f"number of additional prompts={add_prompts_len}"
            )

            if add_prompts_len != 0:
                logger.debug("[Prompt] Extending prompt with additional messages")
                for add_prompt in context.add_prompts:
                    logger.debug(f"[Prompt] Additional prompt: {add_prompt}")
                    final_prompt = f"{final_prompt}\n- {add_prompt}\n"
                    logger.debug(f"final_prompt: {final_prompt}")

            # --------------------------------------------
            # 2. CP1: Debug Checkpoint - before gen_code()
            # --------------------------------------------
            logger.debug(f"[CP1] Current debug_mode: {debug_mode}")
            if settings.debug:
                debug_mode = await debug_checkpoint(
                    cp_name="CP1",
                    current_mode=debug_mode,
                )
                if debug_mode == DebugMode.END:
                    logger.debug("[CP1] Exiting loop")
                    break

            # ------------------
            # 3. Call gen_code()
            # ------------------
            if debug_mode != DebugMode.SKIP_AGENT:
                logger.debug("gen_code_step called")
                step = await gen_code_step(
                    final_prompt=final_prompt,
                    context=context,
                )

                for ev in step.sse_events:
                    yield await sse_event(ev.event, ev.payload)

                if step.final_payload:
                    final_payload = step.final_payload

                if step.action == LoopAction.CONTINUE:
                    continue
                if step.action == LoopAction.BREAK:
                    break
            else:
                logger.debug("[gen_code] Skipping gen_code()")

            # --------------------------------------------------
            # 4. CP2: Debug Checkpoint - before check_gen_code()
            # --------------------------------------------------
            logger.debug(f"[CP2] Current debug_mode: {debug_mode}")
            if settings.debug:
                debug_mode = await debug_checkpoint(
                    cp_name="CP2",
                    current_mode=debug_mode,
                )
                if debug_mode == DebugMode.END:
                    logger.debug("[CP2] Exiting loop")
                    break

            # ------------------------
            # 5. Call check_gen_code()
            # ------------------------
            if debug_mode != DebugMode.SKIP_AGENT:
                logger.debug("check_code_step called")
                step = await check_code_step(
                    prompt=prompt,
                    context=context,
                )

                for ev in step.sse_events:
                    yield await sse_event(ev.event, ev.payload)

                if step.action == LoopAction.CONTINUE:
                    continue
                if step.action == LoopAction.BREAK:
                    success = True
                    break
            else:
                logger.debug("[check_gen_code] Skipping check_gen_code()")

        # ---------------------------------------------
        # 6. Retry Limit Check
        # ---------------------------------------------
        if not success:
            logger.error("[retry limit check] Retry limit exceeded")
            final_payload = DonePayload(
                status=DoneStatus.FAILED,
                message="Retry Limit exceeded",
            )
            yield await sse_event(EventType.DONE, final_payload.model_dump())
            return

        # ---------------------------------------------
        # 7. CP3: Debug Checkpoint - before run_build()
        # ---------------------------------------------
        logger.debug(f"[CP3] Current debug_mode: {debug_mode}")
        if settings.debug:
            debug_mode = await debug_checkpoint(
                cp_name="CP3",
                current_mode=debug_mode,
                context=context,
            )

        # -------------------
        # 8. Call run_build()
        # -------------------
        logger.debug(f"[run_build] context.build_check: {context.build_check}")
        rebuild_flg = False
        if context.build_check and debug_mode != DebugMode.SKIP_AGENT:
            logger.debug("run_build_step called")
            step_result = await run_build_step(
                context=context,
                settings=settings,
            )

            for ev in step_result.sse_events:
                yield await sse_event(ev.event, ev.payload)

            if step_result.final_payload:
                final_payload = step_result.final_payload

            if step_result.result is not None:
                if step_result.result.abort_flg:
                    yield await sse_event(
                        EventType.DONE,
                        final_payload.model_dump(),
                    )
                    return

            if step_result.result is not None:
                rebuild_flg = True

        # ---------------------
        # 9. Call run_rebuild()
        # ---------------------
        build_result = step_result.result
        if rebuild_flg:
            if (
                build_result is not None
                and context.build_check
                and debug_mode != DebugMode.SKIP_AGENT
                and not build_result.result
            ):
                async for ev in run_rebuild_step(
                    context=context,
                    build_result=build_result,
                ):
                    yield await sse_event(ev.event, ev.payload)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        error_payload = SystemError(
            error="Unexpected error",
            detail=str(e),
        )
        yield await sse_event(
            EventType.SYSTEM_ERROR,
            error_payload.model_dump(),
        )
        final_payload = DonePayload(
            status=DoneStatus.FAILED,
            message="unexpected error occurred",
        )

    # =========================
    # Done
    # =========================
    logger.info(f"[{category}]: All Tasks Completed")
    yield await sse_event(
        EventType.DONE,
        final_payload.model_dump(),
    )
