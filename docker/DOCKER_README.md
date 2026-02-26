# Docker Setup - Quick Reference

Complete Docker environment for CumulusCI, Salesforce CLI, and Robot Framework with **shared scratch orgs** between host and container.

## 🚀 Quick Start

```bash
# 1. Set up encryption key (REQUIRED for org sharing)
./docker/get-cci-key.sh
echo "CUMULUSCI_KEY=$(./docker/get-cci-key.sh 2>/dev/null)" >> .env

# 2. Build the image
docker-compose build

# 3. Start interactive shell
./docker-cci.sh

# 4. Inside container - all tools available
cci version
sf version
robot --version
```

## 🎯 Key Features

✅ **CumulusCI** - Latest version with full functionality
✅ **Salesforce CLI** - Modern `sf` CLI with Node.js 20
✅ **Robot Framework** - With SeleniumLibrary and Chromium
✅ **Shared Orgs** - Scratch orgs accessible on both host and container (FIXED!)
✅ **Persistent Auth** - Login once, use everywhere
✅ **Host Network** - Easy OAuth flows
✅ **CI/CD Ready** - Separate configuration for JWT authentication in pipelines

## 📁 What's Included

| File | Purpose |
|------|---------|
| `Dockerfile` | Complete environment with all tools |
| `docker-compose.yml` | Local development configuration |
| `docker-compose.ci.yml` | CI/CD override configuration |
| `docker-cci.sh` | Wrapper script for quick commands |
| `.dockerignore` | Optimized build context |
| `docker/DOCKER_USAGE.md` | Detailed usage guide |
| `docker/DOCKER_EXAMPLES.md` | Real-world workflow examples |

## 💡 Common Commands

```bash
# Interactive shell
./docker-cci.sh

# Run CumulusCI commands
./docker-cci.sh cci org list
./docker-cci.sh cci flow run dev_org

# Run SF CLI commands
./docker-cci.sh sf org list
./docker-cci.sh sf org display

# Run Robot tests
./docker-cci.sh robot robot/rlm-base/tests/
```

## 🔄 Shared Orgs Workflow

```bash
# In container: Create org
./docker-cci.sh
cci org scratch dev my-org
exit

# On host: Use the same org!
cci org info my-org
cci org browser my-org
```

## 📖 Documentation

- **Detailed Usage**: See `DOCKER_USAGE.md`
- **Workflow Examples**: See `DOCKER_EXAMPLES.md`

## 🛠️ Troubleshooting

**Problem**: Container can't find orgs created on host OR "Invalid base64-encoded string" error
**Solution**: Set up the encryption key:

```bash
# Extract and set encryption key
./docker/get-cci-key.sh
echo "CUMULUSCI_KEY=$(./docker/get-cci-key.sh 2>/dev/null)" >> .env

# Rebuild container
docker-compose build

# Test
./docker/test-org-sharing.sh
```

Ensure `~/.cumulusci` and `~/.sf` directories exist:

```bash
mkdir -p ~/.cumulusci ~/.sf ~/.sfdx
```

**Problem**: OAuth login fails
**Solution**: Container uses `network_mode: host` for OAuth flows. Ensure this is set in `docker-compose.yml`

**Problem**: Browser tests fail
**Solution**: Container includes Chromium configured for headless mode. Tests should use appropriate Chrome options.

**Problem**: Need to run in CI/CD
**Solution**: Use the CI/CD configuration with JWT authentication:

```bash
export SFDX_AUTH_URL="force://..."
docker-compose -f docker-compose.yml -f docker-compose.ci.yml run cci-robot
```

## 🔧 Customization

Edit `Dockerfile` to:
- Change Python version (currently 3.11)
- Pin specific CumulusCI version
- Add additional Python packages
- Install additional tools

Rebuild after changes:
```bash
docker-compose build --no-cache
```

## 📋 Requirements

- Docker Desktop or Docker Engine
- Docker Compose
- ~2GB disk space for image
- Internet connection (for building image and OAuth)

## 🎓 Learn More

Run any of these tools with `--help`:
```bash
./docker-cci.sh cci --help
./docker-cci.sh sf --help
./docker-cci.sh robot --help
```
