# Recycle Bin purge

`empty_recycle_bin.py` permanently purges deleted records from an org's Recycle Bin.
Salesforce has no "empty everything" API call, so it finds deleted Ids per object
(`queryAll ... WHERE IsDeleted = true`, counted 25 objects per `composite/batch`)
and passes them to SOAP `emptyRecycleBin` 200 at a time.

```bash
python scripts/recycle_bin/empty_recycle_bin.py --target-org <sf_alias>             # dry run
python scripts/recycle_bin/empty_recycle_bin.py --target-org <sf_alias> --execute   # purge
python scripts/recycle_bin/empty_recycle_bin.py --target-org <sf_alias> --objects Account,Quote --execute
```

`--target-org` is an `sf` alias or username, not a CCI alias. Dry run is the default
because the purge is permanent. Use `--exclude` to leave objects alone.

- **Discovery** covers every object that is `queryable` and `undeletable` (the
  describe flag for "has a Recycle Bin"), about 535 on a 264 scratch org, in roughly
  30 seconds. `--objects` skips discovery.
- **Purged rows linger.** They keep matching `IsDeleted = true` until the platform
  removes them physically, so counts can include rows already purged. A repeat purge
  of such a row returns "no recycle bin entry found"; the script reports that as
  "already purged", not a failure.
- **Permissions.** Modify All Data purges every user's deleted records; otherwise
  only the running user's. Other per-record refusals are listed and exit code is 1.
- **Metadata** (deleted fields, objects) is not in the Recycle Bin; use
  `--purge-on-delete` on a destructive deploy instead.

Exit codes: 0 done / nothing to do / dry run, 1 some records not purged, 2 usage,
auth or API error. Tests: `python tests/test_empty_recycle_bin.py`.
Not wired into `cumulusci.yml` yet.
