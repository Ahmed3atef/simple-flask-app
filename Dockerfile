FROM python:3.14-alpine

# Install build dependencies
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev curl

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.local/bin:$PATH"

# Create non-root user
RUN addgroup -S app && adduser -S -G app app

WORKDIR /app

# Copy dependency files first (better caching)
COPY pyproject.toml uv.lock* ./

# Install dependencies as root
RUN uv sync --frozen

# Copy application code
COPY . .

# Change ownership and switch to non-root user
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Set Flask environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run with uv
CMD ["uv", "run", "flask", "run"]