# Field Service + Revenue Cloud Demo — Quote to Install to Service to Bill

Joint demo for a QuantumBit Rev Cloud CDO with **Field Service Core** enabled
(no FSL managed package). One customer (Infinitech), one asset (a PowerSwerve
R750 rack server) and one continuous loop in nine scenes:

| Act | # | Scene | Persona | What proves it |
|-----|---|-------|---------|----------------|
| 1 · Sell, deliver, bill | 1 | Configure & quote | Seller | Quote with R750 + Installation + Gold maintenance |
| | 2 | Activate the order | Fulfillment Manager | DRO plan: Ship → Field Installation → Billing |
| | 3 | Automatic dispatch | Dispatcher | Install Work Order + Service Appointment created by DRO |
| | 4 | Technician on site | Technician | Appointment assigned, serial number on the Asset |
| | 5 | Billing starts at install | Billing Specialist | Milestone releases billing, invoice posts automatically |
| 2 · Service, protect, grow | 6 | Maintenance runs itself | Service Manager | Maintenance Plan + monthly preventive Work Orders from Gold |
| | 7 | Break/fix with coverage check | Dispatcher & Billing | Covered vs Not Covered; uncovered repair is invoiced |
| | 8 | Upsell from the field | Technician → Seller | Flag Expansion creates an Opportunity from the Work Order |
| | 9 | One install base | Account Team | Asset shows orders, Work Orders, maintenance, entitlements |

## What gets built (`fsl: true`)

