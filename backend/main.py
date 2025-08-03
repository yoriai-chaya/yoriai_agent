from typing import Any

from agents import Runner
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai.types.responses import ResponseTextDeltaEvent
from pydantic import BaseModel

from config import get_settings
from custom_agents import LocalContext, code_gen_agent
from logger import logger


# Model Definition
class PromptRequest(BaseModel):
    prompt: str


class PromptResponse(BaseModel):
    prompt: str


class StreamResponse(BaseModel):
    event: str
    payload: dict[str, Any]

    def to_json_line(self) -> str:
        return self.model_dump_json() + "\n"


# Constant Difinitions
CATEGORY_CODEGEN = "CodeGen"

# Settings
settings = get_settings()

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


# Main Service
@app.post("/main", response_model=PromptRequest)
async def stream_service_post(request: PromptRequest):
    logger.info(f"[Main] request: {request}")

    context = LocalContext(category=CATEGORY_CODEGEN, output_dir=settings.output_dir)

    async def generator():
        result = Runner.run_streamed(
            starting_agent=code_gen_agent, input=request.prompt, context=context
        )
        logger.debug("Agents starting ...")
        yield StreamResponse(
            event="started", payload={"message": "Started Tasks"}
        ).to_json_line()

        async for event in result.stream_events():
            if event.type == "raw_response_event":
                if isinstance(event.data, ResponseTextDeltaEvent):
                    # print(f"token: {event.data.delta}")
                    # delta_text = event.data.delta
                    # yield delta_text
                    pass
            elif event.type == "agent_updated_stream_event":
                logger.debug(f"Agent updated: {event.new_agent.name}")
                agent_name = event.new_agent.name
                yield StreamResponse(
                    event="agent_update", payload={"agent_name": agent_name}
                ).to_json_line()
            elif event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item":
                    logger.debug("Event: tool_call_item")
                elif event.item.type == "tool_call_output_item":
                    logger.debug(f"Event: tool_call_output_item : {event.item.output}")
                elif event.item.type == "message_output_item":
                    logger.debug("Event: message_output_item")
                    logger.debug(f"context code: {context.response.code}")
                    yield StreamResponse(
                        event="code",
                        payload={"language": "tsx", "code": context.response.code},
                    ).to_json_line()
                else:
                    pass

        logger.debug("All Tasks Completed")
        yield StreamResponse(
            event="done", payload={"message": "All Tasks Completed"}
        ).to_json_line()

    return StreamingResponse(content=generator(), media_type="text/event-stream")
