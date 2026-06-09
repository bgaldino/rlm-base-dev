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

## In-Org Setup (One-Time)

### Prerequisites

- A scratch org or sandbox with Revenue Cloud (RLM) installed.
- A product with an existing **Product Configurator** flow assigned
  (configured via **Revenue Configurator** → product record).
- Permission to edit flows.

### Step 1 — Deploy the component

```bash
sf project deploy start \
  --source-dir unpackaged/post_utils/lwc/rlmConfiguratorDebugger \
  --target-org <your-org-alias>
```

Or deploy via CCI if the `post_utils` bundle is already part of a flow step:

```bash
cci task run deploy --org <alias> \
  -o path unpackaged/post_utils/lwc/rlmConfiguratorDebugger
```

### Step 2 — Clone the Product Configurator flow

> **Do not edit the managed Configurator flow directly.** Clone it first.

1. Setup → Flows → find **Product Configurator** (or the existing custom clone
   your org uses).
2. Click **Save As** → save as a new version or a new flow named
   `Product_Configurator_Debug` (or similar).

### Step 3 — Add the component to the flow

1. Open the cloned flow in Flow Builder.
2. Find the **Screen** element that contains the standard Configurator UI
   component (look for the element labelled "Configurator" or similar).
3. Add a new **Screen** element **after** the Configurator screen, or add the
   debugger component as an additional element on the same Configurator screen
   by dragging **RLM Configurator Debugger** from the component list on the
   left.

### Step 4 — Bind Flow variables

With the **RLM Configurator Debugger** component selected in the Screen
element, map each input property to the corresponding Flow output variable
produced by the Data Manager:

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

### Step 5 — Activate and assign

1. **Save** and **Activate** the cloned flow.
2. Navigate to the Product record you want to test.
3. In the **Revenue Configurator** section, change **Configurator Flow** to
   the newly cloned and activated flow.
4. Open the product in the Commerce / Sales flow to launch the configurator.

The debugger panel will appear. Use **Collapse** to hide it once testing is
complete, or remove the component and re-activate the original flow.

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
