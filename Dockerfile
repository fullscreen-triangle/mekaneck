# Mekaneck Pharmaceutical Maxwell Demon Framework
# Multi-stage Dockerfile for Rust + Python validation

# ============================================================================
# Stage 1: Rust Builder
# ============================================================================
FROM rust:1.75-slim as rust-builder

WORKDIR /usr/src/mekaneck

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Rust project files
COPY Cargo.toml ./
COPY mekaneck/ ./mekaneck/

# Build release binary
RUN cargo build --release

# ============================================================================
# Stage 2: Python Validator Builder
# ============================================================================
FROM python:3.11-slim as python-builder

WORKDIR /app

# Install system dependencies for scientific computing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY blindhorse/requirements.txt ./blindhorse/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r blindhorse/requirements.txt

# ============================================================================
# Stage 3: Final Runtime Image
# ============================================================================
FROM python:3.11-slim

LABEL maintainer="Kundai Farai Sachikonye"
LABEL description="Mekaneck: Pharmaceutical Maxwell Demon Framework"
LABEL version="0.1.0"

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libopenblas0 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=python-builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=python-builder /usr/local/bin/ /usr/local/bin/

# Copy Rust binaries from builder
COPY --from=rust-builder /usr/src/mekaneck/target/release/mekaneck /usr/local/bin/

# Copy application code
COPY blindhorse/ ./blindhorse/
COPY mekaneck/ ./mekaneck/
COPY README.md ./

# Create results directory
RUN mkdir -p /app/results

# Set Python path
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command: run validation suite
CMD ["python", "-m", "blindhorse.orchestrator"]

# Alternative commands:
# - Run specific validator: docker run mekaneck python -c "from blindhorse.validators import HardwareOscillationValidator; HardwareOscillationValidator().run_validation()"
# - Run Rust binary: docker run mekaneck mekaneck
# - Interactive shell: docker run -it mekaneck bash

