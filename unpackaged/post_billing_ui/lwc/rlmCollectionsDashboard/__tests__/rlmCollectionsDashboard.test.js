/**
 * @jest-environment <rootDir>/tests/jest/browser-time-zone-environment.js
 */
/* global setBrowserTimeZone */
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
const LOADING = "Loading…";

function row(label, amount, color, unavailable) {
  const r = { label, amount, color };
  if (unavailable) r.unavailable = unavailable;
  return r;
}

// The cards as the controller returns them: everything read, or the named components unavailable, each
// refused unless `reasons` says otherwise ('failed'). unappliedPaymentCount alone leaves the balance read.
function cards(unavailable = [], reasons = {}) {
  const has = (key) => unavailable.includes(key);
  const unavailableReason = {};
  for (const key of unavailable) unavailableReason[key] = reasons[key] || "refused";
  return {
    // The controller's total: none without the unpaid invoices, else what was read.
    totalBalance: has("invoices") ? null : 1455 - (has("unappliedPayments") ? 0 : 20),
    receivablesOutstanding: has("invoices") ? null : 1455,
    invoiceCount: has("invoices") ? null : 3,
    currentDue: has("invoices") ? null : 1000,
    overdue: has("invoices") ? null : 455,
    unappliedPaymentBalance: has("unappliedPayments") ? null : 20,
    unappliedPaymentCount: has("unappliedPayments") || has("unappliedPaymentCount") ? null : 1,
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
    unavailable,
    unavailableReason
  };
}

// The breakdown row of each total component.
const EXCLUDED_ROWS = { debitMemos: "Debit Memos", unappliedCredits: "Unapplied Credits", unappliedPayments: "Unapplied Payments" };

const EMPTY_WORKLIST = { criticalFollowUpInvoices: [], highValueDelinquents: [], disputedInvoices: [], unavailable: [] };

