"use client";
import { useState } from "react";
import StatusBadge from "./StatusBadge";
import PromptFilelistLoader from "./PromptFilelistLoader";
import { RhiMdInfo } from "@/lib/types";
import { Action, FileInfo } from "./types";

interface AutoBlockProps {
  dispatch: React.Dispatch<Action>;
  setFileInfo: React.Dispatch<React.SetStateAction<FileInfo[]>>;
}

const AutoBlock = ({ dispatch, setFileInfo }: AutoBlockProps) => {
  const status = "idle";
  const [mdFiles, setMdFiles] = useState<RhiMdInfo[]>([]);
  return (
    <div className="mx-4">
      <div className="grid grid-cols-2 grid-rows-2 gap-x-2">
        {/* A1 + B1*/}
        <div className="col-span-2 row-start-1">
          <PromptFilelistLoader setMdFiles={setMdFiles} />
        </div>
        {/* A2 */}
        <div className="col-start-1 row-start-2">Play button</div>
        {/* B2 */}
        <div className="col-start-2 row-start-2">
          <StatusBadge status={status} />
        </div>
      </div>
      {/* Debug表示 */}
      {/*
      <div className="mt-4 text-sm text-gray-600">
        {mdFiles.map((file) => (
          <div key={file.name}>
            <p> 📄 {file.name}</p>
            <p className="text-gray-500 text-xs">mtime: {file.mtime}</p>
          </div>
        ))}
      </div>
      */}
    </div>
  );
};

export default AutoBlock;
