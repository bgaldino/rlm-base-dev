// Calendar dates for the Create Billing Schedule Group modal.
//
// Every date is a plain 'YYYY-MM-DD' string: the value lightning-input type="date" reads and
// writes, and what the service sends as StartDate__std and EndDate__std. Nothing here goes through
// a Date read in the browser's time zone or through toISOString() (UTC): a date read one way and
// written the other moves by a day whenever the two zones disagree on the date. "Today" is taken in
// the zone the caller passes, the user's Salesforce time zone, not the browser's.

const YMD_PATTERN = /^(\d{4})-(\d{2})-(\d{2})$/;
const DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

function isLeapYear(year) {
    return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
}

function daysInMonth(year, month) {
    return month === 2 && isLeapYear(year) ? 29 : DAYS_IN_MONTH[month - 1];
}

// { year, month, day } (month 1-12) for a valid 'YYYY-MM-DD' string, else null.
export function parseYmd(value) {
    const match = typeof value === 'string' ? YMD_PATTERN.exec(value) : null;
    if (!match) {
        return null;
    }
    const year = Number(match[1]);
    const month = Number(match[2]);
    const day = Number(match[3]);
    if (month < 1 || month > 12 || day < 1 || day > daysInMonth(year, month)) {
        return null;
    }
    return { year, month, day };
}

function formatYmd({ year, month, day }) {
    return `${String(year).padStart(4, '0')}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
}

function datePartsIn(timeZone, now) {
    const parts = {};
    new Intl.DateTimeFormat('en-US-u-ca-gregory-nu-latn', {
        timeZone,
        year: 'numeric',
        month: 'numeric',
        day: 'numeric'
    })
        .formatToParts(now)
        .forEach((part) => {
            parts[part.type] = part.value;
        });
    return { year: Number(parts.year), month: Number(parts.month), day: Number(parts.day) };
}

// Today's date in the given IANA time zone, as 'YYYY-MM-DD'. A zone this browser does not know
// (Intl throws a RangeError) falls back to the browser's own zone rather than failing the modal.
export function todayInTimeZone(timeZone, now = new Date()) {
    let parts;
    try {
        parts = datePartsIn(timeZone || undefined, now);
    } catch {
        parts = datePartsIn(undefined, now);
    }
    return formatYmd(parts);
}

// `months` calendar months after `date`. A day the target month lacks is moved to that month's last
// day (Jan 31 + 1 month = Feb 28, or Feb 29 in a leap year), as Apex Date.addMonths does and as the
// platform anchors a term (see termEndDate).
function addMonths(date, months) {
    const index = date.year * 12 + (date.month - 1) + months;
    const year = Math.floor(index / 12);
    const month = index - year * 12 + 1;
    return { year, month, day: Math.min(date.day, daysInMonth(year, month)) };
}

function previousDay(date) {
    if (date.day > 1) {
        return { year: date.year, month: date.month, day: date.day - 1 };
    }
    const year = date.month === 1 ? date.year - 1 : date.year;
    const month = date.month === 1 ? 12 : date.month - 1;
    return { year, month, day: daysInMonth(year, month) };
}

// The last day of a term of `months` whole months starting on `startYmd`: the day before the start's
// day of the month `months` later, that day moved to the last day of a month that lacks it. This is the
// end date the platform itself computes for a term-defined quote line from its start date and term
// (measured on a 264 org, 2026-11-26, todo 435; Place Sales Transaction with no EndDate, read back):
// 2027-02-28 + 1 Annual = 2028-02-27 and + 12 Months = 2028-02-27; 2028-02-29 + 1 Annual = 2029-02-27;
// 2027-01-31 + 1 Month = 2027-02-27 and + 1 Annual = 2028-01-30; 2027-03-31 + 1 Month = 2027-04-29;
// 2027-02-28 + 3 and + 6 Months = 2027-05-27 and 2027-08-27. A month-end start gets no special case:
// for 2027-02-28 + 1 Annual the platform returns 2028-02-27 and prices it as 0.9973 of a year, the
// Help's partial-period example (ind.pricing_annual_proration_examples_for_leap_years), not the
// 28-Feb-2028 full period that article also describes. Quarterly and semi-annual units could not be
// measured (no price book entry uses them on that org); they are computed as 3 and 6 months.
// Null when the start is not a valid date or `months` is not a positive whole number.
export function termEndDate(startYmd, months) {
    const start = parseYmd(startYmd);
    if (!start || !Number.isInteger(months) || months <= 0) {
        return null;
    }
    return formatYmd(previousDay(addMonths(start, months)));
}
