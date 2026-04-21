"""
Database backup utilities.

Contains helpers shared by the backup views so the views themselves
remain thin HTTP handlers without duplicate infrastructure logic.
"""
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def get_backup_dir(base_dir: Path) -> Path:
    backup_dir = base_dir / 'backups'
    backup_dir.mkdir(exist_ok=True)
    return backup_dir


def get_db_engine(databases: dict) -> str:
    engine = databases['default']['ENGINE'].lower()
    if 'mssql' in engine or 'sql_server' in engine:
        return 'mssql'
    if 'sqlite' in engine:
        return 'sqlite'
    if 'postgresql' in engine or 'postgres' in engine:
        return 'postgresql'
    if 'mysql' in engine:
        return 'mysql'
    return 'unknown'


def format_file_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def list_backups(backup_dir: Path) -> list[dict]:
    backups = []
    if not backup_dir.exists():
        return backups
    for f in sorted(
        list(backup_dir.glob('*.bak')) + list(backup_dir.glob('*.json')),
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    ):
        try:
            stat = f.stat()
            backups.append({
                'name': f.name,
                'size': stat.st_size,
                'size_formatted': format_file_size(stat.st_size),
                'created': __import__('datetime').datetime.fromtimestamp(stat.st_mtime),
                'path': str(f),
                'type': 'Native DB' if f.suffix == '.bak' else 'JSON Data',
            })
        except Exception as exc:
            logger.error("Error reading backup file %s: %s", f, exc)
    return backups
