FROM eclipse-temurin:17-jammy

RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    unzip \
    curl \
    postgresql-client \
    maven \
    git \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

RUN ["/usr/bin/git", "config", "--global", "--add", "safe.directory", "*"]
COPY ./root /

WORKDIR /hapi-run-cli

RUN python3 --version

RUN python3 -m venv .venv; \
    . .venv/bin/activate; \
    pip install -U pip poetry; \
    poetry install;

ENTRYPOINT ["hapirun"]

CMD ["run-hapi", "--help"]