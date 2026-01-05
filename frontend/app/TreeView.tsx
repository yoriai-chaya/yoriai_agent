"use client";
import { TreeNode } from "./types";
import { formatDateTime } from "./util";

interface TreeViewProps {
  nodes: TreeNode[];
  depth?: number;
}

const indentClass = (depth: number) => `ml-${depth * 2}`;

const TreeView: React.FC<TreeViewProps> = ({ nodes, depth = 0 }) => {
  return (
    <ul className="text-sm">
      {nodes.map((node, index) => {
        if (node.type === "directory") {
          return (
            <li key={`${node.name}-${index}`} className={indentClass(depth)}>
              <div className="font-medium">- {node.name}</div>
              <TreeView nodes={node.children} depth={depth + 1} />
            </li>
          );
        }

        // file
        return (
          <li key={`${node.name}-${index}`} className={indentClass(depth)}>
            <div>- {node.name}</div>
            <div className="ml-2 text-xs text-muted-foreground">
              {formatDateTime(new Date(node.data.mtime))}
            </div>
          </li>
        );
      })}
    </ul>
  );
};

export default TreeView;
