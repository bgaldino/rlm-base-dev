# Docker Workflow Examples

## Run Commands In Container

```bash
./docker-cci.sh cci org list
./docker-cci.sh sf org list
./docker-cci.sh bash -lc "robot --version || true"
```

## Scratch Org In Container, Use On Host

```bash
# Create via SF CLI from Dev Hub, then import alias to CCI in Docker.
./docker-cci.sh sf org create scratch \
  --definition-file orgs/dev.json \
  --alias <DOCKER_ORG_ALIAS> \
  --duration-days 1 \
  --target-dev-hub dockerDevHub
./docker-cci.sh cci org import <DOCKER_ORG_ALIAS> <DOCKER_ORG_ALIAS>
./docker-cci.sh cci flow run <FLOW_NAME> --org <DOCKER_ORG_ALIAS>

# If you need host-side access for this Docker-created org, use unique names.
./docker/docker-transfer-org-to-host.sh \
  <DOCKER_ORG_ALIAS> \
  --host-sf-alias <HOST_SF_ALIAS> \
  --host-cci-org <HOST_CCI_ORG_NAME>

cci org info <HOST_CCI_ORG_NAME>
cci org browser <HOST_CCI_ORG_NAME>
sf org display --target-org <HOST_SF_ALIAS>
```

Important:

- Do not use `--set-default` or `--set-default-dev-hub` during host import.
- Always use new alias/org names to avoid touching existing host auth entries.
- Treat `sfdxAuthUrl` as a secret; do not store it in committed files.

## Run Robot Tests

```bash
./docker-cci.sh robot robot/rlm-base/tests/
./docker-cci.sh robot --loglevel DEBUG --outputdir results robot/rlm-base/tests/
```

## CI Pipeline Commands

```bash
export SFDX_AUTH_URL="force://PlatformCLI::..."

docker compose -f docker-compose.yml -f docker-compose.ci.yml run --rm cci-robot \
  cci org scratch dev <CI_ORG_NAME> --days 1

docker compose -f docker-compose.yml -f docker-compose.ci.yml run --rm cci-robot \
  cci flow run <CI_FLOW_NAME> --org <CI_ORG_NAME>

docker compose -f docker-compose.yml -f docker-compose.ci.yml run --rm cci-robot \
  cci org scratch_delete <CI_ORG_NAME> || true
```

## Validate Org Sharing

```bash
./docker/docker-test-org-sharing.sh
```

If the smoke test fails while container commands work, inspect:

- `.env` contains a valid `SFDX_AUTH_URL`
- Dev Hub alias resolution (`dockerDevHub` by default, or your override alias)
- Any stale local alias collisions (`cci org remove <alias>` then retry)
