import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from subprocess import CompletedProcess

from logger import logger

BACKUP_DIR = "backup"


def run_cmd(command: list[str], output_path: Path, cwd: str) -> CompletedProcess:
    logger.debug("run_cmd called")

    # Check output directory
    output_dir = output_path.parent
    logger.debug(f"output_dir: {output_dir}")
    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")

    # Create results and backup directory
    results_dir = output_dir
    backup_dir = results_dir / BACKUP_DIR
    logger.debug(f"results_dir: {results_dir}")
    logger.debug(f"backup_dir: {backup_dir}")
    backup_dir.mkdir(exist_ok=True)

    # for backup
    if output_path.exists():
        mtime = datetime.fromtimestamp(output_path.stat().st_mtime)
        timestamp = mtime.strftime("%Y%m%d_%H%M%S")

        stem = output_path.stem
        suffix = output_path.suffix.lstrip(".")

        backup_filename = f"{stem}_{timestamp}.{suffix}"
        backup_path = results_dir / backup_dir / backup_filename
        logger.debug(f"backup_path: {backup_path}")

        shutil.copy2(output_path, backup_path)
        logger.debug(f"backup created: {backup_path}")

    with output_path.open("w", encoding="utf-8") as f:
        result = subprocess.run(
            command, cwd=cwd, stdout=f, stderr=subprocess.PIPE, text=True
        )

    return result
