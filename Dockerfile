FROM python:3.12-slim AS builder

WORKDIR /build

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .

RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="TaskFlow" \
      org.opencontainers.image.description="Gerenciador de tarefas com FastAPI + PostgreSQL" \
      org.opencontainers.image.version="1.0.0"

RUN groupadd --gid 1001 appgroup && \
    useradd  --uid 1001 \
             --gid appgroup \
             --no-create-home \
             --shell /bin/false \
             appuser

WORKDIR /app

COPY --from=builder /venv /venv

COPY --chown=appuser:appgroup . .

RUN chmod +x entrypoint.sh

ENV PATH="/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PIP_DISABLE_PIP_VERSION_CHECK=1

EXPOSE 8000

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c \
    "import urllib.request, sys; \
     r = urllib.request.urlopen('http://localhost:8000/login', timeout=4); \
     sys.exit(0 if r.status < 500 else 1)"

ENTRYPOINT ["./entrypoint.sh"]