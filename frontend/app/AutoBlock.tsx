"use client";
import AutoRunLoader from "./AutoRunLoader";
import { useState } from "react";
import { TreeNode } from "./types";

const AutoBlock = () => {
  const [tree, setTree] = useState<TreeNode[]>([]);
  return (
    <div className="mx-4">
      <AutoRunLoader tree={tree} setTree={setTree} />
    </div>
  );
};

export default AutoBlock;
