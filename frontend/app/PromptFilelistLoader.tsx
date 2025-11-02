"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { FileExplorerDialog } from "./FileExploreDialog";
import { formatDateTime } from "./util";
import { RhiYamlInfo, RhiMdInfo } from "@/lib/types";
import { TaskYaml } from "./types";
import yaml from "js-yaml";

interface Props {
  setMdFiles: React.Dispatch<React.SetStateAction<RhiMdInfo[]>>;
}
const PromptFilelistLoader = ({ setMdFiles }: Props) => {
  const [open, setOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<RhiYamlInfo | null>(null);

  const handleSelectFile = async (filename: string, mtime: string) => {
    const date = new Date(mtime);
    setSelectedFile({ name: filename, mtime: formatDateTime(date) });
    setOpen(false);

    // Retrieve the YAML file from the backend.
    const yamlRes = await fetch(`/api/files/${filename}`);
    const yamlData = await yamlRes.json();
    console.log(`yamlData: ${yamlData}`);

    // Parse YAML content
    const parsed = yaml.load(yamlData.content) as TaskYaml;
    const steps = parsed?.steps || [];
    for (const step of steps) {
      const promptFile = step.prompt_file;
      console.log(`promptFile: ${promptFile}`);
      if (!promptFile) continue;

      // Retrieve each prompt_file
      const mdRes = await fetch(`/api/files/${promptFile}`);
      const mdData: RhiMdInfo = await mdRes.json();

      // Add the retrieved data to the parent component's state
      setMdFiles((prev) => [...prev, mdData]);
    }
  };

  return (
    <div className="flex items-center gap-2">
      <div>
        <Button
          onClick={() => setOpen(true)}
          className="text-ctm-blue-500 hover:text-ctm-blue-600"
          variant="ghost"
        >
          Load
        </Button>
        <FileExplorerDialog
          open={open}
          onClose={() => setOpen(false)}
          onSelectFile={handleSelectFile}
        />
      </div>
      <div>
        {selectedFile && (
          <div className="text-app-info text-gray-700">{selectedFile.name}</div>
        )}
      </div>
      <div>
        {selectedFile && (
          <div className="text-app-time text-gray-500">
            {selectedFile.mtime}
          </div>
        )}
      </div>
    </div>
  );
};

export default PromptFilelistLoader;
