FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 gcc g++ ca-certificates bash \
    && rm -rf /var/lib/apt/lists/*
RUN useradd -m runner
USER runner
WORKDIR /work