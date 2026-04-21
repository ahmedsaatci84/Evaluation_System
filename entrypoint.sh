#!/bin/sh
set -e

echo "================================================================"
echo "  Evaluation App — Container Startup"
echo "================================================================"

# ── Wait for SQL Server ──────────────────────────────────────────────────────
echo "[1/3] Waiting for SQL Server at ${DB_HOST}:${DB_PORT:-1433} ..."
until python - <<'PYEOF'
import pyodbc, os, sys
try:
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER={host},{port};"
        "UID={user};PWD={pwd};"
        "TrustServerCertificate=yes".format(
            host=os.environ["DB_HOST"],
            port=os.environ.get("DB_PORT", "1433"),
            user=os.environ["DB_USER"],
            pwd=os.environ["DB_PASSWORD"],
        ),
        timeout=3,
    )
    conn.close()
except Exception as exc:
    print("  Not ready:", exc)
    sys.exit(1)
PYEOF
do
    echo "  SQL Server not ready yet — retrying in 5 s..."
    sleep 5
done
echo "  SQL Server is up."

# ── Create the database if it does not exist ─────────────────────────────────
echo "[2/3] Ensuring database '${DB_NAME:-evaluation_db}' exists ..."
python - <<'PYEOF'
import pyodbc, os
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER={host},{port};"
    "UID={user};PWD={pwd};"
    "TrustServerCertificate=yes".format(
        host=os.environ["DB_HOST"],
        port=os.environ.get("DB_PORT", "1433"),
        user=os.environ["DB_USER"],
        pwd=os.environ["DB_PASSWORD"],
    ),
    autocommit=True,
)
db = os.environ.get("DB_NAME", "evaluation_db")
conn.execute(
    f"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'{db}') "
    f"CREATE DATABASE [{db}]"
)
conn.close()
print(f"  Database '{db}' is ready.")
PYEOF

# ── Django migrations ────────────────────────────────────────────────────────
echo "[3/3] Running Django migrations ..."
python manage.py migrate --no-input

echo "================================================================"
echo "  Starting Waitress on 0.0.0.0:8000 ..."
echo "================================================================"
exec waitress-serve --port=8000 --threads=4 --host=0.0.0.0 EvaluationProject.wsgi:application
