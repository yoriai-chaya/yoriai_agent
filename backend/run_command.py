import subprocess
from pathlib import Path
from subprocess import CompletedProcess

from common import save_backup
from logger import logger


def run_cmd(command: list[str], output_path: Path, cwd: str) -> CompletedProcess:
    logger.debug("run_cmd called")

    # Check output directory
    output_dir = output_path.parent
    logger.debug(f"output_dir: {output_dir}")
    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")

    # for backup
    logger.debug(f"output_path: {output_path}")
    filename = output_path.name
    logger.debug(f"filename: {filename}")
    if output_path.exists():
        save_backup(output_dir, filename)

    with output_path.open("w", encoding="utf-8") as f:
        result = subprocess.run(
            command, cwd=cwd, stdout=f, stderr=subprocess.PIPE, text=True
        )

    return result
