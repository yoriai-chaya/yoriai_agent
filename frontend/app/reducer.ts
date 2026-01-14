import { State, Action } from "./types";

const initialState: State = {
  steps: [{ status: "Unloaded" }],
};
export const reducer = (state: State, action: Action): State => {
  const newSteps = [...state.steps];
  switch (action.type) {
    case "RESET":
      return initialState;
    case "LOAD_FILE":
      newSteps[action.index].status = "Loaded";
      return { steps: newSteps };
    case "SEND_PROMPT":
      newSteps[action.index].status = "Sended";
      return { steps: newSteps };
    case "DONE":
      newSteps[action.index].status = "Done";
      if (action.index === newSteps.length - 1) {
        newSteps.push({ status: "Unloaded" });
      }
      return { steps: newSteps };
    default:
      return state;
  }
};
