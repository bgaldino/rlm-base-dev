# Ramped Quotes — Field legality (live 264 / v68.0)

> Sub-file of `.cursor/skills/ramped-quotes/SKILL.md`.

Snapshot — re-verify with a `describe` on the target org. Writeable = createable/updateable on the graph.

| Object | Writeable (set these) | Read-only (never set) |
|---|---|---|
| `QuoteLineGroup` | `IsRamped`, `SegmentType`, `StartDate`, `EndDate`, `SortOrder`, `Type`, `Name`, `RampUpliftType` | — |
| `QuoteLineItem` | `Quantity`, `StartQuantity`, `UnitPrice`, `UnitPriceUplift`, `Discount`, `DiscountAmount`, `StartDate`, `EndDate`, `SegmentType`, `QuoteLineGroupId` | `RampIdentifier`, `SegmentIdentifier`, `EndQuantity`, `NetUnitPrice`, `TotalPrice`, `ApplUnitPriceUpliftPct`; `RampUpliftType` engine-owned via Place |
| `Quote` | `Status`, `TotalPriceOverride`, `AdjustmentDistributionLogic` | `CalculationStatus`, `TotalPrice`, `GrandTotal`, `QuoteNumber` |
| `Product2` | — | `CanRamp` (direct writes refused on one 264 org via REST, Bulk, Apex, CLI; gates the line-ramp path only) |

The 264 schema snapshot (`scripts/erd/schema_diff/264-schema.json`) lists `RampIdentifier` and
`SegmentIdentifier` as createable/updateable, so the read-only column above is the platform's
rejection of a caller write on the graph, not what a field describe shows `[inferred]`; the rejection was
not re-measured against the describe. `groupRampAction` stamps both, so never set them yourself.

`SegmentType` enum: `Yearly`, `Custom`, `FreeTrial`, `Prorated`.
`QuoteLineGroup.Type` enum: `CPQQuoteGroup`, `RampScheduleGroup`, `AssetSwap`,
`AssetUpgrade`, `AssetDowngrade`.
