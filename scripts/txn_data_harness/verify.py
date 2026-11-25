"""Read-only billing verifier: invoice, line and payment balances against their applications.

``cli verify`` reads invoice and payment ids from harness manifests (or from
``--invoice-ids`` / ``--payment-ids``), runs SOQL reads only, and checks the billing
records against each other. It never writes. Exit 0 when every check passes or is
skipped, 1 when any check fails, 2 on bad input or a refused request.

Checks (formulas are documented in
``.cursor/skills/billing-operations/verification.md``):

``application_level``
    Line Level orgs put applications in ``PaymentLineInvoiceLine`` /
    ``CreditMemoLineInvoiceLine``; Header Level orgs in ``PaymentLineInvoice`` /
    ``CreditMemoInvApplication``. An invoice fails when it has rows of the other
    level, or when its ``SettlementLevel`` names the other level. Skipped for an
    invoice with neither application rows nor a ``SettlementLevel``, however the
    level was chosen.
``invoice_balance``
    ``Balance = TotalAmountWithTax - NetCreditsApplied - NetPaymentsApplied``, and
    each rollup equals the net of the invoice's application rows. Skipped for an
    invoice whose ``Status`` is not Posted (the rollups were measured on Posted
    invoices only), for an invoice with ``Type`` Tax lines or a non-zero
    ``TotalTaxesCapturedAtHeader`` (separate and header tax are unmeasured), and when
    a converted-negative, write-off or adjustment field is set (effect unmeasured).
``invoice_line_balance``
    ``Balance = LineAmount - NetCreditsApplied - NetPaymentsApplied`` per line, and
    each rollup equals the net of the line's application rows. Runs only on an invoice
    whose own evidence is line level alone (line application rows and/or
    ``SettlementLevel`` InvoiceLine, and nothing of the header level); skipped for
    any other invoice, naming its evidence. Also skipped for an invoice that is not
    Posted or has Tax lines or header tax, and for a line with a converted-negative
    or adjustment amount. An invoice with no lines fails.
``payment_balance``
    ``Balance = Amount - NetApplied``, and ``NetApplied`` equals the net of the
    payment's application rows on any invoice. Checked for a Processed payment, and a
    Canceled payment with no application rows (the two measured cases); any other
    status, or a Canceled payment with rows, is skipped. Also skipped for a payment
    whose ``NetRefundApplied`` or ``NetPaymentCreditApplied`` is non-zero.

Unapplied application rows have not been measured on 264 (the org read had none), so
an invoice or payment with any row of ``Type`` Unapplied, or any row flagged unapplied
(``UnappliedStatus`` or ``HasBeenUnapplied`` = Yes), skips every balance check that
reads its application rows. Otherwise the net of a set of application rows is the
sum of their ``Applied`` amounts. Amounts compare exactly as Decimals; ids may be 15
or 18 characters and are normalized to 18 before querying; an 18-character id's
case is restored from its suffix, as Salesforce does.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable, Optional

__all__ = [
    "CHECK_NAMES",
    "VerifyError",
    "fetch_billing_records",
    "ids_from_manifest",
    "render_text",
    "run_checks",
]

CHECK_NAMES = (
    "application_level",
    "invoice_balance",
    "invoice_line_balance",
    "payment_balance",
)

LEVELS = ("line", "header")

# Amounts compare exactly as Decimals, with no tolerance, so no currency precision is
# assumed (JPY has none, some currencies carry three places). The REST client parses
# JSON numbers as floats; each is converted with ``Decimal(str(value))``, and ``str`` of
# a float gives the shortest text that reads back as the same float. For currency
# amounts (at most about 15 significant digits) that is the value the API sent, so the
# Decimal arithmetic below is exact.
_ID_RE = re.compile(r"^[A-Za-z0-9]{15}(?:[A-Za-z0-9]{3})?$")
_SUFFIX_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"
_IN_CHUNK = 200

# Fields that may settle or change a balance outside the four application objects.
# Their effect has not been measured: a non-zero value skips the balance check for
# that invoice or line instead of guessing a formula.
_UNMEASURED_INVOICE_FIELDS = (
    "TotalConvertedNegAmount", "WriteOffTotalChargeAmount", "WriteOffTotalTaxAmount",
    "TotalAdjustmentAmount", "TotalTaxesCapturedAtHeader",
)
_UNMEASURED_LINE_FIELDS = ("ConvertedNegAmount", "ChargeConvertedNegAmount", "AdjustmentAmount")

INVOICE_FIELDS = (
    "Id", "Status", "SettlementLevel", "TotalAmountWithTax",
    "NetCreditsApplied", "NetPaymentsApplied", "Balance", "WriteOffStatus",
) + _UNMEASURED_INVOICE_FIELDS
INVOICE_LINE_FIELDS = (
    "Id", "InvoiceId", "Type", "LineAmount", "NetCreditsApplied", "NetPaymentsApplied",
    "Balance",
) + _UNMEASURED_LINE_FIELDS
PAYMENT_FIELDS = ("Id", "Status", "Amount", "NetApplied", "Balance", "NetRefundApplied",
                  "NetPaymentCreditApplied")
# Payment fields whose effect on Balance has not been measured: a non-zero value skips
# payment_balance for that payment instead of guessing a formula.
_UNMEASURED_PAYMENT_FIELDS = ("NetRefundApplied", "NetPaymentCreditApplied")


@dataclass(frozen=True)
class _AppObject:
    """One of the four application junction objects and the fields that matter."""

    name: str
    level: str          # "line" | "header"
    kind: str           # "payment" | "credit"
    target_field: str   # InvoiceLineId (line) or InvoiceId (header)
    source_field: str   # PaymentId / CreditMemoLineId / CreditMemoId
    unapplied_flag: str  # UnappliedStatus / HasBeenUnapplied

    @property
    def fields(self) -> tuple[str, ...]:
        return ("Id", self.target_field, self.source_field, "Amount", "Type",
                self.unapplied_flag)


APP_OBJECTS = (
    _AppObject("PaymentLineInvoiceLine", "line", "payment", "InvoiceLineId", "PaymentId",
               "UnappliedStatus"),
    _AppObject("CreditMemoLineInvoiceLine", "line", "credit", "InvoiceLineId",
               "CreditMemoLineId", "UnappliedStatus"),
    _AppObject("PaymentLineInvoice", "header", "payment", "InvoiceId", "PaymentId",
               "HasBeenUnapplied"),
    _AppObject("CreditMemoInvApplication", "header", "credit", "InvoiceId", "CreditMemoId",
               "HasBeenUnapplied"),
)
_UNAPPLIED_FLAGS = tuple(sorted({o.unapplied_flag for o in APP_OBJECTS}))
_UNAPPLIED_REASON = "has unapplied application rows (not measured on 264)"
_PAYMENT_APP_OBJECTS = tuple(o for o in APP_OBJECTS if o.kind == "payment")
_SETTLEMENT_LEVEL = {"InvoiceLine": "line", "Invoice": "header"}
# The balance formulas were measured on Posted invoices; any other Status is skipped.
_CHECKED_INVOICE_STATUS = "Posted"
# Measured payment cases: Processed, and Canceled with no application rows.
_CHECKED_PAYMENT_STATUS = "Processed"
_CANCELED_PAYMENT_STATUS = "Canceled"


def _unmeasured(row: dict, fields: Iterable[str]) -> list[str]:
    """Name each listed field that is non-zero on ``row``, with its value."""
    return [f"{f} {_fmt(_dec(row.get(f)))}" for f in fields if _zero(row.get(f)) != 0]


class VerifyError(ValueError):
    """Bad input (bad or unknown id, unreadable manifest). ``cli verify`` prints it, exits 2."""


# --------------------------------------------------------------------------- inputs

def _id18(value: str) -> str:
    """Return the 18-character form the API returns, from a 15- or 18-character id."""
    base = value[:15]
    suffix = ""
    for start in (0, 5, 10):
        bits = sum(1 << i for i, ch in enumerate(base[start:start + 5]) if "A" <= ch <= "Z")
        suffix += _SUFFIX_CHARS[bits]
    return base + suffix


def _restore_case(value: str) -> Optional[str]:
    """Return an 18-character id with the case of its first 15 characters restored.

    As Salesforce does, the suffix decides the case: each suffix character marks which
    of five characters are upper case. None when no casing matches (a marked
    character is a digit, or a suffix character is outside the alphabet).
    """
    chars = list(value[:15])
    for chunk, mark in enumerate(value[15:].upper()):
        if mark not in _SUFFIX_CHARS:
            return None
        bits = _SUFFIX_CHARS.index(mark)
        for i in range(5):
            pos = chunk * 5 + i
            upper = bool(bits & (1 << i))
            if upper and not chars[pos].isalpha():
                return None
            chars[pos] = chars[pos].upper() if upper else chars[pos].lower()
    return "".join(chars) + value[15:].upper()


def _check_ids(ids: Iterable[str], label: str) -> list[str]:
    """Validate ids and return them in 18-character form, deduplicated, in order."""
    out: list[str] = []
    for raw in ids:
        value = (raw or "").strip()
        if not value:
            continue
        if not _ID_RE.match(value):
            raise VerifyError(f"{label}: {value!r} is not a Salesforce id")
        if len(value) == 18:
            canonical = _restore_case(value)
            if canonical is None:
                raise VerifyError(f"{label}: {value!r} has a checksum suffix that matches "
                                  "no casing of its first 15 characters")
        else:
            canonical = _id18(value)
        if canonical not in out:
            out.append(canonical)
    return out


def split_ids(values: Optional[Iterable[str]], label: str) -> list[str]:
    """Accept ``--invoice-ids a,b c`` (commas, spaces or repeated flags)."""
    parts: list[str] = []
    for value in values or []:
        parts.extend(re.split(r"[\s,]+", value))
    return _check_ids(parts, label)


def _as_list(value: Any, where: str) -> list[str]:
    """Return a manifest id value as a list of strings; anything else is bad input."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        return value
    raise VerifyError(f"{where} must be a string id or a list of string ids, "
                      f"not {json.dumps(value)}")


