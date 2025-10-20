import shutil
from datetime import datetime
from pathlib import Path

from logger import logger


def resolve_path(path_str: str) -> Path:
    logger.debug(f"resolve_path called: {path_str}")
    p = Path(path_str)
    if p.is_absolute():
        # Absolute path
        if not p.exists():
            raise FileNotFoundError(f"Path '{path_str}' not found")
        logger.debug(f"Absolute path resolved: {p}")
        return p
    # Relative path
    base = Path().resolve()
    logger.debug(f"base: {base}")
    abs_path = (base / p).resolve()
    logger.debug(f"abs_path: {abs_path}")
    if not abs_path.exists():
        raise FileNotFoundError(f"Path '{abs_path}' not found")
    return abs_path


def save_backup(dir: Path, src_file: str):
    logger.debug("save_backup called")
    src_path = dir / src_file
    logger.debug(f"src_path : {src_path}")
    if not src_path.exists():
        logger.error(f"src_file does not exist : {src_path}")
        raise FileNotFoundError(f"source file not found: {src_path}")
    backup_dir = dir / "backup"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stat = src_path.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime)
    timestamp = mtime.strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{timestamp}_{src_file}"
    try:
        shutil.copy2(str(src_path), str(backup_path))
        logger.debug(f"backup: {src_path.name} -> {backup_path.name}")
    except Exception as e:
        logger.error(f"Failed to backup file: {backup_path}, {e}")
        raise e
