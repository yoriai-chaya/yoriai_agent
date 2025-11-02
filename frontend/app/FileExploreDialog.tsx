"use client";

import { useEffect, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { RhiYamlInfo } from "@/lib/types";

interface Props {
  open: boolean;
  onClose: () => void;
  onSelectFile: (filename: string, mtime: string) => void;
}

export function FileExplorerDialog({ open, onClose, onSelectFile }: Props) {
  const [files, setFiles] = useState<RhiYamlInfo[]>([]);

  useEffect(() => {
    if (open) {
      fetch("/api/files")
        .then((res) => res.json())
        .then((data) => setFiles(data.files));
    }
  }, [open]);

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Select a File</DialogTitle>
          <DialogDescription>
            Choose a file from the list below.
          </DialogDescription>
        </DialogHeader>
        <ul className="space-y-2">
          {files.map((file) => (
            <li key={file.name}>
              <Button
                variant="ghost"
                onClick={() => onSelectFile(file.name, file.mtime)}
                className="w-full justify-start"
              >
                {file.name}
              </Button>
            </li>
          ))}
        </ul>
      </DialogContent>
    </Dialog>
  );
}
