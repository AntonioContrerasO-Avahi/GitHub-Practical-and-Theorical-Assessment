# Dockerfile — RAG ingestion pipeline with cron
FROM alpine:3.21

# - curl: install uv
# - util-linux: provides flock
# - bash: run_ingest.sh uses bash
# - dcron: lightweight cron daemon for Alpine
RUN apk add --no-cache curl util-linux bash dcron

# Install uv (manages Python itself — no system Python needed)
RUN curl -Ls https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY ingest.py .
COPY run_ingest.sh .
COPY texts/ ./texts/

# uv sync: reads pyproject.toml, downloads the right Python, installs deps
RUN uv sync

# Log dir + script permissions
RUN mkdir -p /var/log/avahi && chmod +x run_ingest.sh

# Install crontab entry: run at 2:30 AM daily
RUN echo "30 2 * * * /app/run_ingest.sh" | crontab -

# crond -f: run cron in foreground (keeps container alive)
CMD ["crond", "-f", "-l", "2"]