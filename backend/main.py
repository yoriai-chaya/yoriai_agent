import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from base import (
    DebugMode,
    DonePayload,
    DoneStatus,
    EventType,
    LocalContext,
    PromptCategory,
    PromptHeaderKey,
    PromptRequest,
    PromptResponse,
    StartedPayload,
    StartedStatus,
    SystemError,
)
from common import resolve_path
from config import get_settings
from gen_code_handler import handle_gen_code
from logger import logger
from place_files_handler import handle_place_files
from prompt_parser import extract_from_prompt
from run_tests_handler import handler_run_tests


# Internal Functions
def _resolve_placeholders(prompt: str, context: LocalContext) -> str:
    def replacer(match):
        logger.debug("replacer called")
        file_path = match.group(1).strip()
        logger.debug(f"file_path: {file_path}")
        full_path = context.output_dir / file_path
        logger.debug(f"full_path: {full_path}")
        try:
            content = Path(str(full_path)).read_text(encoding="utf-8")
            return f"[{file_path}]\n```{Path(file_path).suffix.lstrip('.')}\n{content}\n```"
        except FileNotFoundError as e:
            raise e

    filled = re.sub(r"\{\{file:(.+?)\}\}", replacer, prompt)
    return filled


async def sse_event(event_name: str, payload: dict) -> str:
    return f"event: {event_name}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def sse_system_error(error: str, detail: str, sse_event):
    error_payload = SystemError(error=error, detail=detail)
    return await sse_event(EventType.SYSTEM_ERROR, error_payload.model_dump())


async def sse_failed_done(message: str, sse_event):
    fainal_payload = DonePayload(status=DoneStatus.FAILED, message=message)
    return await sse_event(EventType.DONE, fainal_payload.model_dump())


# Settings
settings = get_settings()

# Session Store
sessions: Dict[str, str] = {}

# FastAPI Main
logger.info("Yori-AI start")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# FastAPI Starter
@app.get("/")
async def root():
    logger.info("[Hello]")
    return {"message": "Hello World"}


# Echo Service (for test)
@app.post("/prompt", response_model=PromptRequest)
async def prompt_service(request: PromptRequest):
    logger.info(f"[Echo] request: {request}")
    return PromptResponse(prompt=request.prompt)


# Create Session
@app.post("/main")
async def create_session(request: PromptRequest):
    logger.trace(f"create session request: {request}")
    session_id = str(uuid4())
    sessions[session_id] = request.prompt
    logger.debug(f"session_id: {session_id}")
    return JSONResponse({"session_id": session_id})


# for Debug
async def wait_for_console_input() -> DebugMode:
    loop = asyncio.get_event_loop()
    prompt = 'Enter cmd - "e":end, "s":skip agent, "c": continue, "b": bypass: '
    user_input = await loop.run_in_executor(None, input, prompt)
    cmd = user_input.strip().lower()
    for mode in DebugMode:
        if cmd == mode.value:
            return mode
    return DebugMode.END


