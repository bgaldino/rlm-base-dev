#!/usr/bin/env python3
"""Permanently purge deleted records from an org's Recycle Bin.

There is no "empty the whole bin" API call. The supported route is to find the
deleted record Ids and pass them to the SOAP ``emptyRecycleBin()`` call, 200 Ids
at a time. This script automates that for any mix of objects:

1. **Discover** candidate objects from the global describe: ``queryable`` and
   ``undeletable`` (the platform's flag for "has a Recycle Bin"). Skipped when
   ``--objects`` names them.
2. **Count** deleted rows per object with ``queryAll ... WHERE IsDeleted = true``,
   batched 25 per ``composite/batch`` request, so one run costs a handful of
   calls rather than one per object. Purged rows keep matching that query until
   the platform physically removes them, so counts can include rows that are
   already purged; those are reported as "already purged", not as failures.
3. **Collect** the Ids for objects that have any (paged through ``queryAll``).
4. **Purge** them with SOAP ``emptyRecycleBin``, reporting per-record failures.

It is a dry run unless ``--execute`` is passed, because the purge is permanent.

CCI-free on purpose (stdlib + ``requests``), so it runs ad hoc and can be called
from a build step or a CCI wrapper later without changes::

    python scripts/recycle_bin/empty_recycle_bin.py --target-org <sf_alias>
    python scripts/recycle_bin/empty_recycle_bin.py --target-org <sf_alias> --execute
    python scripts/recycle_bin/empty_recycle_bin.py --target-org <sf_alias> \\
        --objects Account,Quote --execute

Scope: ``emptyRecycleBin`` removes only records the running user may purge. A
user with Modify All Data can purge every user's deleted records; others only
their own. Records that cannot be purged are reported, and the exit code is 1.

Exit codes: 0 = nothing to do or all purged (or dry run), 1 = some records could
not be purged, 2 = usage/auth/API error.
"""

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence
from urllib.parse import quote
from xml.sax.saxutils import escape

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sf_token import SfTokenError, org_auth  # noqa: E402

BATCH_SIZE = 25  # composite/batch subrequest limit
PURGE_CHUNK = 200  # emptyRecycleBin Id limit per call
TIMEOUT = 120

_SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"
_PARTNER_NS = "urn:partner.soap.sforce.com"


class RecycleBinError(RuntimeError):
    """An API call failed in a way the run cannot continue past."""


def chunked(items: Sequence, size: int) -> Iterable[Sequence]:
    for i in range(0, len(items), size):
        yield items[i:i + size]


class Org:
    """Thin REST/SOAP client. Holds the token; never logs or prints it."""

    def __init__(self, instance_url: str, token: str, api_version: Optional[str] = None):
        self.instance_url = instance_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers["Authorization"] = f"Bearer {token}"
        self._token = token
        self.api_version = api_version or self._latest_api_version()

    def _latest_api_version(self) -> str:
        versions = self._get(f"{self.instance_url}/services/data/")
        return max((v["version"] for v in versions), key=float)

    @property
    def data_url(self) -> str:
        return f"{self.instance_url}/services/data/v{self.api_version}"

    def _get(self, url: str, params: Optional[dict] = None):
        resp = self._session.get(url, params=params, timeout=TIMEOUT)
        if resp.status_code >= 400:
            raise RecycleBinError(f"GET {url.split('?')[0]} -> {resp.status_code}: {resp.text[:300]}")
        return resp.json()

    def describe_global(self) -> List[dict]:
        return self._get(f"{self.data_url}/sobjects/")["sobjects"]

    def composite_batch(self, urls: Sequence[str]) -> List[dict]:
        """GET each relative url (<= 25) in one request; return per-item results."""
        body = {"haltOnError": False, "batchRequests": [{"method": "GET", "url": u} for u in urls]}
        resp = self._session.post(f"{self.data_url}/composite/batch", json=body, timeout=TIMEOUT)
        if resp.status_code >= 400:
            raise RecycleBinError(f"composite/batch -> {resp.status_code}: {resp.text[:300]}")
        return resp.json()["results"]

    def query_all(self, soql: str) -> List[dict]:
        data = self._get(f"{self.data_url}/queryAll/", {"q": soql})
        records = list(data["records"])
        while not data["done"]:
            data = self._get(f"{self.instance_url}{data['nextRecordsUrl']}")
            records.extend(data["records"])
        return records

    def empty_recycle_bin(self, ids: Sequence[str]) -> List[dict]:
        """SOAP emptyRecycleBin for <= 200 Ids. Returns [{id, success, errors}]."""
        id_xml = "".join(f"<urn:ids>{escape(i)}</urn:ids>" for i in ids)
        envelope = (
            f'<soapenv:Envelope xmlns:soapenv="{_SOAP_NS}" xmlns:urn="{_PARTNER_NS}">'
            f"<soapenv:Header><urn:SessionHeader><urn:sessionId>{escape(self._token)}"
            f"</urn:sessionId></urn:SessionHeader></soapenv:Header>"
            f"<soapenv:Body><urn:emptyRecycleBin>{id_xml}</urn:emptyRecycleBin></soapenv:Body>"
            f"</soapenv:Envelope>"
        )
        resp = requests.post(
            f"{self.instance_url}/services/Soap/u/{self.api_version}",
            data=envelope.encode("utf-8"),
            headers={"Content-Type": "text/xml; charset=UTF-8", "SOAPAction": '""'},
            timeout=TIMEOUT,
        )
        return parse_empty_response(resp.status_code, resp.text)


