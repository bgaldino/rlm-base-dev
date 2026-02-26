# Docker Setup for RLM Base Development

This Docker setup provides a containerized environment with CumulusCI, Salesforce CLI, and Robot Framework.

## Encryption Key Setup (REQUIRED)

To enable org sharing between host and container, you need to set up the CumulusCI encryption key:

```bash
# 1. Extract your encryption key
./docker/get-cci-key.sh

# 2. Create .env file from template
cp .env.example .env

# 3. Add the key to .env (automated)
echo "CUMULUSCI_KEY=$(./docker/get-cci-key.sh 2>/dev/null)" >> .env

# Or manually edit .env and paste the key
```

**Why is this needed?**
CumulusCI encrypts org credential files using a key stored in your system keyring (macOS Keychain, etc.). Docker containers can't access your keyring, so we explicitly provide the key via environment variable. This ensures both host and container use the same encryption key.

**Skip this if:** You're doing a fresh setup with no existing orgs on your host.

## Quick Start

### Build the Docker image

```bash
docker-compose build
```

### Option 1: Use the Wrapper Script (Recommended)

```bash
```bash
# Make executable (first time only)
chmod +x docker-cci.sh

# Interactive shell
./docker-cci.sh

# Run specific commands
./docker-cci.sh cci org list
./docker-cci.sh sf org list
./docker-cci.sh robot --version
```

### Option 2: Use Docker Compose Directly

```bash
```bash
# Interactive shell
docker-compose run --rm cci-robot

# Run specific commands
docker-compose run --rm cci-robot cci org list
docker-compose run --rm cci-robot sf org display
```

### Option 3: Use Docker Directly

```bash
```bash
docker build -t rlm-base-cci-robot .
docker run -it --rm \
  -v $(pwd):/workspace \
  -v ${HOME}/.cumulusci:/root/.cumulusci \
  -v ${HOME}/.sf:/root/.sf \
  --network host \
  rlm-base-cci-robot
```

## Usage

Once inside the container, you can use all tools:

### CumulusCI

```bash
```bash
# Check version
cci version

# List orgs
cci org list

# Run a flow
cci flow run dev_org

# Run a task
cci task run robot
```

### Salesforce CLI

```bash
```bash
# Check version
sf version

# Login to org
sf org login web

# List orgs
sf org list
```

### Robot Framework

```bash
```bash
# Run Robot tests
robot robot/rlm-base/tests/

# Run specific test suite
robot robot/rlm-base/tests/setup/DocumentBuilder.robot

# Run with variables
robot -v REVENUE_SETTINGS_URL:https://your-org.my.salesforce.com robot/rlm-base/tests/
```

## Shared Scratch Orgs with Host

**Important:** This setup shares your CumulusCI and Salesforce CLI configurations between the host and container. This means:

✅ **Scratch orgs created in the container are accessible on your host machine**
✅ **Scratch orgs created on your host are accessible in the container**
✅ **Auth tokens and org info persist between container restarts**
✅ **No need to re-authenticate when switching between host and container**

The following directories are mounted from your host:
- CumulusCI configuration: `~/.cumulusci` → `/root/.cumulusci`
- CumulusCI orgs: `~/.cumulusci/orgs` → `/root/.cumulusci/orgs`
- Salesforce CLI config: `~/.sf` → `/root/.sf`
- Legacy SFDX config: `~/.sfdx` → `/root/.sfdx`

### Using Orgs Across Host and Container

```bash
# On host: Create a scratch org
cci org scratch dev my-scratch-org

# In container: Use the same org
docker-compose run --rm cci-robot
cci org info my-scratch-org  # Works!
sf org display -o my-scratch-org  # Works!

# In container: Create an org
cci org scratch qa qa-scratch-org

# On host: Use the same org
cci org info qa-scratch-org  # Works!
```

### Accessing Scratch Orgs from Browser

Since orgs are shared, you can:
1. Create/connect orgs in the container
2. Get the org URL on your host: `cci org browser my-scratch-org --url-only`
3. Open in your host browser with full authentication

## Network Mode

The container uses `host` network mode to simplify Salesforce OAuth flows. If you need to change this, edit `docker-compose.yml`.

## Browser Automation

The container includes Chromium configured for headless operation with Robot Framework's SeleniumLibrary. The following are pre-configured:
- `CHROME_BIN=/usr/bin/chromium`
- Headless-friendly flags: `--no-sandbox --disable-dev-shm-usage --disable-gpu`

