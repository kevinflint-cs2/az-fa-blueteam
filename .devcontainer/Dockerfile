# Minimal Dockerfile based on Microsoft's Python 3.11 devcontainer image
ARG VARIANT="0-3.11"
FROM mcr.microsoft.com/devcontainers/python:${VARIANT}

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Basic tooling
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
       ca-certificates curl gnupg lsb-release apt-transport-https build-essential unzip git \
  && rm -rf /var/lib/apt/lists/*

# Install Azure CLI (official script)
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Install Microsoft package feed and try apt install for Functions Core Tools (preferred)
RUN curl -fsSL https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb -o /tmp/packages-microsoft-prod.deb \
  && dpkg -i /tmp/packages-microsoft-prod.deb \
  && rm -f /tmp/packages-microsoft-prod.deb \
  && apt-get update \
  && apt-get install -y --no-install-recommends azure-functions-core-tools-4 || true \
  && rm -rf /var/lib/apt/lists/*

# If func isn't present (apt failed because of arch), fallback to npm install (install nodejs first)
RUN if ! command -v func >/dev/null 2>&1; then \
      echo 'apt install of azure-functions-core-tools failed or not available — installing node 18 and npm fallback'; \
      curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
      apt-get update && apt-get install -y --no-install-recommends nodejs npm && \
      npm install -g azure-functions-core-tools@4 --unsafe-perm=true || true; \
    else \
      echo 'func present via apt'; \
    fi

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Switch to non-root user from base image
USER vscode
WORKDIR /workspaces/${localWorkspaceFolderBasename:-repo}