// Mounts with the filter options answered and every data section still waiting for its wire.
async function mount() {
  getOrgDefaultCurrency.mockResolvedValue("USD");
  getCurrencyOptions.mockResolvedValue([{ value: "", label: "All Currencies" }]);
  getAccountOptions.mockResolvedValue([
    { value: "", label: "All Accounts" },
    { value: "001000000000001AAA", label: "Acme" }
  ]);
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

describe("c-rlm-collections-dashboard figures and lists it cannot read", () => {
  afterEach(() => {
    while (document.body.firstChild) {
      document.body.removeChild(document.body.firstChild);
    }
    jest.clearAllMocks();
  });

  const LOAD_FAILED = (subject) => `${subject} could not be loaded. Refresh the page to try again.`;

  it("shows a readable zero as a zero, with no exclusion note", async () => {
    const element = await mount();
    getDashboardCards.emit(cards());
    await flushPromises();

    expect(breakdown(element, "Debit Memos")).toEqual({ text: "$0.00", title: "" });
    expect(element.shadowRoot.querySelector(".total-balance-note")).toBeNull();
    expect(card(element, "Total Balance").querySelector(".pulse-card-value").textContent).toBe("$1,435.00");
    expect(card(element, "Receivables Outstanding").querySelector(".pulse-card-meta").textContent).toBe("3 invoices");
  });

  it("shows refused debit memos as not available and the total as excluding them", async () => {
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
    expect(breakdown(element, "Unpaid Invoices").text).toBe("$1,455.00");
    expect(card(element, "Total Balance").querySelector(".pulse-card-value").textContent).toBe("$1,435.00");
  });

  it("says debit memos could not be loaded, not 'no access', when their read failed", async () => {
    const element = await mount();
    getDashboardCards.emit(cards(["debitMemos"], { debitMemos: "failed" }));
    await flushPromises();

    expect(breakdown(element, "Debit Memos")).toEqual({ text: DASH, title: LOAD_FAILED("Debit memos") });
    expect(element.shadowRoot.querySelector(".total-balance-note").textContent).toBe(
      "Excludes debit memos: they could not be loaded. Refresh the page to try again."
    );
  });

  // Every total component is a bounded read, so each can be too many: the note then says to narrow, not refresh.
  it.each([
    ["debitMemos", "debit memos"],
    ["unappliedCredits", "unapplied credits"],
    ["unappliedPayments", "unapplied payments"]
  ])("says the total excludes %s when there are too many to total", async (key, name) => {
    const element = await mount();
    getDashboardCards.emit(cards([key], { [key]: "tooMany" }));
    await flushPromises();

    expect(element.shadowRoot.querySelector(".total-balance-note").textContent).toBe(
      `Excludes ${name}: too many records to total here. Choose an account or currency to narrow it.`
    );
    expect(breakdown(element, EXCLUDED_ROWS[key]).title).toBe(
      "Too many records to total here. Choose an account or currency to narrow it."
    );
  });

  it("names each excluded component's reason, and what to do, when all three reasons are mixed", async () => {
    const element = await mount();
    getDashboardCards.emit(cards(["debitMemos", "unappliedCredits", "unappliedPayments"], {
      unappliedCredits: "tooMany",
      unappliedPayments: "failed"
    }));
    await flushPromises();

    expect(element.shadowRoot.querySelector(".total-balance-note").textContent).toBe(
      "Excludes debit memos (you don't have access), unapplied credits (too many records to total) and " +
        "unapplied payments (could not be loaded). Choose an account or currency to narrow it. " +
        "Refresh the page to try again."
    );
  });

  it("names refused and failed components apart when both are excluded", async () => {
    const element = await mount();
    getDashboardCards.emit(cards(["debitMemos", "unappliedPayments"], { unappliedPayments: "failed" }));
    await flushPromises();

    expect(element.shadowRoot.querySelector(".total-balance-note").textContent).toBe(
      "Excludes debit memos (you don't have access) and unapplied payments (could not be loaded). " +
        "Refresh the page to try again."
    );
    expect(card(element, "Unapplied Payments").querySelector(".pulse-card-meta").textContent).toBe(
      LOAD_FAILED("Payments")
    );
  });

  it("shows refused invoices and payments as not available on every card they feed", async () => {
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
    // No total without the unpaid invoices: not a partial "-$20.00".
    expect(card(element, "Total Balance").querySelector(".pulse-card-value").textContent).toBe(DASH);
    expect(element.shadowRoot.querySelector(".total-balance-note").textContent).toBe(
      "You don't have access to invoices."
    );
    expect(breakdown(element, "Debit Memos").text).toBe("$0.00");
  });

  it("shows only the count as not available when just the payment count could not be read", async () => {
    const element = await mount();
    getDashboardCards.emit(cards(["unappliedPaymentCount"], { unappliedPaymentCount: "failed" }));
    await flushPromises();

    const payments = card(element, "Unapplied Payments");
    expect(payments.querySelector(".pulse-card-value").textContent).toBe("$20.00");
    expect(payments.querySelector(".pulse-card-meta").textContent).toBe(`${DASH} records · Action required`);
    expect(element.shadowRoot.querySelector(".total-balance-note")).toBeNull();
    expect(breakdown(element, "Unapplied Payments").text).toBe("-$20.00");
    expect(card(element, "Total Balance").querySelector(".pulse-card-value").textContent).toBe("$1,435.00");
  });

  it("shows no total when the unpaid invoices were refused, whatever else was read", async () => {
    const element = await mount();
    getDashboardCards.emit(cards(["invoices", "debitMemos", "unappliedCredits", "unappliedPayments"]));
    await flushPromises();

    expect(card(element, "Total Balance").querySelector(".pulse-card-value").textContent).toBe(DASH);
    expect(element.shadowRoot.querySelector(".total-balance-note").textContent).toBe(
      "You don't have access to invoices."
    );
    for (const label of ["Unpaid Invoices", "Debit Memos", "Unapplied Credits", "Unapplied Payments"]) {
      expect(breakdown(element, label).text).toBe(DASH);
    }
  });

  it("says nothing about payment promises, tasks or plans while they are still loading", async () => {
    const element = await mount();

    expect(text(element, ".payment-promises-empty")).toEqual([]);
    expect(text(element, ".cp-tasks-empty")).toEqual([]);
    expect(text(element, ".my-cp-empty")).toEqual([]);
    expect(text(element, ".cp-tasks-meta")).toEqual([""]);
    expect(text(element, ".my-cp-meta")).toEqual([""]);
  });

  it.each([
    ["refused", "You don't have access to payment schedules."],
    ["failed", LOAD_FAILED("Payment schedules")]
  ])("says the payment schedules are unavailable (%s) instead of 'No payment promises'", async (reason, message) => {
    const element = await mount();
    getPaymentPromiseSummary.emit({ buckets: [], unavailable: true, unavailableReason: reason });
    await flushPromises();

    expect(text(element, ".payment-promises-empty")).toEqual([message]);
    expect(text(element, ".payment-promises-label")).toEqual([`Payment Promises (${DASH})`]);

    getPaymentPromiseSummary.emit({ buckets: [], unavailable: false });
    await flushPromises();
    expect(text(element, ".payment-promises-empty")).toEqual(["No payment promises."]);
    expect(text(element, ".payment-promises-label")).toEqual(["Payment Promises ($0.00)"]);
  });

  it.each([
    ["refused", "You don't have access to collection plans."],
    ["failed", LOAD_FAILED("Collection plans")],
    // Progress does not follow the filters, so its too-many text does not suggest narrowing them.
    ["tooMany", "Too many records to total here."]
  ])("says the collection plans are unavailable (%s) instead of zero averages", async (reason, message) => {
    const element = await mount();
    getCollectionsProgress.emit({
      totalPlans: 0, avgDaysToClose: 0, avgDaysPastDue: 0, unavailable: true, unavailableReason: reason
    });
    await flushPromises();

    expect(text(element, ".progress-empty")).toEqual([message]);
    expect(text(element, ".progress-avg-value")).toEqual([DASH, DASH]);

    getCollectionsProgress.emit({ totalPlans: 0, avgDaysToClose: 0, avgDaysPastDue: 0, unavailable: false });
    await flushPromises();
    expect(text(element, ".progress-empty")).toEqual(["No collection plan data available."]);
    expect(text(element, ".progress-avg-value")).toEqual(["0", "0"]);
  });

  it("says payment schedules and collection plans could not be loaded when those calls fail", async () => {
    const element = await mount();
    getPaymentPromiseSummary.error();
    getCollectionsProgress.error();
    await flushPromises();

    expect(text(element, ".payment-promises-empty")).toEqual([LOAD_FAILED("Payment schedules")]);
    expect(text(element, ".payment-promises-label")).toEqual([`Payment Promises (${DASH})`]);
    expect(text(element, ".progress-empty")).toEqual([LOAD_FAILED("Collection plans")]);
    expect(text(element, ".progress-avg-value")).toEqual([DASH, DASH]);
  });

  it.each([
    [
      "a refused read",
      (adapter) => adapter.emit({ items: [], unavailable: true, unavailableReason: "refused" }),
      "You don't have access to collection plan tasks.",
      "You don't have access to collection plans."
    ],
    [
      "a failed read",
      (adapter) => adapter.emit({ items: [], unavailable: true, unavailableReason: "failed" }),
      LOAD_FAILED("Collection plan tasks"),
      LOAD_FAILED("Collection plans")
    ],
    ["a failed call", (adapter) => adapter.error(), LOAD_FAILED("Collection plan tasks"), LOAD_FAILED("Collection plans")]
  ])("shows the plan tasks and my plans as not available after %s, not a count of 0", async (_, fail, tasksText, plansText) => {
    const element = await mount();
    fail(getCollectionPlanTasks);
    fail(getMyCollectionPlans);
    await flushPromises();

    expect(text(element, ".cp-tasks-meta")).toEqual([DASH]);
    expect(text(element, ".cp-tasks-empty")).toEqual([tasksText]);
    expect(text(element, ".my-cp-meta")).toEqual([DASH]);
    expect(text(element, ".my-cp-empty")).toEqual([plansText]);
  });

  it("shows empty readable lists as empty, with a count of 0", async () => {
    const element = await mount();
    getCollectionPlanTasks.emit({ items: [], unavailable: false });
    getMyCollectionPlans.emit({ items: [], unavailable: false });
    await flushPromises();

    expect(text(element, ".cp-tasks-meta")).toEqual(["0"]);
    expect(text(element, ".cp-tasks-empty")).toEqual(["No tasks linked to Collection Plans."]);
    expect(text(element, ".my-cp-meta")).toEqual(["0"]);
    expect(text(element, ".my-cp-empty")).toEqual(["No collection plans assigned to you."]);
  });

  it.each([
    ["refused", "You don't have access to the records this list is built from."],
    ["failed", LOAD_FAILED("The records this list is built from")]
  ])("says a worklist tab is unavailable (%s) instead of 'No items in this view'", async (reason, message) => {
    const element = await mount();
    getWorklist.emit({ ...EMPTY_WORKLIST, unavailable: ["critical"], unavailableReason: { critical: reason } });
    await flushPromises();

    expect(text(element, ".worklist-empty")).toEqual([message]);
  });

  it("marks every worklist tab as not loaded on a worklist wire error, next to the error", async () => {
    const element = await mount();
    getWorklist.error({ message: "wire down" });
    await flushPromises();

    expect(text(element, ".worklist-empty")).toEqual([LOAD_FAILED("The records this list is built from")]);
    expect(element.shadowRoot.textContent).toContain("Worklist:");
    expect(element.shadowRoot.textContent).not.toContain("No items in this view");
  });

  it("says a read, empty worklist tab has no items", async () => {
    const element = await mount();
    getWorklist.emit(EMPTY_WORKLIST);
    await flushPromises();

    expect(text(element, ".worklist-empty")).toEqual(["No items in this view. Change filters or aging selection."]);
  });

  // Before the data wires answer (the filter options already have), no section shows a figure, a count
  // or a "none" message: each is loading.
  it("shows no figures and no 'none' messages while the data is still loading", async () => {
    const element = await mount();

    for (const label of ["Receivables Outstanding", "Current Due", "Overdue", "Unapplied Payments", "Total Balance"]) {
      expect(card(element, label).querySelector(".pulse-card-value").textContent).toBe("");
    }
    expect(card(element, "Receivables Outstanding").querySelector(".pulse-card-meta").textContent).toBe(LOADING);
    expect(element.shadowRoot.querySelectorAll(".pulse-card-breakdown > div")).toHaveLength(0);
    expect(text(element, ".payment-promises-label")).toEqual(["Payment Promises"]);
    expect(text(element, ".payment-promises-empty")).toEqual([]);
    expect(text(element, ".progress-empty")).toEqual([]);
    expect(text(element, ".progress-avg-value")).toEqual(["", ""]);
    expect(text(element, ".worklist-empty")).toEqual([]);
    expect(text(element, ".worklist-loading")).toEqual([LOADING]);
    expect(element.shadowRoot.textContent).not.toContain("$0.00");
    expect(element.shadowRoot.textContent).not.toContain("0 invoices");
  });

  // A filter change puts the filtered sections back to loading: the previous filter's figures never
  // show under the new "Viewing:" label. Progress and my plans read no filter and stay as they were.
  it("clears the filtered sections to loading on a filter change, until the new answer arrives", async () => {
    const element = await mount();
    getDashboardCards.emit(cards());
    getPaymentPromiseSummary.emit({ buckets: [], unavailable: false });
    getWorklist.emit(EMPTY_WORKLIST);
    getCollectionPlanTasks.emit({ items: [], unavailable: false });
    getCollectionsProgress.emit({ totalPlans: 0, avgDaysToClose: 0, avgDaysPastDue: 0, unavailable: false });
    await flushPromises();
    expect(card(element, "Receivables Outstanding").querySelector(".pulse-card-value").textContent).toBe("$1,455.00");

    const account = Array.from(element.shadowRoot.querySelectorAll("lightning-combobox")).find(
      (box) => box.name === "account"
    );
    account.dispatchEvent(new CustomEvent("change", { detail: { value: "001000000000001AAA" } }));
    await flushPromises();

    expect(card(element, "Receivables Outstanding").querySelector(".pulse-card-value").textContent).toBe("");
    expect(text(element, ".payment-promises-label")).toEqual(["Payment Promises"]);
    expect(text(element, ".payment-promises-empty")).toEqual([]);
    expect(text(element, ".worklist-loading")).toEqual([LOADING]);
    expect(text(element, ".cp-tasks-meta")).toEqual([""]);
    // Not filtered by account: still the answer it had.
    expect(text(element, ".progress-empty")).toEqual(["No collection plan data available."]);

    getDashboardCards.emit(cards(["debitMemos"]));
    await flushPromises();
    expect(card(element, "Receivables Outstanding").querySelector(".pulse-card-value").textContent).toBe("$1,455.00");
  });

  it("says there are too many invoices to total instead of a cut-off figure", async () => {
    const element = await mount();
    getDashboardCards.emit(cards(["invoices"], { invoices: "tooMany" }));
    await flushPromises();

    const message = "Too many records to total here. Choose an account or currency to narrow it.";
    expect(card(element, "Receivables Outstanding").querySelector(".pulse-card-value").textContent).toBe(DASH);
    expect(card(element, "Receivables Outstanding").querySelector(".pulse-card-meta").textContent).toBe(message);
    expect(card(element, "Total Balance").querySelector(".pulse-card-value").textContent).toBe(DASH);
    expect(element.shadowRoot.querySelector(".total-balance-note").textContent).toBe(message);
  });

  // A failed cards call no longer replaces the page: the other sections still show what they read.
  it("keeps the other sections visible when the cards call fails", async () => {
    const element = await mount();
    getDashboardCards.error({ body: { message: "cards down" } });
    getPaymentPromiseSummary.emit({ buckets: [], unavailable: false });
    getCollectionsProgress.emit({ totalPlans: 0, avgDaysToClose: 0, avgDaysPastDue: 0, unavailable: false });
    getWorklist.emit(EMPTY_WORKLIST);
    await flushPromises();

    expect(card(element, "Receivables Outstanding").querySelector(".pulse-card-value").textContent).toBe(DASH);
    expect(card(element, "Receivables Outstanding").querySelector(".pulse-card-meta").textContent).toBe(
      LOAD_FAILED("Invoices")
    );
    expect(text(element, ".payment-promises-empty")).toEqual(["No payment promises."]);
    expect(text(element, ".progress-empty")).toEqual(["No collection plan data available."]);
    expect(text(element, ".worklist-empty")).toEqual(["No items in this view. Change filters or aging selection."]);
  });

  // A row's plan or promise lookup that was refused is "Not available" (it may exist), with no Create.
  it("shows a row's unreadable plan as not available, with no Create Collection Plan", async () => {
    const element = await mount();
    getWorklist.emit({
      ...EMPTY_WORKLIST,
      criticalFollowUpInvoices: [
        { invoiceId: "3tt000000000001AAA", invoiceNumber: "INV-1", balance: 2500, billingAccountId: "001000000000001AAA",
          billingAccountName: "Acme", collectionPlanUnavailable: true },
        { invoiceId: "3tt000000000002AAA", invoiceNumber: "INV-2", balance: 2600, billingAccountId: "001000000000001AAA",
          billingAccountName: "Acme", collectionPlanUnavailable: false }
      ]
    });
    await flushPromises();

    const rows = Array.from(element.shadowRoot.querySelectorAll(".worklist-table tbody tr"));
    expect(rows).toHaveLength(2);
    expect(rows[0].textContent).toContain("Not available");
    expect(rows[0].textContent).not.toContain("Create Collection Plan");
    expect(rows[1].textContent).not.toContain("Not available");
    expect(rows[1].textContent).toContain("Create Collection Plan");
  });

  it("shows a disputed row's unreadable promise date as not available", async () => {
    const element = await mount();
    getWorklist.emit({
      ...EMPTY_WORKLIST,
      disputedInvoices: [{ accountId: "001000000000001AAA", accountName: "Acme", balance: 10, ptpUnavailable: true }]
    });
    await flushPromises();
    const tab = Array.from(element.shadowRoot.querySelectorAll("button.folder-tab")).find(
      (button) => button.dataset.tab === "disputed"
    );
    tab.click();
    await flushPromises();

    const disputedRow = element.shadowRoot.querySelector(".worklist-table tbody tr");
    expect(disputedRow.textContent).toContain("Not available");
  });

  // Date-only values are calendar dates: west of UTC they must not show as the day before.
  it("shows a task's due date as its calendar date in a US time zone", async () => {
    setBrowserTimeZone("America/Los_Angeles");
    const element = await mount();
    getCollectionPlanTasks.emit({
      items: [{ taskId: "00T000000000001AAA", subject: "Call", status: "Open", activityDate: "2026-11-25",
        collectionPlanId: "0Wn000000000001AAA" }],
      unavailable: false
    });
    getWorklist.emit({
      ...EMPTY_WORKLIST,
      disputedInvoices: [{ accountId: "001000000000001AAA", accountName: "Acme", balance: 10, ptpDate: "2026-12-01" }]
    });
    await flushPromises();

    expect(element.shadowRoot.querySelector(".cp-tasks-table tbody").textContent).toContain("Nov 25, 2026");
    const tab = Array.from(element.shadowRoot.querySelectorAll("button.folder-tab")).find(
      (button) => button.dataset.tab === "disputed"
    );
    tab.click();
    await flushPromises();
    expect(element.shadowRoot.querySelector(".worklist-table tbody tr").textContent).toContain("Dec 1, 2026");
    setBrowserTimeZone("UTC");
  });

  // Each section says what it is (a figure is totalled, a list listed) and which filters narrow it.
  it("says payment promises have too many records to total, narrowed by account or currency", async () => {
    const element = await mount();
    getPaymentPromiseSummary.emit({ buckets: [], unavailable: true, unavailableReason: "tooMany" });
    await flushPromises();

    expect(text(element, ".payment-promises-empty")).toEqual([
      "Too many records to total here. Choose an account or currency to narrow it."
    ]);
  });

  it.each([
    ["critical", "Too many records to list here. Choose an account or currency to narrow it."],
    ["highValue", "Too many records to list here. Choose an account or currency to narrow it."],
    // Disputed starts from open cases and its account cap: only the account narrows it.
    ["disputed", "Too many records to list here. Choose an account to narrow it."]
  ])("says the %s tab has too many records to list, naming the filter that narrows it", async (tab, message) => {
    const element = await mount();
    getWorklist.emit({ ...EMPTY_WORKLIST, unavailable: [tab], unavailableReason: { [tab]: "tooMany" } });
    await flushPromises();
    const button = Array.from(element.shadowRoot.querySelectorAll("button.folder-tab")).find(
      (candidate) => candidate.dataset.tab === tab
    );
    button.click();
    await flushPromises();

    expect(text(element, ".worklist-empty")).toEqual([message]);
  });

  it("says plan tasks have too many records to list, narrowed by account only", async () => {
    const element = await mount();
    getCollectionPlanTasks.emit({ items: [], unavailable: true, unavailableReason: "tooMany" });
    await flushPromises();

    expect(text(element, ".cp-tasks-empty")).toEqual(["Too many records to list here. Choose an account to narrow it."]);
  });

  it("says the user's plans have too many records to list, with no filter to suggest", async () => {
    const element = await mount();
    getMyCollectionPlans.emit({ items: [], unavailable: true, unavailableReason: "tooMany" });
    await flushPromises();

    expect(text(element, ".my-cp-empty")).toEqual(["Too many records to list here."]);
  });
});
