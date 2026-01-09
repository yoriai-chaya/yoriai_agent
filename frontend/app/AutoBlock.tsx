"use client";
import AutoRunLoader from "./AutoRunLoader";
import { TreeNode, Action, FileInfo, ResponseInfo } from "./types";

interface AutoBlockProps {
  tree: TreeNode[];
  setTree: React.Dispatch<React.SetStateAction<TreeNode[]>>;
  dispatch: React.Dispatch<Action>;
  setFileInfo: React.Dispatch<React.SetStateAction<FileInfo[]>>;
  setResponseInfo: React.Dispatch<React.SetStateAction<ResponseInfo[]>>;
}
const AutoBlock: React.FC<AutoBlockProps> = ({
  tree,
  setTree,
  dispatch,
  setFileInfo,
  setResponseInfo,
}) => {
  return (
    <div className="mx-4">
      <AutoRunLoader
        tree={tree}
        setTree={setTree}
        dispatch={dispatch}
        setFileInfo={setFileInfo}
        setResponseInfo={setResponseInfo}
      />
    </div>
  );
};

export default AutoBlock;
