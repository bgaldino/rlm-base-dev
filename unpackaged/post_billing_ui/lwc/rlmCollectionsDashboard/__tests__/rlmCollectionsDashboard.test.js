import { createElement } from "lwc";
import RlmCollectionsDashboard from "c/rlmCollectionsDashboard";
import getAccountOptions from "@salesforce/apex/RLM_CollectionsDashboardController.getAccountOptions";
import getCurrencyOptions from "@salesforce/apex/RLM_CollectionsDashboardController.getCurrencyOptions";
import getOrgDefaultCurrency from "@salesforce/apex/RLM_CollectionsDashboardController.getOrgDefaultCurrency";
import getDashboardCards from "@salesforce/apex/RLM_CollectionsDashboardController.getDashboardCards";
import getWorklist from "@salesforce/apex/RLM_CollectionsDashboardController.getWorklist";
import getPaymentPromiseSummary from "@salesforce/apex/RLM_CollectionsDashboardController.getPaymentPromiseSummary";
import getCollectionsProgress from "@salesforce/apex/RLM_CollectionsDashboardController.getCollectionsProgress";
import getCollectionPlanTasks from "@salesforce/apex/RLM_CollectionsDashboardController.getCollectionPlanTasks";
import getMyCollectionPlans from "@salesforce/apex/RLM_CollectionsDashboardController.getMyCollectionPlans";

// A figure the user cannot read (todo 435) arrives from the controller as unavailable: null, or
// listed in the cards' `unavailable`. These tests pin that the page says so instead of showing a
// zero, and that a readable zero still shows as a zero.

jest.mock("@salesforce/apex/RLM_CollectionsDashboardController.getAccountOptions", () => ({ default: jest.fn() }), { virtual: true });
jest.mock("@salesforce/apex/RLM_CollectionsDashboardController.getCurrencyOptions", () => ({ default: jest.fn() }), { virtual: true });
jest.mock("@salesforce/apex/RLM_CollectionsDashboardController.getOrgDefaultCurrency", () => ({ default: jest.fn() }), { virtual: true });
jest.mock(
  "@salesforce/apex/RLM_CollectionsDashboardController.getDashboardCards",
  () => {
    const { createApexTestWireAdapter } = jest.requireActual("@salesforce/sfdx-lwc-jest");
    return { default: createApexTestWireAdapter(jest.fn()) };
  },
  { virtual: true }
);
jest.mock(
  "@salesforce/apex/RLM_CollectionsDashboardController.getWorklist",
  () => {
    const { createApexTestWireAdapter } = jest.requireActual("@salesforce/sfdx-lwc-jest");
    return { default: createApexTestWireAdapter(jest.fn()) };
  },
  { virtual: true }
);
jest.mock(
  "@salesforce/apex/RLM_CollectionsDashboardController.getCollectionPlanTasks",
  () => {
    const { createApexTestWireAdapter } = jest.requireActual("@salesforce/sfdx-lwc-jest");
    return { default: createApexTestWireAdapter(jest.fn()) };
  },
  { virtual: true }
);
jest.mock(
  "@salesforce/apex/RLM_CollectionsDashboardController.getPaymentPromiseSummary",
  () => {
    const { createApexTestWireAdapter } = jest.requireActual("@salesforce/sfdx-lwc-jest");
    return { default: createApexTestWireAdapter(jest.fn()) };
  },
  { virtual: true }
);
jest.mock(
  "@salesforce/apex/RLM_CollectionsDashboardController.getMyCollectionPlans",
  () => {
    const { createApexTestWireAdapter } = jest.requireActual("@salesforce/sfdx-lwc-jest");
    return { default: createApexTestWireAdapter(jest.fn()) };
  },
  { virtual: true }
);
jest.mock(
  "@salesforce/apex/RLM_CollectionsDashboardController.getCollectionsProgress",
  () => {
    const { createApexTestWireAdapter } = jest.requireActual("@salesforce/sfdx-lwc-jest");
    return { default: createApexTestWireAdapter(jest.fn()) };
  },
  { virtual: true }
);

const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));
const DASH = "—";

function row(label, amount, color, unavailable) {
  const r = { label, amount, color };
  if (unavailable) r.unavailable = unavailable;
  return r;
}

