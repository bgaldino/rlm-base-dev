# Docker Setup

This project uses an `SFDX_AUTH_URL`-only Docker workflow for running CumulusCI, Salesforce CLI, SFDMU, and Robot Framework in a container.

## What Is Included

- `Dockerfile` builds `rlm-base-cci-robot:latest`
- `docker-compose.yml` for local development
- `docker-compose.ci.yml` for CI usage
- `docker-cci.sh` wrapper for day-to-day commands
- `docker/docker-test-org-sharing.sh` smoke test

## Quick Start

```bash
# From repo root
cp .env.example .env
# Required: add your Dev Hub auth URL from host
# sf org display --verbose --target-org <DEV_HUB_ALIAS> | grep "Sfdx Auth Url"
# SFDX_AUTH_URL=force://PlatformCLI::...

docker compose build
./docker-cci.sh cci version
./docker-cci.sh sf --version
./docker-cci.sh bash -lc "robot --version || true"
```

## Fresh Environment Setup (Step-by-Step)

Use this sequence on a brand-new machine:

1. Verify required host tools:

   ```bash
   docker --version
   docker compose version
   sf --version
   ```

2. Create local env file:

   ```bash
   cp .env.example .env
   ```

3. Ensure your Dev Hub is authenticated on host `sf`:

   ```bash
   sf org list
   # If needed:
   sf org login web --alias <DEV_HUB_ALIAS> --set-default-dev-hub
   ```

4. Generate auth URL and populate `.env`:

   ```bash
   sf org display --verbose --target-org <DEV_HUB_ALIAS> | rg "Sfdx Auth Url"
   ```

   Set these values in `.env`:

   ```bash
   SFDX_AUTH_URL=force://PlatformCLI::...
   DOCKER_NETWORK_MODE=bridge
   ```

   `DOCKER_DEVHUB_ALIAS` is optional. If unset, Docker auto-uses `dockerDevHub`.

5. Build and verify Docker runtime:

   ```bash
   docker compose build
   ./docker-cci.sh cci version
   ./docker-cci.sh sf --version
   ./docker-cci.sh cci org list
   ```

6. Run a flow/build in Docker:

   ```bash
   ./docker-cci.sh cci flow run <FLOW_NAME> --org <ORG_NAME>
   ```

## Authentication Model

Docker uses isolated local state directories:

- `.docker/state/cumulusci -> /root/.cumulusci`
- `.docker/state/sf -> /root/.sf`
- `.docker/state/sfdx -> /root/.sfdx`
- repo workspace -> `/workspace`

Docker uses `CUMULUSCI_KEYCHAIN_CLASS=EnvironmentProjectKeychain` and reads org auth from environment variables.
`SFDX_AUTH_URL` is required and is the only supported auth bootstrap path for Docker.

This design intentionally avoids mutating host auth/keychain files during Docker runs.
Container encryption remains enabled by default (`SF_DISABLE_ENCRYPTION=false` unless explicitly overridden).

## Incident History and Critical Behavior

### Issue Encountered (March 2026)

While validating Docker workflow updates, host `sf org list` showed:

- `BG_DEVHUB` -> `AuthDecryptError`
- Other orgs remained `Connected`

The observed error text was: `Failed to decipher auth data. reason: Unsupported state or unable to authenticate data.`

### Why It Happened

The earlier Docker configuration mounted host auth state directly into the container:

- `${HOME}/.sf -> /root/.sf`
- `${HOME}/.sfdx -> /root/.sfdx`

That made container and host share the same Salesforce CLI auth store. Any container-side auth read/write could affect host-visible auth records. On macOS, host keychain-backed credential behavior can diverge from Linux container crypto behavior, so a single alias can become unreadable and surface as `AuthDecryptError`.

### Why This Is Critical

- This is not just a Docker-local failure; it can break host Dev Hub aliases used for daily development.
- The failure is subtle (one alias breaks while others still work), which can delay detection.
- It can interrupt unrelated workflows (`cci flow run`, scratch org creation, CI prep) because Dev Hub auth is a dependency.

### Preventive Controls Implemented

To prevent recurrence, Docker auth/config state is now isolated under repository-local paths:

- `.docker/state/sf`
- `.docker/state/sfdx`
- `.docker/state/cumulusci`

No host `~/.sf` or `~/.sfdx` bind-mount is used in local Docker runs.

### Operational Guidance

- Treat container auth as disposable and re-bootstrap with `SFDX_AUTH_URL` when needed.
- Keep host aliases for interactive development and container aliases for Docker automation.
- If `AuthDecryptError` appears on host, re-auth the affected alias (`sf org login web -a <alias>`), then continue with isolated Docker auth storage.

## Safe Transfer To Host

Use this only when you intentionally need a Docker-created org on host `sf` + `cci`.

```bash
./docker/docker-transfer-org-to-host.sh \
  <DOCKER_ORG_ALIAS> \
  --host-sf-alias <HOST_SF_ALIAS> \
  --host-cci-org <HOST_CCI_ORG_NAME>
```

`<DOCKER_ORG_ALIAS>` is required positional input. Host alias/org names are optional and auto-generated when omitted.

Safety behavior:

- Fails if host `sf` alias already exists.
- Fails if host `cci` org name already exists.
- Never sets host default org or default Dev Hub.
- Uses secure temp files for `sfdxAuthUrl` and deletes them automatically.

This is critical to avoid accidental mutation of existing host authorizations.

## Secrets Handling (Do Not Commit)

The following values are secrets and must never be committed to git:

- `SFDX_AUTH_URL` (contains a refresh token; full org access)
- Any value that starts with `force://` (same token material as `SFDX_AUTH_URL`)
- Salesforce access tokens or refresh tokens from CLI JSON output (`accessToken`, `refreshToken`)
- Session IDs copied from `sf` command output
- Files under `.docker/state/` (container auth/config state)
- Any exported auth-url files such as `*.authurl` or temporary files containing `sfdxAuthUrl`
- Host auth stores if ever copied into the repo (`~/.sf`, `~/.sfdx`, `~/.cumulusci`)

Protections already in this repo:

- `.env` is gitignored
- `.docker/state/` and `.docker/*.authurl` are gitignored

Required practice:

- Keep real secrets only in local `.env` or CI secret storage
- Never paste raw auth URLs or tokens into docs, issues, commits, or PR descriptions
- Delete temporary auth files immediately after transfer (the helper script does this automatically)

Pre-commit safety check:

```bash
git status --short
git diff --cached
rg -n "force://|SFDX_AUTH_URL=|accessToken|refreshToken|sfdxAuthUrl" . --glob "!.git/**" --glob "!.docker/state/**"
```

If the scan finds a real secret, rotate/re-auth immediately and remove it from history before pushing.

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
./docker/docker-test-org-sharing.sh
```

`docker/docker-test-org-sharing.sh` validates Docker scratch creation from Dev Hub plus safe host transfer via `docker/docker-transfer-org-to-host.sh`.

## Scratch Org Creation Pattern

Use this pattern in Docker to avoid keychain persistence issues:

```bash
./docker-cci.sh sf org create scratch \
  --definition-file orgs/dev.json \
  --alias <DOCKER_SCRATCH_ALIAS> \
  --duration-days 1 \
  --target-dev-hub dockerDevHub

./docker-cci.sh cci org import <DOCKER_SCRATCH_ALIAS> <DOCKER_SCRATCH_ALIAS>
```
