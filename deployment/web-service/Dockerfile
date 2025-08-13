FROM python:3.12.3-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY ./deployment/web-service /app
COPY "README.md" "pyproject.toml" "uv.lock" "LICENSE" /app/
COPY ./lap /app/lap

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache --no-dev

# Expose the port the app runs on.
EXPOSE 80

CMD ["/app/.venv/bin/uvicorn", "predict:app", "--port", "80", "--host", "0.0.0.0"]
