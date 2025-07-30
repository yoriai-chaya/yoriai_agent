"use client";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";
import StreamEvent from "./StreamEvent";
import { Action, FileInfo, PromptRequest } from "./types";
import { ResponseInfo, StreamResponse } from "./types";

interface QAProps {
  status: string;
  index: number;
  dispatch: React.Dispatch<Action>;
  fileInfo: FileInfo;
  setResponseInfo: React.Dispatch<React.SetStateAction<ResponseInfo[]>>;
  responseInfo: ResponseInfo;
}

const QA = ({
  status,
  index,
  dispatch,
  fileInfo,
  setResponseInfo,
  responseInfo,
}: QAProps) => {
  const sendPrompt = async () => {
    console.log("sendPrompt called");
    const requestBody: PromptRequest = { prompt: fileInfo.content };
    try {
      const response = await fetch("http://localhost:8000/main", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });
      if (!response.body) {
        console.log("fetch response error");
        return;
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let partial = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          dispatch({ type: "DONE", index });
          break;
        }

        partial += decoder.decode(value, { stream: true });
        const lines = partial.split("\n");
        partial = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.trim()) continue;

          try {
            const data: StreamResponse = JSON.parse(line.trim());
            switch (data.event) {
              case "started":
                console.log(`Started: ${data.payload.message}`);
                dispatch({ type: "SEND_PROMPT", index });
                const event_time = new Date();
                setResponseInfo((prev) => {
                  const updated = [...prev];
                  updated[index] = {
                    r_event: [{ s_res: data, r_time: event_time }],
                  };
                  return updated;
                });
                break;
              case "agent_update":
                console.log(`Agent updated to ${data.payload.agent_name}`);
                const update_time = new Date();
                setResponseInfo((prev) => {
                  const updated = [...prev];
                  const prevEvents = updated[index]?.r_event ?? [];
                  updated[index] = {
                    r_event: [
                      ...prevEvents,
                      { s_res: data, r_time: update_time },
                    ],
                  };
                  return updated;
                });
                break;
              case "code":
                console.log(`code: `);
                const code_time = new Date();
                setResponseInfo((prev) => {
                  const updated = [...prev];
                  const prevEvents = updated[index]?.r_event ?? [];
                  updated[index] = {
                    r_event: [
                      ...prevEvents,
                      { s_res: data, r_time: code_time },
                    ],
                  };
                  return updated;
                });
                break;
              case "done":
                console.log(`Done: ${data.payload.message}`);
                const done_time = new Date();
                setResponseInfo((prev) => {
                  const updated = [...prev];
                  const prevEvents = updated[index]?.r_event ?? [];
                  updated[index] = {
                    r_event: [
                      ...prevEvents,
                      { s_res: data, r_time: done_time },
                    ],
                  };
                  return updated;
                });
                break;
            }
          } catch (e) {
            console.log("Failed to parse stream line", line, e);
          }
        }
      }
    } catch (error) {
      console.log("Error sending: ", error);
    }
  };

  return (
    <div className="space-y-2 mb-4">
      {(status === "Loaded" || status === "Sended" || status === "Done") && (
        <div className="grid grid-cols-6 items-center">
          {/* --- filename row --- */}
          {/* column-A */}
          <div></div>
          {/* column-B */}
          <div className="text-gray-500 text-sm">filename:</div>
          {/* column-C,D,E */}
          <div className="col-span-3 text-sm">{fileInfo.filename}</div>
          {/* column-F */}
          <div className="col-span-1 row-span-2">
            <Button
              onClick={sendPrompt}
              disabled={status === "Sended" || status === "Done"}
            >
              <Send className="w-4 h-4 mr-2" />
            </Button>
          </div>
          {/* --- mtime row --- */}
          {/* column-A */}
          <div></div>
          {/* column-B */}
          <div className="text-gray-500 text-sm">mtime:</div>
          {/* column-C,D,E */}
          <div className="col-span-3 text-sm">
            {fileInfo.mtime.toLocaleString()}
          </div>
          {/* column-F */}
          <div></div>
        </div>
      )}
      {(status === "Sended" || status === "Done") && (
        <div className="grid grid-cols-6 items-center">
          {/* --- avatar row --- */}
          {/* column-A */}
          <div>
            <Avatar>
              <AvatarImage src="/assistant.png" />
              <AvatarFallback>As</AvatarFallback>
            </Avatar>
          </div>
          {/* column-B */}
          <span>Assistant</span>
          {/* column-C,D,E,F */}
          <div className="col-span-4"></div>

          {/* --- StreamEvent rows --- */}
          <div className="col-span-6">
            <StreamEvent status={status} responseInfo={responseInfo} />
          </div>
        </div>
      )}
    </div>
  );
};

export default QA;