def ids_from_manifest(path: Path) -> tuple[list[str], list[str]]:
    """Return ``(invoice_ids, payment_ids)`` named by a manifest file.

    Reads the raw JSON rather than ``Manifest.from_dict`` so that keys added by
    later stages (payment ids, for example) are read without a model change.
    """
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        raise VerifyError(f"manifest not found: {path}") from None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerifyError(f"manifest {path} could not be read as JSON: {exc}") from None
    if not isinstance(data, dict):
        raise VerifyError(f"manifest {path} is not a JSON object")
    invoices: list[str] = []
    payments: list[str] = []
    for key, out in (("invoice_id", invoices), ("invoice_ids", invoices),
                     ("payment_id", payments), ("payment_ids", payments)):
        out.extend(_as_list(data.get(key), f"manifest {path} {key}"))
    return (_check_ids(invoices, f"{path.name} invoice id"),
            _check_ids(payments, f"{path.name} payment id"))


# --------------------------------------------------------------------------- fetch

def _query_in(client, obj: str, fields: Iterable[str], where_field: str,
              ids: list[str]) -> list[dict]:
    rows: list[dict] = []
    for start in range(0, len(ids), _IN_CHUNK):
        chunk = ids[start:start + _IN_CHUNK]
        quoted = ", ".join(f"'{i}'" for i in chunk)
        soql = (f"SELECT {', '.join(fields)} FROM {obj} "
                f"WHERE {where_field} IN ({quoted})")
        for row in client.query(soql):
            row = {k: v for k, v in row.items() if k != "attributes"}
            rows.append(row)
    return rows


