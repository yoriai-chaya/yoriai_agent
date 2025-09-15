import asyncio
import json
import re
from pathlib import Path
from typing import Dict
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from base import (
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
from config import get_settings
from gen_code_handler import handle_gen_code
from logger import logger
from place_files_handler import handle_place_files
from prompt_parser import extract_from_prompt


# Internal Functions
def _resolve_path(path_str: str) -> Path:
    logger.debug(f"_resolve_path called: {path_str}")
    p = Path(path_str)
    if p.is_absolute():
        # Absolute path
        if not p.exists():
            raise FileNotFoundError(f"Path '{path_str}' not found")
        logger.debug(f"Absolute path resolved: {p}")
        return p
    # Relative path
    base = Path().resolve()
    logger.debug(f"base: {base}")
    abs_path = (base / p).resolve()
    logger.debug(f"abs_path: {abs_path}")
    if not abs_path.exists():
        raise FileNotFoundError(f"Path '{abs_path}' not found")
    return abs_path


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
    logger.info(f"[Main] create session request: {request}")
    session_id = str(uuid4())
    sessions[session_id] = request.prompt
    logger.debug(f"session_id: {session_id}")
    return JSONResponse({"session_id": session_id})


# for Debug
async def wait_for_console_input() -> bool:
    loop = asyncio.get_event_loop()
    user_input = await loop.run_in_executor(
        None, input, 'Press Enter "y" to continue: '
    )
    return user_input.strip().lower() == "y"


# Main Service
@app.get("/main/stream/{session_id}")
async def stream_service_get(session_id: str):
    logger.info("[Main] stream_service_get called")
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="session not found")

    prompt = sessions.pop(session_id)
    category = extract_from_prompt(prompt, PromptHeaderKey.CATEGORY)

    async def sse_event(event_name: str, payload: dict) -> str:
        return (
            f"event: {event_name}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
        )

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
        started_payload = StartedPayload(
            status=StartedStatus.STARTED, message="Started Tasks"
        )
        yield await sse_event(EventType.STARTED, started_payload.model_dump())

        if not category:
            error_payload = SystemError(
                error="InvalidPrompt", detail="Category not found"
            )
            yield await sse_event(EventType.SYSTEM_ERROR, error_payload.model_dump())
            final_payload = DonePayload(
                status=DoneStatus.FAILED, message="Invalid prompt"
            )
            yield await sse_event(EventType.DONE, final_payload.model_dump())
            return

        try:
            output_dir = _resolve_path(settings.output_dir)
        except Exception as e:
            error_payload = SystemError(error="Resolve path error", detail=str(e))
            yield await sse_event(EventType.SYSTEM_ERROR, error_payload.model_dump())
            final_payload = DonePayload(status=DoneStatus.FAILED, message="Path error")
            yield await sse_event(EventType.DONE, final_payload.model_dump())
            return
        logger.debug(f"output_dir: {output_dir}")

        context = LocalContext(
            category=category,
            output_dir=output_dir,
            max_turns=settings.openai_max_turns,
            gen_code_filepath="",
            is_retry_gen_code=True,
            add_prompts=[],
        )

        try:
            resolved_prompt = _resolve_placeholders(prompt=prompt, context=context)
        except Exception as e:
            error_payload = SystemError(error="InvalidPrompt", detail=str(e))
            yield await sse_event(EventType.SYSTEM_ERROR, error_payload.model_dump())
            final_payload = DonePayload(
                status=DoneStatus.FAILED, message="Invalid prompt"
            )
            yield await sse_event(EventType.DONE, final_payload.model_dump())
            return

        handler_map = {
            PromptCategory.GEN_CODE: handle_gen_code,
            PromptCategory.PLACE_FILES: handle_place_files,
        }

        handler = handler_map.get(category)  # type: ignore
        if not handler:
            error_payload = SystemError(
                error="InvalidCategory", detail=f"Unknown category: {category}"
            )
            yield await sse_event(EventType.SYSTEM_ERROR, error_payload.model_dump())
            final_payload = DonePayload(
                status=DoneStatus.FAILED, message="Invalid category"
            )
            yield await sse_event(EventType.DONE, final_payload.model_dump())
            return

        logger.debug(f"handler call: resolved_prompt: {resolved_prompt}")
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
