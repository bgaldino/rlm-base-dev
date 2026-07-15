# Post–data-load refresh (decision tables + catalog search index)

After loading product catalog (PCM) and/or pricing data into an org **outside** a full
`prepare_rlm_org` run — for example SFDMU loads of `kld-pcm` / `kld-pricing` into a
connected org — you must refresh pricing decision tables and rebuild the Product Catalog
search index. Otherwise products may exist in Salesforce data but not appear in product
search, and quote pricing may not resolve new price book entries or volume tiers.

A full `prepare_rlm_org` already does this at the end (steps 33–34). This guide is for
**incremental** loads on an existing org.

## Prerequisites

1. Data plans already loaded (e.g. `insert_kld_pcm_data` / `insert_kld_pricing_data`, or
   equivalent `sf sfdmu run`).
2. CumulusCI can authenticate to the target org.

If CCI fails with `INVALID_AUTH_HEADER` while `sf` still works, see
[CCI sf CLI token workaround](cci-sf-cli-token-workaround.md). Quick fix for the current
shell (also set by repo `.envrc` when direnv is available):

```bash
export SF_TEMP_SHOW_SECRETS=true
```

## Connect the org to CCI

```bash
# SF CLI username or alias, then a CCI org name you choose
cci org import camkld@salesforce.com camkld
cci org info camkld
cci org default camkld
```

## Refresh pricing decision tables

`refresh_dt_default_pricing` does **not** accept `--org` on the CLI. Set the default org
first, then run:

```bash
export SF_TEMP_SHOW_SECRETS=true
cci org default <cci_org_name>
cci task run refresh_dt_default_pricing
```

This queues a refresh for the default pricing decision tables, including:

- `Price_Book_Entry_Decision_Table_v2`
- `Price_Adjustment_Tier_Decision_Table`
- Related attribute/bundle/contract/tax tables in the project anchor list

Status `Queued` / `isSuccess: True` means the platform accepted the refresh; completion is
asynchronous (often several minutes).

For a broader refresh (rating, commerce, etc.), use:

```bash
cci flow run refresh_all_decision_tables
```

(subject to feature flags / org default).

## Rebuild the Product Catalog search index

```bash
cci task run rebuild_search_index --org <cci_org_name>
```

This starts a FULL, IMMEDIATE PCM catalog index build via Connect API. The task logs a
snapshot id and returns while the build continues asynchronously — allow several minutes
before expecting new products in search / guided selling.

## Wait, then verify

1. Wait **5–10 minutes** after both tasks succeed.
2. In the UI, search for a newly loaded SKU (e.g. a `KLD-*` product) and a known existing
   SKU (e.g. QuantumBit).
3. On a quote using the Standard Price Book, add a line and confirm list / tier pricing
   resolves.

## Related

- [Prepare RLM Org build guide](prepare-rlm-org-build-guide.md) — end-of-build DT refresh and index rebuild in the full flow
- [CCI sf CLI token workaround](cci-sf-cli-token-workaround.md) — `INVALID_AUTH_HEADER` / token redaction
- [kld-pcm README](../../datasets/sfdmu/kld/en-US/kld-pcm/README.md) — KLDiscovery product plan
- [kld-pricing README](../../datasets/sfdmu/kld/en-US/kld-pricing/README.md) — KLDiscovery pricing plan