def _merge(rows: list[dict], more: list[dict]) -> list[dict]:
    seen = {r["Id"] for r in rows}
    return rows + [r for r in more if r["Id"] not in seen]


def fetch_billing_records(client, invoice_ids: list[str],
                          payment_ids: Optional[list[str]] = None) -> dict[str, list[dict]]:
    """Read everything the checks need, by id. SOQL reads only.

    Returns ``{object name: rows}`` for Invoice, InvoiceLine, Payment and the four
    application objects. Payments are the ones asked for plus every payment that
    has an application row on these invoices; for each payment, all of its payment
    application rows are read too, so ``NetApplied`` can be checked against rows on
    invoices outside the set.
    """
    invoice_ids = _check_ids(invoice_ids, "invoice id")
    payment_ids = _check_ids(payment_ids or [], "payment id")
    if not invoice_ids and not payment_ids:
        raise VerifyError("no invoice or payment ids to verify")

    records: dict[str, list[dict]] = {}
    invoices = _query_in(client, "Invoice", INVOICE_FIELDS, "Id", invoice_ids)
    missing = sorted(set(invoice_ids) - {r["Id"] for r in invoices})
    if missing:
        raise VerifyError(f"invoice ids not found or not readable: {', '.join(missing)}")
    records["Invoice"] = invoices
    lines = (_query_in(client, "InvoiceLine", INVOICE_LINE_FIELDS, "InvoiceId", invoice_ids)
             if invoice_ids else [])
    records["InvoiceLine"] = lines
    line_ids = [r["Id"] for r in lines]

    for obj in APP_OBJECTS:
        targets = line_ids if obj.level == "line" else invoice_ids
        records[obj.name] = (_query_in(client, obj.name, obj.fields, obj.target_field, targets)
                             if targets else [])

    for obj in _PAYMENT_APP_OBJECTS:
        for row in records[obj.name]:
            pid = row.get(obj.source_field)
            if pid and pid not in payment_ids:
                payment_ids.append(pid)
    payments = _query_in(client, "Payment", PAYMENT_FIELDS, "Id", payment_ids) if payment_ids else []
    missing = sorted(set(payment_ids) - {r["Id"] for r in payments})
    if missing:
        raise VerifyError(f"payment ids not found or not readable: {', '.join(missing)}")
    records["Payment"] = payments
    if payment_ids:
        for obj in _PAYMENT_APP_OBJECTS:
            more = _query_in(client, obj.name, obj.fields, obj.source_field, payment_ids)
            records[obj.name] = _merge(records[obj.name], more)
    return records


