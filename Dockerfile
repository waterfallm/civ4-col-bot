# ── Stage 1: builder ────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ── Stage 2: runtime ────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Target architecture: linux/arm64 (Raspberry Pi cluster)
# Build with: docker buildx build --platform linux/arm64 -t civ4bot:latest .

# Non-root user for security
RUN useradd --create-home --uid 1000 civ4bot

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /root/.local /home/civ4bot/.local

# Copy application source
COPY src/ src/
COPY config.json .

# Ensure the user's local bin is on PATH
ENV PATH=/home/civ4bot/.local/bin:$PATH

USER civ4bot

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
