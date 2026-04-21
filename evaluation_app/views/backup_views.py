import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import FileResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST

from ..decorators import admin_required
from ..services import get_backup_dir, get_db_engine, format_file_size, list_backups

logger = logging.getLogger(__name__)


@admin_required
@ensure_csrf_cookie
def database_backup(request):
    try:
        backup_dir = get_backup_dir(settings.BASE_DIR)
        backups = list_backups(backup_dir)
        db_config = settings.DATABASES['default']
        db_engine = get_db_engine(settings.DATABASES)
        total_size = sum(b['size'] for b in backups)
        return render(request, 'evaluation_app/backup/database_backup.html', {
            'backups': backups[:20],
            'total_backups': len(backups),
            'total_size': format_file_size(total_size),
            'db_info': {
                'name': db_config.get('NAME', 'Unknown'),
                'host': db_config.get('HOST', 'localhost'),
                'engine': db_engine.upper(),
                'engine_type': db_engine,
            },
            'backup_dir': str(backup_dir),
        })
    except Exception as e:
        logger.error("Database backup page error: %s", e)
        messages.error(request, f'Error loading backup page: {str(e)}')
        return redirect('dashboard')


@csrf_exempt
@require_POST
@admin_required
def database_backup_create(request):
    try:
        backup_dir = get_backup_dir(settings.BASE_DIR)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        db_config = settings.DATABASES['default']
        db_name = db_config.get('NAME', 'database')
        db_engine = get_db_engine(settings.DATABASES)
        db_name_clean = os.path.basename(str(db_name))
        backup_filename = f'{db_name_clean}_backup_{timestamp}.bak'
        backup_path = backup_dir / backup_filename
        backup_method = "native"

        if db_engine == 'mssql':
            try:
                backup_path_str = str(backup_path.absolute()).replace('/', '\\')
                with connection.cursor() as cursor:
                    cursor.execute("SELECT HAS_PERMS_BY_NAME(NULL, NULL, 'BACKUP DATABASE')")
                    if not cursor.fetchone()[0]:
                        raise PermissionError("Fallback to dumpdata")
                    cursor.execute(f"""
                        BACKUP DATABASE [{db_name}]
                        TO DISK = N'{backup_path_str}'
                        WITH FORMAT, INIT, NAME = N'{db_name}-Full Database Backup',
                        SKIP, NOREWIND, NOUNLOAD, COMPRESSION, STATS = 10
                    """)
                    cursor.execute(f"RESTORE VERIFYONLY FROM DISK = N'{backup_path_str}'")
            except PermissionError:
                backup_filename = f'{db_name_clean}_backup_{timestamp}.json'
                backup_path = backup_dir / backup_filename
                result = subprocess.run(
                    [sys.executable, 'manage.py', 'dumpdata',
                     '--natural-foreign', '--natural-primary', '--indent', '2'],
                    capture_output=True, text=False, cwd=settings.BASE_DIR,
                    env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
                )
                if result.returncode != 0:
                    raise Exception(f"Django dumpdata failed: {result.stderr.decode('utf-8', errors='replace')}")
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(result.stdout.decode('utf-8', errors='replace'))
                backup_method = "django_dumpdata"

        elif db_engine == 'sqlite':
            db_path = Path(db_name)
            if not db_path.exists():
                raise FileNotFoundError(f"SQLite database not found: {db_name}")
            shutil.copy2(db_path, backup_path)

        elif db_engine == 'postgresql':
            result = subprocess.run([
                'pg_dump', '-h', db_config.get('HOST', 'localhost'),
                '-U', db_config.get('USER', 'postgres'), '-F', 'c',
                '-f', str(backup_path), db_name,
            ], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"pg_dump failed: {result.stderr}")

        elif db_engine == 'mysql':
            result = subprocess.run([
                'mysqldump', '-h', db_config.get('HOST', 'localhost'),
                '-u', db_config.get('USER', 'root'),
                f'-p{db_config.get("PASSWORD", "")}',
                '--result-file', str(backup_path), db_name,
            ], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"mysqldump failed: {result.stderr}")
        else:
            raise NotImplementedError(f"Backup not implemented for {db_engine}")

        if not backup_path.exists():
            raise FileNotFoundError("Backup file was not created")

        file_size = backup_path.stat().st_size
        success_msg = (
            f'Database backup created (JSON format). File: {backup_filename}'
            if backup_method == "django_dumpdata"
            else f'Database backup created successfully! File: {backup_filename}'
        )
        messages.success(request, success_msg)
        return JsonResponse({
            'success': True, 'message': success_msg,
            'filename': backup_filename, 'size': file_size,
            'size_formatted': format_file_size(file_size), 'backup_method': backup_method,
        })

    except PermissionError as e:
        return JsonResponse({'success': False, 'error': f'Permission denied: {e}'}, status=403)
    except Exception as e:
        logger.error("Backup creation failed: %s", e)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_POST
