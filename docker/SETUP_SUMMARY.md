# Docker CumulusCI Setup - Complete Solution

## ✅ What We Fixed

Your Docker setup now enables **full org sharing between host and container** with proper encryption support.

### Original Problem
- Orgs created on host were invisible in Docker container
- Orgs created in container were invisible on host
- Error: "Invalid base64-encoded string" when accessing orgs
- Root cause: Docker container couldn't access macOS Keychain encryption key

### Solution Implemented
Added encryption key sharing via `.env` file so both host and container use the same CumulusCI encryption key.

## 🚀 Quick Setup (One-Time)

```bash
# 1. Extract your encryption key from macOS Keychain
./docker/get-cci-key.sh

# 2. Create .env file with the key
echo "CUMULUSCI_KEY=$(./docker/get-cci-key.sh 2>/dev/null)" > .env

# 3. Build the Docker container
docker-compose build

# 4. Test org sharing
./docker/test-org-sharing.sh
```

## 📂 Files Created/Modified

### New Files
- **[docker/get-cci-key.sh](get-cci-key.sh)** - Extracts encryption key from system keyring
- **[.env.example](.env.example)** - Template for environment variables
- **[.env](.env)** - Contains your encryption key (gitignored)
- **[docker-compose.ci.yml](docker-compose.ci.yml)** - CI/CD configuration with JWT auth

### Modified Files
- **[docker-compose.yml](docker-compose.yml)** - Added `CUMULUSCI_KEY=${CUMULUSCI_KEY}` environment variable
- **[docker/DOCKER_USAGE.md](DOCKER_USAGE.md)** - Added encryption key setup instructions
- **[docker/DOCKER_README.md](DOCKER_README.md)** - Updated quick start and troubleshooting
- **[docker/DOCKER_EXAMPLES.md](DOCKER_EXAMPLES.md)** - Added CI/CD examples
- **[docker/test-org-sharing.sh](test-org-sharing.sh)** - Enhanced to check for encryption key

## ✅ Verification

Your setup has been tested and verified:

1. **Encryption Key Extraction**: ✅ Successfully extracts key from macOS Keychain
2. **.env File**: ✅ Created with `CUMULUSCI_KEY=GKekWSHjO0naP7n5`
3. **Docker Build**: ✅ Container rebuilt with encryption key
4. **Org Visibility**: ✅ Existing orgs visible in container
5. **Org Creation**: ✅ New orgs in container visible on host
6. **Encryption**: ✅ Org files properly encrypted with shared key

## 📝 Usage

### Local Development (Default)

```bash
# Start container
./docker-cci.sh

# Inside container - all your orgs are available!
cci org list              # See all host orgs
cci org info afternoonFeb25  # Access host org
sf org display -o afternoonFeb25  # SF CLI works too

# Create new org in container
cci org scratch dev my-org

# Exit container
exit

# On host - new org is available!
cci org list | grep my-org
cci org browser my-org    # Opens in host browser
```

### CI/CD Pipelines

For automated builds, use JWT authentication:

```bash
# Get DevHub auth URL (one-time)
sf org display --verbose -o YourDevHub | grep "Sfdx Auth Url"

# In CI/CD pipeline
export SFDX_AUTH_URL="force://..."
docker-compose -f docker-compose.yml -f docker-compose.ci.yml run cci-robot cci org list
```

## 🔧 How It Works

### Encryption Key Flow

1. **Host CumulusCI** uses encryption key from macOS Keychain
2. **Docker Container** receives same key via `CUMULUSCI_KEY` environment variable
3. **Both environments** encrypt/decrypt `.org` files with same key
4. **Org files** are shared via Docker volume mount `~/.cumulusci`

### Architecture

```
┌─────────────────┐                  ┌──────────────────┐
│   macOS Host    │                  │ Docker Container │
├─────────────────┤                  ├──────────────────┤
│ Keychain        │                  │ CUMULUSCI_KEY    │
│   └─ key ──────┼──────┐           │  (from .env)     │
│                 │      │           │                  │
│ CumulusCI ──────┼──────┼─ Volume ─┼─→ CumulusCI      │
│   uses key      │      │  Mount   │    uses key      │
│                 │      │           │                  │
│ ~/.cumulusci/   │      │           │ ~/.cumulusci/    │
│   ├─ org1.org ──┼──────┼───────────┼──→ org1.org     │
│   └─ org2.org ──┼──────┘           │   └─ org2.org   │
└─────────────────┘                  └──────────────────┘
        │                                     │
        └──── Encrypted with same key ───────┘
```

## 🛡️ Security Notes

- **.env file** contains sensitive encryption key - it's gitignored
- **Key grants access** to all your org credentials
- **For teams**: Share key securely (1Password, encrypted secrets)
- **For CI/CD**: Store as pipeline secret (GitHub Secrets, etc.)

## 🎯 Next Steps

Your setup is complete and ready to use! Try these:

1. **Test org sharing**: `./docker/test-org-sharing.sh`
2. **Create a dev org**: `./docker-cci.sh cci org scratch dev test`
3. **Run tests**: `./docker-cci.sh robot robot/rlm-base/tests/`
4. **Set up CI/CD**: See [DOCKER_EXAMPLES.md](DOCKER_EXAMPLES.md#example-10-github-actions-integration)

## 📚 Documentation

- **Detailed Usage**: [docker/DOCKER_USAGE.md](DOCKER_USAGE.md)
- **Workflow Examples**: [docker/DOCKER_EXAMPLES.md](DOCKER_EXAMPLES.md)
- **Quick Reference**: [docker/DOCKER_README.md](DOCKER_README.md)

## 🆘 Troubleshooting

### "Unable to store an encryption key" in container
**Fix**: Rebuild with encryption key
```bash
echo "CUMULUSCI_KEY=$(./docker/get-cci-key.sh 2>/dev/null)" >> .env
docker-compose build
```

### "Invalid base64-encoded string" on host
**Fix**: Encryption key mismatch - regenerate .env file
```bash
./docker/get-cci-key.sh
echo "CUMULUSCI_KEY=$(./docker/get-cci-key.sh 2>/dev/null)" > .env
docker-compose build
```

### Orgs still not visible
**Fix**: Check volume mounts and directory permissions
```bash
mkdir -p ~/.cumulusci ~/.sf ~/.sfdx
ls -la ~/.cumulusci/rlm-base/
docker-compose run --rm cci-robot ls -la /root/.cumulusci/rlm-base/
```

## 🎉 Success!

You now have a fully functional Docker CumulusCI environment with:
- ✅ Bidirectional org sharing (host ↔ container)
- ✅ Encrypted org credentials
- ✅ OAuth flow support
- ✅ CI/CD ready configuration
- ✅ Complete documentation

Happy developing! 🚀