| Piece | Source |
|-------|--------|
| Field Service settings (Work Orders, SA lifecycle) | `unpackaged/pre_fsl/` |
| Skills, `RLM_Field_Service` PS + `RLM_Field_Service_PSG` | `unpackaged/post_fsl/` |
| `WorkOrder.RLM_Order__c`, `RLM_Fulfillment_Step__c`, `RLM_Service_Coverage__c`, `RLM_Billable_Order__c`; `Opportunity.RLM_Source_Work_Order__c` | `unpackaged/post_fsl/objects/` |
| Flows and Apex actions (see [Automation](#automation)) | `unpackaged/post_fsl/flows/`, `unpackaged/post_fsl/classes/` |
| `WorkOrder.RLM_Flag_Expansion` quick action | `unpackaged/post_fsl/quickActions/` |
| Operating hours, territory, work types | `datasets/sfdmu/qb/en-US/qb-fsl/` |
| Time slots, skill/product requirements, service resource, territory member | `scripts/apex/setupFslFoundation.apex` |
| Field Installation step group, steps, decomposition rules | `datasets/sfdmu/qb/en-US/qb-dro-fsl/` |
| Install (QB-INST-1000) and repair (QB-SVC-REPAIR) prices, Installation Milestone billing policy | `scripts/apex/setupFslRevenue.apex` |
| Work Order record page (header actions incl. Flag Expansion) + View override | `templates/flexipages/standalone/fsl/`, `templates/objects/fsl/` |
| Work Order / maintenance / entitlement related lists on Account, Asset, Order pages | `templates/flexipages/patches/fsl/`, `templates/layouts/fsl/` |
| Field Service app tabs | `templates/applications/patches/fsl/` |

## Build

1. Confirm the org has Field Service PSLs (see `docs/analysis/fsl-cdo-license-audit.md`).
2. Set `fsl: true` in `cumulusci.yml` (`project.custom`). Scenes 5–7 also need
   `billing: true`; the Field Installation plan needs `dro: true`.
3. On a fresh build, `prepare_rlm_org` runs `prepare_fsl` at step 11.5,
   `setup_fsl_revenue` at step 13.5 (after `prepare_billing`, whose
   `qb-billing` load resets product billing policies) and refreshes the
   pricing decision tables later in the flow. On an org that already has
   QuantumBit, DRO and billing data, run the sub-flow and the revenue task,
   refresh the decision tables and redeploy UX:

   ```bash
   cci flow run prepare_fsl --org <alias>
   cci task run setup_fsl_revenue --org <alias>
   sf api request rest /services/data/v66.0/actions/standard/refreshDecisionTable --method POST \
     --body '{"inputs":[{"decisionTableApiName":"Price_Book_Entry_Decision_Table_v2","isIncremental":false}]}' \
     --target-org <sf_alias>
   sf api request rest /services/data/v66.0/actions/standard/refreshDecisionTable --method POST \
     --body '{"inputs":[{"decisionTableApiName":"RLM_ProductCategoryQualification","isIncremental":false}]}' \
     --target-org <sf_alias>
   cci task run assemble_and_deploy_ux   # or the prepare_ux flow
   ```

   Without the refresh, quoting QB-INST-1000 fails with *Could not find product*.

`prepare_fsl` and `setup_fsl_revenue` are idempotent — re-running them
creates no duplicates. Re-run `setup_fsl_revenue` after any `qb-billing`
reload so the R750, RAXS and install products return to the Installation
Milestone billing policy.
`deploy_post_fsl` runs only `RLM_FSL_ServiceBillingTest`, so production-type
CDOs without org-wide Apex coverage can deploy it.

## Automation

| Trigger | Automation | Result |
|---------|------------|--------|
| DRO *Create Install Work Order* AutoTask | `RLM_FSL_Create_Install_Work_Order` | Work Order (Account, Order, Asset, step, Server Rack Installation, San Francisco) + Service Appointment |
| Install Work Order → Completed | `RLM_FSL_Complete_Fulfillment_Step` → `RLM_FSL_InvoiceOrder` | Completes *Installation Complete*, accomplishes the *Installation Complete* billing milestones, posts the invoice for the order's ready billing schedules |
| Install Work Order → Completed, Gold on the order | `RLM_FSL_Activate_Service_Coverage` | Entitlement on the Asset + Maintenance Plan with a monthly rule and the Asset |
| Break/Fix Work Order saved | `RLM_FSL_Check_Service_Coverage` (before save) | Active Entitlement on the Asset → `Covered` + EntitlementId, otherwise `Not Covered` |
| Not Covered Work Order → Completed | `RLM_FSL_Bill_Uncovered_Repair` → `RLM_FSL_BillRepair` | Activated QB-SVC-REPAIR order linked on `RLM_Billable_Order__c`, then a posted invoice |
| *Flag Expansion* on a Work Order | `RLM_FSL_Flag_Expansion` screen flow | Qualification Opportunity on the account, linked through `RLM_Source_Work_Order__c` |

DRO passes the **FulfillmentOrderLineItem** Id as `recordId` to AutoTask flows.
The install flow resolves the step through `FulfillmentStepSource.SourceLineItemId`,
then the plan (`SourceIdentifier` = Order Id) and the plan's
"Installation Complete" step, which it stores on `WorkOrder.RLM_Fulfillment_Step__c`.

Billing for the R750 and installation lines uses the **Installation Milestone**
billing treatment: their billing schedules wait in
*Waiting for Milestone Event Accomplishment* until the install Work Order is
completed. Gold maintenance bills on its normal recurring schedule.

## Demo script

Shortcut for preparing (or rehearsing) the first scenes:

```bash
python scripts/place_fsl_demo_order.py --target-org <sf_alias> [--ship]
```

The script creates an Opportunity and a Place Sales Transaction quote with
the R750, Installation and Assembly and Gold maintenance (`--no-support` drops
Gold), converts it to an order, waits for the Revenue Lifecycle Management
usage assignment, activates the order, and waits for the fulfillment plan and
assets. `--ship` also completes *Ship Hardware* and waits for the install
Work Order.

### Act 1 — Sell, deliver, bill

1. **Configure & quote** — Infinitech opportunity → New Quote. Add the
   PowerSwerve R750 bundle (QB-BDL-R750), *Installation and Assembly*
   (QB-INST-1000, one-time $2,500) and *Gold Hardware Maintenance*
   (QB-SUPP-1005, flat annual price). Create Order → Activate.
2. **Activate the order** — Order → **Fulfillment** tab. Walk the plan: Ship
   Hardware → Field Installation → Installation Complete → Initiate Billing,
   and point at billing waiting behind the install. Complete *Ship Hardware*
   (the stand-in for the warehouse).
3. **Automatic dispatch** — The *Installation Work Orders* list on the
   Fulfillment tab now shows the install Work Order. Open it: Order,
   fulfillment step, Asset, *Server Rack Installation* work type and
   *QuantumBit San Francisco* territory are filled in, and a Service
   Appointment exists.
4. **Technician on site** — Schedule the appointment and assign the
   technician (Assigned Resources on the appointment). Enter the serial number
   on the Asset (for example `PSR750-SF-24601`).
5. **Billing starts at install** — Open the R750 billing schedule: *Waiting
   for Milestone Event Accomplishment*. Complete the Service Appointment, then
   the Work Order. The Fulfillment tab shows *Installation Complete* done; the
   billing schedule moves to Ready for Invoicing and then Completely Billed,
   and a posted invoice for hardware + install + Gold appears on the account
   within about a minute.

### Act 2 — Service, protect, grow

6. **Maintenance runs itself** — Completing the install created a Gold
   Maintenance Plan on the Asset (monthly rule, 3-month generation window) and
   an Entitlement. On the plan, click **Generate Work Orders**; the monthly
   *Preventive Maintenance* Work Orders and appointments appear.
7. **Break/fix with coverage check** — Create a *Hardware Break/Fix* Work
   Order on the covered R750: *Service Coverage* = Covered and the Gold
   Entitlement is linked. Create one for a customer whose R750 has no Gold
   (Apex Dynamics; prepare it with
   `place_fsl_demo_order.py --account-name "Apex Dynamics" --no-support`):
   Not Covered. Complete the uncovered one; a $1,200 Break/Fix Repair order
   appears in *Billable Order* and its invoice posts automatically.
8. **Upsell from the field** — On the install Work Order, click **Flag
   Expansion**, describe what you saw and enter an estimated value. The
   Opportunity appears on the account (and in *Expansion Opportunities* on
   the Work Order). The seller continues from the Account **Assets** tab
   (asset amendment) or the opportunity's New Quote.
9. **One install base** — Open the R750 Asset: serial number, then
   **Related**: Work Orders, Maintenance Assets, Entitlements, billing schedule
   groups. The Account's Related tab shows all Work Orders and orders.

## Known limitations

- *Post Invoice* and *Receive Payment* in the DRO Finance group are manual
  steps; the invoice itself is posted by `RLM_FSL_InvoiceOrder`.
- Orders placed directly through the Place Sales Transaction API (not from a
  quote) get no Revenue Lifecycle Management usage assignment, so
  `RLM_Submit_Order_on_Activation` skips them. The demo script uses the quote
  path; `RLM_FSL_BillRepair` inserts the assignment itself.
- The pricing engine occasionally rejects the first quote after idle time
  (*unable to proceed with pricing calculation*); the demo script retries.
- QB-BDL-RAXS has decomposition rules but no standard USD price in some CDOs;
  use QB-BDL-R750 for the demo.
- Dispatcher Console / optimized scheduling need the FSL managed package
  (`fsl_managed_package: true` + `fsl_package_version_id`), which is off by
  default; scenes are shown on desktop record pages.

## Teardown

```bash
cci task run delete_qb_fsl_data --org <alias>
```

Deletes demo Work Orders, Service Appointments, Maintenance Plans (rules and
assets), Gold Entitlements and the FSL foundation records (child → parent).
DRO step definitions from `qb-dro-fsl`, orders and invoices are left in place.
