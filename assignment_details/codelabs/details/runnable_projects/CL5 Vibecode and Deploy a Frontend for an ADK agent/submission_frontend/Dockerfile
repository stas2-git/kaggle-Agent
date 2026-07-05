FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY dashboard ./dashboard
COPY static ./static
COPY main.py ./main.py

ENV PORT=8080
EXPOSE 8080
CMD ["uv", "run", "python", "main.py"]
