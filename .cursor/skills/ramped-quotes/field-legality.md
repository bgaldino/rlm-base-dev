# Ramped Quotes — Field legality (live 264 / v68.0)

> Sub-file of `.cursor/skills/ramped-quotes/SKILL.md`.

Snapshot — re-verify with a `describe` on the target org. Writeable = accepted on the graph; read-only = rejected on the graph or by direct API writes, or engine-owned. These are not the describe createable/updateable flags.

| Object | Writeable (set these) | Read-only (never set) |
|---|---|---|
| `QuoteLineGroup` | `IsRamped`, `SegmentType`, `StartDate`, `EndDate`, `SortOrder`, `Type`, `Name`, `RampUpliftType` | — |
| `QuoteLineItem` | `Quantity`, `StartQuantity`, `UnitPrice`, `UnitPriceUplift`, `Discount`, `DiscountAmount`, `StartDate`, `EndDate`, `SegmentType`, `QuoteLineGroupId` | `RampIdentifier`, `SegmentIdentifier`, `EndQuantity`, `NetUnitPrice`, `TotalPrice`, `ApplUnitPriceUpliftPct`; `RampUpliftType` engine-owned via Place |
| `Quote` | `Status`, `TotalPriceOverride`, `AdjustmentDistributionLogic` | `CalculationStatus`, `TotalPrice`, `GrandTotal`, `QuoteNumber` |
| `Product2` | — | `CanRamp` (direct writes refused on one 264 org via REST, Bulk, Apex, CLI; gates the line-ramp path only) |

`RampIdentifier` and `SegmentIdentifier` are read-only here because the ramp actions stamp them:
`EditGroup` stamps `RampIdentifier` (SKILL.md Quick Rule 1 and build step 2), and every ramped line
carries both after `groupRampAction` (SKILL.md validation checks). The 264 schema marks both
createable/updateable on `QuoteLineItem`. Never set them.
[Open: send a caller value for `RampIdentifier` on a Place and record whether it is refused or overwritten]

`SegmentType` enum: `Yearly`, `Custom`, `FreeTrial`, `Prorated`.
`QuoteLineGroup.Type` enum: `CPQQuoteGroup`, `RampScheduleGroup`, `AssetSwap`,
`AssetUpgrade`, `AssetDowngrade`.
