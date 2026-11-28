# schema_diff snapshots

`{260,262,264}-schema.json` are describe snapshots, one per release, kept as captured.

**Key-casing edit (not a re-capture).** Three object keys were renamed to the describe's canonical
casing: `PriceBook2` to `Pricebook2`, `PriceBookEntry` to `PricebookEntry`, `PricingAPIExecution`
to `PricingApiExecution` (object describe is case-insensitive, so the wrong casing went unnoticed).
Verified against the pre-edit files at the base branch: the only differences in each of the three
files are those three keys, with every value identical. Re-check with
`git diff --word-diff` or by loading both versions and comparing key sets and values.
