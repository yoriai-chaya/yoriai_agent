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
from common import save_backup
from config import get_settings
from eslint_checker import run_eslint
from logger import logger
from playwright_runner import run_playwright

SNAPSHOT_ERROR_MESSAGE_PREF = "Error: A snapshot doesn't exist at"


# Callback Functions
async def on_save(ctx: RunContextWrapper[LocalContext], input_data: CodeSaveData):
    logger.debug("on_save called")
    output_dir = Path(str(ctx.context.output_dir))
    target_dir = output_dir / input_data.directory
    logger.debug(f"target_dir: {str(target_dir)}")
    target_dir.mkdir(exist_ok=True)

    # Save file
    file_path = os.path.join(target_dir, input_data.filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(input_data.code)
    logger.debug(f"Saved file at {file_path}")
    response = CodeGenResponse(
        result=True, detail="saved successfully", code=input_data.code
    )

    # Save backup
    save_backup(target_dir, input_data.filename)

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

            filename = Path(src).name
            logger.debug(f"filename: {filename}")
            save_backup(Path(abs_to), filename)

        return result

    except (OSError, PermissionError, shutil.Error, ValueError) as e:
        return AgentResult(result=False, error_detail=f"Unexpected error: {e}")


# Function Tools
@function_tool
async def run_tests(
    ctx: RunContextWrapper, test_dir: str, test_file: str, project: str
) -> FunctionResult:
    """Run tests using playwright.

    Args:
        test_dir: directory containing test files
        test_file: test file name
        project: project name

    Return:
        FunctionResult: execute command result

    """
    logger.debug("run_tests called")
    output_dir: Path = ctx.context.output_dir
    logger.debug(f"output_dir: {output_dir}")
    logger.debug(f"test_dir: {test_dir}")
    logger.debug(f"test_file: {test_file}")
    logger.debug(f"project: {project}")

    # Run Tests
    result = run_playwright(
        ctx=ctx, test_dir=test_dir, test_file=test_file, project=project
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

CODE_GEN = """
あなたはNext.jsフレームワークのアプリケーション開発を担う
Typescriptのプログラマです。
プログラム生成のための要求仕様や条件に基づき、
TypeScriptプログラムを生成します。
生成したコードをsave_codeツールを使ってファイル保存してください。
"""
code_gen_agent = Agent[LocalContext](
    name="CodeGenAgent",
    instructions=CODE_GEN,
    model=model,
    output_type=CodeType,
    handoffs=[save_handoff],
)

CODE_CHECK = """
あなたはNext.jsフレームワークのアプリケーションプログラム
の静的チェックを行う専門家です。
指定されたプログラムファイルに記述された内容を
check_codeツールを使って静的チェックを行います。
"""
code_check_agent = Agent[LocalContext](
    name="CodeCheckAgent",
    instructions=CODE_CHECK,
    model=model,
    tools=[check_code],
    output_type=CodeCheckResult,
)

PLACE_FILES = """
あなたはNext.jsフレームワークのアプリケーションで必要なファイル資材を
適切なディレクトリに配置するアドミニストレータです。
指定されたファイルを指定されたコピー元ディレクトリからコピー先
ディレクトリに配置します。
配置は指定されたツールを使います。
"""
place_files_agent = Agent[LocalContext](
    name="PlaceFilesAgent",
    instructions=PLACE_FILES,
    model=model,
    output_type=AgentResult,
    tools=[place_files],
)

RUN_TESTS = """
あなたはNext.jsのアプリケーションのテスト実行を行う専門家です。
指定されたディレクトリにある指定されたテストプログラムファイルに
記述された内容を登録されたツールを使ってテストを実行します。
"""
run_tests_agent = Agent[LocalContext](
    name="RunTestsAgent",
    instructions=RUN_TESTS,
    model=model,
    tools=[run_tests],
    output_type=FunctionResult,
)
