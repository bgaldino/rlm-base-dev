# Field Service License Audit — Rev Cloud CDO

**Date:** 2026-10-21  
**Org audited:** `260 rc demo april 8 2026 - test customer template upload`  
(`trailsignup.b06ac1f8b1c4bc@salesforce.com`, `00Dak00000pYiinEAC`)

Also spot-checked: Agentic Memberships Demo, Equinox, ADT — same PSL pattern.

## Results

| Check | Result |
|-------|--------|
| Field Service Standard / Dispatcher / Mobile / Scheduling PSLs | **Present** (e.g. Standard 55, Dispatcher 55, Mobile 65, Scheduling 105) |
| FSL managed package (`NamespacePrefix = FSL`) | **Not installed** |
| WorkOrder / ServiceAppointment / ServiceTerritory / WorkType / OperatingHours | **Queryable** (Field Service Core objects available) |
| `FieldServiceSettings.fieldServiceOrgPref` | Already `true` on audited org |
| `FieldServiceSettings.enableWorkOrders` | Was `false` — enable via `pre_fsl` settings deploy |
| PSL assignments for FieldService* | None observed at audit time |

## Build Org: `fsl-rc`

**Org:** `alostumbo@fsl.rc.demo` (`00DjV000006tRYoUAM`, CCI alias `fsl-rc`)

| Check | Result |
|-------|--------|
| Field Service PSLs | **Present** — Standard 55, Dispatcher 55, Mobile 65, Scheduling 105 |
| FSL managed package | **Not installed** |
| `FieldServiceSettings.enableWorkOrders` | `false` before `deploy_pre_fsl`, `true` after |
| `prepare_fsl` | Ran twice; second run created no duplicates |
| End-to-end | Order → DRO Field Installation → Work Order + Service Appointment → WO Completed → Installation Complete → Initiate Billing |

## Decision

Proceed with **Field Service Core** (`fsl: true`). Keep `fsl_managed_package: false` by default (Dispatcher Console / optimized scheduling package is optional later).

Trialforce CDO templates used for QuantumBit Rev Cloud demos already include Field Service PSLs — no new CDO template is required for Core enablement.
