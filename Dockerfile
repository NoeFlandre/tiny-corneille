FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.11.16 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY pyproject.toml uv.lock README.md .python-version ./
COPY src ./src
RUN uv sync --locked --no-dev

RUN useradd --create-home --uid 10001 app
WORKDIR /work
USER app

ENTRYPOINT ["tiny-corneille"]
CMD ["--help"]
