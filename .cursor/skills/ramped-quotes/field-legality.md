# Ramped Quotes — Field legality (live 264 / v68.0)

> Sub-file of `.cursor/skills/ramped-quotes/SKILL.md`.

Snapshot — re-verify with a `describe` on the target org. Writeable = accepted on the graph; read-only = rejected or engine-owned there. These are not the describe createable/updateable flags.

| Object | Writeable (set these) | Read-only (never set) |
|---|---|---|
| `QuoteLineGroup` | `IsRamped`, `SegmentType`, `StartDate`, `EndDate`, `SortOrder`, `Type`, `Name`, `RampUpliftType` | — |
| `QuoteLineItem` | `Quantity`, `StartQuantity`, `UnitPrice`, `UnitPriceUplift`, `Discount`, `DiscountAmount`, `StartDate`, `EndDate`, `SegmentType`, `QuoteLineGroupId` | `RampIdentifier`, `SegmentIdentifier`, `EndQuantity`, `NetUnitPrice`, `TotalPrice`, `ApplUnitPriceUpliftPct`; `RampUpliftType` engine-owned via Place |
| `Quote` | `Status`, `TotalPriceOverride`, `AdjustmentDistributionLogic` | `CalculationStatus`, `TotalPrice`, `GrandTotal`, `QuoteNumber` |
| `Product2` | — | `CanRamp` (direct writes refused on one 264 org via REST, Bulk, Apex, CLI; gates the line-ramp path only) |

The 264 schema marks `RampIdentifier` and `SegmentIdentifier` createable/updateable. They are listed
read-only because the graph rejected caller writes (not re-tested against the describe) `[inferred]`.
`groupRampAction` stamps both; never set them.

`SegmentType` enum: `Yearly`, `Custom`, `FreeTrial`, `Prorated`.
`QuoteLineGroup.Type` enum: `CPQQuoteGroup`, `RampScheduleGroup`, `AssetSwap`,
`AssetUpgrade`, `AssetDowngrade`.
