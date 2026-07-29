#!/usr/bin/env python3
"""Orchestration for building a ramped quote end-to-end.

Part of the self-contained ``scripts/ramp_deals/`` toolkit (imports nothing from
``tasks/``). :class:`RampLifecycle` wraps a :class:`_client.Transport` and
sequences the multi-call dance a ramped quote requires — no single Connect call
produces one:

    place (Quote + group + lines)  →  poll CalculationStatus to settled
      →  EditGroup (convert group 1 into the first ramp segment)  →  poll
      →  clone × (N-1)  (each adds the next segment; poll between)
      →  read back  →  verify invariants

The pure pieces do the thinking: ``_schedule`` sizes the segments, ``_payload``
shapes every body (and rejects read-only / bad-enum inputs before the call),
``_verify`` owns the ``CalculationStatus`` classification and the read-back
assertions, ``_resolve`` turns names into ids and loads the read-back. This engine
only sequences them and extracts ids from responses.

``transport`` is the one dependency: every call routes through it, so its
``dry_run``/``logger`` govern the whole engine and a unit test injects a fake
transport (no org). The ``sleep`` seam is injectable for the same reason — tests
pass a no-op so polling does not actually wait.

Errors raise :class:`RampLifecycleError`.
"""

import time
from typing import Any, Callable, Dict, List, Optional

from . import _payload, _resolve, _verify
from ._client import RampClientError
from ._verify import classify_status


class RampLifecycleError(RuntimeError):
    """Raised on an orchestration failure while building a ramped quote."""


def _extract_id(resp: Any, ref_id: str) -> Optional[str]:
    """Pull the created record id for ``ref_id`` from a ``place`` response.

    The Composite-Graph-style response nests results under ``graphs[].
    graphResponse.compositeResponse[]`` keyed by ``referenceId``; different builds
    also surface a flat ``records``/``compositeResponse`` list or a direct
    ``{referenceId: id}`` map. Probe the shapes we have seen rather than assuming
    one — an id we cannot find is returned as ``None`` for the caller to handle.
    """
    if not isinstance(resp, (dict, list)):
        return None

    def _from_composite(items):
        for item in items or []:
            if not isinstance(item, dict):
                continue
            if item.get("referenceId") == ref_id:
                body = item.get("body") or {}
                if isinstance(body, dict) and body.get("id"):
                    return body["id"]
                if item.get("id"):
                    return item["id"]
        return None

    if isinstance(resp, dict):
        # graphs[].graphResponse.compositeResponse[]
        for graph in resp.get("graphs") or []:
            gr = (graph or {}).get("graphResponse") or {}
            found = _from_composite(gr.get("compositeResponse"))
            if found:
                return found
        # flat compositeResponse / records
        found = _from_composite(resp.get("compositeResponse")) or \
            _from_composite(resp.get("records"))
        if found:
            return found
        # direct {referenceId: id} map
        val = resp.get(ref_id)
        if isinstance(val, str):
            return val
    return None


