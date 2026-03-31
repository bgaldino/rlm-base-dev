# Docker Workflow Examples

## Run Commands In Container

```bash
./docker-cci.sh cci org list
./docker-cci.sh sf org list
./docker-cci.sh bash -lc "robot --version || true"
```

## Scratch Org In Container, Use On Host

```bash
./docker-cci.sh cci org scratch dev my-dev-org
./docker-cci.sh cci flow run dev_org --org my-dev-org

cci org info my-dev-org
cci org browser my-dev-org
sf org display -o my-dev-org
```

## Run Robot Tests

```bash
./docker-cci.sh robot robot/rlm-base/tests/
./docker-cci.sh robot --loglevel DEBUG --outputdir results robot/rlm-base/tests/
```

## CI Pipeline Commands

```bash
export SFDX_AUTH_URL="force://PlatformCLI::..."

docker compose -f docker-compose.yml -f docker-compose.ci.yml run --rm cci-robot \
  cci org scratch dev ci-org --days 1

docker compose -f docker-compose.yml -f docker-compose.ci.yml run --rm cci-robot \
  cci flow run ci_feature --org ci-org

docker compose -f docker-compose.yml -f docker-compose.ci.yml run --rm cci-robot \
  cci org scratch_delete ci-org || true
```

## Validate Org Sharing

```bash
./docker/test-org-sharing.sh
```

If the smoke test fails while container commands work, inspect:

- `.env` key value freshness (`CUMULUSCI_KEY`)
- Host keychain vs env key mismatch
- Existing host CCI org files created with a different key
