import { Card } from "@/components/ui/card";
import { ResponseInfo } from "./types";
import Markdown from "./Markdown";

interface ShowResponseProps {
  status: string;
  index: number;
  responseInfo: ResponseInfo[];
}

const ResponsePrompt = ({ status, index, responseInfo }: ShowResponseProps) => {
  return (
    <div>
      {status === "Sended" && (
        <div>
          <p className="text-lg my-1">Response</p>
          <Card className="p-4 bg-slate-200 rounded-md">
            <div className="flex overflow-x-auto">
              <Markdown markdown={responseInfo[index].content} />
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default ResponsePrompt;
