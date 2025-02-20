FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir pip setuptools wheel && \
    pip install --no-cache-dir -e .

# Copy project code
COPY . .

# Create directories for data and credentials
RUN mkdir -p data credentials

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create a non-root user
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Command to run when container starts
ENTRYPOINT ["python", "-m", "src.instaagent.main"]
CMD ["run"]