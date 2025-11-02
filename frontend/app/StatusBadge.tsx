import { Badge } from "@/components/ui/badge";

type StatusBadgeProps = {
  status: "idle" | "running" | "stopped" | "success" | "failed" | string;
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  const statusMap: Record<string, string> = {
    idle: "bg-gray-200 text-gray-700",
    running: "bg-blue-100 text-blue-700",
    stopped: "bg-yellow-100 text-yellow-700",
    success: "bg-green-100 text-green-700",
    failed: "bg-red-100 text-red-700",
  };

  const badgeClass = statusMap[status] || "bg-gray-100 text-gray-700";

  return <Badge className={badgeClass}>{status}</Badge>;
}
