# Git Commit Stamping

## Overview

The `stamp_git_commit` CCI task writes the current git commit hash, branch, timestamp, dirty-tree flag, org definition, and active feature flags into the target Salesforce org as a **Custom Metadata Type record** (`RLM_Build_Info__mdt`). This makes it possible to determine exactly which version of the repository and configuration was used to build or configure an org.

## Why This Was Added

When debugging issues or auditing org configurations, there was no way to trace an org back to the specific git commit that produced it. Teams had to rely on memory, Slack messages, or manual notes to track which branch/commit was deployed. This metadata closes that gap by embedding the build provenance directly in the org, queryable via SOQL and visible in Setup.

## How It Works

### Custom Metadata Type

**Object:** `RLM_Build_Info__mdt` (deployed via `force-app/` at step 5 of `prepare_rlm_org`)

| Field | Type | Description |
|-------|------|-------------|
| `RLM_Commit_Hash__c` | Text(7) | Short git commit hash |
| `RLM_Full_Commit_Hash__c` | Text(40) | Full 40-character SHA for precise lookup |
| `RLM_Branch__c` | LongTextArea(1000) | Git branch name (handles detached HEAD: shows tag or `detached@<hash>`) |
| `RLM_Dirty_Tree__c` | Checkbox | `true` when the build ran with uncommitted changes in the working tree |
| `RLM_Build_Timestamp__c` | Text(25) | ISO 8601 timestamp of the CCI run |
| `RLM_CCI_Flow__c` | LongTextArea(1000) | Name of the CCI flow or task that triggered the stamp |
| `RLM_Org_Definition__c` | LongTextArea(1000) | Org definition used (e.g. `beta (scratch, orgs/beta.json)`) |
| `RLM_Feature_Flags__c` | LongTextArea(32000) | Full `project__custom` config serialized as YAML (all feature flags and settings) |

### CCI Task

**Task:** `stamp_git_commit` (class: `tasks.rlm_stamp_commit.StampGitCommit`)

The task reads the current git state and project config, generates a CMDT record XML in a temporary directory, and deploys it to the org via `sf project deploy start`. It runs as the last step (step 31) of `prepare_rlm_org`.

**Non-fatal by design:** Deploy failures are logged as warnings. The task never fails a flow that has already completed all real work. This protects against network blips, first-run scenarios where the CMDT type hasn't been deployed yet, or other transient issues.

```bash
# Standalone usage
cci task run stamp_git_commit --org beta

# Override the flow name label
cci task run stamp_git_commit -o flow_name my_custom_flow --org beta
```

### Querying Build Info

```sql
SELECT DeveloperName, RLM_Commit_Hash__c, RLM_Branch__c,
       RLM_Dirty_Tree__c, RLM_Build_Timestamp__c, RLM_CCI_Flow__c,
       RLM_Org_Definition__c, RLM_Feature_Flags__c
FROM RLM_Build_Info__mdt
```

Or navigate to **Setup > Custom Metadata Types > RLM Build Info > Manage Records**.

### Robustness

- **XML escaping:** All field values are escaped via `xml.sax.saxutils.escape()` to handle branch names with `&`, `<`, `>`, etc.
- **Detached HEAD:** When `git rev-parse --abbrev-ref HEAD` returns `HEAD` (common in CI), the task tries `git describe --tags --exact-match` for a tag name, then falls back to `detached@<short-hash>`.
- **Dirty tree detection:** `git status --porcelain` flags uncommitted changes so you know whether the stamped commit fully represents what was deployed. Known build-output paths (`unpackaged/post_ux/`) are excluded from the dirty check since they are regenerated during the flow and would always flag dirty in CI.
- **Non-fatal deploy:** The deploy step is wrapped in a try/except; deploy failures produce a warning, not an error. Git and file I/O errors still raise normally.

## Enhancement Opportunities

### Per-Flow Tracking

Currently the task writes a single record with `DeveloperName: Latest`. A natural extension is to use the **flow name as the DeveloperName** (e.g., `prepare_rlm_org`, `prepare_ux`, `prepare_billing`). This would allow multiple records to coexist, each showing the last commit/timestamp for that specific flow. Useful for answering questions like "was `prepare_ux` re-run after the main build?"

### Stamp Additional Flows

Add the `stamp_git_commit` step to other key flows beyond `prepare_rlm_org` — for example `prepare_ux`, `prepare_billing`, `prepare_rating` — so each independently tracks when it was last run and from which commit.

### CCI and CLI Version Tracking

Capture the CumulusCI version (`cci version`) and sf CLI version (`sf --version`) alongside the git commit, providing a full picture of the toolchain used for the build.

### Org User Context

Record the username of the CCI-connected org user who ran the build, useful when multiple team members share an org.

### Build Duration

Capture how long the flow took to complete (start timestamp at step 1, end timestamp at the stamp step) to track org build performance over time.

### CI/CD Integration

If running in a CI environment (GitHub Actions, Jenkins, etc.), capture the run ID or URL so the CMDT record links directly back to the pipeline execution log.