// The cards as the controller returns them: everything read, or the named components refused.
function cards(unavailable = []) {
  const has = (key) => unavailable.includes(key);
  const all = ["invoices", "debitMemos", "unappliedCredits", "unappliedPayments"].every(has);
  return {
    // The controller's total: what was read, or null when nothing was.
    totalBalance: all ? null : (has("invoices") ? 0 : 1455) - (has("unappliedPayments") ? 0 : 20),
    receivablesOutstanding: has("invoices") ? null : 1455,
    invoiceCount: has("invoices") ? null : 3,
    currentDue: has("invoices") ? null : 1000,
    overdue: has("invoices") ? null : 455,
    unappliedPaymentBalance: has("unappliedPayments") ? null : 20,
    unappliedPaymentCount: has("unappliedPayments") ? null : 1,
    unappliedCredits: has("unappliedCredits") ? null : 0,
    agingBuckets: has("invoices")
      ? []
      : [{ label: "Current", amount: 1000, key: "current" }, { label: "1-30", amount: 455, key: "1-30" }],
    totalBalanceBreakdown: [
      row("Unpaid Invoices", has("invoices") ? null : 1455, "blue", has("invoices") && "invoices"),
      row("Debit Memos", has("debitMemos") ? null : 0, "orange", has("debitMemos") && "debitMemos"),
      row("Unapplied Credits", has("unappliedCredits") ? null : 0, "green", has("unappliedCredits") && "unappliedCredits"),
      row("Unapplied Payments", has("unappliedPayments") ? null : -20, "red", has("unappliedPayments") && "unappliedPayments")
    ],
    unavailable
  };
}

async function mount(worklist = { criticalFollowUpInvoices: [], highValueDelinquents: [], disputedInvoices: [] }) {
  getOrgDefaultCurrency.mockResolvedValue("USD");
  getCurrencyOptions.mockResolvedValue([{ value: "", label: "All Currencies" }]);
  getAccountOptions.mockResolvedValue([{ value: "", label: "All Accounts" }]);
  getWorklist.mockResolvedValue(worklist);
  const element = createElement("c-rlm-collections-dashboard", { is: RlmCollectionsDashboard });
  document.body.appendChild(element);
  await flushPromises();
  return element;
}

const text = (element, selector) =>
  Array.from(element.shadowRoot.querySelectorAll(selector)).map((node) => node.textContent.trim());

function card(element, labelText) {
  return Array.from(element.shadowRoot.querySelectorAll(".pulse-card")).find(
    (node) => node.querySelector(".pulse-card-label").textContent.trim() === labelText
  );
}

function breakdown(element, labelText) {
  const line = Array.from(element.shadowRoot.querySelectorAll(".pulse-card-breakdown > div")).find(
    (node) => node.querySelector("span").textContent.trim() === labelText
  );
  const [, value] = line.querySelectorAll("span");
  return { text: value.textContent.trim(), title: value.title };
}

