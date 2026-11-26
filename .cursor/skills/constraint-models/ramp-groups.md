# Ramp groups and segments in constraint models

Depth behind the parent [SKILL.md](SKILL.md#ramp-groups-and-segments).

Rules can target quote groups, ramp groups and ramp segments through the
`SalesTransactionItemGroup` context tag. Use the 264 dev guide for syntax:
[Define Constraints for Quote Groups, Ramps, and Ramp Segments](../../../docs/salesforce/264/dev-guide/articles/cml-quote-group-ramp-segment-constraints.md).
Three attributes do the work:

- `SalesTransactionItemGroup` on a `groupBy` container (`@(virtual = true, groupBy = SalesTransactionItemGroup)`)
  scopes the rule to one group. The engine runs one virtual container for each group that
  contains one or more products from the `QuoteGroup` container.
- `IsLineGroupRamped__std` in a `require` restricts a rule to ramp groups; `!(...)` restricts it to unramped groups.
- `ItemSegmentType` tests the segment type of a ramped line. `RLM_SalesTransactionContext` maps it from
  `QuoteLineItem.SegmentType` (`OrderItem.SegmentType` for orders), so it carries that picklist's value
  (`Yearly`, `Custom`, `FreeTrial` or `Prorated` on the 264 org tested). The dev guide's example tests
  `ItemSegmentType != "Trial"`; `Trial` is not a value, so that test never excludes a segment. Test
  `"FreeTrial"`. Measured on one 264 org (2026-11-06): in a FreeTrial segment a rule on `== "FreeTrial"`
  fired and one on `== "Yearly"` did not; `== "Yearly"` rules fired in Yearly segments.

A virtual `Quote` container is not scoped to a group: the configurator receives every line of the quote,
across all segments, as one set, and no scoping by group was found other than a `groupBy` container
(`[Platform behaviour, traced]`; see [quantities-from-attributes.md](quantities-from-attributes.md#checks-across-top-level-lines-a-virtual-quote-container)).

Groups don't support rules such as `hide`, `disable` or `recommend`, which act on a condition. Use `require` in groups.

Measured with a test `groupBy` container on one 264 org (2026-11-06; standalone Term Annual products, Place API):

- **Declare the group container on the transaction container.** The rules fired only after `type Quote` had
  `relation quotegroup : QuoteGroup;`, as in the dev guide's quote-group example. The ramp and segment
  examples omit it. Without it nothing fired and nothing reported an error.
- **Set `configurationMethod: Force` to make a Place call run the rules.** The method defaults to `Skip`
  (dev guide, *Configurator Preference Input*), so `configurationOptions.executeConfigurationRules: true` on
  its own ran nothing. Group-level rules were tested through Place with `Force` only. `System` lets the
  platform decide: with the shipped QuantumBitBundle model (a quote-level `require`, no group container) it
  ran the rule in the call that added the triggering line, and on a quote-only PATCH of a quote missing the
  required product. So `System` doesn't limit rules to calls that add lines.
- **A Connect clone ran group rules with no configuration preference.** Rules keyed on
  `IsLineGroupRamped__std` and `ItemSegmentType == "Yearly"` fired during the clone calls, with every
  Place call `Skip`.
- **Products a group `require` adds outside `AddProducts` have no ramp ids.** Added during a clone, or by
  a `Force` Place without `groupRampAction`, they had blank `RampIdentifier`, `SegmentIdentifier` and
  `SegmentType`. An EditGroup with `Force` added nothing. A `Force` Place with
  `groupRampAction: AddProducts` stamped the products it added, each with its own `RampIdentifier` and the
  segment's `SegmentType` (Yearly, or FreeTrial in a FreeTrial segment). It did not stamp blank lines
  already on the quote. How the blank lines behave at order and amend was not measured.

Configuration rules don't recognize quote or order groups (Help, *Considerations for Ramp Deals*). A rule that adds a standalone
product to a ramp segment doesn't ramp it or add it to later segments; a rule-added child of a ramped parent is
ramped and carried forward. The shipped QuantumBit models have no group-level container. For the ramp side, see
the [ramped-quotes skill](../ramped-quotes/SKILL.md) and
[Cloning a segment that holds a bundle](../ramped-quotes/bundle-children-lifecycle.md#cloning-a-segment-that-holds-a-bundle).
