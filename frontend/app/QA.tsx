"use client";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";
import StreamEvent from "./StreamEvent";
import { Action, FileInfo, PromptRequest } from "./types";
import { ResponseInfo, StreamResponse, EventTypes } from "./types";
import { formatDateTime } from "./util";
import { useRef } from "react";

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
  // useRef
  const esRef = useRef<EventSource | null>(null);

  // Environments
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL;

  // setEvent
  const setEvent = (sres: StreamResponse, index: number) => {
    console.log("setEvent called");
    setResponseInfo((prev) => {
      const updated = [...prev];
      const prevEvents = updated[index]?.r_event ?? [];
      updated[index] = {
        r_event: [
          ...prevEvents,
          {
            s_res: sres,
            r_time: new Date(),
          },
        ],
      };
      return updated;
    });
  };

  // sendPrompt
  const sendPrompt = async () => {
    console.log("sendPrompt called");
    if (esRef.current) {
      // Prevent duplicate
      console.log("prevent duplicate");
      esRef.current.close();
      esRef.current = null;
    }
    try {
      // Create Session
      const requestBody: PromptRequest = { prompt: fileInfo.content };
      const res = await fetch(`${API_BASE}/main`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });
      if (!res.ok) throw new Error(`create session failed: ${res.status}`);
      const { session_id } = await res.json();
      if (!session_id) throw new Error("no session_id");
      console.log(`session_id: ${session_id}`);

      // Starting subscribing to SSE
      const url = `${API_BASE}/main/stream/${session_id}`;
      console.log("new EventSource");
      const es = new EventSource(url, { withCredentials: false });
      console.log(`es : ${es}`);

      // Listen "started"
      es.addEventListener(EventTypes.STARTED, (e) => {
        console.log("- started event -");
        const data = JSON.parse((e as MessageEvent).data);
        console.log(`data: ${JSON.stringify(data, null, 2)}`);
        console.log("dispatch send_prompt");
        dispatch({ type: "SEND_PROMPT", index });
        const sres: StreamResponse = {
          event: EventTypes.STARTED,
          payload: data,
        };
        setResponseInfo((prev) => {
          const updated = [...prev];
          updated[index] = {
            r_event: [
              {
                s_res: sres,
                r_time: new Date(),
              },
            ],
          };
          return updated;
        });
      });

      // Listen "code"
      es.addEventListener(EventTypes.CODE, (e) => {
        console.log("- code event -");
        const data = JSON.parse((e as MessageEvent).data);
        console.log(`data: ${JSON.stringify(data, null, 2)}`);
        const sres: StreamResponse = {
          event: EventTypes.CODE,
          payload: data,
        };
        setEvent(sres, index);
      });

      // Listen "agent_update"
      es.addEventListener(EventTypes.AGENT_UPDATE, (e) => {
        console.log("- agent_update event -");
        const data = JSON.parse((e as MessageEvent).data);
        console.log(`data: ${JSON.stringify(data, null, 2)}`);
        const sres: StreamResponse = {
          event: EventTypes.AGENT_UPDATE,
          payload: data,
        };
        setEvent(sres, index);
      });

      // Listen "check_result"
      es.addEventListener(EventTypes.CHECK_RESULT, (e) => {
        console.log("- check_result event -");
        const data = JSON.parse((e as MessageEvent).data);
        console.log(`data: ${JSON.stringify(data, null, 2)}`);
        const sres: StreamResponse = {
          event: EventTypes.CHECK_RESULT,
          payload: data,
        };
        setEvent(sres, index);
      });

      // Listen "done"
      es.addEventListener(EventTypes.DONE, (e) => {
        console.log("- done event -");
        const data = JSON.parse((e as MessageEvent).data);
        console.log(`data: ${JSON.stringify(data, null, 2)}`);
        const sres: StreamResponse = {
          event: EventTypes.DONE,
          payload: data,
        };
        setEvent(sres, index);

        es.close();
        esRef.current = null;
        console.log("dispatch done");
        dispatch({ type: "DONE", index });
      });
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
            {formatDateTime(fileInfo.mtime)}
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
