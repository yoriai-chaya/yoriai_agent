import { Card } from "@/components/ui/card";
import { ResponseInfo } from "./types";
import Markdown from "./Markdown";

interface ShowResponseProps {
  status: string;
  index: number;
  responseInfo: ResponseInfo[];
}

const ResponsePrompt = ({ status, index, responseInfo }: ShowResponseProps) => {
  const codeEvent = responseInfo[index]?.r_event.find(
    (ev) => ev.s_res.event === "code"
  );

  let code = "";
  if (codeEvent && codeEvent.s_res.event === "code") {
    code = `\`\`\`${codeEvent.s_res.payload.language}\n${codeEvent.s_res.payload.code}\n\`\`\``;
  }

  return (
    <div>
      {(status === "Sended" || status === "Done") && (
        <div>
          <p className="text-lg my-1">Response</p>
          <Card className="p-4 bg-slate-200 rounded-md">
            <div className="flex overflow-x-auto">
              <Markdown markdown={code} />
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default ResponsePrompt;
