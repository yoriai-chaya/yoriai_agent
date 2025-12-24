import os
import shutil
import sys
from pathlib import Path
from typing import List

from agents import (
    Agent,
    RunContextWrapper,
    function_tool,
    handoff,
    set_default_openai_key,
)
from pydantic import ValidationError

from base import (
    AgentResult,
    CodeCheckResult,
    CodeGenResponse,
    CodeSaveData,
    CodeType,
    FunctionResult,
    LocalContext,
)
from common import archive
from config import get_settings
from eslint_checker import run_eslint
from logger import logger
from playwright_runner import run_playwright
from prompt_parser import load_agents_prompt, require_str

SNAPSHOT_ERROR_MESSAGE_PREF = "Error: A snapshot doesn't exist at"


# Callback Functions
async def on_save(ctx: RunContextWrapper[LocalContext], input_data: CodeSaveData):
    logger.debug("on_save called")
    output_dir = Path(str(ctx.context.output_dir))
    target_dir = output_dir / input_data.directory
    logger.debug(f"target_dir: {str(target_dir)}")
    target_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = os.path.join(target_dir, input_data.filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(input_data.code)
    logger.debug(f"Saved file at {file_path}")
    response = CodeGenResponse(
        result=True, detail="saved successfully", code=input_data.code
    )

    # Archive
    src_dir: Path = target_dir
    stepid_dir = ctx.context.stepid_dir
    dir = Path(input_data.directory)
    archive(
        src_dir=src_dir, src_file=input_data.filename, stepid_dir=stepid_dir, dir=dir
    )

    # Return
    ctx.context.response = response
    ctx.context.gen_code_filepath = file_path
    return


# Settings
try:
    settings = get_settings()
except ValidationError as e:
    print(f"Settings failed : {e}")
    sys.exit(1)

set_default_openai_key(key=settings.openai_api_key, use_for_tracing=True)
model = settings.openai_model
logger.debug(f"model: {model}")


# Function Tools
@function_tool
async def check_code(ctx: RunContextWrapper, filename: str) -> CodeCheckResult:
    """Static code check of specified program file.

    Args:
        filename: check target file

    """
    result = run_eslint(ctx=ctx, filename=filename)
    return result


@function_tool
async def place_files(
    ctx: RunContextWrapper, from_dir: str, to_dir: str, files: List[str]
) -> AgentResult:
    """Place Files from 'from_dir' to 'to_dir'

    Args:
        from_dir: source directory name
        to_dir: destination directory name
        files: files to be placed

    """
    logger.debug(
        f"place_files called : from_dir: {from_dir}, to_dir: {to_dir}, files: {files}"
    )
    result = AgentResult(result=True, error_detail="")
    try:
        abs_from = os.path.abspath(from_dir)
        abs_to = os.path.abspath(to_dir)
        logger.debug(f"abs_from: {abs_from}, abs_to: {abs_to}")

        if not os.path.isdir(abs_from):
            return AgentResult(
                result=False, error_detail=f"Cannot find source directory: {abs_from}"
            )
        if not os.path.isdir(abs_to):
            return AgentResult(
                result=False,
                error_detail=f"Cannot find destination directory: {abs_from}",
            )

        for f in files:
            src = os.path.normpath(os.path.join(abs_from, f))
            logger.debug(f"src: {src}")
            if os.path.commonpath([abs_from, src]) != abs_from:
                return AgentResult(
                    result=False,
                    error_detail="Invalid file path (outside source dir)",
                )
            if not os.path.isfile(src):
                return AgentResult(
                    result=False,
                    error_detail=f"Cannot find file: {src}",
                )
            dst = os.path.join(abs_to, os.path.basename(src))

            logger.debug(f"dst: {dst}")
            shutil.copy2(src, dst)
            logger.debug(f"Copied {src} -> {dst}")

        return result

    except (OSError, PermissionError, shutil.Error, ValueError) as e:
        return AgentResult(result=False, error_detail=f"Unexpected error: {e}")


# Function Tools
@function_tool
async def run_tests(
    ctx: RunContextWrapper,
    test_dir: str,
    test_file: str,
    project: str,
    screenshot_file: str,
) -> FunctionResult:
    """Run tests using playwright.

    Args:
        test_dir: directory containing test files
        test_file: test file name
        project: project name
        screenshot_file: screenshot file name

    Return:
        FunctionResult: execute command result

    """
    logger.debug("run_tests called")
    output_dir: Path = ctx.context.output_dir
    logger.debug(f"output_dir: {output_dir}")
    logger.debug(f"test_dir: {test_dir}")
    logger.debug(f"test_file: {test_file}")
    logger.debug(f"project: {project}")
    logger.debug(f"screenshot_file: {screenshot_file}")

    # Run Tests
    result = run_playwright(
        ctx=ctx,
        test_dir=test_dir,
        test_file=test_file,
        project=project,
        screenshot_file=screenshot_file,
    )
    logger.debug(f"result: {result}")

    # Return
    logger.debug(f"run_tests return : {result}")
    return result


# Agents
file_save_agent = Agent(
    name="FileSaveAgent", instructions="ファイル保存を行うエージェント"
)

save_handoff = handoff(
    agent=file_save_agent,
    on_handoff=on_save,
    input_type=CodeSaveData,
    tool_name_override="save_code",
    tool_description_override="Generate and save code to file",
)

# Get Agentes
_code_gen_agent: Agent[LocalContext] | None = None
_code_check_agent: Agent[LocalContext] | None = None
_place_files_agent: Agent[LocalContext] | None = None
_run_tests_agent: Agent[LocalContext] | None = None


def get_code_gen_agent() -> Agent[LocalContext]:
    logger.debug("get_code_gen_agent called")
    global _code_gen_agent
    if _code_gen_agent is not None:
        logger.debug("get_code_gen_agent return")
        return _code_gen_agent

    agents_prompt = load_agents_prompt()
    logger.debug(f"agents_prompt: {agents_prompt}")
    prompt_code_gen = require_str(data=agents_prompt, key="code_gen")
    logger.debug(f"prompt_code_gen: {prompt_code_gen}")
    _code_gen_agent = Agent[LocalContext](
        name="CodeGenAgent",
        instructions=prompt_code_gen,
        model=model,
        output_type=CodeType,
        handoffs=[save_handoff],
    )
    logger.debug("get_code_gen_agent return")
    return _code_gen_agent


def get_code_check_agent() -> Agent[LocalContext]:
    logger.debug("get_code_check_agent called")
    global _code_check_agent
    if _code_check_agent is not None:
        logger.debug("get_code_check_agent return")
        return _code_check_agent

    agents_prompt = load_agents_prompt()
    logger.debug(f"agents_prompt: {agents_prompt}")
    prompt_code_check = require_str(data=agents_prompt, key="code_check")
    logger.debug(f"prompt_code_check: {prompt_code_check}")
    _code_check_agent = Agent[LocalContext](
        name="CodeCheckAgent",
        instructions=prompt_code_check,
        model=model,
        tools=[check_code],
        output_type=CodeCheckResult,
    )
    logger.debug("get_code_check_agent return")
    return _code_check_agent


def get_place_files_agent() -> Agent[LocalContext]:
    logger.debug("get_place_files_agent called")
    global _place_files_agent
    if _place_files_agent is not None:
        logger.debug("get_place_files_agent return")
        return _place_files_agent

    agents_prompt = load_agents_prompt()
    logger.debug(f"agents_prompt: {agents_prompt}")
    prompt_place_files = require_str(data=agents_prompt, key="place_files")
    logger.debug(f"prompt_place_files: {prompt_place_files}")

    _place_files_agent = Agent[LocalContext](
        name="PlaceFilesAgent",
        instructions=prompt_place_files,
        model=model,
        output_type=AgentResult,
        tools=[place_files],
    )
    logger.debug("get_place_files_agent return")
    return _place_files_agent


def get_run_tests_agent() -> Agent[LocalContext]:
    logger.debug("get_run_tests_agent called")
    global _run_tests_agent
    if _run_tests_agent is not None:
        logger.debug("get_run_tests_agent return")
        return _run_tests_agent

    agents_prompt = load_agents_prompt()
    logger.debug(f"agents_prompt: {agents_prompt}")
    prompt_run_tests = require_str(data=agents_prompt, key="run_tests")
    logger.debug(f"prompt_run_tests: {prompt_run_tests}")

    _run_tests_agent = Agent[LocalContext](
        name="RunTestsAgent",
        instructions=prompt_run_tests,
        model=model,
        tools=[run_tests],
        output_type=FunctionResult,
    )
    logger.debug("get_run_tests_agent return")
    return _run_tests_agent
