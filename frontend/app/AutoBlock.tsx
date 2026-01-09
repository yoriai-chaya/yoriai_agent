"use client";
import AutoRunLoader from "./AutoRunLoader";
import { TreeNode } from "./types";

interface AutoBlockProps {
  tree: TreeNode[];
  setTree: React.Dispatch<React.SetStateAction<TreeNode[]>>;
}
const AutoBlock: React.FC<AutoBlockProps> = ({ tree, setTree }) => {
  return (
    <div className="mx-4">
      <AutoRunLoader tree={tree} setTree={setTree} />
    </div>
  );
};

export default AutoBlock;
