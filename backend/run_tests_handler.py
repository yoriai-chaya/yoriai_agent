from agents import Runner

from agent_logger import AgentLogger
from base import (
    AgentUpdatePayload,
    DonePayload,
    DoneStatus,
    EventType,
    SystemError,
)
from custom_agents import run_tests_agent
from eval_tests import eval_test_results
from logger import logger


async def handler_run_tests(
    prompt: str, context, settings, sse_event, wait_for_console_input
):
    category = context.category
    logger.info(f"[{category}] : Run Tests Handler started")

    final_payload = DonePayload(
        status=DoneStatus.COMPLETED, message="RunTests completed"
    )

    try:
        result = Runner.run_streamed(
            starting_agent=run_tests_agent,
            input=prompt,
            context=context,
            max_turns=context.max_turns,
            hooks=AgentLogger(),
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
                    logger.debug("Event: tool_call_output_item")
                elif event.item.type == "message_output_item":
                    logger.debug("Event: message_output_item")

        final = result.final_output
        logger.trace(f"final: {final}")

        # Evaluate
        test_results = eval_test_results(context=context)
        logger.trace(f"test_results: {test_results}")
        yield await sse_event(EventType.TEST_RESULT, test_results.model_dump())

        if not final.result:
            final_payload = DonePayload(
                status=DoneStatus.FAILED, message="RunTests failed"
            )

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.debug(f"name: {e.__class__.__name__}, detail: {str(e)}")
        error_payload = SystemError(error="Unexpected error", detail=str(e))
        yield await sse_event(EventType.SYSTEM_ERROR, error_payload.model_dump())
        final_payload = DonePayload(
            status=DoneStatus.FAILED, message="run tests code error occurred"
        )

    logger.info(f"[{category}] : Run Tests Handler completed")
    yield await sse_event(EventType.DONE, final_payload.model_dump())
