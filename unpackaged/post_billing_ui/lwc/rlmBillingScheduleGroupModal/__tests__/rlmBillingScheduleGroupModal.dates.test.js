/**
 * @jest-environment <rootDir>/tests/jest/browser-time-zone-environment.js
 */
/* global setBrowserTimeZone */
// The modal's dates: Start Date defaults to today in the user's Salesforce time zone, the billing
// day and month come from that same date, and the End Date of a termed charge is calendar math on
// the 'YYYY-MM-DD' value. Each case pins the browser's time zone (setBrowserTimeZone, from the test
// environment above), the user's Salesforce time zone (@salesforce/i18n/timeZone) and the current
// instant, so the suite gives the same answer on a developer's machine and on a UTC CI runner.
import { createElement } from "lwc";
import RlmBillingScheduleGroupModal from "c/rlmBillingScheduleGroupModal";
import createBillingScheduleGroupAndScheduleViaAPI from "@salesforce/apex/RLM_BillingScheduleGroupService.createBillingScheduleGroupAndScheduleViaAPI";
import getAccountBillingInfo from "@salesforce/apex/RLM_BillingScheduleGroupService.getAccountBillingInfo";
import getLegalEntities from "@salesforce/apex/RLM_BillingScheduleGroupService.getLegalEntities";
import getTaxTreatments from "@salesforce/apex/RLM_BillingScheduleGroupService.getTaxTreatments";
import getProducts from "@salesforce/apex/RLM_BillingScheduleGroupService.getProducts";

// The user's Salesforce time zone. The component reads @salesforce/i18n/timeZone once, when its
// module loads, and the LWC engine cannot be loaded twice in one document (a second copy cannot
// upgrade the base-component tags the first registered), so the mock is an object whose string
// value is the zone the current case sets: Intl reads a timeZone option as a string.
let mockUserTimeZone = "America/Los_Angeles";
jest.mock(
  "@salesforce/i18n/timeZone",
  () => ({ default: { toString: () => mockUserTimeZone } }),
  { virtual: true }
);
jest.mock(
  "lightning/actions",
  () => ({
    CloseActionScreenEvent: class CloseActionScreenEvent extends CustomEvent {
      constructor() {
        super("closeactionscreen");
      }
    }
  }),
  { virtual: true }
);
jest.mock(
  "@salesforce/apex/RLM_BillingScheduleGroupService.createBillingScheduleGroupAndScheduleViaAPI",
  () => ({ default: jest.fn() }),
  { virtual: true }
);
jest.mock(
  "@salesforce/apex/RLM_BillingScheduleGroupService.getAccountBillingInfo",
  () => {
    const { createApexTestWireAdapter } = jest.requireActual(
      "@salesforce/sfdx-lwc-jest"
    );
    return { default: createApexTestWireAdapter(jest.fn()) };
  },
  { virtual: true }
);
jest.mock(
  "@salesforce/apex/RLM_BillingScheduleGroupService.getLegalEntities",
  () => {
    const { createApexTestWireAdapter } = jest.requireActual(
      "@salesforce/sfdx-lwc-jest"
    );
    return { default: createApexTestWireAdapter(jest.fn()) };
  },
  { virtual: true }
);
jest.mock(
  "@salesforce/apex/RLM_BillingScheduleGroupService.getTaxTreatments",
  () => {
    const { createApexTestWireAdapter } = jest.requireActual(
      "@salesforce/sfdx-lwc-jest"
    );
    return { default: createApexTestWireAdapter(jest.fn()) };
  },
  { virtual: true }
);
jest.mock(
  "@salesforce/apex/RLM_BillingScheduleGroupService.getProducts",
  () => {
    const { createApexTestWireAdapter } = jest.requireActual(
      "@salesforce/sfdx-lwc-jest"
    );
    return { default: createApexTestWireAdapter(jest.fn()) };
  },
  { virtual: true }
);

const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

// Opens the modal at `now` with the browser in `browserTimeZone` and the user in `userTimeZone`.
async function open({ now, browserTimeZone, userTimeZone }) {
  setBrowserTimeZone(browserTimeZone);
  mockUserTimeZone = userTimeZone;
  // Only Date is faked: the tests wait on setTimeout to flush promises.
  jest.useFakeTimers({
    now: new Date(now),
    doNotFake: [
      "hrtime",
      "nextTick",
      "performance",
      "queueMicrotask",
      "requestAnimationFrame",
      "cancelAnimationFrame",
      "requestIdleCallback",
      "cancelIdleCallback",
      "setImmediate",
      "clearImmediate",
      "setInterval",
      "clearInterval",
      "setTimeout",
      "clearTimeout"
    ]
  });
  const element = createElement("c-rlm-billing-schedule-group-modal", {
    is: RlmBillingScheduleGroupModal
  });
  element.recordId = "001000000000001AAA";
  document.body.appendChild(element);
  getAccountBillingInfo.emit({
    accountName: "Acme",
    billingAccountId: "0aa000000000001AAA",
    billingAccountName: "Acme BA",
    billingCity: "Austin"
  });
  getLegalEntities.emit([{ id: "0le000000000001AAA", name: "LE" }]);
  getTaxTreatments.emit([{ id: "0tt000000000001AAA", name: "TT" }]);
  getProducts.emit([{ id: "01t000000000001AAA", name: "Product" }]);
  await flushPromises();
  return { element, create: createBillingScheduleGroupAndScheduleViaAPI };
}

