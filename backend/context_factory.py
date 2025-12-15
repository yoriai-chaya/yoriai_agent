import json
from datetime import datetime
from pathlib import Path

import yaml

from base import IsCodeCheckError, LocalContext
from common import resolve_path
from config import Settings
from logger import logger

DIR_PROMPTS = "prompts"


class InvalidPromptConfigError(ValueError):
    """Configuration file does not match application requirements."""


def load_agents_prompt(path: Path) -> dict:
    try:
        with path.open() as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML format: {path}")
        raise ValueError(f"Invalid YAML format: {path}") from e

    if data is None:
        raise ValueError(f"YAML file is empty: {path}")

    if not isinstance(data, dict):
        raise ValueError(
            f"YAML root must be mapping(dict): {path}, actual={type(data)}"
        )
    return data


"""
def require_keys(data: dict, keys: list[str], path: Path) -> None:
    missing = [k for k in keys if k not in data]
    if missing:
        raise KeyError(
            f"Missing required keys in YAML: {missing}, "
            f"file={path}, available_keys={list(data.keys())}"
        )
"""


def require_str(data: dict, key: str, path: Path) -> str:
    if key not in data:
        raise KeyError(
            f"Invalid agents prompt YAML configuration: "
            f"required key '{key}' is not defined. "
            f"Please add  '{key}' to the YAML file. "
            f"file={path}, "
            f"your defined keys={list(data.keys())}"
        )
    value = data[key]
    if not isinstance(value, str):
        raise TypeError(
            f"Invalid type for '{key}' in YAML: {path}, "
            f"expected=str, actual={type(value).__name__}"
        )
    return value


def create_local_context(
    category: str,
    build_check: bool,
    settings: Settings,
) -> LocalContext:
    """
    Load config files, prepare directories, and create LocalContext.
    """
    # output_dir
    output_dir = resolve_path(settings.output_dir)

    # load custom config
    custom_config_file = output_dir / settings.playwright_customconfig_file
    if not custom_config_file.exists():
        logger.error(f"{custom_config_file} not found")
        raise FileNotFoundError(f"{custom_config_file} not found")

    logger.debug(f"custom_config_file: {custom_config_file}")
    with open(custom_config_file, "r") as f:
        custom_config = json.load(f)

    # extract config values
    results = custom_config["results"]
    logger.debug(f"results: {results}")
    playwright_info_file = custom_config["playwright_info_file"]
    logger.debug(f"playwright_info_file: {playwright_info_file}")
    playwright_report_file = custom_config["playwright_report_file"]
    logger.debug(f"playwright_report_file: {playwright_report_file}")
    playwright_report_summary_file = custom_config["playwright_report_summary_file"]
    logger.debug(f"playwright_report_summary_file: {playwright_report_summary_file}")

    now = datetime.now()
    formatted_time = now.strftime("%Y%m%d-%H%M%S")
    step_id = f"StepID-{formatted_time}"
    logger.debug(f"step_id: {step_id}")

    archive_dir = settings.archive_dir
    logger.debug(f"archive_dir: {archive_dir}")
    archive_dir.mkdir(exist_ok=True)
    abs_archive_dir = resolve_path(archive_dir)
    logger.debug(f"abs_archive_dir: {abs_archive_dir}")
    stepid_dir = abs_archive_dir / step_id
    logger.debug(f"stepid_dir: {stepid_dir}")
    stepid_dir.mkdir(exist_ok=False)
    agents_prompt_file = settings.agents_prompt_file
    logger.debug(f"agents_prompt_file: {agents_prompt_file}")

    base = Path().resolve()
    logger.debug(f"base: {base}")
    agents_prompt_filepath = base / DIR_PROMPTS / agents_prompt_file
    logger.debug(f"agents_prompt_filepath: {agents_prompt_filepath}")
    agents_prompt = load_agents_prompt(agents_prompt_filepath)
    logger.debug(f"agents_prompt: {agents_prompt}")
    # require_keys(agents_prompt, keys=["run_tests"], path=agents_prompt_filepath)
    # run_tests = agents_prompt["run_tests"]
    code_gen = require_str(
        data=agents_prompt, key="code_gen", path=agents_prompt_filepath
    )
    logger.debug(f"code_gen: {code_gen}")
    code_check = require_str(
        data=agents_prompt, key="code_check", path=agents_prompt_filepath
    )
    logger.debug(f"code_check: {code_check}")

    return LocalContext(
        category=category,
        output_dir=output_dir,
        max_turns=settings.openai_max_turns,
        gen_code_filepath="",
        is_code_check_error=IsCodeCheckError.NO_ERROR,
        add_prompts=[],
        results_dir=results,
        playwright_info_file=playwright_info_file,
        playwright_report_file=playwright_report_file,
        playwright_report_summary_file=playwright_report_summary_file,
        test_file="dummy.spec.ts",
        before_mtime=0,
        step_id=step_id,
        stepid_dir=stepid_dir,
        build_check=build_check,
        agents_prompt_filepath=str(agents_prompt_filepath),
    )
