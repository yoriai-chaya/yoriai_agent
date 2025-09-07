import re
from typing import Optional


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