function field(element, tag, name) {
  const found = Array.from(element.shadowRoot.querySelectorAll(tag)).find(
    (candidate) => candidate.name === name
  );
  expect(found).toBeTruthy();
  return found;
}

function change(element, tag, name, value) {
  field(element, tag, name).dispatchEvent(
    new CustomEvent("change", { detail: { value } })
  );
}

// A recurring, termed charge with every required value; the term is set by the caller.
async function fillTermed(element, { duration = "1", unit = "Year" } = {}) {
  change(element, "lightning-radio-group", "chargeType", "Recurring");
  await flushPromises();
  change(element, "lightning-combobox", "billingFrequency", "Month");
  change(element, "lightning-radio-group", "billingTiming", "Advance");
  change(element, "lightning-radio-group", "termSetting", "Termed");
  await flushPromises();
  change(element, "lightning-combobox", "product", "01t000000000001AAA");
  change(element, "lightning-combobox", "legalEntity", "0le000000000001AAA");
  change(element, "lightning-combobox", "taxTreatment", "0tt000000000001AAA");
  change(element, "lightning-input", "unitPrice", "10");
  change(element, "lightning-input", "termDuration", duration);
  change(element, "lightning-combobox", "termDurationUnit", unit);
  await flushPromises();
}

async function submit(element, create) {
  Array.from(element.shadowRoot.querySelectorAll("lightning-button"))
    .find((button) => button.variant === "brand")
    .click();
  await flushPromises();
  expect(create).toHaveBeenCalledTimes(1);
  return create.mock.calls[0][0];
}

afterEach(() => {
  while (document.body.firstChild) {
    document.body.removeChild(document.body.firstChild);
  }
  jest.useRealTimers();
  jest.clearAllMocks();
});

