"use client";
import { useState } from "react";
import StatusBadge from "./StatusBadge";
import PromptFilelistLoader from "./PromptFilelistLoader";
import { RhiMdInfo } from "@/lib/types";
import { Action, FileInfo } from "./types";
import { Play } from "lucide-react";
import { Button } from "@/components/ui/button";

interface AutoBlockProps {
  dispatch: React.Dispatch<Action>;
  setFileInfo: React.Dispatch<React.SetStateAction<FileInfo[]>>;
}

const AutoBlock = ({ dispatch, setFileInfo }: AutoBlockProps) => {
  const status = "idle";
  const [mdFiles, setMdFiles] = useState<RhiMdInfo[]>([]);

  const handlePlay = async () => {
    console.log("handlePlay called");
  };
  return (
    <div className="mx-4">
      <div className="flex flex-col">
        <div>
          <PromptFilelistLoader setMdFiles={setMdFiles} />
        </div>
        <div>
          <StatusBadge status={status} />
        </div>
        <div>
          <Button onClick={handlePlay} variant="ghost" size="icon">
            <Play />
          </Button>
        </div>
      </div>
      {/* Debug表示 */}
      <div className="text-xs text-gray-600">
        {mdFiles.map((file) => (
          <div key={file.name}>
            <p>{file.name}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AutoBlock;
