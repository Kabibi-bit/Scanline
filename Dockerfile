FROM python:3.12-slim
 
WORKDIR /app
 
# Build tools needed for any packages that require them
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
 
# Redirect Rust's build cache to a folder we know is writable,
# since some Python packages (pydantic-core) compile via Rust
# and were failing to write to their default system location.
ENV CARGO_HOME=/app/.cargo
ENV RUSTUP_HOME=/app/.rustup
RUN mkdir -p /app/.cargo /app/.rustup
 
RUN pip install --upgrade pip
 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
COPY . .
 
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
 
