import { Card } from "@/components/ui/card";
import {
  ResponseEvent,
  ResponseInfo,
  EventTypes,
  StreamResponse,
} from "./types";
import Markdown from "./Markdown";

interface StreamDetailProps {
  status: string;
  responseInfo: ResponseInfo;
}

// Type Guard Function
function isCodeEvent(
  event: StreamResponse
): event is Extract<StreamResponse, { event: typeof EventTypes.CODE }> {
  return event.event === EventTypes.CODE;
}
function isUpdateEvent(
  event: StreamResponse
): event is Extract<StreamResponse, { event: typeof EventTypes.AGENT_UPDATE }> {
  return event.event === EventTypes.AGENT_UPDATE;
}
function isCheckResultEvent(
  event: StreamResponse
): event is Extract<StreamResponse, { event: typeof EventTypes.CHECK_RESULT }> {
  return event.event === EventTypes.CHECK_RESULT;
}

// StreamDetail Function
const StreamDetail = ({ status, responseInfo }: StreamDetailProps) => {
  const events = responseInfo?.r_event ?? [];
  return (
    <div>
      {(status === "Sended" || status === "Done") && (
        <div>
          <p className="text-lg my-1">Response</p>
          {events.map((ev: ResponseEvent, idx: number) => {
            const sr = ev.s_res;
            // ----- agent_update event -----
            if (isUpdateEvent(sr)) {
              const agentName = sr.payload.agent_name;
              return (
                <div key={`agent_update-${idx}`}>
                  <div className="text-sm">{agentName}</div>
                </div>
              );
            }

            // ----- code event -----
            if (isCodeEvent(sr)) {
              const code = `\`\`\`${sr.payload.language}\n${sr.payload.code}\n\`\`\``;
              const filePath = sr.payload.file_path;
              return (
                <div key={`code-${idx}`}>
                  <div className="text-sm pl-2">Filepath: {filePath}</div>
                  <Card className="my-2 p-1 bg-gray-200 rounded-sm shadow-md">
                    <div className="flex overflow-x-auto">
                      <Markdown markdown={code} />
                    </div>
                  </Card>
                </div>
              );
            }
            // ----- check_result event -----
            if (isCheckResultEvent(sr)) {
              const checker = sr.payload.checker;
              const result = sr.payload.result;
              const result_str = result ? "OK" : "Error";
              const rule_id = sr.payload.rule_id;
              const detail = sr.payload.detail;
              return (
                <div key={`check-${idx}`}>
                  <span className="text-sm pl-2">
                    {checker} check:{" "}
                    {result ? (
                      <span className="text-blue-500">{result_str}</span>
                    ) : (
                      <>
                        <span className="text-red-500">{result_str}</span>
                        <div className="text-sm pl-4">rule: {rule_id}</div>
                        <div className="text-sm pl-4">detail: {detail}</div>
                      </>
                    )}
                  </span>
                </div>
              );
            }
          })}
        </div>
      )}
    </div>
  );
};

export default StreamDetail;
