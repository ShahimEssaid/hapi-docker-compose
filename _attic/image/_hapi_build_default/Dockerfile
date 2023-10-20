FROM eclipse-temurin:17-jammy
WORKDIR /hapi-build
RUN apt-get update && apt-get install -y \
    maven \
    git \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

RUN ["/usr/bin/git", "config", "--global", "--add", "safe.directory", "*"]
COPY ./copy /
CMD ["hapisetup-hapi-build"]
