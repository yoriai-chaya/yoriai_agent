from enum import StrEnum
from typing import Any, List

from pydantic import BaseModel


class EventType(StrEnum):
    CODE = "code"
    AGENT_UPDATE = "agent_update"
    DELTA = "delta"
    STARTED = "started"
    DONE = "done"
    CHECK_CODE = "check_code"
    SYSTEM_ERROR = "system_error"


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
    output_dir: str
    response: CodeGenResponse | None = None
    gen_code_filepath: str


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
