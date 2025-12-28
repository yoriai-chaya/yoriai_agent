from logger import logger
from prompt_parser import load_agents_prompt, require_str


def create_prompt_for_builderror(code: str, error_message: str) -> str:
    logger.debug("create_prompt_for_builderror called")
    logger.debug(f"code: {code}")
    logger.debug(f"error_message: {error_message}")
    agents_prompt = load_agents_prompt()
    prompt_build_error = require_str(data=agents_prompt, key="build_error_prompt")
    logger.debug(f"prompt_build_error: {prompt_build_error}")

    filled_prompt = prompt_build_error.replace("{{source_code}}", code).replace(
        "{{error_message}}", error_message
    )
    return filled_prompt
