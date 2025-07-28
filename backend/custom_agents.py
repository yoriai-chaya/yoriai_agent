from agents import Agent, set_default_openai_key
from pydantic import BaseModel, ValidationError

from config import Settings


class CodeType(BaseModel):
    code: str


# Settings
try:
    settings = Settings()  # type: ignore
except ValidationError as e:
    print("-- Settings() failed --")
    print(e)
set_default_openai_key(key=settings.openai_api_key, use_for_tracing=True)
model = settings.openai_model
print(f"model: {model}")

# Agents
INSTRUCTION_CODE_GEN = """
あなたはNext.jsフレームワークのアプリケーション開発を担う
Typescriptのプログラマです。
プログラム生成のための要求仕様や条件に基づき、
TypeScriptプログラムを生成します。
"""
code_gen_agent = Agent(
    name="CodeGenAgent",
    instructions=INSTRUCTION_CODE_GEN,
    model=model,
    output_type=CodeType,
)
