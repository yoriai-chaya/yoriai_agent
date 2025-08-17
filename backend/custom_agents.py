import os
import shutil
import sys
from datetime import datetime

from agents import (
    Agent,
    RunContextWrapper,
    function_tool,
    handoff,
    set_default_openai_key,
)
from pydantic import ValidationError

from base import CodeCheckResult, CodeGenResponse, CodeSaveData, CodeType, LocalContext
from config import get_settings
from eslint_checker import run_eslint
from logger import logger


# Callback Functions
async def on_save(ctx: RunContextWrapper[LocalContext], input_data: CodeSaveData):
    logger.debug("on_save called")
    base_output = os.path.join(os.getcwd(), ctx.context.output_dir)
    target_dir = os.path.join(base_output, input_data.directory)
    os.makedirs(target_dir, exist_ok=True)
    file_path = os.path.join(target_dir, input_data.filename)

    if os.path.exists(file_path):
        backup_dir = os.path.join(target_dir, "backup")
        logger.debug(f"backup_dir: {backup_dir}")
        os.makedirs(backup_dir, exist_ok=True)

        base, ext = os.path.splitext(input_data.filename)
        dt_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{base}_{dt_str}{ext}"
        logger.debug(f"backup_file: {backup_file}")
        backup_path = os.path.join(backup_dir, backup_file)
        logger.debug(f"backup_path: {backup_path}")
        shutil.move(file_path, backup_path)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(input_data.code)
    logger.debug(f"Saved file at {file_path}")
    response = CodeGenResponse(
        result=True, detail="saved successfully", code=input_data.code
    )
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
    result = run_eslint(filename=filename)
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
