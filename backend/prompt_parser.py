import re
from pathlib import Path
from typing import Optional

from base import LocalContext
from logger import logger


def resolve_placeholders(prompt: str, context: LocalContext) -> str:
    def replacer(match):
        logger.debug("replacer called")
        file_path = match.group(1).strip()
        logger.debug(f"file_path: {file_path}")
        full_path = context.output_dir / file_path
        logger.debug(f"full_path: {full_path}")
        try:
            content = Path(str(full_path)).read_text(encoding="utf-8")
            return f"[{file_path}]\n```{Path(file_path).suffix.lstrip('.')}\n{content}\n```"
        except FileNotFoundError as e:
            raise e

    filled = re.sub(r"\{\{file:(.+?)\}\}", replacer, prompt)
    return filled


def extract_header_section(prompt: str) -> str:
    """
    Extracts the range from # Header to # Body from the entire prompt.
    """
    header_pattern = re.compile(
        r"#\s*Header(.*?)(?=#\s*Body|$)", re.DOTALL | re.IGNORECASE
    )
    match = header_pattern.search(prompt)
    return match.group(1).strip() if match else ""


def parse_header_fields(header_text: str) -> dict[str, str]:
    """
    Converts the header section into a dictionary in key:value format.
    - "Key:Value" format
    "Key:Value" format
    Both are supported.
    """
    fields: dict[str, str] = {}
    for line in header_text.splitlines():
        line = line.strip("- ").strip()
        if not line:
            continue
        match = re.match(r"(\w+)\s*:\s*(.+)", line)
        if match:
            key, value = match.groups()
            fields[key.strip()] = value.strip()
    return fields


def extract_from_prompt(prompt: str, key: str) -> Optional[str]:
    """
    Extracts the value of the specified key from the header section.
    """
    header_text = extract_header_section(prompt)
    fields = parse_header_fields(header_text)
    return fields.get(key)


def parse_build_check(value: Optional[str]) -> bool:
    """
    Convert BuildCheck header value to bool.
    Returns:
        True  : "on"
        False : "off" or not specified
    """
    if value is None:
        return False

    v = value.strip().lower()
    if v == "on":
        return True
    if v == "off":
        return False
    return False
