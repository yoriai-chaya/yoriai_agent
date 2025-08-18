from agents import Runner
from openai.types.responses import ResponseTextDeltaEvent

from base import EventType, LocalContext, PromptRequest, StreamResponse
from custom_agents import code_gen_agent
from logger import logger


async def gen_code(request: PromptRequest, context: LocalContext):
    logger.debug("gen_code called")
    result = Runner.run_streamed(
        starting_agent=code_gen_agent, input=request.prompt, context=context
    )
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
                event=EventType.AGENT_UPDATE, payload={"agent_name": agent_name}
            ).to_json_line()
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                logger.debug("Event: tool_call_item")
            elif event.item.type == "tool_call_output_item":
                logger.debug(f"Event: tool_call_output_item : {event.item.output}")
            elif event.item.type == "message_output_item":
                logger.debug("Event: message_output_item")
                if context.response:
                    # logger.debug(f"context code: {context.response.code}")
                    yield StreamResponse(
                        event=EventType.CODE,
                        payload={
                            "language": "tsx",
                            "code": context.response.code,
                            "file_path": context.gen_code_filepath,
                        },
                    ).to_json_line()
            else:
                pass