# --------------------------------------------------------------------------- checks

def _dec(value: Any) -> Optional[Decimal]:
    if value is None:
        return None
    return Decimal(str(value))


def _zero(value: Any) -> Decimal:
    d = _dec(value)
    return d if d is not None else Decimal("0")


def _eq(a: Optional[Decimal], b: Optional[Decimal]) -> bool:
    return a is not None and b is not None and a == b


def _fmt(value: Optional[Decimal]) -> str:
    return "null" if value is None else format(value, "f")


def _net(rows: Iterable[dict]) -> Decimal:
    """Sum of the Applied amounts. Callers skip any set with unapplied rows first."""
    return sum((_zero(r.get("Amount")) for r in rows if r.get("Type") == "Applied"),
               Decimal("0"))


def _has_unapplied(rows: Iterable[dict]) -> bool:
    """True when any row is of Type Unapplied or flagged unapplied (not measured)."""
    return any(r.get("Type") == "Unapplied"
               or any(r.get(f) == "Yes" for f in _UNAPPLIED_FLAGS) for r in rows)


@dataclass
class _Index:
    invoices: list[dict]
    lines_by_invoice: dict[str, list[dict]] = field(default_factory=dict)
    line_rows: dict[str, dict[str, list[dict]]] = field(default_factory=dict)  # kind -> line id -> rows
    header_rows: dict[str, dict[str, list[dict]]] = field(default_factory=dict)  # kind -> invoice id -> rows
    rows_by_payment: dict[str, list[dict]] = field(default_factory=dict)


