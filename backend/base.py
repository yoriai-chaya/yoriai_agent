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
    TEST_RUN = "test_run"
    TEST_RESULT = "test_result"


class StartedStatus(StrEnum):
    STARTED = "Started"


class DoneStatus(StrEnum):
    COMPLETED = "Completed"
    FAILED = "Failed"


class PromptCategory(StrEnum):
    GEN_CODE = "GenCode"
    PLACE_FILES = "PlaceFiles"
    RUN_TESTS = "RunTests"


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
    results_dir: Path
    playwright_info_file: str
    playwright_report_file: str
    playwright_report_summary_file: str
    test_file: str
    before_mtime: float


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


class PlaywrightSpecs(BaseModel):
    title: str
    result: bool
    error_summary: str | None = None
    error_message: str | None = None
    error_stack: str | None = None


class PlaywrightSuites(BaseModel):
    name: str
    file: str
    result: bool
    total: int
    ok: int
    ng: int
    specs: List[PlaywrightSpecs]


class LoadPlaywrightReport(BaseModel):
    result: bool
    detail: str | None = None
    suites: PlaywrightSuites | None = None


class RunTestsResultPayload(BaseModel):
    result: bool
    detail: str | None = None
    name: str | None = None
    file: str | None = None
    total: int | None = None
    ok: int | None = None
    ng: int | None = None
    specs: List[PlaywrightSpecs] | None = None


class FunctionResult(BaseModel):
    result: bool
    detail: str | None = None
