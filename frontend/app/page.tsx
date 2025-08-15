"use client";
import { useEffect, useReducer, useState, useRef } from "react";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import FileUploader from "./FileUploader";
import QA from "./QA";
import ShowPrompt from "./ShowPrompt";
import ShowResponse from "./ShowResponse";
import { State, FileInfo, ResponseInfo } from "./types";
import { reducer } from "./reducer";

const initialState: State = {
  steps: [{ status: "Unloaded" }],
};
const initialFileInfo: FileInfo[] = [
  { filename: "", content: "", mtime: new Date(0) },
];
const initialResponseInfo: ResponseInfo[] = [];

export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const [fileInfo, setFileInfo] = useState<FileInfo[]>(initialFileInfo);
  const [responseInfo, setResponseInfo] =
    useState<ResponseInfo[]>(initialResponseInfo);
  useEffect(() => {
    console.log("fileInfo updated: ", fileInfo);
    scrollRightPanel();
  }, [fileInfo]);
  useEffect(() => {
    console.log("state updated: ", state);
    scrollLeftPanel();
  }, [state]);
  useEffect(() => {
    console.log("responseInfo updated: ", responseInfo);
    scrollRightPanel();
  }, [responseInfo]);
  useEffect(() => {
    setFileInfo((prev) => {
      if (prev.length >= state.steps.length) return prev;
      return [...prev, { filename: "", content: "", mtime: new Date(0) }];
    });
  }, [state.steps.length]);

  const rightPanel = useRef<HTMLDivElement>(null);
  const leftPanel = useRef<HTMLDivElement>(null);

  const scrollRightPanel = () => {
    if (rightPanel.current) {
      rightPanel.current.scrollIntoView({
        behavior: "smooth",
        block: "end",
      });
    }
  };
  const scrollLeftPanel = () => {
    if (leftPanel.current) {
      leftPanel.current.scrollIntoView({
        behavior: "smooth",
        block: "end",
      });
    }
  };

  //if (fileInfo.length < state.steps.length) {
  //  setFileInfo((prev) => [
  //    ...prev,
  //    { filename: "", content: "", mtime: new Date(0) },
  //  ]);
  // }

  return (
    <div className="flex h-screen">
      {/* Left-Panel */}
      <ScrollArea className="w-1/2 p-4 border-r space-y-4">
        <div ref={leftPanel}>
          {state.steps.map((step, index) => (
            <div key={index}>
              <p className="text-xl my-2">
                Step {index} - Status: {step.status}
              </p>
              <FileUploader
                index={index}
                status={step.status}
                dispatch={dispatch}
                setFileInfo={setFileInfo}
              />
              <QA
                index={index}
                status={step.status}
                dispatch={dispatch}
                fileInfo={fileInfo[index]}
                setResponseInfo={setResponseInfo}
                responseInfo={responseInfo[index]}
              />
              <Separator />
            </div>
          ))}
        </div>
      </ScrollArea>
      {/* Right-Panel */}
      <ScrollArea className="w-1/2 p-4 border-r space-y-4">
        <div ref={rightPanel}>
          {state.steps.map((step, index) => (
            <div key={index}>
              <p className="text-xl my-2">
                Step {index} - Status: {step.status}
              </p>
              <ShowPrompt
                index={index}
                status={step.status}
                fileInfo={fileInfo}
              />
              <ShowResponse
                index={index}
                status={step.status}
                responseInfo={responseInfo}
              />
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