def _index(records: dict[str, list[dict]]) -> _Index:
    idx = _Index(invoices=records.get("Invoice", []))
    for line in records.get("InvoiceLine", []):
        idx.lines_by_invoice.setdefault(line["InvoiceId"], []).append(line)
    for kind in ("payment", "credit"):
        idx.line_rows[kind] = {}
        idx.header_rows[kind] = {}
    for obj in APP_OBJECTS:
        for row in records.get(obj.name, []):
            # Rows a payment has on invoices outside the set are indexed too; lookups go
            # by this set's invoice and line ids, so they count for the payment only.
            bucket = idx.line_rows if obj.level == "line" else idx.header_rows
            bucket[obj.kind].setdefault(row.get(obj.target_field), []).append(row)
            if obj.kind == "payment":
                idx.rows_by_payment.setdefault(row.get(obj.source_field), []).append(row)
    return idx


def _invoice_rows(idx: _Index, invoice_id: str, kind: str, level: str) -> list[dict]:
    if level == "header":
        return idx.header_rows[kind].get(invoice_id, [])
    rows: list[dict] = []
    for line in idx.lines_by_invoice.get(invoice_id, []):
        rows.extend(idx.line_rows[kind].get(line["Id"], []))
    return rows


def _all_invoice_rows(idx: _Index, invoice_id: str) -> list[dict]:
    return [r for kind in ("payment", "credit") for level in LEVELS
            for r in _invoice_rows(idx, invoice_id, kind, level)]


def _facts(idx: _Index, invoice: dict) -> str:
    iid = invoice["Id"]
    line_n = sum(len(_invoice_rows(idx, iid, k, "line")) for k in ("payment", "credit"))
    head_n = sum(len(_invoice_rows(idx, iid, k, "header")) for k in ("payment", "credit"))
    return (f"{line_n} line application row(s), {head_n} header application row(s), "
            f"SettlementLevel {invoice.get('SettlementLevel') or 'null'}")


def _evidence(idx: _Index, invoice: dict) -> set[str]:
    found: set[str] = set()
    iid = invoice["Id"]
    for level in LEVELS:
        if any(_invoice_rows(idx, iid, kind, level) for kind in ("payment", "credit")):
            found.add(level)
    settlement = _SETTLEMENT_LEVEL.get(invoice.get("SettlementLevel") or "")
    if settlement:
        found.add(settlement)
    return found


def _detect_level(idx: _Index) -> tuple[Optional[str], str]:
    found: set[str] = set()
    for invoice in idx.invoices:
        found |= _evidence(idx, invoice)
    if len(found) == 1:
        return next(iter(found)), "records"
    if not found:
        return None, "undetermined"
    return None, "mixed"


def _result(check: str, subject: str, status: str, detail: str) -> dict:
    return {"check": check, "subject": subject, "status": status, "detail": detail}


def _tax_lines(idx: _Index, invoice: dict) -> list[str]:
    """Name the invoice's separate Tax lines, whose effect on balances is unmeasured."""
    n = sum(1 for line in idx.lines_by_invoice.get(invoice["Id"], [])
            if line.get("Type") == "Tax")
    return [f"{n} Type Tax line(s)"] if n else []


def _not_posted(invoice: dict) -> Optional[str]:
    """The skip reason for an invoice whose Status is not Posted, else None."""
    status = invoice.get("Status")
    if status == _CHECKED_INVOICE_STATUS:
        return None
    return (f"Status {status or 'null'}; balances are checked on "
            f"{_CHECKED_INVOICE_STATUS} invoices only")


