from agents import ItemHelpers, Runner

from base import (
    AgentResult,
    AgentResultPayload,
    AgentUpdatePayload,
    DonePayload,
    DoneStatus,
    EventType,
)
from custom_agents import place_files_agent
from logger import logger


async def handle_place_files(
    prompt: str, context, settings, sse_event, wait_for_console_input
):
    logger.info("PlaceFiles handler called")

    final_payload = DonePayload(
        status=DoneStatus.COMPLETED, message="PlaceFiles completed"
    )
    result = Runner.run_streamed(
        starting_agent=place_files_agent,
        input=prompt,
        context=context,
        max_turns=context.max_turns,
    )
    async for event in result.stream_events():
        if event.type == "agent_updated_stream_event":
            logger.debug(f"Agent updated: {event.new_agent.name}")
            agent_name = event.new_agent.name
            agent_update_payload = AgentUpdatePayload(agent_name=agent_name)
            yield await sse_event(
                EventType.AGENT_UPDATE, agent_update_payload.model_dump()
            )
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                logger.debug("Event: tool_call_item")
            elif event.item.type == "tool_call_output_item":
                logger.debug(f"Event: tool_call_output_item : {event.item.output}")
                output = event.item.output
                if isinstance(output, AgentResult):
                    place_files_result = output.result
                    place_files_error_detail = output.error_detail
                    logger.debug(
                        f"place_files_result: {place_files_result}, place_files_error_detail: {place_files_error_detail}"
                    )
                    if place_files_result:
                        agent_result_payload = AgentResultPayload(
                            result=True, error_detail=""
                        )
                        yield await sse_event(
                            EventType.AGENT_RESULT, agent_result_payload.model_dump()
                        )
                    else:
                        agent_result_payload = AgentResultPayload(
                            result=False, error_detail=place_files_error_detail
                        )
                        yield await sse_event(
                            EventType.AGENT_RESULT, agent_result_payload.model_dump()
                        )
                        final_payload = DonePayload(
                            status=DoneStatus.FAILED, message="PlaceFiles Failed"
                        )

            elif event.item.type == "message_output_item":
                logger.debug("Event: message_output_item")
                logger.debug(
                    f"Message Output:\n {ItemHelpers.text_message_output(event.item)}"
                )

    yield await sse_event(EventType.DONE, final_payload.model_dump())
