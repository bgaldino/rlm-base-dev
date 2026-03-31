# Docker Setup Summary (Archived)

This document preserves the earlier rollout summary for Docker org-sharing setup.

Current source-of-truth docs:

- `docs/guides/docker-setup.md`
- `docs/references/docker-workflow-examples.md`

Notes from earlier rollout:

- Added Docker compose-based local and CI workflows.
- Current standard is `SFDX_AUTH_URL`-only for Docker auth bootstrap.
- Added helper scripts:
  - `docker/docker-test-org-sharing.sh`
- Added wrapper:
  - `docker-cci.sh`

As of current state:

- Docker image builds successfully.
- `cci` and `sf` run successfully in container.
- Docker auth should be driven by `SFDX_AUTH_URL` and CCI EnvironmentProjectKeychain.
