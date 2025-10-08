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
function isAgentResultEvent(
  event: StreamResponse
): event is Extract<StreamResponse, { event: typeof EventTypes.AGENT_RESULT }> {
  return event.event === EventTypes.AGENT_RESULT;
}
function isTestResultEvent(
  event: StreamResponse
): event is Extract<StreamResponse, { event: typeof EventTypes.TEST_RESULT }> {
  return event.event === EventTypes.TEST_RESULT;
}
function isSystemErrorEvent(
  event: StreamResponse
): event is Extract<StreamResponse, { event: typeof EventTypes.SYSTEM_ERROR }> {
  return event.event === EventTypes.SYSTEM_ERROR;
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

            // ----- agent_result event -----
            if (isAgentResultEvent(sr)) {
              const result = sr.payload.result;
              const resultStr = result ? "OK" : "Error";
              const error_detail = sr.payload.error_detail;
              return (
                <div key={`agent-result-${idx}`}>
                  <span className="text-sm pl-2">
                    {result ? (
                      <>
                        <span>result: </span>
                        <span className="text-blue-500">{resultStr}</span>
                      </>
                    ) : (
                      <>
                        <span>result: </span>
                        <span className="text-red-500">{resultStr}</span>
                        <div className="text-sm pl-4">
                          detail: {error_detail}
                        </div>
                      </>
                    )}
                  </span>
                </div>
              );
            }

            // ----- test_result event -----
            if (isTestResultEvent(sr)) {
              const payload = sr.payload;
              const { result, detail, name, file, total, ok, ng, specs } =
                payload;
              const resultStr = result ? "OK" : "Error";
              return (
                <div key={`test-result-${idx}`}>
                  <span className="text-sm pl-2">
                    check:{" "}
                    {result ? (
                      <>
                        <span className="text-blue-500">{resultStr}</span>
                      </>
                    ) : (
                      <>
                        <span className="text-red-500">{resultStr}</span>
                      </>
                    )}
                    <div className="text-sm pl-4">
                      <span>
                        Total:{total}, OK:{ok}, NG:{ng}
                      </span>
                      <div>Name: {name}</div>
                      <div>File: {file}</div>
                      <div>Error detail: {detail}</div>
                      {specs && specs.length > 0 && (
                        <div className="mt-1">
                          <div className="font-semibold">Test Specs:</div>
                          <ul className="pl-4 list-disc">
                            {specs.map((spec, sIdx) => (
                              <li
                                key={`spec-${idx}-${sIdx}`}
                                className="text-sm"
                              >
                                <div>
                                  <span>Title:</span>
                                  {spec.title}
                                </div>
                                <div>
                                  Result:{" "}
                                  {spec.result ? (
                                    <span className="text-blue-500">OK</span>
                                  ) : (
                                    <span className="text-red-500">NG</span>
                                  )}
                                </div>
                                {!spec.result && (
                                  <div className="pl-4 text-gray-500">
                                    {spec.error_summary && (
                                      <div>Summary: {spec.error_summary}</div>
                                    )}
                                    {spec.error_message && (
                                      <div>Message: {spec.error_message}</div>
                                    )}
                                  </div>
                                )}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </span>
                </div>
              );
            }

            // ----- system-error event -----
            if (isSystemErrorEvent(sr)) {
              const error = sr.payload.error;
              const detail = sr.payload.detail;
              return (
                <div key={`system-error-${idx}`}>
                  <div className="text-sm pl-2">
                    <div>{error}</div>
                    <div>{detail}</div>
                  </div>
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
