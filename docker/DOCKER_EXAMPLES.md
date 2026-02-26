# Docker Workflow Examples

This document shows common workflows using the Docker container with shared scratch orgs.

## Example 1: Create Scratch Org in Container, Use on Host

```bash
# 1. Start container
./docker-cci.sh

# 2. Inside container: Create scratch org
cci org scratch dev my-dev-org

# 3. Inside container: Deploy metadata
cci flow run dev_org --org my-dev-org

# 4. Exit container
exit

# 5. On host: Access the same org
cci org info my-dev-org
cci org browser my-dev-org  # Opens in host browser
sf org display -o my-dev-org
```

## Example 2: Run Robot Tests in Container

```bash
# Option 1: Using wrapper script
./docker-cci.sh robot robot/rlm-base/tests/

# Option 2: Using docker-compose
docker-compose run --rm cci-robot robot robot/rlm-base/tests/

# Option 3: Run specific test with variables
./docker-cci.sh robot \
  -v REVENUE_SETTINGS_URL:https://my-org.scratch.my.salesforce-setup.com \
  robot/rlm-base/tests/setup/DocumentBuilder.robot
```

## Example 3: CumulusCI Flow with Robot Tests

```bash
# In container
./docker-cci.sh

# Create and setup org
cci org scratch qa qa-org
cci flow run qa_org --org qa-org

# Run Robot Framework tests against the org
robot -v ORG:qa-org robot/rlm-base/tests/

# Exit and the org is still available on host
exit
cci org info qa-org
```

## Example 4: Authenticate to Production/Sandbox

```bash
# Start container
./docker-cci.sh

# Inside container: Authenticate to production org
cci org connect production
# Or with SF CLI
sf org login web --alias production --instance-url https://login.salesforce.com

# Exit container
exit

# On host: Use the connected org
cci org info production
sf org display -o production
```

## Example 5: CI/CD Pipeline Integration (Basic)

```bash
# In your CI/CD pipeline (e.g., GitHub Actions, Jenkins)

# Build image (or pull from registry)
docker-compose build

# Create scratch org
docker-compose run --rm cci-robot cci org scratch dev ci-scratch-org

# Run tests
docker-compose run --rm cci-robot cci flow run ci_feature --org ci-scratch-org

# Run Robot tests
docker-compose run --rm cci-robot robot robot/rlm-base/tests/

# Cleanup
docker-compose run --rm cci-robot cci org scratch_delete ci-scratch-org
```

## Example 6: Multiple Scratch Orgs

```bash
# Start container
./docker-cci.sh

# Create multiple orgs for different purposes
cci org scratch dev feature-1-org
cci org scratch dev feature-2-org
cci org scratch qa qa-org

# Switch between them
cci org info feature-1-org
cci org default feature-1-org
cci flow run dev_org

# All orgs persist and are available on host
exit
cci org list  # Shows all three orgs
```

## Example 7: Development Workflow

```bash
# Day 1: Setup development environment
./docker-cci.sh
cci org scratch dev my-feature-org
cci flow run dev_org --org my-feature-org
exit

# Day 2: Continue development (org still exists!)
./docker-cci.sh
cci org info my-feature-org  # Still there!
cci task run deploy --org my-feature-org
robot robot/rlm-base/tests/
exit

# Day 3: Test on host, cleanup in container
cci org browser my-feature-org  # Test manually
./docker-cci.sh cci org scratch_delete my-feature-org
```

## Example 8: Debugging Robot Tests

```bash
# Run tests with more verbose output
./docker-cci.sh robot \
  --loglevel DEBUG \
  --outputdir results \
  robot/rlm-base/tests/

# Check results on host (they're in the mounted directory)
ls results/
open results/report.html  # View on host browser
```

## Example 9: CI/CD with JWT Authentication

```bash
# One-time setup: Get SFDX Auth URL from authenticated DevHub
sf org display --verbose -o YourDevHub | grep "Sfdx Auth Url"

# In CI/CD pipeline, set as environment variable or secret
export SFDX_AUTH_URL="force://PlatformCLI::5Aep861..."

# Use CI/CD configuration
docker-compose -f docker-compose.yml -f docker-compose.ci.yml run --rm cci-robot \
  cci org list

# Create scratch org (authenticated with DevHub via JWT)
docker-compose -f docker-compose.yml -f docker-compose.ci.yml run --rm cci-robot \
  cci org scratch dev ci-org

# Run deployment
docker-compose -f docker-compose.yml -f docker-compose.ci.yml run --rm cci-robot \
  cci flow run ci_feature --org ci-org

# Cleanup
docker-compose -f docker-compose.yml -f docker-compose.ci.yml run --rm cci-robot \
  cci org scratch_delete ci-org
```

## Example 10: GitHub Actions Integration

```yaml
# .github/workflows/ci.yml
name: CumulusCI Build

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: docker-compose build

      - name: Authenticate to DevHub
        env:
          SFDX_AUTH_URL: ${{ secrets.DEVHUB_AUTH_URL }}
        run: |
          docker-compose -f docker-compose.yml -f docker-compose.ci.yml run --rm cci-robot \
            cci org list

      - name: Create scratch org
        env:
          SFDX_AUTH_URL: ${{ secrets.DEVHUB_AUTH_URL }}
        run: |
          docker-compose -f docker-compose.yml -f docker-compose.ci.yml run --rm cci-robot \
            cci org scratch dev ci-org --days 1

      - name: Run tests
        env:
          SFDX_AUTH_URL: ${{ secrets.DEVHUB_AUTH_URL }}
        run: |
          docker-compose -f docker-compose.yml -f docker-compose.ci.yml run --rm cci-robot \
            cci flow run ci_feature --org ci-org

      - name: Cleanup
        if: always()
        env:
          SFDX_AUTH_URL: ${{ secrets.DEVHUB_AUTH_URL }}
        run: |
          docker-compose -f docker-compose.yml -f docker-compose.ci.yml run --rm cci-robot \
            cci org scratch_delete ci-org || true
```

## Example 11: Testing Org Sharing

```bash
# Verify that org sharing is working correctly

# 1. Run the test script
./docker/test-org-sharing.sh

# 2. Or test manually:
# Create org in container
./docker-cci.sh cci org scratch dev test-sharing

# Verify on host
cci org list | grep test-sharing
cci org info test-sharing

# Use in container
./docker-cci.sh cci org info test-sharing

# Cleanup
cci org scratch_delete test-sharing
```

## Tips

1. **Org URLs**: Get org URLs for host browser access:

   ```bash
   cci org browser my-org --url-only
   ```

2. **List All Orgs**: See all orgs from host or container:

   ```bash
   cci org list
   sf org list
   ```

3. **Default Org**: Set a default org to avoid typing `--org` each time:

   ```bash
   cci org default my-org
   sf config set target-org=my-org
   ```

4. **Parallel Development**: You can work on the host and container simultaneously with the same orgs!

5. **Container Updates**: When you update the Dockerfile, rebuild:

   ```bash
   docker-compose build --no-cache
   ```

6. **CI/CD Authentication**: For pipelines, always use the CI configuration:

   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.ci.yml run cci-robot
   ```
