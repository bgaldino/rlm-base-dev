# Docker SF CLI & CumulusCI Guide

This guide explains how to use Salesforce CLI and CumulusCI inside the Docker container for scratch org development and automated builds.

## Quick Start

### Run Commands in Docker

Use the `docker-cci.sh` wrapper script to run any SF CLI or CCI command:

```bash
# SF CLI commands
./docker-cci.sh sf org list
./docker-cci.sh sf project deploy start

# CumulusCI commands
./docker-cci.sh cci org list
./docker-cci.sh cci flow run dev_org --org dev
./docker-cci.sh cci task run deploy

# Interactive shell
./docker-cci.sh bash
```

### Create a Scratch Org

```bash
# Create a scratch org using a config from cumulusci.yml
./docker-cci.sh cci org scratch dev myorg

# Run a full dev org setup flow
./docker-cci.sh cci flow run dev_org --org myorg
```

### Run CCI Builds

```bash
# Run a complete build in a fresh scratch org
./docker-cci.sh cci flow run dev_org --org build-test

# Run tests
./docker-cci.sh cci task run run_tests --org build-test
```

## Setup Details

### What's Included

The Docker image (`rlm-base-cci-robot:latest`) includes:
- **Salesforce CLI** (latest) with SFDMU plugin
- **CumulusCI** v4.8+ for automation
- **Robot Framework** with Selenium for UI testing
- **Chromium** for headless browser automation
- **Python 3.11** with all necessary dependencies

### Volume Mounts

The container shares these directories with your host machine:
- `~/.cumulusci` - CCI configuration and org info
- `~/.sf` - SF CLI v2 configuration
- `~/.sfdx` - SFDX/SF CLI v1 configuration
- `.` (project directory) - Your source code

### Authentication

**DevHub**: Pre-authenticated as `bgDevHub` (scheck@usa794.devhub)

To authenticate additional DevHubs or orgs from Docker:
```bash
# Generate auth URL on host
sf org display --verbose -o <alias> | grep "Sfdx Auth Url"

# Import in Docker
./docker-cci.sh bash
echo '<auth-url>' | sf org login sfdx-url -f - -a <alias> -d
```

### Network Configuration

The container uses `network_mode: host` to enable OAuth flows. This allows:
- Scratch org creation (OAuth callbacks to localhost)
- Interactive SF CLI authentication
- Access to local services

## Common Workflows

### Development Workflow

```bash
# 1. Create a scratch org
./docker-cci.sh cci org scratch dev mydev

# 2. Run development setup
./docker-cci.sh cci flow run dev_org --org mydev

# 3. Deploy changes
./docker-cci.sh cci task run deploy --org mydev

# 4. Run tests
./docker-cci.sh cci task run run_tests --org mydev
```

### CI/CD Workflow

For automated pipelines, use JWT authentication with `docker-compose.ci.yml`:

```bash
# Set DevHub auth URL
export SFDX_AUTH_URL="force://PlatformCLI::..."

# Run build
docker-compose -f docker-compose.yml -f docker-compose.ci.yml run cci-robot \
  cci flow run ci_feature --org ci-scratch
```

### Interactive Development

```bash
# Start interactive shell
./docker-cci.sh bash

# Inside container:
cci org list
sf org list
cci flow list
cci task list

# Work with orgs interactively
cci org info myorg
sf data query -q "SELECT Id, Name FROM Account LIMIT 5" -o myorg
```

## Troubleshooting

### "No orgs found"
- Verify DevHub on host: `sf org list`
- Check volume mounts in docker-compose.yml
- Re-authenticate DevHub in Docker (see Authentication section)

### "AuthDecryptError"
- This is expected for host orgs due to encryption
- Re-authenticate the org from inside Docker if needed
- Or export/import using auth URLs

### Scratch org creation fails
- Verify DevHub is active on host: `sf org list`
- Check DevHub limits: Some DevHubs have daily scratch org limits
- Ensure `network_mode: host` is set in docker-compose.yml

### Container can't access files
- Check that project is in Docker's file sharing settings
- Verify volume mounts: `docker-compose config`

## Configuration Files

- **Dockerfile** - Image definition with all tools
- **docker-compose.yml** - Service configuration with volume mounts
- **docker-compose.ci.yml** - CI/CD override configuration
- **docker-cci.sh** - Convenience wrapper script
- **cumulusci.yml** - CCI project configuration

## Tips

- Use `./docker-cci.sh` wrapper for all commands (easier than docker-compose run)
- The container is stateless - orgs and config are stored in mounted volumes
- Robot Framework tests run headless using Chromium
- For faster builds, create a base scratch org and clone it
- Use `cci org scratch_delete <name>` to clean up old scratch orgs

## Next Steps

- Review available scratch org configs in `cumulusci.yml`
- Check available CCI flows: `./docker-cci.sh cci flow list`
- Explore CCI tasks: `./docker-cci.sh cci task list`
- See CCI docs: https://cumulusci.readthedocs.io/
