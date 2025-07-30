import { ResponseInfo } from "./types";

interface StreamEventProps {
  status: string;
  responseInfo: ResponseInfo;
}

const StreamEvent = ({ status, responseInfo }: StreamEventProps) => {
  // --- started ---
  const startedEvent = responseInfo?.r_event.find(
    (ev) => ev.s_res.event === "started"
  );
  const startedMessage =
    startedEvent && startedEvent.s_res.event === "started"
      ? startedEvent.s_res.payload.message
      : "";
  const startedTime =
    startedEvent && startedEvent.s_res.event === "started"
      ? startedEvent.r_time.toLocaleString()
      : "";

  // --- agent update ---
  const updateEvent = responseInfo?.r_event.find(
    (ev) => ev.s_res.event === "agent_update"
  );
  const updateMessage =
    updateEvent && updateEvent.s_res.event === "agent_update"
      ? updateEvent.s_res.payload.agent_name
      : "";
  const updateTime =
    updateEvent && updateEvent.s_res.event === "agent_update"
      ? updateEvent.r_time.toLocaleString()
      : "";

  // --- done ---
  const doneEvent = responseInfo?.r_event.find(
    (ev) => ev.s_res.event === "done"
  );
  const doneMessage =
    doneEvent && doneEvent.s_res.event === "done"
      ? doneEvent.s_res.payload.message
      : "";
  const doneTime =
    doneEvent && doneEvent.s_res.event === "done"
      ? doneEvent.r_time.toLocaleString()
      : "";

  return (
    <div>
      {(status === "Sended" || status === "Done") && (
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
          <div className="col-span-2 text-sm text-gray-500">{startedTime}</div>

          {/* --- agent update ---*/}
          {/* column-A */}
          <div></div>
          {/* column-B,C,D */}
          {updateMessage && (
            <div className="col-span-3 text-base">
              <span className="text-[12px] pr-2">&#x1F7E2;</span>
              {updateMessage}
            </div>
          )}
          {/* column-E,F */}
          <div className="col-span-2 text-sm text-gray-500">{updateTime}</div>

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
      )}
    </div>
  );
};

export default StreamEvent;
