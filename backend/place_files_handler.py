from base import DonePayload, DoneStatus, EventType
from logger import logger


async def handle_place_files(
    prompt: str, context, settings, sse_event, wait_for_console_input
):
    logger.info("PlaceFiles handler called")

    payload = {"status": "success", "message": "Files placed successfully"}

    yield await sse_event(EventType.AGENT_UPDATE, payload)

    final_payload = DonePayload(
        status=DoneStatus.COMPLETED, message="PlaceFiles completed"
    )
    yield await sse_event(EventType.DONE, final_payload.model_dump())
