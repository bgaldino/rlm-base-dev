"""The Create Billing Schedule Group modal reads and writes calendar dates as 'YYYY-MM-DD' only (todo 435).

Its Jest suite (rlmBillingScheduleGroupModal.dates.test.js) pins the browser zones it names. This
guard keeps a date read back through a local or UTC Date from returning in a zone no case covers:
a date read in one zone and written in another moves by a day (the defect). The only Date the
modal makes is the current instant, handed to Intl with the user's zone (billingDates.todayInTimeZone).
"""
import re
from pathlib import Path

MODAL = Path(__file__).resolve().parents[1] / "unpackaged/post_billing_ui/lwc/rlmBillingScheduleGroupModal"
FORBIDDEN = re.compile(
    r"toISOString|toJSON|\.get(UTC)?(FullYear|Month|Date|Day)\(|\.set(UTC)?(FullYear|Month|Date)\("
    r"|Date\.parse|new Date\([^)]"
)


def _code(name):
    # Comments may name the forbidden calls to explain why they are gone.
    text = (MODAL / name).read_text(encoding="utf-8")
    return re.sub(r"//.*$", "", text, flags=re.M)


def test_component_makes_no_date():
    code = _code("rlmBillingScheduleGroupModal.js")
    assert not FORBIDDEN.search(code)
    assert "new Date(" not in code


def test_date_helper_reads_no_local_or_utc_calendar_fields():
    assert not FORBIDDEN.search(_code("billingDates.js"))


def test_guard_catches_the_old_code():
    old = "this.startDate = today.toISOString().split('T')[0]; this.billingDayOfMonth = today.getDate();"
    assert FORBIDDEN.search(old)
    assert FORBIDDEN.search("const start = new Date(this.startDate + 'T00:00:00');")
