FROM eclipse-temurin:17-jammy
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    unzip \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /hapi
#RUN #mkdir -p /hapi/.fhir
#RUN ln -s /hapi/.fhir /.fhir
COPY ./copy /
CMD ["hapisetup-hapi-run"]

