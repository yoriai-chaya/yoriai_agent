from enum import StrEnum
from pathlib import Path
from typing import Any, List

from pydantic import BaseModel


# Enum Definitions
class EventType(StrEnum):
    STARTED = "started"
    CODE = "code"
    AGENT_UPDATE = "agent_update"
    DONE = "done"
    CHECK_RESULT = "check_result"
    SYSTEM_ERROR = "system_error"
    AGENT_RESULT = "agent_result"


class StartedStatus(StrEnum):
    STARTED = "Started"


class DoneStatus(StrEnum):
    COMPLETED = "Completed"
    FAILED = "Failed"


class PromptCategory(StrEnum):
    GEN_CODE = "GenCode"
    PLACE_FILES = "PlaceFiles"


class PromptHeaderKey(StrEnum):
    CATEGORY = "Category"


# Model Definitions
class PromptRequest(BaseModel):
    prompt: str


class PromptResponse(BaseModel):
    prompt: str


class StreamResponse(BaseModel):
    event: str
    payload: dict[str, Any]

    def to_json_line(self) -> str:
        return self.model_dump_json() + "\n"


class CodeType(BaseModel):
    code: str


class CodeSaveData(BaseModel):
    code: str
    directory: str
    filename: str


class CodeGenResponse(BaseModel):
    result: bool
    detail: str
    code: str


class LocalContext(BaseModel):
    category: str
    output_dir: Path
    max_turns: int
    response: CodeGenResponse | None = None
    gen_code_filepath: str
    is_retry_gen_code: bool
    add_prompts: List[str]


class ESLintInfo(BaseModel):
    message: str
    description: str
    rule_id: str


class CodeCheckResult(BaseModel):
    result: bool
    output_filename: str | None = None
    error_detail: str | None = None
    eslint_result: bool | None = None
    eslint_info: List[ESLintInfo] | None = None


class SystemError(BaseModel):
    error: str
    detail: str | None = None


class StartedPayload(BaseModel):
    status: StartedStatus
    message: str


class DonePayload(BaseModel):
    status: DoneStatus
    message: str


class AgentUpdatePayload(BaseModel):
    agent_name: str


class AgentResult(BaseModel):
    result: bool
    error_detail: str | None = None


class AgentResultPayload(BaseModel):
    result: bool
    error_detail: str | None = None
