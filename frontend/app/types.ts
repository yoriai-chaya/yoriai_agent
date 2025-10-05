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

export type CheckResultPayload = {
  checker: string;
  result: boolean;
  rule_id: string;
  detail: string;
};

export type TestResultSpec = {
  title: string;
  result: boolean;
  error_summary: string | null;
  error_message: string | null;
  error_stack: string | null;
};

export type TestResultPayload = {
  name: string;
  file: string;
  result: boolean;
  detail: string;
  total: number;
  ok: number;
  ng: number;
  specs: TestResultSpec[];
};

export type StreamResponse =
  | { event: "started"; payload: { status: string; message: string } }
  | {
      event: "code";
      payload: { language: string; code: string; file_path: string };
    }
  | { event: "agent_update"; payload: { agent_name: string } }
  | { event: "done"; payload: { status: string; message: string } }
  | { event: "check_result"; payload: CheckResultPayload }
  | { event: "system_error"; payload: { error: string; detail: string } }
  | {
      event: "agent_result";
      payload: { result: boolean; error_detail: string };
    }
  | { event: "test_result"; payload: TestResultPayload };

export type ResponseEvent = {
  s_res: StreamResponse;
  r_time: Date;
};

export type ResponseInfo = {
  r_event: ResponseEvent[];
};

export const EventTypes = {
  STARTED: "started",
  CODE: "code",
  AGENT_UPDATE: "agent_update",
  DONE: "done",
  CHECK_RESULT: "check_result",
  SYSTEM_ERROR: "system_error",
  AGENT_RESULT: "agent_result",
  TEST_RUN: "test_run",
  TEST_RESULT: "test_result",
} as const;

export type CheckResultEvent = {
  event: "check_result";
  payload: CheckResultPayload;
};

export type CheckResultItem = {
  s_res: CheckResultEvent;
  r_time: Date;
};

export enum Emoji {
  WHITE_CIRCLE = "\u26AA", // ⚪
  RED_CIRCLE = "\u{1F534}", // 🔴
  BLUE_CIRCLE = "\u{1F535}", // 🔵
  GREEN_CIRCLE = "\u{1F7E2}", // 🟢
}

export enum ResponseStatus {
  COMPLETED = "Completed",
  FAILED = "Failed",
}