describe("c-rlm-billing-schedule-group-modal dates", () => {
  // 2026-11-26T04:10Z is 2026-11-25 20:10 in Los Angeles, the instant the defect was measured at.
  const US_EVENING = "2026-11-26T04:10:00Z";

  it.each([
    // The measured case: user and org in Los Angeles, browser at UTC+7.
    ["Asia/Bangkok", "America/Los_Angeles", US_EVENING, "2026-11-25", 25, 11],
    // US evenings: the UTC date is already tomorrow.
    ["America/Los_Angeles", "America/Los_Angeles", US_EVENING, "2026-11-25", 25, 11],
    ["America/New_York", "America/New_York", "2026-11-26T03:30:00Z", "2026-11-25", 25, 11],
    // Mornings east of UTC: the UTC date is still yesterday.
    ["Europe/Berlin", "Europe/Berlin", "2026-11-24T23:30:00Z", "2026-11-25", 25, 11],
    ["Asia/Bangkok", "Asia/Bangkok", "2026-11-24T18:00:00Z", "2026-11-25", 25, 11],
    ["Asia/Tokyo", "Asia/Tokyo", "2026-11-24T22:00:00Z", "2026-11-25", 25, 11],
    ["Australia/Sydney", "Australia/Sydney", "2026-11-24T20:00:00Z", "2026-11-25", 25, 11],
    // London (UTC+0 in November) was right before the fix and stays right.
    ["Europe/London", "Europe/London", "2026-11-25T23:30:00Z", "2026-11-25", 25, 11],
    // Month and year boundaries follow the user's date too.
    ["America/Los_Angeles", "America/Los_Angeles", "2027-01-01T05:00:00Z", "2026-12-31", 31, 12],
    ["Asia/Tokyo", "Asia/Tokyo", "2026-12-31T16:00:00Z", "2027-01-01", 1, 1]
  ])(
    "browser in %s, user in %s, at %s: Start Date defaults to the user's today",
    async (browserTimeZone, userTimeZone, now, today, day, month) => {
      const { element, create } = await open({ now, browserTimeZone, userTimeZone });
      expect(field(element, "lightning-input", "startDate").value).toBe(today);

      await fillTermed(element);
      const args = await submit(element, create);
      expect(args.startDate).toBe(today);
      expect(args.billingDayOfMonth).toBe(day);
      expect(args.billingStartMonth).toBe(month);
    }
  );

  it.each([
    "America/Los_Angeles",
    "America/New_York",
    "Europe/London",
    "Europe/Berlin",
    "Asia/Bangkok",
    "Asia/Tokyo",
    "Australia/Sydney",
    "UTC"
  ])(
    "browser in %s: Start 2026-11-25 + 1 Year ends 2027-11-24 and bills on day 25 of month 11",
    async (browserTimeZone) => {
      const { element, create } = await open({
        now: "2026-11-25T12:00:00Z",
        browserTimeZone,
        userTimeZone: browserTimeZone
      });
      await fillTermed(element, { duration: "1", unit: "Year" });
      change(element, "lightning-input", "startDate", "2026-11-25");
      await flushPromises();

      expect(field(element, "lightning-input", "endDate").value).toBe("2027-11-24");
      const args = await submit(element, create);
      expect(args.startDate).toBe("2026-11-25");
      expect(args.endDate).toBe("2027-11-24");
      expect(args.billingDayOfMonth).toBe(25);
      expect(args.billingStartMonth).toBe(11);
    }
  );

  // A day the end month lacks is clamped to that month's last day before the day is taken off, as
  // Salesforce Pricing anchors a period (Help: ind.pricing_monthly_proration_examples_for_leap_years,
  // 31-Jan-2025 to 27-Feb-2025 and 28-Feb-2027 to 27-Mar-2027). A whole-year term from the last day of a
  // month ends the day before that month's last day (ind.pricing_annual_proration_examples_for_leap_years:
  // 28-Feb-2027 to 28-Feb-2028, 29-Feb-2024 to 27-Feb-2025). The old Date.setMonth overflow ran
  // Jan 31 + 1 Month into March.
  const TERMS = [
    // The Help article's own examples, then the same rules across leap years.
    ["2025-01-31", "1", "Month", "2025-02-27"],
    ["2027-02-28", "1", "Month", "2027-03-27"],
    ["2027-02-28", "1", "Year", "2028-02-28"],
    ["2024-02-29", "1", "Year", "2025-02-27"],
    ["2027-02-28", "12", "Month", "2028-02-28"],
    ["2027-02-28", "2", "Year", "2029-02-27"],
    ["2026-02-28", "1", "Year", "2027-02-27"],
    ["2028-02-28", "1", "Year", "2029-02-27"],
    ["2031-02-28", "1", "Year", "2032-02-28"],
    ["2027-02-28", "1", "Quarter", "2027-05-27"],
    ["2026-04-30", "1", "Year", "2027-04-29"],
    ["2027-01-31", "1", "Month", "2027-02-27"],
    ["2028-01-31", "1", "Month", "2028-02-28"],
    ["2028-02-29", "1", "Year", "2029-02-27"],
    ["2028-02-29", "4", "Year", "2032-02-28"],
    ["2026-11-25", "1", "Quarter", "2027-02-24"],
    ["2026-11-30", "1", "Quarter", "2027-02-27"],
    ["2026-08-31", "1", "Semi-Annual", "2027-02-27"],
    ["2026-11-25", "2", "Semi-Annual", "2027-11-24"],
    ["2026-12-01", "1", "Month", "2026-12-31"],
    ["2026-12-15", "1", "Month", "2027-01-14"]
  ];
  it.each(
    TERMS.flatMap((term) =>
      ["Asia/Tokyo", "America/Los_Angeles", "UTC"].map((zone) => [...term, zone])
    )
  )(
    "Start %s + %s %s ends %s, browser in %s",
    async (start, duration, unit, end, browserTimeZone) => {
      const { element } = await open({
        now: "2026-11-25T12:00:00Z",
        browserTimeZone,
        userTimeZone: "America/Los_Angeles"
      });
      await fillTermed(element, { duration, unit });
      change(element, "lightning-input", "startDate", start);
      await flushPromises();
      expect(field(element, "lightning-input", "endDate").value).toBe(end);
    }
  );

  it("blocks a termed charge whose term is not a whole number of months", async () => {
    const { element, create } = await open({
      now: "2026-11-25T12:00:00Z",
      browserTimeZone: "UTC",
      userTimeZone: "UTC"
    });
    await fillTermed(element, { duration: "1.5", unit: "Month" });

    expect(field(element, "lightning-input", "endDate").value).toBeFalsy();
    expect(element.shadowRoot.querySelector('[role="alert"]').textContent).toContain(
      "End Date"
    );
    expect(create).not.toHaveBeenCalled();
  });
});