@admin_required
def database_backup_restore(request, filename):
    try:
        backup_dir = get_backup_dir(settings.BASE_DIR)
        backup_path = backup_dir / filename

        if not str(backup_path.resolve()).startswith(str(backup_dir.resolve())):
            raise PermissionError('Invalid backup file path!')
        if not backup_path.exists():
            raise FileNotFoundError('Backup file not found!')

        if backup_path.suffix == '.json':
            result = subprocess.run(
                [sys.executable, 'manage.py', 'loaddata', str(backup_path)],
                capture_output=True, text=False, cwd=settings.BASE_DIR,
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
            )
            if result.returncode != 0:
                raise Exception(f"Django loaddata failed: {result.stderr.decode('utf-8', errors='replace')}")
            messages.success(request, f'Database restored successfully from: {filename}')
            return JsonResponse({'success': True, 'message': f'Restored from JSON backup: {filename}'})

        db_config = settings.DATABASES['default']
        db_name = db_config.get('NAME', 'database')
        db_engine = get_db_engine(settings.DATABASES)

        if db_engine == 'mssql':
            backup_path_str = str(backup_path.absolute()).replace('/', '\\')
            with connection.cursor() as cursor:
                cursor.execute("SELECT HAS_PERMS_BY_NAME(NULL, NULL, 'BACKUP DATABASE')")
                if not cursor.fetchone()[0]:
                    raise PermissionError("No RESTORE DATABASE permission")
                cursor.execute(f"ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
                try:
                    cursor.execute(f"""
                        RESTORE DATABASE [{db_name}]
                        FROM DISK = N'{backup_path_str}'
                        WITH REPLACE, RECOVERY, STATS = 10
                    """)
                finally:
                    cursor.execute(f"ALTER DATABASE [{db_name}] SET MULTI_USER")

        elif db_engine == 'sqlite':
            db_path = Path(db_name)
            if db_path.exists():
                shutil.copy2(db_path, db_path.with_suffix('.bak.current'))
            shutil.copy2(backup_path, db_path)

        elif db_engine == 'postgresql':
            result = subprocess.run([
                'pg_restore', '-h', db_config.get('HOST', 'localhost'),
                '-U', db_config.get('USER', 'postgres'),
                '-d', db_name, '--clean', str(backup_path),
            ], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"pg_restore failed: {result.stderr}")

        elif db_engine == 'mysql':
            with open(backup_path, 'r') as f:
                result = subprocess.run([
                    'mysql', '-h', db_config.get('HOST', 'localhost'),
                    '-u', db_config.get('USER', 'root'),
                    f'-p{db_config.get("PASSWORD", "")}', db_name,
                ], stdin=f, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"mysql restore failed: {result.stderr}")
        else:
            raise NotImplementedError(f"Restore not implemented for {db_engine}")

        messages.success(request, f'Database restored from: {filename}')
        return JsonResponse({'success': True, 'message': f'Restored from: {filename}'})

    except PermissionError as e:
        return JsonResponse({'success': False, 'error': f'Permission denied: {e}'}, status=403)
    except Exception as e:
        logger.error("Restore failed: %s", e)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@admin_required
def database_backup_download(request, filename):
    try:
        backup_dir = get_backup_dir(settings.BASE_DIR)
        backup_path = backup_dir / filename
        if not str(backup_path.resolve()).startswith(str(backup_dir.resolve())):
            messages.error(request, 'Invalid backup file path!')
            return redirect('database_backup')
        if not backup_path.exists():
            messages.error(request, 'Backup file not found!')
            return redirect('database_backup')
        return FileResponse(open(backup_path, 'rb'), as_attachment=True, filename=filename)
    except Exception as e:
        logger.error("Download failed: %s", e)
        messages.error(request, f'Download failed: {str(e)}')
        return redirect('database_backup')


@admin_required
def database_backup_delete(request, filename):
    if request.method != 'POST':
        return redirect('database_backup')
    try:
        backup_dir = get_backup_dir(settings.BASE_DIR)
        backup_path = backup_dir / filename
        if not str(backup_path.resolve()).startswith(str(backup_dir.resolve())):
            messages.error(request, 'Invalid backup file path!')
            return redirect('database_backup')
        if backup_path.exists():
            backup_path.unlink()
            messages.success(request, f'Backup deleted: {filename}')
        else:
            messages.warning(request, 'Backup file not found!')
    except Exception as e:
        logger.error("Delete failed: %s", e)
        messages.error(request, f'Delete failed: {str(e)}')
    return redirect('database_backup')