# Main Service
@app.get("/main/stream/{session_id}")
async def stream_service_get(session_id: str):
    logger.debug("stream_service_get called")
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="session not found")

    prompt = sessions.pop(session_id)
    category = extract_from_prompt(prompt, PromptHeaderKey.CATEGORY)

    async def generator(prompt: str):
        # Heartbeat
        async def heartbeat():
            while True:
                yield ": keep-alive\n\n"  # SSE Comment Frame
                await asyncio.sleep(15)

        hb = heartbeat()
        yield await hb.__anext__()

        # Start
        logger.debug("Agents starting ...")
        now = datetime.now()
        formatted_time = now.strftime("%Y%m%d-%H%M%S")
        step_id = f"StepID-{formatted_time}"
        started_payload = StartedPayload(
            status=StartedStatus.STARTED, message="Started Tasks", step_id=step_id
        )
        yield await sse_event(EventType.STARTED, started_payload.model_dump())

        if not category:
            logger.error("Category not found")
            yield await sse_system_error(
                error="InvalidPrompt", detail="Category not found", sse_event=sse_event
            )
            yield await sse_failed_done("Invalid prompt", sse_event=sse_event)
            return

        try:
            output_dir = resolve_path(settings.output_dir)
        except Exception as e:
            logger.error(f"_resolve_path error: {e}")
            yield await sse_system_error(
                error="Resolve path error", detail=str(e), sse_event=sse_event
            )
            yield await sse_failed_done("Path error", sse_event=sse_event)
            return
        logger.debug(f"output_dir: {output_dir}")

        custom_config_file = output_dir / settings.playwright_customconfig_file
        if not custom_config_file.exists():
            logger.error(f"{custom_config_file} not found")
            yield await sse_system_error(
                error="Config file error",
                detail=f"{custom_config_file} not found",
                sse_event=sse_event,
            )
            yield await sse_failed_done("Config error", sse_event=sse_event)
            return

        logger.debug(f"custom_config_file: {custom_config_file}")
        try:
            with open(custom_config_file, "r") as f:
                custom_config = json.load(f)
        except Exception as e:
            logger.error(f"{custom_config_file} open failed: {e}")
            yield await sse_system_error(
                error="Config file open error",
                detail=str(e),
                sse_event=sse_event,
            )
            yield await sse_failed_done("Config file error", sse_event=sse_event)
            return

        base_url = custom_config["base_url"]
        logger.debug(f"base_url: {base_url}")
        results = custom_config["results"]
        logger.debug(f"results: {results}")
        playwright_info_file = custom_config["playwright_info_file"]
        logger.debug(f"playwright_info_file: {playwright_info_file}")
        playwright_report_file = custom_config["playwright_report_file"]
        logger.debug(f"playwright_report_file: {playwright_report_file}")
        playwright_report_summary_file = custom_config["playwright_report_summary_file"]
        logger.debug(
            f"playwright_report_summary_file: {playwright_report_summary_file}"
        )
        archive_dir = settings.archive_dir
        archive_dir.mkdir(exist_ok=True)
        abs_archive_dir = resolve_path(archive_dir)
        stepid_dir = abs_archive_dir / step_id
        try:
            stepid_dir.mkdir(exist_ok=False)
        except Exception as e:
            logger.error(f"{str(stepid_dir)} mkdir failed: {e}")
            yield await sse_system_error(
                error="archive mkdir error",
                detail=str(e),
                sse_event=sse_event,
            )
            yield await sse_failed_done("archive mkdir error", sse_event=sse_event)
            return
        context = LocalContext(
            category=category,
            output_dir=output_dir,
            max_turns=settings.openai_max_turns,
            gen_code_filepath="",
            is_retry_gen_code=True,
            add_prompts=[],
            results_dir=results,
            playwright_info_file=playwright_info_file,
            playwright_report_file=playwright_report_file,
            playwright_report_summary_file=playwright_report_summary_file,
            test_file="dummy.spec.ts",
            before_mtime=0,
            step_id=step_id,
            stepid_dir=stepid_dir,
        )

        try:
            resolved_prompt = _resolve_placeholders(prompt=prompt, context=context)
        except Exception as e:
            logger.error("_resolve_placeholders failed")
            yield await sse_system_error(
                error="InvalidPrompt",
                detail=str(e),
                sse_event=sse_event,
            )
            yield await sse_failed_done("Invalid prompt", sse_event=sse_event)
            return

        handler_map = {
            PromptCategory.GEN_CODE: handle_gen_code,
            PromptCategory.PLACE_FILES: handle_place_files,
            PromptCategory.RUN_TESTS: handler_run_tests,
        }

        handler = handler_map.get(category)  # type: ignore
        if not handler:
            logger.error("InvalidCategory")
            yield await sse_system_error(
                error="InvalidCategory",
                detail="Unknown category: {category}",
                sse_event=sse_event,
            )
            yield await sse_failed_done("Invalid category", sse_event=sse_event)
            return

        logger.trace(f"handler call: resolved_prompt: {resolved_prompt}")
        async for event in handler(
            resolved_prompt, context, settings, sse_event, wait_for_console_input
        ):
            yield event

    headers = {
        "Cache-Control": "no-cache, no-transform",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*",
    }
    return StreamingResponse(
        content=generator(prompt=prompt),
        media_type="text/event-stream",
        headers=headers,
    )
