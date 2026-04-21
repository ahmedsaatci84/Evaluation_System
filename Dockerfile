# ── Stage: production image ──────────────────────────────────────────────────
FROM python:3.11-slim

# Install system packages required for ODBC Driver 17 + pyodbc
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gnupg2 \
        apt-transport-https \
        ca-certificates \
        unixodbc-dev \
    # Add Microsoft package repository
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
        | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] \
        https://packages.microsoft.com/debian/12/prod bookworm main" \
        > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project
COPY . .

# Fix line endings on the entrypoint (safe for Windows-developed repos)
# then make it executable and collect static files
RUN sed -i 's/\r$//' entrypoint.sh \
    && chmod +x entrypoint.sh \
    && python manage.py collectstatic --no-input

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
