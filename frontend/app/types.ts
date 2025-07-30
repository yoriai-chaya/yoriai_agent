export type ChatStep = { status: "Unloaded" | "Loaded" | "Sended" | "Done" };
export type State = { steps: ChatStep[] };
export type Action =
  | { type: "LOAD_FILE"; index: number }
  | { type: "SEND_PROMPT"; index: number }
  | { type: "DONE"; index: number };
export type FileInfo = {
  filename: string;
  content: string;
  mtime: Date;
};
export type PromptRequest = {
  prompt: string;
};
export type PromptResponse = {
  prompt: string;
};

export type StreamResponse =
  | { event: "code"; payload: { language: string; code: string } }
  | { event: "agent_update"; payload: { agent_name: string } }
  | { event: "delta"; payload: { text: string } }
  | { event: "started"; payload: { message: string } }
  | { event: "done"; payload: { message: string } };

export type ResponseEvent = {
  s_res: StreamResponse;
  r_time: Date;
};

export type ResponseInfo = {
  r_event: ResponseEvent[];
};
