import { ResponseInfo, EventTypes, StreamResponse } from "./types";
import { formatDateTime } from "./util";

interface StreamEventProps {
  status: string;
  responseInfo: ResponseInfo;
}

// Type Guard Function
function isStartedEvent(
  event: StreamResponse
): event is Extract<StreamResponse, { event: typeof EventTypes.STARTED }> {
  return event.event === EventTypes.STARTED;
}
function isUpdateEvent(
  event: StreamResponse
): event is Extract<StreamResponse, { event: typeof EventTypes.AGENT_UPDATE }> {
  return event.event === EventTypes.AGENT_UPDATE;
}
function isDoneEvent(
  event: StreamResponse
): event is Extract<StreamResponse, { event: typeof EventTypes.DONE }> {
  return event.event === EventTypes.DONE;
}

const StreamEvent = ({ status, responseInfo }: StreamEventProps) => {
  // --- started ---
  const startedEvent = responseInfo?.r_event.find((ev) =>
    isStartedEvent(ev.s_res)
  );
  const startedMessage =
    startedEvent && isStartedEvent(startedEvent.s_res)
      ? startedEvent.s_res.payload.message
      : "";
  const startedTime = startedEvent ? formatDateTime(startedEvent.r_time) : "";

  // --- agent update ---
  const agentUpdates = responseInfo.r_event.filter((event) =>
    isUpdateEvent(event.s_res)
  );
  if (agentUpdates.length === 0) {
    return null;
  }

  // --- done ---
  const doneEvent = responseInfo?.r_event.find((ev) => isDoneEvent(ev.s_res));
  const doneMessage =
    doneEvent && isDoneEvent(doneEvent.s_res)
      ? doneEvent.s_res.payload.message
      : "";
  const doneTime = doneEvent ? formatDateTime(doneEvent.r_time) : "";

  return (
    <div>
      {(status === "Sended" || status === "Done") && (
        <div>
          <div className="grid grid-cols-6 items-center">
            {/* --- started ---*/}
            {/* column-A */}
            <div></div>
            {/* column-B,C,D */}
            {startedMessage && (
              <div className="col-span-3 text-base">
                <span className="text-[12px] pr-2">&#x1F535;</span>
                {startedMessage}
              </div>
            )}
            {/* column-E,F */}
            <div className="col-span-2 text-sm text-gray-500">
              {startedTime}
            </div>
          </div>

          {agentUpdates.map((event, index) => {
            if (!isUpdateEvent(event.s_res)) return null;
            return (
              <div key={index}>
                <div className="grid grid-cols-6 items-center">
                  <div></div>
                  <div className="col-span-3 text-base">
                    <span className="text-[12px] pr-2">&#x1F7E2;</span>
                    {event.s_res.payload.agent_name}
                  </div>
                  <div className="col-span-2 text-sm text-gray-500">
                    {formatDateTime(event.r_time)}
                  </div>
                </div>
              </div>
            );
          })}
          <div className="grid grid-cols-6 items-center">
            {/* --- done ---*/}
            {/* column-A */}
            <div></div>
            {/* column-B,C,D */}
            {doneMessage && (
              <div className="col-span-3 text-base">
                <span className="text-[12px] pr-2">&#x1F535;</span>
                {doneMessage}
              </div>
            )}
            {/* column-E,F */}
            <div className="col-span-2 text-sm text-gray-500">{doneTime}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StreamEvent;
