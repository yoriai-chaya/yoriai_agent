"use client";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";
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

      dispatch({ type: "SEND_PROMPT", index });

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        partial += decoder.decode(value, { stream: true });
        const lines = partial.split("\n");
        partial = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.trim()) continue;

          try {
            const data: StreamResponse = JSON.parse(line.trim());
            console.log(`data (StreamResponse): ${data}`);
            switch (data.event) {
              case "started":
                console.log(`Started: ${data.payload.message}`);
                const event_time = new Date();
                setResponseInfo((prev) => {
                  const updated = [...prev];
                  updated[index] = {
                    res_info: [data],
                    stime: stime,
                    etime: etime,
                  };
                  return updated;
                });

                break;
              case "agent_update":
                console.log(`Agent updated to ${data.payload.agent_name}`);
                break;
              case "code":
                setResponseInfo((prev) => {
                  const updated = [...prev];
                  const current = updated[index] ?? {
                    res: [],
                    stime: new Date(0),
                    etime: new Date(0),
                  };
                  updated[index] = {
                    ...current,
                    res: [...current.res, data],
                    //content: `\`\`\`${data.payload.language}\n${data.payload.code}\n\`\`\``,
                  };
                  return updated;
                });
                break;
              case "done":
                console.log(`Done: ${data.payload.message}`);
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
      {(status === "Loaded" || status === "Sended") && (
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
            <Button onClick={sendPrompt} disabled={status === "Sended"}>
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
      {status === "Sended" && (
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
          {/* --- rtime row --- */}
          {/* column-A */}
          <div></div>
          {/* column-B */}
          <div className="text-gray-500 text-sm">rtime:</div>
          {/* column-C,D,E */}
          <div className="col-span-3 text-sm">
            {responseInfo.res[0].payload.}
          </div>
          {/* column-F */}
          <div></div>
        </div>
      )}
    </div>
  );
};

export default QA;
