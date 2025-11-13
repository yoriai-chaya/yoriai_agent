import shutil
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


def archive(src_dir: Path, src_file: str, stepid_dir: Path, dir: Path):
    """
    archive: back up the generated source files, test report files, etc.

    Args:
        src_dir: directory of source file
        src_file: source file to be backed up
        stepid_dir: stepid directory (contained in the local context)
        dir: relative directory from stepid_dir
    """
    logger.debug("archive called")
    src_path = src_dir / src_file
    logger.debug(f"src_path : {src_path}")

    backup_dir = stepid_dir / dir
    logger.debug(f"backup_dir : {backup_dir}")
    backup_dir.mkdir(exist_ok=True)
    backup_path = backup_dir / src_file

    try:
        shutil.copy2(str(src_path), str(backup_path))
        logger.debug(f"backup: {src_path.name} -> {backup_path.name}")
    except Exception as e:
        logger.error(f"Failed to backup file: {backup_path}, {e}")
        raise e
