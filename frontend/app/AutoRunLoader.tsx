"use client";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import {
  TreeNode,
  Action,
  FileInfo,
  ResponseInfo,
  AutoRunFileStatusMap,
  ResponseStatus,
  AutoRunState,
} from "./types";
import { useState, useMemo, useRef } from "react";
import { flattenTree } from "./autorunUtil";
import TreeView from "./TreeView";
import { useSSEPrompt } from "./useSSEPrompt";

interface AutoRunLoaderProps {
  tree: TreeNode[];
  setTree: React.Dispatch<React.SetStateAction<TreeNode[]>>;
  dispatch: React.Dispatch<Action>;
  setFileInfo: React.Dispatch<React.SetStateAction<FileInfo[]>>;
  setResponseInfo: React.Dispatch<React.SetStateAction<ResponseInfo[]>>;
}

const AutoRunLoader: React.FC<AutoRunLoaderProps> = ({
  tree,
  setTree,
  dispatch,
  setFileInfo,
  setResponseInfo,
}) => {
  const [autorunId, setAutorunId] = useState("");
  const [inputAutorunId, setInputAutorunId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [errorDetail, setErrorDetail] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // file status
  const [fileStatusByKey, setFileStatusKey] = useState<AutoRunFileStatusMap>(
    {}
  );
  // auto-run status
  const [autoRunState, setAutoRunState] = useState<AutoRunState>("idle");
  const [currentIndex, setCurrentIndex] = useState<number>(-1);

  const pauseRequestRef = useRef(false);

  const { sendPrompt } = useSSEPrompt({ dispatch, setResponseInfo });
  const files = useMemo(() => flattenTree(tree), [tree]);

  const buildUserMessage = (status: number): string => {
    switch (status) {
      case 404:
        return "AutoRunID not found";
      case 422:
        return "Directory structure is too deep";
      case 500:
        return "Internal Error";
      default:
        return "Failed to load file list";
    }
  };

  const handleLoad = async () => {
    setLoading(true);
    setError(null);
    setErrorDetail(null);

    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL;
      const params = new URLSearchParams({ autorun_id: inputAutorunId });
      const res = await fetch(
        `${API_BASE}/autorun/filelist?${params.toString()}`,
        {
          method: "GET",
        }
      );
      if (!res.ok) {
        const body = await res.json().catch(() => null);
        setError(buildUserMessage(res.status));
        setErrorDetail(body?.detail ?? null);
        return;
      }
      const data: TreeNode[] = await res.json();
      console.log("TreeNode data: ", data);
      setTree(data);
      setAutorunId(inputAutorunId);

      const f = flattenTree(data);
      const initMap: AutoRunFileStatusMap = {};
      for (const item of f) initMap[item.key] = "pending";
      setFileStatusKey(initMap);

      setAutoRunState("idle");
      setCurrentIndex(-1);
      pauseRequestRef.current = false;
    } catch (e) {
      setError("Network Error");
      setErrorDetail(String(e));
    } finally {
      setLoading(false);
    }
  };

  const ensureFileInfoSlot = (i: number) => {
    setFileInfo((prev) => {
      const next = [...prev];
      while (next.length <= i) {
        next.push({ filename: "", content: "", mtime: new Date(0) });
      }
      return next;
    });
  };
  const ensureResponseInfoSlot = (i: number) => {
    setResponseInfo((prev) => {
      const next = [...prev];
      while (next.length <= i) {
        next.push({ r_event: [] });
      }
      return next;
    });
  };

  const runFrom = async (startIndex: number) => {
    if (files.length === 0) {
      setError("No files");
      setErrorDetail("Tree has no files");
      return;
    }
    if (startIndex >= files.length) {
      setAutoRunState("finished");
      return;
    }
    setAutoRunState("running");
    pauseRequestRef.current = false;

    for (let i = startIndex; i < files.length; i++) {
      const f = files[i];
      setCurrentIndex(i);

      setFileStatusKey((prev) => ({ ...prev, [f.key]: "running" }));

      ensureFileInfoSlot(i);
      ensureResponseInfoSlot(i);

      setFileInfo((prev) => {
        const next = [...prev];
        next[i] = { filename: f.name, content: f.content, mtime: f.mtime };
        return next;
      });
      dispatch({ type: "LOAD_FILE", index: i });

      try {
        const done = await sendPrompt(
          { filename: f.name, content: f.content, mtime: f.mtime },
          i
        );

        if (done.status === ResponseStatus.COMPLETED) {
          setFileStatusKey((prev) => ({ ...prev, [f.key]: "success" }));
        } else {
          setFileStatusKey((prev) => ({ ...prev, [f.key]: "failed" }));
          setAutoRunState("failed");
          return;
        }
        if (pauseRequestRef.current) {
          setAutoRunState("pause");
          return;
        }
      } catch (e) {
        setFileStatusKey((prev) => ({ ...prev, [f.key]: "failed" }));
        setAutoRunState("failed");
        setError("Run failed");
        setErrorDetail(e instanceof Error ? e.message : String(e));
        return;
      }
    }
    setAutoRunState("finished");
  };

  const handleRunAll = async () => {
    setError(null);
    setErrorDetail(null);

    if (autoRunState === "running") return;
    await runFrom(0);
  };

  const handleStop = async () => {
    pauseRequestRef.current = true;
  };

  const handleResume = async () => {
    setError(null);
    setErrorDetail(null);

    if (files.length === 0) return;
    if (!(autoRunState === "pause" || autoRunState === "failed")) return;

    const start = currentIndex + 1;

    if (
      autoRunState === "failed" &&
      currentIndex >= 0 &&
      currentIndex < files.length
    ) {
      const failedKey = files[currentIndex].key;
      setFileStatusKey((prev) => ({ ...prev, [failedKey]: "skipped" }));
    }

    await runFrom(start);
  };

  // for debug (incremental development: run only one file)
  const handleRunOne = async () => {
    setError(null);
    setErrorDetail(null);

    if (files.length === 0) {
      setError("No files");
      setErrorDetail("Tree has no files");
      return;
    }
    if (autoRunState === "running") return;

    await runFrom(0);
  };

  // Button condition
  const canRun = !loading && tree.length > 0 && autoRunState !== "running";
  const canStop = autoRunState === "running";
  const canResume = autoRunState === "pause" || autoRunState === "failed";

  const isLoadDisabled = loading || inputAutorunId.trim().length === 0;
  //const isRunDisabled = loading || tree.length === 0 || autoRunState === "running";

  return (
    <div className="flex flex-col">
      <Label className="mt-2">AutoRunID</Label>
      <Input
        id="autorun-id"
        placeholder="dir, dir/subdir"
        value={inputAutorunId}
        onChange={(e) => setInputAutorunId(e.target.value)}
        className="border-0 border-b rounded-none focus-visible:ring-0 h-6 mt-1"
      />
      <div className="flex flex-col gap-2 mt-1">
        <Button
          size="sm"
          onClick={handleLoad}
          disabled={isLoadDisabled}
          variant="ghost"
          className="
          shrink-0
          text-ctm-blue-500
          hover:text-ctm-blue-600
          hover:bg-transparent 
          mt-1
        "
        >
          {loading ? "Loading..." : "Load"}
        </Button>

        <Button
          size="sm"
          onClick={handleRunAll}
          disabled={!canRun}
          variant="ghost"
          className="shrink-0 text-ctm-blue-500 hover:text-ctm-blue-600 hover:bg-transparent"
        >
          Run All
        </Button>

        <Button
          size="sm"
          onClick={handleStop}
          disabled={!canStop}
          variant="ghost"
          className="shrink-0 text-ctm-blue-500 hover:text-ctm-blue-600 hover:bg-transparent"
        >
          Stop
        </Button>

        <Button
          size="sm"
          onClick={handleResume}
          disabled={!canResume}
          variant="ghost"
          className="shrink-0 text-ctm-blue-500 hover:text-ctm-blue-600 hover:bg-transparent"
        >
          Resume
        </Button>

        <Button
          size="sm"
          onClick={handleRunOne}
          disabled={!canRun}
          variant="ghost"
          className="shrink-0 text-ctm-blue-500 hover:text-ctm-blue-600 hover:bg-transparent"
        >
          Run One
        </Button>
      </div>
      {tree.length > 0 && (
        <div className="mt-2 text-xs text-muted-foreground">
          state: <span className="font-medium">{autoRunState}</span>
          {files.length > 0 && (
            <>
              {" "}
              / index:{" "}
              <span className="font-medium">
                {currentIndex >= 0
                  ? `${currentIndex + 1}/${files.length}`
                  : "-"}
              </span>
            </>
          )}
        </div>
      )}
      {error && (
        <div className="text-xs text-red-500">
          <div>{error}</div>
          {errorDetail && (
            <details className="mt-1 cursor-pointer">
              <summary className="text-xs">detail</summary>
              <p className="text-xs">{errorDetail}</p>
            </details>
          )}
        </div>
      )}

      {tree.length > 0 && (
        <div className="mt-4 border-t pt-2">
          <div className="font-semibold mb-1">{autorunId}</div>
          <TreeView nodes={tree} fileStatusByKey={fileStatusByKey} />
        </div>
      )}
    </div>
  );
};

export default AutoRunLoader;