def _check_level(idx: _Index, expected: Optional[str], source: str) -> list[dict]:
    out = []
    for invoice in idx.invoices:
        iid = invoice["Id"]
        line_n = sum(len(_invoice_rows(idx, iid, k, "line")) for k in ("payment", "credit"))
        head_n = sum(len(_invoice_rows(idx, iid, k, "header")) for k in ("payment", "credit"))
        settlement = invoice.get("SettlementLevel")
        facts = _facts(idx, invoice)
        own = _evidence(idx, invoice)
        if not own:
            # Nothing on this invoice shows a level, whether the level was detected,
            # forced or undetermined: skip rather than pass on no evidence.
            out.append(_result("application_level", iid, "skip",
                               f"no application rows and no SettlementLevel to compare; {facts}"))
            continue
        if expected is None:
            if len(own) > 1:
                out.append(_result("application_level", iid, "fail",
                                   f"this invoice shows both levels; {facts}"))
            else:
                # Mixed: this invoice is consistent with itself but another invoice in
                # the set shows the other level. Fail the ones that have rows.
                out.append(_result("application_level", iid, "fail",
                                   f"this invoice is {next(iter(own))} level but other "
                                   f"invoices in the set are not; {facts}"))
            continue
        other = "header" if expected == "line" else "line"
        wrong_rows = head_n if expected == "line" else line_n
        settled = _SETTLEMENT_LEVEL.get(settlement or "")
        problems = []
        if wrong_rows:
            problems.append(f"{wrong_rows} {other}-level row(s)")
        if settled == other:
            problems.append(f"SettlementLevel is {settlement}")
        if problems:
            out.append(_result("application_level", iid, "fail",
                               f"expected {expected} level ({source}) but found "
                               f"{' and '.join(problems)}; {facts}"))
        else:
            out.append(_result("application_level", iid, "pass",
                               f"{expected} level ({source}); {facts}"))
    return out


def _check_invoice_balance(idx: _Index) -> list[dict]:
    out = []
    for invoice in idx.invoices:
        iid = invoice["Id"]
        not_posted = _not_posted(invoice)
        if not_posted:
            out.append(_result("invoice_balance", iid, "skip", not_posted))
            continue
        unmeasured = _unmeasured(invoice, _UNMEASURED_INVOICE_FIELDS) + _tax_lines(idx, invoice)
        if invoice.get("WriteOffStatus"):
            unmeasured.append(f"WriteOffStatus {invoice['WriteOffStatus']}")
        if unmeasured:
            out.append(_result("invoice_balance", iid, "skip",
                               f"{', '.join(unmeasured)}: the effect on Balance is not "
                               "measured"))
            continue
        if _has_unapplied(_all_invoice_rows(idx, iid)):
            out.append(_result("invoice_balance", iid, "skip", _UNAPPLIED_REASON))
            continue
        total = _dec(invoice.get("TotalAmountWithTax"))
        credits = _zero(invoice.get("NetCreditsApplied"))
        payments = _zero(invoice.get("NetPaymentsApplied"))
        balance = _dec(invoice.get("Balance"))
        rec_pay = sum((_net(_invoice_rows(idx, iid, "payment", lvl)) for lvl in LEVELS), Decimal("0"))
        rec_cred = sum((_net(_invoice_rows(idx, iid, "credit", lvl)) for lvl in LEVELS), Decimal("0"))
        expected = None if total is None else total - credits - payments
        problems = []
        if not _eq(balance, expected):
            problems.append(f"Balance {_fmt(balance)} != TotalAmountWithTax {_fmt(total)} "
                            f"- NetCreditsApplied {_fmt(credits)} - NetPaymentsApplied "
                            f"{_fmt(payments)} = {_fmt(expected)}")
        if not _eq(payments, rec_pay):
            problems.append(f"NetPaymentsApplied {_fmt(payments)} != payment rows {_fmt(rec_pay)}")
        if not _eq(credits, rec_cred):
            problems.append(f"NetCreditsApplied {_fmt(credits)} != credit rows {_fmt(rec_cred)}")
        if problems:
            out.append(_result("invoice_balance", iid, "fail", "; ".join(problems)))
        else:
            out.append(_result("invoice_balance", iid, "pass",
                               f"{_fmt(balance)} = {_fmt(total)} - {_fmt(credits)} - {_fmt(payments)}"))
    return out


