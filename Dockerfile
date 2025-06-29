FROM node:latest AS frontend

WORKDIR /frontend
COPY /eira /frontend

RUN npm install -g npm
RUN npm install --force

FROM python:3.13.5-slim

LABEL org.opencontainers.image.source=https://github.com/pythonistaguild/tio-token-relay
LABEL org.opencontainers.image.description="Container for running TwitchIO Token Relay Service"
LABEL org.opencontainers.image.licenses="Apache-2.0 license"

RUN mkdir -p /etc/apt/keyrings \
    && apt update -y \
    && apt-get install --no-install-recommends -y \
    # deps for building python deps
    git \
    build-essential \
    libcurl4-gnutls-dev \
    gnutls-dev \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# copy project requirement files here to ensure they will be cached.
WORKDIR /app
COPY ember/requirements.txt ./

# install runtime deps
RUN pip install -Ur requirements.txt

COPY /ember /app/
COPY --from=frontend /frontend/dist eira/dist

ENTRYPOINT python -O main.py