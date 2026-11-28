# Verified behavior: product search, sort rules and the `language` parameter

Read this when searching, sorting or translating catalog data through the PCM and Connect APIs. Results of runs
on sale, order, asset and renewal behavior sit next to their rules in the other sub-files. Tag meanings and org
kinds are defined in `SKILL.md` (the paragraph that opens the skill).

## 1. Searching and sorting products through the API

- `POST /connect/cpq/products/search` with `orderBy` on the standard field `ProductCode` ordered the results [Measured: 2026-11-27, 264, org kind not recorded].
  An invalid field name in `orderBy` returned `UnknownError` [Measured: 2026-11-27, 264, org kind not recorded]. `orderBy` on a custom numeric product field ordered
  the results while the sort-rule gate was off (see the next bullet) [Measured: 2026-11-26, 264, ent-sb0 harness build]. The `orderBy` string is
  `property[:direction]`; direction defaults to ascending and a bad direction is skipped
  [Platform behaviour, traced].
- **Sort rules** (admin-defined product-list sort options, set in a Sort Settings tab of Product Catalog
  Management) are behind a feature gate. On the org tested the gate was off: there was no Sort
  Settings tab on Index and Search Configuration [Measured: 2026-11-26, 264, ent-sb0 harness build], the sort-rule API returned `FORBIDDEN` [Measured: 2026-11-26, 264, ent-sb0 harness build], and Browse Catalog
  offered only a name ascending or descending toggle [Measured: 2026-11-26, 264, ent-sb0 harness build]. The validator accepts a Product2-based rule
  on a custom field [Platform behaviour, traced]. The product-list request takes `sortRuleIds` (only the first id
  is honored) and `includeSortRules` [Platform behaviour, traced]. Where the Sort Settings tab sits once the gate is on is
  [Open: on an org with the gate on, open Index and Search Configuration and confirm the Sort Settings tab]. Everything else about sort rules, including
  whether a rule can be the default on load and whether a rule applies per category, is
  [Open: needs an org with the sort-rule gate on; run: create a rule on a numeric custom field, refresh the index,
  open Browse Catalog and compare the sort dropdown with and without a category selected]. Until then, use `orderBy`
  in a custom browse screen, or the name toggle.

## 2. The `language` parameter of the PCM Connect APIs

- The PCM resources (catalog, category and product detail and lists under `/connect/pcm/`) take `language` for
  translated data [Dev guide: connect-resources-get-category-by-id.md].
- On an org without the data translation object, `es` and `fr_CA` were accepted and returned localized status
  text [Measured: 2026-11-27, 264, org kind not recorded]. `spanish` and an invented value were also accepted, but returned English status text [Measured: 2026-11-27, 264, org kind not recorded]. No value
  returned an error [Measured: 2026-11-27, 264, org kind not recorded].
- With data translation on, the platform check accepts only the platform's language enum names (for example
  `spanish`), case-insensitive, not ISO codes; an ISO code returns an "Invalid language for translation" error
  [Platform behaviour, traced]. [Open: re-run with data translation on and a translated record; check whether fr_CA
  has an enum name]. A client that holds ISO codes should map them to the enum names before calling.
