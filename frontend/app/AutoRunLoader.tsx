"use client";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { TreeNode } from "./types";
import { useState } from "react";
import TreeView from "./TreeView";

interface AutoRunLoaderProps {
  tree: TreeNode[];
  setTree: React.Dispatch<React.SetStateAction<TreeNode[]>>;
}

const AutoRunLoader: React.FC<AutoRunLoaderProps> = ({ tree, setTree }) => {
  const [autorunId, setAutorunId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [errorDetail, setErrorDetail] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

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
      const params = new URLSearchParams({ autorun_id: autorunId });
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
    } catch (e) {
      setError("Network Error");
      setErrorDetail(String(e));
    } finally {
      setLoading(false);
    }
  };

  const isLoadDisabled = loading || autorunId.trim().length === 0;

  return (
    <div className="flex flex-col">
      <Label className="mt-2">AutoRunID</Label>
      <Input
        id="autorun-id"
        placeholder="dir, dir/subdir"
        value={autorunId}
        onChange={(e) => setAutorunId(e.target.value)}
        className="border-0 border-b rounded-none focus-visible:ring-0 h-6 mt-1"
      />
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
          <TreeView nodes={tree} />
        </div>
      )}
    </div>
  );
};

export default AutoRunLoader;
