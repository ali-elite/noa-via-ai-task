# Use the official uv image to get the binary
FROM ghcr.io/astral-sh/uv:latest AS uv

# Use a standard Python slim image for the runtime
FROM python:3.13-slim

# Copy the uv binary from the first stage
COPY --from=uv /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy project files for dependency installation
COPY pyproject.toml uv.lock ./

# Install dependencies using uv sync (installs into .venv by default)
# We use --no-install-project to cache the dependencies separately
RUN uv sync --frozen --no-install-project

# Copy source code and data
COPY src/ /app/src/
COPY data/ /app/data/

# Place .venv on the path
ENV PATH="/app/.venv/bin:$PATH"

# Expose port
EXPOSE 8080

# Command to run the application
# We use 'uv run' to ensure the environment is correctly activated
CMD ["uv", "run", "python", "src/app.py"]