class RampLifecycle:
    """Sequences place → EditGroup → clone×N → verify over a Transport.

    Args:
        transport: a :class:`_client.Transport` (or any object exposing
            ``connect`` / ``soql``). Its ``dry_run`` and ``logger`` drive the run.
        sleep: injectable sleeper (defaults to ``time.sleep``); tests pass a no-op.
        max_wait_seconds / poll_interval_seconds: bound the CalculationStatus poll.
    """

    def __init__(
        self,
        transport,
        *,
        logger: Callable[..., None] = None,
        sleep: Callable[[float], None] = time.sleep,
        max_wait_seconds: int = 300,
        poll_interval_seconds: int = 5,
    ):
        self.t = transport
        self.log = logger or getattr(transport, "logger", print)
        self.dry_run = getattr(transport, "dry_run", False)
        self._sleep = sleep
        self.max_wait = max(0, max_wait_seconds)
        self.poll = max(1, poll_interval_seconds)

    # -- status polling --------------------------------------------------

    def wait_until_settled(self, quote_id: str) -> str:
        """Poll ``Quote.CalculationStatus`` until terminal; return the final status.

        Returns immediately under dry-run (nothing has changed to wait for). A
        'failure' status raises; an 'unknown' status raises rather than silently
        treating it as done (see ``_verify.classify_status``). A poll that exhausts
        ``max_wait`` while still in-flight raises.
        """
        if self.dry_run:
            return "CompletedWithPricing"  # nominal; no real calc under dry-run

        waited = 0
        last = "NotStarted"
        while True:
            rows = self.t.soql(
                "SELECT CalculationStatus FROM Quote "
                f"WHERE Id = '{_resolve._client.soql_literal(quote_id)}'"
            )
            if not rows:
                raise RampLifecycleError(f"Quote {quote_id} vanished during polling.")
            last = rows[0].get("CalculationStatus") or "NotStarted"
            kind = classify_status(last)
            if kind == "success":
                return last
            if kind == "failure":
                raise RampLifecycleError(
                    f"Quote {quote_id} calculation failed: CalculationStatus={last!r}."
                )
            if kind == "unknown":
                raise RampLifecycleError(
                    f"Quote {quote_id} returned an unrecognized CalculationStatus "
                    f"{last!r} — stopping rather than assuming success. Add it to the "
                    "_verify status sets if it is legitimate."
                )
            # in_flight → keep waiting
            if waited >= self.max_wait:
                raise RampLifecycleError(
                    f"Quote {quote_id} still in-flight (CalculationStatus={last!r}) "
                    f"after {self.max_wait}s."
                )
            self._sleep(self.poll)
            waited += self.poll

    # -- steps -----------------------------------------------------------

    def place(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """POST the initial ``place`` body; return {quote_id, group_id, response}."""
        resp = self.t.connect("POST", _payload.PLACE_PATH, body)
        quote_id = _extract_id(resp, "refQuote")
        group_id = _extract_id(resp, "refGroup")
        if not self.dry_run and not quote_id:
            raise RampLifecycleError(
                "place() response did not yield a Quote id for 'refQuote'. "
                f"Response shape: {list(resp.keys()) if isinstance(resp, dict) else type(resp).__name__}"
            )
        return {"quote_id": quote_id, "group_id": group_id, "response": resp}

    def edit_group(self, **kwargs) -> Dict[str, Any]:
        """POST an EditGroup body (built by ``_payload.build_edit_group``)."""
        body = _payload.build_edit_group(**kwargs)
        return self.t.connect("POST", _payload.PLACE_PATH, body)

    def clone_segment(self, **kwargs) -> Dict[str, Any]:
        """POST a clone body (built by ``_payload.build_clone_segment``)."""
        body = _payload.build_clone_segment(**kwargs)
        return self.t.connect("POST", _payload.CLONE_PATH, body)

    # -- full build ------------------------------------------------------

    def build_ramped_quote(
        self,
        *,
        account_id: str,
        pricebook_id: str,
        lines: List[dict],
        schedule: List[dict],
        opportunity_id: Optional[str] = None,
        currency: Optional[str] = None,
        quote_name: str = "Ramped Quote",
        line_scope: str = "AllLines",
        verify: bool = True,
    ) -> Dict[str, Any]:
        """Build a full multi-segment ramped quote from a resolved schedule.

        ``schedule`` is the output of ``_schedule.build_schedule`` (segments with
        ``segment_type`` / ``start_date`` / ``end_date`` / ``sort_order``). Segment
        1 is created by place + EditGroup; each later segment by a clone.

        Returns {"quote_id", "status", "verify": <Result.to_dict()|None>}.
        Raises :class:`RampLifecycleError` on any step failure.
        """
        if not schedule:
            raise RampLifecycleError("schedule is empty — nothing to build.")

        first, rest = schedule[0], schedule[1:]

        # 1. place the shell (Quote + group + lines), all POST.
        place_body = _payload.build_place_create(
            account_id=account_id, pricebook_id=pricebook_id, lines=lines,
            opportunity_id=opportunity_id, currency=currency,
            quote_name=quote_name, start_date=first["start_date"],
        )
        placed = self.place(place_body)
        quote_id, group_id = placed["quote_id"], placed["group_id"]
        self.log(f"placed quote={quote_id} group={group_id}")
        status = self.wait_until_settled(quote_id) if quote_id else "dry-run"

        # 2. convert group 1 into the first ramp segment.
        self.edit_group(
            quote_id=quote_id, group_id=group_id,
            start_date=first["start_date"], end_date=first["end_date"],
            segment_type=first["segment_type"], sort_order=first["sort_order"],
        )
        if quote_id:
            status = self.wait_until_settled(quote_id)
        self.log(f"segment 1 ({first['segment_type']}) created")

        # 3. clone the rest — only the LAST segment can be cloned each time. The
        # clone response's last group becomes the next clone's source, but under
        # this CLI we re-read the last group id from the quote between clones to
        # avoid guessing the response shape.
        last_group_id = group_id
        for i, seg in enumerate(rest, start=2):
            self.clone_segment(
                quote_id=quote_id, last_segment_group_id=last_group_id,
                line_scope=line_scope,
            )
            if quote_id:
                status = self.wait_until_settled(quote_id)
                last_group_id = self._last_group_id(quote_id) or last_group_id
            self.log(f"segment {i} ({seg['segment_type']}) cloned")

        # 4. read back + verify.
        verify_result = None
        if verify and quote_id and not self.dry_run:
            quote = _resolve.read_quote(quote_id, transport=self.t)
            result = _verify.verify_quote(quote, expected_segments=len(schedule))
            verify_result = result.to_dict()
            if not result.passed:
                raise RampLifecycleError(
                    "ramped quote failed verification:\n" + result.format_report()
                )
            self.log("verification passed")

        return {"quote_id": quote_id, "status": status, "verify": verify_result}

    def _last_group_id(self, quote_id: str) -> Optional[str]:
        """The highest-SortOrder ramped group on the quote (the clone source)."""
        rows = self.t.soql(
            "SELECT Id, SortOrder FROM QuoteLineGroup "
            f"WHERE QuoteId = '{_resolve._client.soql_literal(quote_id)}' "
            "AND IsRamped = true ORDER BY SortOrder DESC LIMIT 1"
        )
        return rows[0]["Id"] if rows else None

    # -- single-segment operations (add / edit / delete) -----------------

    def add_segment(
        self, *, quote_id: str, last_segment_group_id: Optional[str] = None,
        line_scope: str = "AllLines",
    ) -> Dict[str, Any]:
        """Add one segment by cloning the quote's last ramped segment.

        Only the **last** segment can be cloned. When ``last_segment_group_id`` is
        omitted it is read from the quote (highest SortOrder ramped group). Returns
        {"quote_id", "cloned_from", "status"}.
        """
        source = last_segment_group_id or self._last_group_id(quote_id)
        if not source and not self.dry_run:
            raise RampLifecycleError(
                f"no ramped segment found on quote {quote_id} to clone from — is it "
                "a ramped quote? (build the first segment before adding more)"
            )
        self.clone_segment(
            quote_id=quote_id, last_segment_group_id=source, line_scope=line_scope,
        )
        status = self.wait_until_settled(quote_id) if not self.dry_run else "dry-run"
        self.log(f"segment cloned from {source} on quote {quote_id}")
        return {"quote_id": quote_id, "cloned_from": source, "status": status}

    def edit_segment(self, **kwargs) -> Dict[str, Any]:
        """Edit an existing ramp segment (dates / type / sort order) via EditGroup.

        Takes the same keywords as ``_payload.build_edit_group`` (quote_id,
        group_id, start_date, end_date, segment_type, sort_order). Returns
        {"quote_id", "group_id", "status"}.
        """
        self.edit_group(**kwargs)
        quote_id = kwargs.get("quote_id")
        status = self.wait_until_settled(quote_id) if not self.dry_run else "dry-run"
        self.log(f"segment {kwargs.get('group_id')} edited on quote {quote_id}")
        return {"quote_id": quote_id, "group_id": kwargs.get("group_id"),
                "status": status}

    def delete_quote(self, quote_id: str) -> Dict[str, Any]:
        """Delete a whole quote (DML delete on the Quote sObject).

        Cascades to its groups and lines by platform rules. Returns
        {"quote_id", "deleted": bool}. Skipped (deleted=False) under dry-run.
        """
        self.t.connect("DELETE", f"sobjects/Quote/{quote_id}")
        self.log(f"deleted quote {quote_id}")
        return {"quote_id": quote_id, "deleted": not self.dry_run}
