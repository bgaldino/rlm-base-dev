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
    } catch (e) {
        parts = datePartsIn(undefined, now);
    }
    return formatYmd(parts);
}

// `months` calendar months after `date`. A day the target month lacks is moved to that month's last
// day (Jan 31 + 1 month = Feb 28, or Feb 29 in a leap year), as Apex Date.addMonths does and as
// Salesforce Pricing anchors a period that starts on the 29th, 30th or 31st.
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

// The last day of a term of `months` whole months starting on `startYmd`: the day before the start
// date `months` later. Salesforce Pricing ends its periods the same way (Help: a 31-Jan-2025 monthly
// period ends 27-Feb-2025, a 29-Feb-2024 annual period ends 27-Feb-2025). Null when the start is not
// a valid date or `months` is not a positive whole number.
export function termEndDate(startYmd, months) {
    const start = parseYmd(startYmd);
    if (!start || !Number.isInteger(months) || months <= 0) {
        return null;
    }
    return formatYmd(previousDay(addMonths(start, months)));
}