describe("c-rlm-collections-dashboard figures the user cannot read", () => {
  afterEach(() => {
    while (document.body.firstChild) {
      document.body.removeChild(document.body.firstChild);
    }
    jest.clearAllMocks();
  });

  it("shows a readable zero as a zero, with no exclusion note", async () => {
    const element = await mount();
    getDashboardCards.emit(cards());
    await flushPromises();

    expect(breakdown(element, "Debit Memos")).toEqual({ text: "$0.00", title: "" });
    expect(element.shadowRoot.querySelector(".total-balance-note")).toBeNull();
    expect(card(element, "Total Balance").querySelector(".pulse-card-value").textContent).toBe("$1,435.00");
    expect(card(element, "Receivables Outstanding").querySelector(".pulse-card-meta").textContent).toBe("3 invoices");
  });

  it("shows unreadable debit memos as not available and the total as excluding them", async () => {
    const element = await mount();
    getDashboardCards.emit(cards(["debitMemos"]));
    await flushPromises();

    expect(breakdown(element, "Debit Memos")).toEqual({
      text: DASH,
      title: "You don't have access to debit memos."
    });
    expect(element.shadowRoot.querySelector(".total-balance-note").textContent).toBe(
      "Excludes debit memos: you don't have access to them."
    );
    // The components that were read keep their amounts.
    expect(breakdown(element, "Unpaid Invoices").text).toBe("$1,455.00");
    expect(card(element, "Total Balance").querySelector(".pulse-card-value").textContent).toBe("$1,435.00");
  });

  it("shows unreadable invoices and payments as not available on every card they feed", async () => {
    const element = await mount();
    getDashboardCards.emit(cards(["invoices", "unappliedCredits", "unappliedPayments"]));
    await flushPromises();

    for (const label of ["Receivables Outstanding", "Current Due", "Overdue", "Unapplied Payments"]) {
      expect(card(element, label).querySelector(".pulse-card-value").textContent).toBe(DASH);
    }
    expect(card(element, "Receivables Outstanding").querySelector(".pulse-card-meta").textContent).toBe(
      "You don't have access to invoices."
    );
    expect(card(element, "Unapplied Payments").querySelector(".pulse-card-meta").textContent).toBe(
      "You don't have access to payments."
    );
    expect(text(element, ".aging-unavailable")).toEqual(["You don't have access to invoices."]);
    expect(element.shadowRoot.querySelector(".total-balance-note").textContent).toBe(
      "Excludes unpaid invoices, unapplied credits and unapplied payments: you don't have access to them."
    );
    expect(breakdown(element, "Debit Memos").text).toBe("$0.00");
  });

  it("shows no total at all when every component of it was refused", async () => {
    const element = await mount();
    getDashboardCards.emit(cards(["invoices", "debitMemos", "unappliedCredits", "unappliedPayments"]));
    await flushPromises();

    expect(card(element, "Total Balance").querySelector(".pulse-card-value").textContent).toBe(DASH);
    expect(element.shadowRoot.querySelector(".total-balance-note").textContent).toBe(
      "Excludes unpaid invoices, debit memos, unapplied credits and unapplied payments: you don't have access to them."
    );
    for (const label of ["Unpaid Invoices", "Debit Memos", "Unapplied Credits", "Unapplied Payments"]) {
      expect(breakdown(element, label).text).toBe(DASH);
    }
  });

  it("says the payment schedules could not be read instead of 'No payment promises'", async () => {
    const element = await mount();
    getPaymentPromiseSummary.emit(null);
    await flushPromises();

    expect(text(element, ".payment-promises-empty")).toEqual(["You don't have access to payment schedules."]);
    expect(text(element, ".payment-promises-label")).toEqual([`Payment Promises (${DASH})`]);

    getPaymentPromiseSummary.emit([]);
    await flushPromises();
    expect(text(element, ".payment-promises-empty")).toEqual(["No payment promises."]);
    expect(text(element, ".payment-promises-label")).toEqual(["Payment Promises ($0.00)"]);
  });

  it("says the collection plans could not be read instead of zero averages", async () => {
    const element = await mount();
    getCollectionsProgress.emit({ totalPlans: 0, avgDaysToClose: 0, avgDaysPastDue: 0, unavailable: true });
    await flushPromises();

    expect(text(element, ".progress-empty")).toEqual(["You don't have access to collection plans."]);
    expect(text(element, ".progress-avg-value")).toEqual([DASH, DASH]);

    getCollectionsProgress.emit({ totalPlans: 0, avgDaysToClose: 0, avgDaysPastDue: 0, unavailable: false });
    await flushPromises();
    expect(text(element, ".progress-empty")).toEqual(["No collection plan data available."]);
    expect(text(element, ".progress-avg-value")).toEqual(["0", "0"]);
  });
  it("says the payment schedules could not be read when the call fails, not '$0.00'", async () => {
    const element = await mount();
    getPaymentPromiseSummary.error();
    await flushPromises();

    expect(text(element, ".payment-promises-empty")).toEqual(["You don't have access to payment schedules."]);
    expect(text(element, ".payment-promises-label")).toEqual([`Payment Promises (${DASH})`]);
  });

  it("says the collection plans could not be read when the progress call fails, not zero averages", async () => {
    const element = await mount();
    getCollectionsProgress.error();
    await flushPromises();

    expect(text(element, ".progress-empty")).toEqual(["You don't have access to collection plans."]);
    expect(text(element, ".progress-avg-value")).toEqual([DASH, DASH]);
  });

  it.each([
    ["a refused read", (adapter) => adapter.emit(null)],
    ["a failed call", (adapter) => adapter.error()]
  ])("shows the plan tasks and my plans as not available after %s, not a count of 0", async (_, fail) => {
    const element = await mount();
    fail(getCollectionPlanTasks);
    fail(getMyCollectionPlans);
    await flushPromises();

    expect(text(element, ".cp-tasks-meta")).toEqual([DASH]);
    expect(text(element, ".cp-tasks-empty")).toEqual(["You don't have access to collection plan tasks."]);
    expect(text(element, ".my-cp-meta")).toEqual([DASH]);
    expect(text(element, ".my-cp-empty")).toEqual(["You don't have access to collection plans."]);
  });

  it("shows empty readable lists as empty, with a count of 0", async () => {
    const element = await mount();
    getCollectionPlanTasks.emit([]);
    getMyCollectionPlans.emit([]);
    await flushPromises();

    expect(text(element, ".cp-tasks-meta")).toEqual(["0"]);
    expect(text(element, ".cp-tasks-empty")).toEqual(["No tasks linked to Collection Plans."]);
    expect(text(element, ".my-cp-meta")).toEqual(["0"]);
    expect(text(element, ".my-cp-empty")).toEqual(["No collection plans assigned to you."]);
  });

  it("says a worklist tab could not be read instead of 'No items in this view'", async () => {
    const element = await mount({
      criticalFollowUpInvoices: [],
      highValueDelinquents: [],
      disputedInvoices: [],
      unavailable: ["critical"]
    });
    await flushPromises();

    expect(text(element, ".worklist-empty")).toEqual([
      "You don't have access to the records this list is built from."
    ]);
  });
});
