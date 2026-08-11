# Asset-Based Ordering Console

A native-first Revenue Cloud (RLM) feature that lets an internal sales/service
agent navigate an account's assets across multiple contracts, launch the
platform's native asset-lifecycle actions, and consolidate selections from
several contracts into a **single Quote**. Delivered as the opt-in
`unpackaged/post_asset_ordering` bundle (feature flag `asset_ordering`, default
`false`).

## Guiding principle

Thin custom UI + orchestration; every state change is delegated to native RLM
engines. No pricing, assetization, or lifecycle logic is re-implemented in Apex.

## What is native vs custom

| Concern | Implementation |
|---|---|
| Amend / Upgrade / Downgrade / Renew / Cancel | **Native** standard invocable actions (`initiateAmendment` with `actionSubtype` for up/downgrade, `initiateRenewal`, `initiateCancellation`) |
| Multi-contract consolidation into one Quote | **Custom** orchestration that chains the native action per contract group, reusing the output record id (`amendRecordId`/`renewRecordId`/`cancelRecordId`) so all groups land on one output |
| Guided reconfiguration | **Native** Product Configurator Connect API (`/connect/cpq/configurator/actions/*`) via a thin Apex bridge |
| Suspend / Resume | **Native** billing suspension (`blngSvcSuspendBilling`, account-level, with a scheduled resume) + a custom `Asset.RLM_Asset_Status__c` and an auto-resume Schedulable |
| Asset navigation + portfolio timeline | Custom LWC (grid grouped by contract) + migrated Chart.js timeline |

The verified action schemas and endpoint findings are recorded privately in
`.agents/artifacts/abo-endpoint-verification.md` (Phase 0).

## Architecture

```mermaid
flowchart TD
  U[Agent on Account or Contract record page] --> LWC[rlmAssetConsole LWC]
  LWC -->|@AuraEnabled| CTRL[RLM_AssetConsoleController]
  CTRL --> SVC[RLM_AssetOrderingService]
  SVC -->|initiateAmendment / initiateRenewal / initiateCancellation| STD[Native standard actions]
  SVC -->|chain via output record id| QUOTE[(Single consolidated Quote)]
  CTRL --> SUS[RLM_AssetSuspensionService]
  SUS -->|blngSvcSuspendBilling| BILL[Native billing suspend + scheduled resume]
  SUS --> STATUS[Asset.RLM_Asset_Status__c]
  SCHED[RLM_AssetResumeScheduler] --> STATUS
  LWC --> CFG[rlmAssetConfigurator LWC]
  CFG --> CFGSVC[RLM_AssetConfiguratorService]
  CFGSVC -->|/connect/cpq/configurator/actions/*| CONF[Native Product Configurator]
  LWC --> TL[rlmAccountAssetPortfolio timeline tab]
```

## Components

### Apex (`unpackaged/post_asset_ordering/classes`)
- `RLM_AssetConsoleController` — `@AuraEnabled` facade. Reads assets grouped by
  contract (`WITH USER_MODE`, `Id.valueOf` at entry); regroups a flat selection
  by owning contract and delegates writes.
- `RLM_AssetOrderingService` — drives the native lifecycle actions through
  `Invocable.Action.createStandardAction` and consolidates across contract
  groups by threading the output record id. Test isolation via `@TestVisible`
  `mockOutcome`.
- `RLM_AssetConfiguratorService` — own-domain REST bridge to the Configurator
  Connect API (session-id VF page + `System.Url.getOrgDomainUrl()` pattern).
- `RLM_AssetSuspensionService` — native `blngSvcSuspendBilling` + custom status
  stamp (`as user` DML).
- `RLM_AssetResumeScheduler` — `Schedulable` that flips due assets back to
  Active.
- `RLM_AccountAssetPortfolioService` — read-only timeline data (migrated + hardened to `WITH USER_MODE`).

### LWC (`unpackaged/post_asset_ordering/lwc`)
- `rlmAssetConsole` — asset grid (grouped by contract via the Contract column),
  multi-select across contracts, action toolbar (Amend/Upgrade/Downgrade/Renew/
  Cancel/Suspend/Resume), consolidated-output banner, and a Portfolio Timeline
  tab. Exposed on Account and Contract record pages.
- `rlmAssetConfigurator` — embedded guided reconfiguration scoped to the
  consolidated Quote.
- `rlmAccountAssetPortfolio` — Chart.js MRR/quantity timeline.

### Metadata
- `objects/Asset/fields/RLM_Asset_Status__c` (picklist Active/Suspended),
  `RLM_Suspension_Resume_Date__c` (date).
- `permissionsets/RLM_AssetBasedOrdering` — least-privilege, built from the code
  (object read + FLS for exactly the fields queried; Asset edit + custom-field
  FLS for the suspend/resume writes). The running user must **also** hold the
  standard RLM sales / asset-lifecycle permissions (from the RLM persona
  permission set group) to execute the native actions and create the output —
  an intentional, documented dependency, not duplicated here.
- `pages/RLM_SessionId` — session-id page for the Configurator callout.

## Install

```bash
# enable the flag (cumulusci.yml → project.custom.asset_ordering: true) then:
cci flow run prepare_asset_ordering --org <alias>
# or standalone:
cci task run deploy_post_asset_ordering --org <alias>
cci task run assign_permission_sets --org <alias> -o api_names RLM_AssetBasedOrdering
```

Add the **Asset-Based Ordering Console** component to an Account or Contract
Lightning record page. Optionally schedule auto-resume:

```apex
System.schedule('RLM Asset Auto-Resume', '0 0 1 * * ?', new RLM_AssetResumeScheduler());
```

## Verification status

- **Phase 0 (done):** endpoint/schema verification recorded in
  `.agents/artifacts/abo-endpoint-verification.md`.
- **Offline Apex tests (done):** `RLM_AssetOrderingServiceTest`,
  `RLM_AssetConsoleControllerTest`, `RLM_AccountAssetPortfolioServiceTest`,
  `RLM_AssetConfiguratorServiceTest`, `RLM_AssetSuspensionServiceTest`.
- **Live verification (required before merge):** the console's behavioral paths
  (native action invocation, multi-contract → single Quote consolidation,
  Configurator `configure` request/response shape, `blngSvcSuspendBilling`) must
  be exercised on an org with seeded assets. The Phase 0 target org was empty
  (0 assets), so these were validated by schema/endpoint probing and mocked unit
  tests only. Open items to confirm live: `amendOutputType`/`renewOutputType`/
  `cancelOutputType` values, `actionSubtype` values for Upgrade/Downgrade, and
  whether mixed action types can share one output record.
