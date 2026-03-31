# Docker image for CumulusCI, Salesforce CLI, SFDMU, and Robot Framework
FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONWARNINGS="ignore:pkg_resources is deprecated as an API:UserWarning" \
    CUMULUSCI_DISABLE_ANALYTICS=true \
    SF_AUTOUPDATE_DISABLE=true \
    CHROME_BIN=/usr/bin/chromium \
    CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu"

# Install OS dependencies and Chromium for headless Robot/Selenium runs.
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    chromium \
    chromium-driver \
    curl \
    fonts-liberation \
    git \
    gnupg \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libffi-dev \
    libfontconfig1 \
    libgdk-pixbuf-xlib-2.0-0 \
    libnss3 \
    libnspr4 \
    libssl-dev \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    nodejs \
    npm \
    python3-dev \
    unzip \
    wget \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js LTS and Salesforce CLI from npm (official recommended path).
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install --global @salesforce/cli \
    && sf --version \
    && rm -rf /var/lib/apt/lists/*

# Install SFDMU plugin.
RUN sf plugins install sfdmu --force

WORKDIR /workspace

# Copy dependency manifest from repo so image build is self-contained.
COPY robot/requirements.txt /tmp/robot-requirements.txt

# Install Python toolchain and project-required automation dependencies.
RUN python -m pip install --no-cache-dir --upgrade pip "setuptools>=75,<81" wheel \
    && python -m pip install --no-cache-dir cumulusci \
    && python -m pip install --no-cache-dir -r /tmp/robot-requirements.txt \
    && python -m pip install --no-cache-dir \
        "selenium==3.141.0" \
        "robotframework-seleniumlibrary==5.1.3" \
    && rm -f /tmp/robot-requirements.txt

# Verify critical tool availability at build time.
RUN python --version \
    && pip --version \
    && cci version \
    && sf --version \
    && (robot --version || true)

CMD ["/bin/bash"]
