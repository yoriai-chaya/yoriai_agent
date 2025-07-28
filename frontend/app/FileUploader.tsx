"use client";
import { ChangeEvent } from "react";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Action, FileInfo } from "./types";

interface FileUploaderProps {
  status: string;
  index: number;
  dispatch: React.Dispatch<Action>;
  setFileInfo: React.Dispatch<React.SetStateAction<FileInfo[]>>;
}
const FileUploader = ({
  status,
  index,
  dispatch,
  setFileInfo,
}: FileUploaderProps) => {
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    console.log(`Selected file: ${file.name}`);
    const reader = new FileReader();
    reader.onload = () => {
      const content = reader.result as string;
      const filename = file.name;
      const mtime = new Date(file.lastModified);

      setFileInfo((prev) => {
        const updated = [...prev];
        updated[index] = { filename, content, mtime };
        return updated;
      });
      dispatch({ type: "LOAD_FILE", index });
    };
    reader.readAsText(file);
  };

  return (
    <div className="grid grid-cols-6 items-center gap-2 mb-2">
      {/* column-A */}
      <div>
        <Avatar>
          <AvatarImage src="/you.png" />
          <AvatarFallback>Yo</AvatarFallback>
        </Avatar>
      </div>
      {/* column-B */}
      <span className="col-span-1">You</span>
      {/* column-C,D,E */}
      {(status === "Unloaded" || status === "Loaded") && (
        <div className="col-span-3">
          <Input type="file" onChange={handleFileChange} />
        </div>
      )}
      {/* column-F */}
      <div></div>
    </div>
  );
};

export default FileUploader;
