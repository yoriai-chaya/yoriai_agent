import asyncio
import json
from typing import Dict
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from base import EventType, LocalContext, PromptRequest, PromptResponse
from check_code import check_gen_code
from config import get_settings
from create_code import gen_code
from logger import logger

# Constant Difinitions
CATEGORY_CODEGEN = "CodeGen"

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
    context = LocalContext(
        category=CATEGORY_CODEGEN, output_dir=settings.output_dir, gen_code_filepath=""
    )

    async def sse_event(event_name: str, payload: dict) -> str:
        return (
            f"event: {event_name}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
        )

    async def generator():
        # Heartbeat
        async def heartbeat():
            while True:
                yield ": keep-alive\n\n"  # SSE Comment Frame
                await asyncio.sleep(15)

        hb = heartbeat()
        yield await hb.__anext__()

        # Start
        logger.debug("Agents starting ...")
        yield await sse_event(EventType.STARTED, {"message": "Started Tasks"})

        # Create Code
        async for line in gen_code(
            request=PromptRequest(prompt=prompt), context=context
        ):
            try:
                data = json.loads(line)
                yield await sse_event(data["event"], data.get("payload", {}))
            except Exception as e:
                logger.debug(f"Invalid JSON from gen_code: {e}")

        # Wait for console input (for debug)
        if settings.debug:
            logger.debug("[debug] stop")
            await wait_for_console_input()
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

        # Done
        yield await sse_event(EventType.DONE, {"message": "All Tasks Completed"})

        logger.debug("All Tasks Completed")

    headers = {
        "Cache-Control": "no-cache, no-transform",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*",
    }
    return StreamingResponse(
        content=generator(), media_type="text/event-stream", headers=headers
    )
