import {
  ResponseInfo,
  EventTypes,
  StreamResponse,
  CheckResultItem,
  Emoji,
} from "./types";
import { formatDateTime } from "./util";
import CheckResult from "./CheckResult";

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
function isCheckResultEvent(
  event: StreamResponse
): event is Extract<StreamResponse, { event: typeof EventTypes.CHECK_RESULT }> {
  return event.event === EventTypes.CHECK_RESULT;
}

const StreamEvent = ({ status, responseInfo }: StreamEventProps) => {
  const events = responseInfo?.r_event ?? [];

  // --- started ---
  const startedEvent = events.find((ev) => isStartedEvent(ev.s_res));
  const startedMessage =
    startedEvent && isStartedEvent(startedEvent.s_res)
      ? startedEvent.s_res.payload.message
      : "";
  const startedTime = startedEvent ? formatDateTime(startedEvent.r_time) : "";

  // --- agent_update ---
  const agentUpdates = events.filter((event) => isUpdateEvent(event.s_res));

  // --- check_result ---
  const checkResults = events.filter((event): event is CheckResultItem =>
    isCheckResultEvent(event.s_res)
  );
  console.log(`checkResults: ${JSON.stringify(checkResults, null, 2)}`);

  // --- done ---
  const doneEvent = events.find((ev) => isDoneEvent(ev.s_res));
  const doneMessage =
    doneEvent && isDoneEvent(doneEvent.s_res)
      ? doneEvent.s_res.payload.message
      : "";
  const doneTime = doneEvent ? formatDateTime(doneEvent.r_time) : "";

  return (
    <div>
      {(status === "Sended" || status === "Done") && (
        <div>
          {/* ----- started event ----- */}
          <div className="grid grid-cols-6 items-center">
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

          {/* ----- agent_update event ----- */}
          {agentUpdates.map((event, index) => {
            if (!isUpdateEvent(event.s_res)) return null;
            const agentName = event.s_res.payload.agent_name;
            const isCodeCheckAgent = agentName === "CodeCheckAgent";
            let agentEmoji = Emoji.GREEN_CIRCLE;
            if (isCodeCheckAgent) {
              agentEmoji = Emoji.WHITE_CIRCLE;
              if (checkResults.length > 0) {
                const checkResult = checkResults[0].s_res.payload.result;
                console.log(`*** checkResult: ${checkResult}`);
                agentEmoji = checkResult ? Emoji.BLUE_CIRCLE : Emoji.RED_CIRCLE;
              }
            }
            return (
              <div key={index}>
                <div className="grid grid-cols-6 items-center">
                  <div></div>
                  <div className="col-span-3 text-base">
                    <span className="text-[12px] pr-2">{agentEmoji}</span>
                    {agentName}
                  </div>
                  <div className="col-span-2 text-sm text-gray-500">
                    {formatDateTime(event.r_time)}
                  </div>
                </div>
                <div className="grid grid-cols-6 items-center">
                  <div></div>
                  {/* ----- check_result event ----- */}
                  <div className="col-span-5 text-base">
                    {isCodeCheckAgent && (
                      <CheckResult checkResults={checkResults} />
                    )}
                  </div>
                </div>
              </div>
            );
          })}

          {/* ----- done event ----- */}
          <div className="grid grid-cols-6 items-center">
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
