# Docker Setup

This project includes a Docker workflow for running CumulusCI, Salesforce CLI, SFDMU, and Robot Framework in a container while sharing org state with the host.

## What Is Included

- `Dockerfile` builds `rlm-base-cci-robot:latest`
- `docker-compose.yml` for local development
- `docker-compose.ci.yml` for CI keychain override
- `docker-cci.sh` wrapper for day-to-day commands
- `docker/get-cci-key.sh` helper for host key extraction
- `docker/test-org-sharing.sh` smoke test

## Quick Start

```bash
# From repo root
cp .env.example .env
echo "CUMULUSCI_KEY=$(./docker/get-cci-key.sh 2>/dev/null)" >> .env

docker compose build
./docker-cci.sh cci version
./docker-cci.sh sf --version
./docker-cci.sh bash -lc "robot --version || true"
```

## Org Sharing Model

Container and host share these mounts:

- `${HOME}/.cumulusci -> /root/.cumulusci`
- `${HOME}/.sf -> /root/.sf`
- `${HOME}/.sfdx -> /root/.sfdx`
- repo workspace -> `/workspace`

Encryption is coordinated by `CUMULUSCI_KEY` from `.env`.

## Networking

`docker-compose.yml` defaults to `bridge` mode for portability.

Set this in `.env` when host networking is required:

```bash
DOCKER_NETWORK_MODE=host
```

## CI/CD

Use the CI override for environment-based keychain auth:

```bash
export SFDX_AUTH_URL="force://PlatformCLI::..."
docker compose -f docker-compose.yml -f docker-compose.ci.yml run --rm cci-robot cci org list
```

## Verification Checklist

```bash
docker compose build
./docker-cci.sh cci version
./docker-cci.sh sf --version
./docker-cci.sh bash -lc "robot --version || true"
./docker/test-org-sharing.sh
```

`docker/test-org-sharing.sh` can still fail if host keychain/key material and existing local CCI state are inconsistent. In that case, refresh `.env` and re-auth orgs using a single key source.
