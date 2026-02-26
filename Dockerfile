# Multi-stage Dockerfile for CumulusCI, Salesforce CLI, and Robot Framework
FROM python:3.11-slim as base

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SF_CLI_VERSION=latest \
    # Disable CumulusCI analytics
    CUMULUSCI_DISABLE_ANALYTICS=true

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core utilities
    curl \
    git \
    gnupg \
    unzip \
    wget \
    ca-certificates \
    # Browser dependencies for Robot Framework/Selenium
    chromium \
    chromium-driver \
    libnss3 \
    libfontconfig1 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf-xlib-2.0-0 \
    libnspr4 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    fonts-liberation \
    # Build dependencies for Python packages
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Salesforce CLI
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get update && apt-get install -y nodejs && \
    npm install --global @salesforce/cli && \
    sf version && \
    rm -rf /var/lib/apt/lists/*

# Install SFDMU plugin
RUN sf plugins install sfdmu

# Upgrade pip and install Python tools
# Pin setuptools to a version that includes pkg_resources (required by CumulusCI dependencies)
RUN pip install --no-cache-dir --upgrade pip 'setuptools<71' wheel

# Install CumulusCI first (installs compatible selenium 3.x and robotframework-seleniumlibrary 5.x)
RUN pip install --no-cache-dir cumulusci

# Install Robot Framework requirements with version constraints compatible with CumulusCI
# Note: CumulusCI requires selenium<4 and robotframework-seleniumlibrary<6
# These versions are pinned to avoid conflicts while maintaining functionality
# IMPORTANT: Quote version specifiers containing < or > to prevent shell interpretation
RUN pip install --no-cache-dir \
    robotframework-seleniumlibrary==5.1.3 \
    selenium==3.141.0 \
    'robotframework>=6,<8' \
    'webdriver-manager>=4,<5' \
    'urllib3>=2.6.3' && \
    pip install --no-cache-dir --force-reinstall --no-deps 'setuptools<71'

# Set Chrome/Chromium options for Robot Framework
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu"

# Create working directory
WORKDIR /workspace

# Verify installations
RUN echo "=== Verifying installations ===" && \
    python --version && \
    pip --version && \
    cci version && \
    (sf version || true) && \
    (sf plugins || true) && \
    (robot --version || true) && \
    echo "=== All tools installed successfully ==="

# Default command
CMD ["/bin/bash"]
