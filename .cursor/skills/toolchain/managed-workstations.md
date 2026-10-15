# Managed Workstations

On a managed workstation, IT tools configure the machine for you. They write
blocks into your shell files, add `/etc/paths.d` entries, install corporate
certificates, or limit which browsers can be automated. The toolchain works on
these machines, but an agent has to work *around* that configuration, never over
it. On a plain workstation none of this applies.

The procedures live in [dev-environment-setup.md](../../../docs/guides/dev-environment-setup.md)
(**DES**). This file is the agent's checklist: what to look for, what not to touch,
and which section to follow.

| Situation | Look for | Don't | Follow |
|-----------|----------|-------|--------|
| Shell files hold blocks between marker comments (`# >>> tool >>>` … `# <<< tool <<<`, `# tool-managed-start` … `# tool-managed-end`) | A setting that doesn't take effect: a later block may set the same variable, and a block can re-add itself after the user removed it | Move, edit or delete a block; replace the file with a template | [DES §2, Shell config responsibilities](../../../docs/guides/dev-environment-setup.md#shell-config-responsibilities); merging is [DES §5](../../../docs/guides/dev-environment-setup.md#5-replicating-on-a-new-workstation) step 3 |
| `python3` is `/usr/bin/python3` (or Homebrew's) inside the repo | A login shell that *started* in the repo ([audit §5](workstation-audit.md#5-path-order-in-fresh-shells)) | `direnv reload`, or `cd` out and back: both drop `/etc/paths.d` and rc-file PATH entries | Open the terminal outside the repo and `cd` in ([DES §2, `~/.zprofile`](../../../docs/guides/dev-environment-setup.md#zprofile--runs-in-login-shells-only)) |
| npm or sf TLS errors (`SELF_SIGNED_CERT_IN_CHAIN`, `UNABLE_TO_GET_ISSUER_CERT_LOCALLY`) | `NODE_EXTRA_CA_CERTS` colon-joined, missing in one shell type, or overridden by a later block ([audit §6](workstation-audit.md#6-corporate-ca-managed-workstations)) | Set a colon-joined list; `cat` bundles together | [DES: Node TLS errors behind a corporate CA](../../../docs/guides/dev-environment-setup.md#node-tls-errors-behind-a-corporate-ca-node_extra_ca_certs) |
| `nvm install` reports `Version '' (with LTS filter) not found` | A certificate problem in nvm's silent curl/wget download | Treat it as a `NODE_EXTRA_CA_CERTS` problem | The same DES entry (the curl/wget paragraph) |
| A Python tool (pip, CumulusCI) fails TLS | The tool's own error | Add Python CA variables unless a Python tool actually fails; a workstation whose CumulusCI and pip work needs nothing | Ask the user; nothing in the guides covers it yet |
| Robot setup tasks fail on Salesforce Setup pages (`Unable to receive message from renderer`) | Stock headless Chrome crashing there (seen only on managed machines; root cause unconfirmed) | Put browser paths in `.envrc` or a shell profile | [LI: Chrome for Testing](../../../docs/guides/local-installation.md#chrome-for-testing-managed-workstations), with paths in `.env.local` |
| A token exported from an rc file | The variable's **name** only | Print or paste the value | Recommend moving it to the OS keychain, and rotating it if it was ever shown |

## Internal specifics

The names and behaviour of a particular organization's management tools, its
certificate paths and its identity setup are private. If you have access to the
maintainers' private tracker, the pack for this work records them; otherwise ask
the user rather than guessing. Keep them out of anything public, including
verification reports ([`verification-handoff.md`](verification-handoff.md)).
