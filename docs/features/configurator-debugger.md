# Configurator Debugger LWC

A developer/debugging Flow Screen component that attaches to the Product
Configurator flow and provides:

- **State tab** — live formatted JSON snapshot of all Data Manager `@api`
  properties (optionGroups, header, messages, summary, flags, …)
- **LMS Log tab** — timestamped, expandable log of every inbound
  `lightning__productConfigurator_notification` LMS event
- **Edit & Publish tab** — JSON editor with one-click snippet insertion,
  payload validation for attribute updates, and direct LMS publish back to the
  Data Manager, with a race-condition guard
- **API timing + state search** — in-progress API duration, last API timing,
  and searchable state JSON subtabs

## Component Location

```
unpackaged/post_utils/lwc/rlmConfiguratorDebugger/
```

## How It Works

The Data Manager exposes all configuration state as Flow output variables that
are bound to `@api` properties on this component. Communication is handled
entirely over the shared LMS channel
`@salesforce/messageChannel/lightning__productConfigurator_notification`.

### Race-condition guard

When the user clicks **Apply**, the payload is queued and the component sets
`_waitingForDataManager = true`. It then waits for the Data Manager to push
an updated `optionGroups` value (which triggers the custom setter). Only then
is the publish fired. A 500 ms fallback timer ensures the message is sent even
if the Data Manager does not echo back.

### Optional automatic instant pricing

If `automaticInstantPricing` is set to `true`, the debugger attempts a one-time
`toggleInstantPricing` publish after LMS is ready, only when
`isInstantPricingEnabled` is currently false.

## In-Org Setup

### Automated (via CCI)

The `prepare_quantumbit` flow deploys everything automatically:

1. **`deploy_post_utils`** — deploys the LWC, the `RLM_Debug_Configurator` flow,
   and the `RLM_ConfigDebug` permission set.
2. **`insert_qb_decision_explainer_data`** — creates the Decision Explainer
   records (Configuration Logs) and registers the flow as a
   `ProductConfigurationFlow`.

After the flow runs, assign `RLM_ConfigDebug` to users who need configuration
log access, then assign the `RLM_Debug_Configurator` flow to a product via
the **Revenue Configurator** section on the Product record.

### Manual (standalone deploy)

```bash
# Deploy the full post_utils bundle (LWC + flow + permission set)
sf project deploy start \
  --source-dir unpackaged/post_utils \
  --target-org <your-org-alias>

# Load Decision Explainer + ProductConfigurationFlow records
cci task run insert_qb_decision_explainer_data --org <alias>
```

### Assigning the flow to a product

1. Navigate to the Product record you want to debug.
2. In the **Revenue Configurator** section, change **Configurator Flow** to
   `RLM_Debug_Configurator`.
3. Open the product in the Commerce / Sales flow to launch the configurator.

The debugger panel will appear. Use **Collapse** to hide it once testing is
complete, or switch the product back to the standard configurator flow.

### Flow variable bindings

The `RLM_Debug_Configurator` flow ships pre-wired with all Data Manager
bindings. For reference, these are the `@api` properties bound:

| Component Property | Flow Variable |
|-------------------|---------------|
| `transactionId` | `{!transactionId}` |
| `transactionLineId` | `{!transactionLineId}` |
| `currentTransactionLineId` | `{!currentTransactionLineId}` |
| `optionGroups` | `{!optionGroups}` |
| `parentName` | `{!parentName}` |
| `origin` | `{!origin}` |
| `headerTitle` | `{!headerTitle}` |
| `currencyCode` | `{!currencyCode}` |
| `searchResultOptionId` | `{!searchResultOptionId}` |
| `messages` | `{!messages}` |
| `summary` | `{!summary}` |
| `attributeCategories` | `{!attributeCategories}` |
| `addedNodes` | `{!addedNodes}` |
| `salesTransactionItems` | `{!salesTransactionItems}` |
| `transactionRecord` | `{!transactionRecord}` |
| `isDesignTime` | `{!isDesignTime}` |
| `isClassContext` | `{!isClassContext}` |
| `isInstantPricingToggleEnabled` | `{!isInstantPricingToggleEnabled}` |
| `isApiInProgress` | `{!isApiInProgress}` |
| `isInstantPricingEnabled` | `{!isInstantPricingEnabled}` |
| `isProductValidationEnabled` | `{!isProductValidationEnabled}` |
| `isCompactLayoutEnabled` | `{!isCompactLayoutEnabled}` |
| `showPrices` | `{!showPrices}` |
| `isPriceRampEnabled` | `{!isPriceRampEnabled}` |
| `isConfiguratorDisabled` | `{!isConfiguratorDisabled}` |
| `automaticInstantPricing` | `true`/`false` (optional) |

### Configuration Logs setup

The `insert_qb_decision_explainer_data` task also creates the Decision
Explainer framework records required for Configuration Logs:

- `ApplicationSubtypeDefinition` — `SolverPath`
- `BusinessProcessTypeDef` — `SolverPath`
- `ExplainabilityActionDef` — `SolverPath`
- `ExplainabilityActionVersion` — `SolverPath` (active)

Assign the `RLM_ConfigDebug` permission set to users who need log access.
Logs are viewable in the **Revenue Cloud Operations Console** app.

## Edit & Publish — Quick Reference

### Payload envelope

All publish calls must use this top-level shape (matching the `valueChanged`
LMS event):

```json
{
  "action": "valueChanged",
  "data": [
    { /* one change object per item */ }
  ]
}
```

### Snippet types (Insert buttons)

| Button | Use case | Key fields |
|--------|----------|------------|
| **Quantity** | Change line-item quantity | `key`, `field: "Quantity"`, `value` |
| **Attribute** | Update a product attribute | `key`, `field: "AttributeField"`, `attributeId`, `value` |
| **Select** | Select / deselect a bundle option | `productRelatedComponentId`, `field: "isSelected"`, `value` |
| **Custom Field** | Update a custom field via multi-value syntax | `key`, `values: [{field, value}]` |
| **PSM** | Switch Product Selling Model | `key`, `field: "ProductSellingModel"`, `value: {psmId, pbeId}` |

### Finding `transactionLineId` and other IDs

The **State** tab shows the live `transactionLineId` and all `optionGroups`
data. Expand option groups to find `key` values for child items.

### Attribute payload guardrails

For `field: "AttributeField"` entries, the debugger validates:

- `attributeId` must be a string and should be the attribute definition id
  (typically `0tj...`), not a picklist id.
- If `attributeCategories` is present, `attributeId` must exist in that
  state snapshot.
- If a picklist id is mistakenly supplied as `attributeId`, the debugger blocks
  publish and returns a targeted error.

## LMS Events Reference

| Event (`action`) | Direction | Description |
|-----------------|-----------|-------------|
| `valueChanged` | UI → DM | Notify the Data Manager of a field change |
| `navigate` | UI → DM | Navigate to a child bundle or back |
| `toggleInstantPricing` | UI → DM | Toggle real-time pricing on/off |
| `toggleRulesValidation` | UI → DM | Toggle constraint rules validation |
| `toggleCompactLayout` | UI → DM | Toggle compact vs. full layout |
| `updatePrices` | UI → DM | Force a price recalculation |
| `validateProduct` | UI → DM | Run product validation |
| `cloneItems` | UI → DM | Clone selected line items |
| `closePreview` | UI → DM | Close a preview/preview panel |

All inbound events (DM → UI) are captured in the **LMS Log** tab.