def parse_empty_response(status: int, text: str) -> List[dict]:
    """Parse an emptyRecycleBin SOAP response (or fault) into per-Id results."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        raise RecycleBinError(f"emptyRecycleBin returned non-XML (HTTP {status})") from None
    fault = root.find(f".//{{{_SOAP_NS}}}Fault")
    if fault is not None:
        msg = fault.findtext("faultstring") or "unknown fault"
        raise RecycleBinError(f"emptyRecycleBin fault: {msg[:300]}")
    results = []
    for res in root.iter(f"{{{_PARTNER_NS}}}result"):
        errors = [
            e.findtext(f"{{{_PARTNER_NS}}}message") or "unknown error"
            for e in res.findall(f"{{{_PARTNER_NS}}}errors")
        ]
        results.append({
            "id": res.findtext(f"{{{_PARTNER_NS}}}id"),
            "success": res.findtext(f"{{{_PARTNER_NS}}}success") == "true",
            "errors": errors,
        })
    if not results:
        raise RecycleBinError(f"emptyRecycleBin returned no results (HTTP {status})")
    return results


def candidate_objects(sobjects: Iterable[dict]) -> List[str]:
    """Objects that can hold Recycle Bin rows: queryable and undeletable."""
    return sorted(s["name"] for s in sobjects if s.get("queryable") and s.get("undeletable"))


def count_deleted(org: Org, objects: Sequence[str], log=print) -> Dict[str, int]:
    """Deleted-row count per object, via composite/batch. Objects that reject the
    IsDeleted query (no such field, not queryable to this user) are skipped."""
    counts: Dict[str, int] = {}
    for group in chunked(list(objects), BATCH_SIZE):
        urls = [
            f"v{org.api_version}/queryAll/?q="
            + quote(f"SELECT COUNT() FROM {name} WHERE IsDeleted = true")
            for name in group
        ]
        for name, item in zip(group, org.composite_batch(urls)):
            if item.get("statusCode") == 200:
                total = item["result"].get("totalSize", 0)
                if total:
                    counts[name] = total
            else:
                log(f"  skip {name}: HTTP {item.get('statusCode')}")
    return counts


# Purged rows stay visible to queryAll (IsDeleted = true) until the platform
# physically removes them, so a re-run finds Ids that are already gone.
# emptyRecycleBin answers those with this message. That is the desired end state,
# not a failure. Verified live: purged Accounts still counted, undelete said
# "Entity is not in the recycle bin", and a second purge returned this error.
ALREADY_PURGED = "no recycle bin entry found"


def purge(org: Org, ids: Sequence[str]) -> tuple:
    """Purge Ids in 200-Id chunks; return (failures, already_purged_count)."""
    failures = []
    already = 0
    for group in chunked(list(ids), PURGE_CHUNK):
        for res in org.empty_recycle_bin(group):
            if res["success"]:
                continue
            if res["errors"] and all(ALREADY_PURGED in e.lower() for e in res["errors"]):
                already += 1
            else:
                failures.append({"id": res["id"], "errors": res["errors"]})
    return failures, already


def run(org: Org, objects: Optional[Sequence[str]], exclude: Iterable[str],
        execute: bool, log=print) -> int:
    excluded = {e.lower() for e in exclude}
    if objects:
        names = list(objects)
    else:
        names = candidate_objects(org.describe_global())
        log(f"Discovered {len(names)} objects with a Recycle Bin.")
    names = [n for n in names if n.lower() not in excluded]

    counts = count_deleted(org, names, log)
    if not counts:
        log("Recycle Bin is empty for the selected objects. Nothing to do.")
        return 0
    total = sum(counts.values())
    for name, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        log(f"  {name}: {n}")
    log(f"Total deleted records: {total}")
    if not execute:
        log("Dry run. Re-run with --execute to permanently purge them.")
        return 0

    purged = 0
    failed = 0
    already_total = 0
    for name in sorted(counts):
        ids = [r["Id"] for r in org.query_all(f"SELECT Id FROM {name} WHERE IsDeleted = true")]
        failures, already = purge(org, ids)
        purged += len(ids) - len(failures) - already
        already_total += already
        failed += len(failures)
        for f in failures[:5]:
            log(f"  FAILED {name} {f['id']}: {'; '.join(f['errors'])}")
        if len(failures) > 5:
            log(f"  ... and {len(failures) - 5} more {name} failures")
        log(f"  {name}: purged {len(ids) - len(failures) - already}, "
            f"already purged {already}, failed {len(failures)}")
    log(f"Purged {purged} record(s); {already_total} already purged; "
        f"{failed} could not be purged.")
    return 1 if failed else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--target-org", required=True, help="sf CLI alias or username (not a CCI alias)")
    p.add_argument("--objects", help="Comma-separated sObjects to purge; default is every object with a Recycle Bin")
    p.add_argument("--exclude", default="", help="Comma-separated sObjects to leave alone")
    p.add_argument("--api-version", help="API version, e.g. 68.0 (default: org's latest)")
    p.add_argument("--execute", action="store_true", help="Actually purge; without it this is a dry run")
    args = p.parse_args(argv)

    split = lambda s: [x.strip() for x in s.split(",") if x.strip()]  # noqa: E731
    try:
        instance_url, token = org_auth(args.target_org)
        org = Org(instance_url, token, args.api_version)
        return run(org, split(args.objects or ""), split(args.exclude), args.execute)
    except (SfTokenError, RecycleBinError, requests.RequestException) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
