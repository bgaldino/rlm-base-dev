// Calendar dates for the billing UI (todo 510).
//
// Salesforce Date fields reach a component as 'YYYY-MM-DD'. new Date('YYYY-MM-DD') reads that as
// midnight UTC, which in a time zone behind UTC (all of the Americas) is the evening of the day
// before: shown, it is a day early, and bucketed by month, the 1st lands in the previous month.
// parseDateOnly reads it as midnight of that same calendar day in the browser's zone instead, so
// getFullYear/getMonth/getDate and toLocaleDateString give back the stored date in every zone.

const YMD_PATTERN = /^(\d{4})-(\d{2})-(\d{2})$/;

// A 'YYYY-MM-DD' value as local midnight of that day; any other value as new Date(value) reads it.
export function parseDateOnly(value) {
    const match = typeof value === 'string' ? YMD_PATTERN.exec(value) : null;
    if (!match) {
        return new Date(value);
    }
    return new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
}

// The calendar date of a Date in the browser's zone, as 'YYYY-MM-DD' (toISOString gives the UTC date).
export function dateOnlyKey(date) {
    const pad = (n) => String(n).padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}
