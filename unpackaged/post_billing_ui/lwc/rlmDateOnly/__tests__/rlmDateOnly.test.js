/**
 * @jest-environment <rootDir>/tests/jest/browser-time-zone-environment.js
 */
/* global setBrowserTimeZone */
// Todo 510: a Salesforce Date ('YYYY-MM-DD') is read as that calendar day in every browser time zone.
import { parseDateOnly, dateOnlyKey } from 'c/rlmDateOnly';

const ZONES = ['America/Los_Angeles', 'America/New_York', 'Pacific/Honolulu', 'UTC', 'Asia/Tokyo'];

describe.each(ZONES)('rlmDateOnly with the browser in %s', (timeZone) => {
    beforeEach(() => setBrowserTimeZone(timeZone));

    it('reads a date-only value as midnight of that day, in the browser zone', () => {
        const d = parseDateOnly('2026-01-01');
        expect([d.getFullYear(), d.getMonth(), d.getDate(), d.getHours()]).toEqual([2026, 0, 1, 0]);
        expect(d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })).toBe('Jan 1, 2026');
    });

    it('gives back the same date as a key', () => {
        ['2026-01-01', '2026-03-08', '2026-11-01', '2028-02-29', '2026-12-31']
            .forEach((value) => expect(dateOnlyKey(parseDateOnly(value))).toBe(value));
    });

    it('reads any other value as new Date does', () => {
        const instant = '2026-01-01T12:00:00.000Z';
        expect(parseDateOnly(instant).getTime()).toBe(new Date(instant).getTime());
        expect(Number.isNaN(parseDateOnly(undefined).getTime())).toBe(true);
    });
});
