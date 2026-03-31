# Docker Setup Summary (Archived)

This document preserves the earlier rollout summary for Docker org-sharing setup.

Current source-of-truth docs:

- `docs/guides/docker-setup.md`
- `docs/references/docker-workflow-examples.md`

Notes from earlier rollout:

- Added Docker compose-based local and CI workflows.
- Added explicit `CUMULUSCI_KEY` sharing via `.env`.
- Added helper scripts:
  - `docker/get-cci-key.sh`
  - `docker/test-org-sharing.sh`
- Added wrapper:
  - `docker-cci.sh`

As of current state:

- Docker image builds successfully.
- `cci` and `sf` run successfully in container.
- org sharing smoke test may still fail in environments with pre-existing key/keychain mismatch; remediation is to align key source and re-auth org credentials.