## First-Time Setup

If you've never used CumulusCI or SF CLI on your host, create the directories first:

```bash
mkdir -p ~/.cumulusci ~/.sf ~/.sfdx
```

The container will then populate these with configuration files on first run.

## CI/CD Configuration

For automated pipelines (GitHub Actions, Jenkins, etc.), use the CI/CD configuration with JWT authentication:

### Setup JWT Authentication

1. **Create a Connected App in Salesforce** (one-time setup):
   - Setup → App Manager → New Connected App
   - Enable OAuth Settings
   - Enable "Use digital signatures" and upload a certificate
   - Select OAuth scopes: `full`, `refresh_token`, `web`
   - Note the Consumer Key

2. **Generate an SFDX Auth URL**:

   ```bash
   # On host with authenticated DevHub:
   sf org display --verbose -o YourDevHub
   # Copy the "Sfdx Auth Url" value
   ```

3. **Use CI/CD configuration**:

   ```bash
   # Set environment variable
   export SFDX_AUTH_URL="force://PlatformCLI::..."

   # Run with CI configuration
   docker-compose -f docker-compose.yml -f docker-compose.ci.yml run cci-robot cci org list
   ```

4. **In CI/CD pipelines**, store `SFDX_AUTH_URL` as a secret and inject it as an environment variable.

### CI/CD vs Local Development

| Feature | Local Dev (default) | CI/CD (with docker-compose.ci.yml) |
| --- | --- | --- |
| Keychain | EncryptedFileProjectKeychain | EnvironmentProjectKeychain |
| Org Storage | Files in ~/.cumulusci | Environment variables |
| Authentication | Interactive OAuth | JWT/SFDX_AUTH_URL |
| Org Sharing | Shared with host | Container-only |
| Use Case | Development, testing | Automated builds, deployments |

## Troubleshooting

### Orgs Not Visible Between Host and Container

**Problem**: Orgs authenticated on the host don't appear in the container (or vice versa), or you see "Invalid base64-encoded string" errors.

**Root Cause**: The container can't access your system keyring (macOS Keychain) to get the encryption key. Without the key, the container writes unencrypted files that your host CCI can't read.

**Solution**: Set up the encryption key in your .env file:

```bash
# Extract key
./docker/get-cci-key.sh

# Create .env file
echo "CUMULUSCI_KEY=$(./docker/get-cci-key.sh 2>/dev/null)" >> .env

# Rebuild container
docker-compose build
```

**If you still see this issue**:

1. Ensure you're using the latest `docker-compose.yml` (without `CUMULUSCI_KEYCHAIN_CLASS` environment variable)
2. Rebuild the container: `docker-compose build`
3. Verify volume mounts exist in `docker-compose.yml`:

   ```yaml
   - ${HOME}/.cumulusci:/root/.cumulusci
   - ${HOME}/.sf:/root/.sf
   ```

4. Check that the directories exist on host: `ls ~/.cumulusci`

**Technical Details**:

- **EncryptedFileProjectKeychain** (default): Reads/writes `.org` files in `~/.cumulusci/PROJECT_NAME/`. These files are shared between host and container via volume mounts.
- **EnvironmentProjectKeychain** (CI/CD): Reads org credentials from environment variables like `SFDX_AUTH_URL`. Good for pipelines, but doesn't create/read `.org` files.

### Testing Org Sharing

Use the helper script to verify org sharing is working:

```bash
./docker/test-org-sharing.sh
```

This script:

1. Creates a test scratch org in the container
2. Verifies it's visible on the host
3. Cleans up the test org

### OAuth/Login Issues

If you have trouble with OAuth flows, ensure the container is using `network_mode: host` in `docker-compose.yml`.

### Browser Issues

If Robot Framework tests fail with browser errors, ensure Chrome options include:

```robot
${chrome_options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
Call Method    ${chrome_options}    add_argument    --no-sandbox
Call Method    ${chrome_options}    add_argument    --disable-dev-shm-usage
Call Method    ${chrome_options}    add_argument    --headless
```

### Permission Issues
If you encounter permission issues with mounted volumes, you may need to adjust the container's user or volume permissions.

### Version Conflicts
If you have different versions of CumulusCI or SF CLI on your host vs. container:
- The container uses the versions specified in the Dockerfile
- Your host uses whatever you have installed locally
- Org configurations are generally compatible, but if you see issues, use the same tool version in both environments
