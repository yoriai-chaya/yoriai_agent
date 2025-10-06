import os
import shutil
import sys
from datetime import datetime
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

from backup_playwright_results import save_playwright_results
from base import (
    AgentResult,
    CodeCheckResult,
    CodeGenResponse,
    CodeSaveData,
    CodeType,
    LocalContext,
    RunTestsResultPayload,
)
from config import get_settings
from eslint_checker import run_eslint
from eval_tests import eval_test_results
from logger import logger
from playwright_runner import run_playwright


# Internal Functions
def _backup_existing_file(target_dir: str, filename: str) -> None:
    file_path = os.path.join(target_dir, filename)
    if os.path.exists(file_path):
        backup_dir = os.path.join(target_dir, "backup")
        logger.debug(f"backup_dir: {backup_dir}")
        os.makedirs(backup_dir, exist_ok=True)

        base, ext = os.path.splitext(filename)
        dt_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{base}_{dt_str}{ext}"
        logger.debug(f"backup_file: {backup_file}")
        backup_path = os.path.join(backup_dir, backup_file)
        logger.debug(f"backup_path: {backup_path}")
        shutil.move(file_path, backup_path)
        logger.debug(f"Moved existing file to backup: {backup_path}")


# Callback Functions
async def on_save(ctx: RunContextWrapper[LocalContext], input_data: CodeSaveData):
    logger.debug("on_save called")
    base_output = str(ctx.context.output_dir)
    logger.debug(f"base_output: {base_output}")
    target_dir = os.path.join(base_output, input_data.directory)
    os.makedirs(target_dir, exist_ok=True)

    _backup_existing_file(target_dir, input_data.filename)

    file_path = os.path.join(target_dir, input_data.filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(input_data.code)
    logger.debug(f"Saved file at {file_path}")
    response = CodeGenResponse(
        result=True, detail="saved successfully", code=input_data.code
    )
    ctx.context.response = response
    ctx.context.gen_code_filepath = file_path
    return


# Callback Functions
async def on_eval_tests(ctx: RunContextWrapper[LocalContext]) -> RunTestsResultPayload:
    logger.debug("on_eval_tests called")
    test_results = eval_test_results(ctx=ctx)
    logger.debug(f"return test_results: {test_results}")
    save_playwright_results(ctx=ctx)
    return test_results


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

            _backup_existing_file(abs_to, os.path.basename(src))

            logger.debug(f"dst: {dst}")
            shutil.copy2(src, dst)
            logger.debug(f"Copied {src} -> {dst}")

        return result

    except (OSError, PermissionError, shutil.Error, ValueError) as e:
        return AgentResult(result=False, error_detail=f"Unexpected error: {e}")


# Function Tools
@function_tool
async def run_tests(ctx: RunContextWrapper, test_dir: str, test_file: str) -> bool:
    """Run tests using playwright.

    Args:
        test_dir: directory containing test files
        test_file: test file name

    """
    logger.debug("run_tests called")
    output_dir: Path = ctx.context.output_dir
    logger.debug(f"output_dir: {output_dir}")
    logger.debug(f"test_dir: {test_dir}")
    logger.debug(f"test_file: {test_file}")
    result = run_playwright(ctx=ctx, test_dir=test_dir, test_file=test_file)
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

# Agents
EVAL_TESTS = """
あなたはPlaywrightを用いてテスト実行したテスト結果をチェックする専門家です。
指定されたディレクトリにある指定されたテスト結果ファイルを確認します。
"""
eval_tests_agent = Agent(
    name="EvalTestsAgent",
    instructions=EVAL_TESTS,
    model=model,
    output_type=RunTestsResultPayload,
)

eval_tests_handoff = handoff(
    agent=eval_tests_agent,
    on_handoff=on_eval_tests,
    tool_name_override="eval_tests",
    tool_description_override="Check test results",
)

RUN_TESTS = """
あなたはNext.jsのアプリケーションのテスト実行を行う専門家です。
指定されたディレクトリにある指定されたテストプログラムファイルに
記述された内容を登録されたツールを使ってテストを実行します。
テスト実行が完了したら、eval_testsツールを使ってテスト結果を確認します。
"""
run_tests_agent = Agent[LocalContext](
    name="RunTestsAgent",
    instructions=RUN_TESTS,
    model=model,
    tools=[run_tests],
    output_type=bool,
    handoffs=[eval_tests_handoff],
)
