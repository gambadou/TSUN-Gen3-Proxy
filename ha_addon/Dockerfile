ARG BUILD_FROM=ghcr.io/hassio-addons/base:18.1.2
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install system dependencies
RUN \
    apk add --no-cache \
        python3=~3.12 \
        python3-dev=~3.12 \
        py3-pip \
        gcc \
        musl-dev \
        linux-headers \
        tzdata \
    && pip3 install --no-cache-dir --upgrade pip

# Copy requirements first for better Docker layer caching
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy application files
COPY app/ /app/
COPY rootfs/ /

# Set working directory
WORKDIR /app

# Ensure run script is executable
RUN chmod a+x /etc/services.d/tsun-proxy/run

# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_DESCRIPTION
ARG BUILD_NAME
ARG BUILD_REF
ARG BUILD_REPOSITORY
ARG BUILD_VERSION
LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version="${BUILD_VERSION}" \
    maintainer="Stefan Allius" \
    org.opencontainers.image.title="${BUILD_NAME}" \
    org.opencontainers.image.description="${BUILD_DESCRIPTION}" \
    org.opencontainers.image.vendor="TSUN Gen3 Proxy" \
    org.opencontainers.image.authors="Stefan Allius" \
    org.opencontainers.image.licenses="BSD-3-Clause" \
    org.opencontainers.image.url="https://github.com/s-allius/tsun-gen3-proxy" \
    org.opencontainers.image.source="https://github.com/s-allius/tsun-gen3-proxy" \
    org.opencontainers.image.documentation="https://s-allius.github.io/tsun-gen3-proxy/" \
    org.opencontainers.image.created="${BUILD_DATE}" \
    org.opencontainers.image.revision="${BUILD_REF}" \
    org.opencontainers.image.version="${BUILD_VERSION}"