def _check_line_balance(idx: _Index) -> list[dict]:
    out = []
    for invoice in idx.invoices:
        iid = invoice["Id"]
        # Line balances were measured at Line Level only, so the one gate is this
        # invoice's own evidence, whatever level the set has or was forced to.
        own = _evidence(idx, invoice)
        if own != {"line"}:
            shown = {0: "no level", 1: f"{''.join(own)} level"}.get(len(own), "both levels")
            out.append(_result("invoice_line_balance", iid, "skip",
                               f"this invoice's own evidence shows {shown} "
                               f"({_facts(idx, invoice)}); line balances are checked only "
                               "when it is line level alone"))
            continue
        not_posted = _not_posted(invoice)
        if not_posted:
            out.append(_result("invoice_line_balance", iid, "skip", not_posted))
            continue
        tax = _unmeasured(invoice, ("TotalTaxesCapturedAtHeader",)) + _tax_lines(idx, invoice)
        if tax:
            out.append(_result("invoice_line_balance", iid, "skip",
                               f"{', '.join(tax)}: separate or header tax is not measured"))
            continue
        if _has_unapplied(_all_invoice_rows(idx, iid)):
            out.append(_result("invoice_line_balance", iid, "skip", _UNAPPLIED_REASON))
            continue
        lines = idx.lines_by_invoice.get(iid, [])
        if not lines:
            # A posted invoice always has lines; none read means the lines are missing
            # or not readable, so the line check cannot pass.
            out.append(_result("invoice_line_balance", iid, "fail",
                               "invoice has no lines (none readable)"))
            continue
        for line in lines:
            lid = line["Id"]
            subject = f"{iid}/{lid}"
            unmeasured = _unmeasured(line, _UNMEASURED_LINE_FIELDS)
            if line.get("Type") == "Adjustment":
                unmeasured.insert(0, "Type Adjustment")
            if unmeasured:
                out.append(_result("invoice_line_balance", subject, "skip",
                                   f"{', '.join(unmeasured)}: the effect on Balance is not "
                                   "measured"))
                continue
            amount = _dec(line.get("LineAmount"))
            credits = _zero(line.get("NetCreditsApplied"))
            payments = _zero(line.get("NetPaymentsApplied"))
            balance = _dec(line.get("Balance"))
            rec_pay = _net(idx.line_rows["payment"].get(lid, []))
            rec_cred = _net(idx.line_rows["credit"].get(lid, []))
            expected = None if amount is None else amount - credits - payments
            problems = []
            if not _eq(balance, expected):
                problems.append(f"Balance {_fmt(balance)} != LineAmount {_fmt(amount)} "
                                f"- NetCreditsApplied {_fmt(credits)} - NetPaymentsApplied "
                                f"{_fmt(payments)} = {_fmt(expected)}")
            if not _eq(payments, rec_pay):
                problems.append(f"NetPaymentsApplied {_fmt(payments)} != "
                                f"PaymentLineInvoiceLine rows {_fmt(rec_pay)}")
            if not _eq(credits, rec_cred):
                problems.append(f"NetCreditsApplied {_fmt(credits)} != "
                                f"CreditMemoLineInvoiceLine rows {_fmt(rec_cred)}")
            if problems:
                out.append(_result("invoice_line_balance", subject, "fail", "; ".join(problems)))
            else:
                out.append(_result("invoice_line_balance", subject, "pass",
                                   f"{_fmt(balance)} = {_fmt(amount)} - {_fmt(credits)} - "
                                   f"{_fmt(payments)}"))
    return out


def _check_payment_balance(records: dict[str, list[dict]], idx: _Index) -> list[dict]:
    out = []
    for payment in records.get("Payment", []):
        pid = payment["Id"]
        status = payment.get("Status")
        rows = idx.rows_by_payment.get(pid, [])
        if status == _CANCELED_PAYMENT_STATUS and rows:
            out.append(_result("payment_balance", pid, "skip",
                               f"Status {status} with {len(rows)} application row(s); only a "
                               "Canceled payment with no applications is measured"))
            continue
        if status not in (_CHECKED_PAYMENT_STATUS, _CANCELED_PAYMENT_STATUS):
            out.append(_result("payment_balance", pid, "skip",
                               f"Status {status or 'null'}; balances are checked on "
                               f"{_CHECKED_PAYMENT_STATUS} payments and on "
                               f"{_CANCELED_PAYMENT_STATUS} payments with no applications only"))
            continue
        unmeasured = _unmeasured(payment, _UNMEASURED_PAYMENT_FIELDS)
        if unmeasured:
            out.append(_result("payment_balance", pid, "skip",
                               f"Status {status}; {', '.join(unmeasured)}: the effect on "
                               "Balance is not measured"))
            continue
        if _has_unapplied(rows):
            out.append(_result("payment_balance", pid, "skip",
                               f"Status {status}; {_UNAPPLIED_REASON}"))
            continue
        amount = _dec(payment.get("Amount"))
        applied = _zero(payment.get("NetApplied"))
        balance = _dec(payment.get("Balance"))
        rec = _net(rows)
        expected = None if amount is None else amount - applied
        problems = []
        if not _eq(balance, expected):
            problems.append(f"Balance {_fmt(balance)} != Amount {_fmt(amount)} - NetApplied "
                            f"{_fmt(applied)} = {_fmt(expected)}")
        if not _eq(applied, rec):
            problems.append(f"NetApplied {_fmt(applied)} != application rows {_fmt(rec)}")
        if problems:
            out.append(_result("payment_balance", pid, "fail",
                               f"Status {status}; " + "; ".join(problems)))
        else:
            out.append(_result("payment_balance", pid, "pass",
                               f"Status {status}; {_fmt(balance)} = {_fmt(amount)} - {_fmt(applied)}"))
    return out


def run_checks(records: dict[str, list[dict]], expect_level: str = "auto") -> dict:
    """Run every check on fetched (or recorded) rows. Pure: no org access."""
    if expect_level not in ("auto",) + LEVELS:
        raise VerifyError(f"expect_level must be auto, line or header (got {expect_level!r})")
    idx = _index(records)
    if expect_level == "auto":
        level, source = _detect_level(idx)
    else:
        level, source = expect_level, "argument"
    results = (
        _check_level(idx, level, source)
        + _check_invoice_balance(idx)
        + _check_line_balance(idx)
        + _check_payment_balance(records, idx)
    )
    failed = sorted({r["check"] for r in results if r["status"] == "fail"},
                    key=CHECK_NAMES.index)
    return {
        "ok": not failed,
        "level": level,
        "level_source": source,
        "invoice_ids": [r["Id"] for r in records.get("Invoice", [])],
        "payment_ids": [r["Id"] for r in records.get("Payment", [])],
        "failed_checks": failed,
        "checks": results,
    }


def render_text(report: dict) -> str:
    lines = [f"Level: {report['level'] or report['level_source']} ({report['level_source']})"]
    for r in report["checks"]:
        lines.append(f"{r['status'].upper():4} {r['check']:20} {r['subject']}: {r['detail']}")
    if report["ok"]:
        lines.append("RESULT: pass")
    else:
        lines.append(f"RESULT: fail ({', '.join(report['failed_checks'])})")
    return "\n".join(lines)
