import { createElement } from "lwc";
import RlmBillingScheduleGroupModal from "c/rlmBillingScheduleGroupModal";
import createBillingScheduleGroupAndScheduleViaAPI from "@salesforce/apex/RLM_BillingScheduleGroupService.createBillingScheduleGroupAndScheduleViaAPI";
import getAccountBillingInfo from "@salesforce/apex/RLM_BillingScheduleGroupService.getAccountBillingInfo";
import getLegalEntities from "@salesforce/apex/RLM_BillingScheduleGroupService.getLegalEntities";
import getTaxTreatments from "@salesforce/apex/RLM_BillingScheduleGroupService.getTaxTreatments";
import getProducts from "@salesforce/apex/RLM_BillingScheduleGroupService.getProducts";

// The sfdx-lwc-jest stubs have no lightning/actions module.
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

// The component reads the modal's own state, so the tests drive it through its handlers the
// way the form's change events do, and read the Create button's disabled state and the Apex call.
async function mount() {
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
  return element;
}

function change(element, selector, value) {
  // name is a public property on the base components, not a reflected attribute.
  const field = Array.from(
    element.shadowRoot.querySelectorAll(selector.split("[")[0])
  ).find((candidate) => candidate.name === selector.match(/name="([^"]+)"/)[1]);
  expect(field).toBeTruthy();
  field.dispatchEvent(new CustomEvent("change", { detail: { value } }));
}

async function fillRecurring(element, termSetting) {
  change(element, 'lightning-radio-group[name="chargeType"]', "Recurring");
  await flushPromises();
  change(element, 'lightning-combobox[name="billingFrequency"]', "Month");
  change(element, 'lightning-radio-group[name="billingTiming"]', "Advance");
  change(element, 'lightning-radio-group[name="termSetting"]', termSetting);
  change(element, 'lightning-combobox[name="product"]', "01t000000000001AAA");
  change(
    element,
    'lightning-combobox[name="taxTreatment"]',
    "0tt000000000001AAA"
  );
  change(
    element,
    'lightning-combobox[name="legalEntity"]',
    "0le000000000001AAA"
  );
  change(element, 'lightning-input[name="unitPrice"]', "10");
  await flushPromises();
}

// Collects every toast the component fires, so a test can assert none was an error.
function recordToasts(element) {
  const toasts = [];
  element.addEventListener("lightning__showtoast", (event) =>
    toasts.push(event.detail)
  );
  return toasts;
}

async function fillOneTime(element) {
  change(element, 'lightning-radio-group[name="chargeType"]', "OneTime");
  await flushPromises();
  change(element, 'lightning-combobox[name="product"]', "01t000000000001AAA");
  change(
    element,
    'lightning-combobox[name="taxTreatment"]',
    "0tt000000000001AAA"
  );
  change(
    element,
    'lightning-combobox[name="legalEntity"]',
    "0le000000000001AAA"
  );
  change(element, 'lightning-input[name="unitPrice"]', "10");
  await flushPromises();
}

function createButton(element) {
  return Array.from(
    element.shadowRoot.querySelectorAll("lightning-button")
  ).find((button) => button.variant === "brand");
}

describe("c-rlm-billing-schedule-group-modal submit validation", () => {
  afterEach(() => {
    while (document.body.firstChild) {
      document.body.removeChild(document.body.firstChild);
    }
    jest.clearAllMocks();
  });

  it("allows an evergreen charge with a computed total price and no end date", async () => {
    const element = await mount();
    await fillRecurring(element, "Evergreen");
    const toasts = recordToasts(element);

    expect(createButton(element).disabled).toBe(false);
    createButton(element).click();
    await flushPromises();

    expect(toasts.filter((toast) => toast.variant === "error")).toEqual([]);
    expect(createBillingScheduleGroupAndScheduleViaAPI).toHaveBeenCalledTimes(
      1
    );
    const args = createBillingScheduleGroupAndScheduleViaAPI.mock.calls[0][0];
    expect(args.totalPrice).toBe(10);
    expect(args.endDate).toBeNull();
    expect(args.pageAccountId).toBe("001000000000001AAA");
  });

  it("allows a termed charge with an end date and a total price", async () => {
    const element = await mount();
    await fillRecurring(element, "Termed");
    const toasts = recordToasts(element);

    expect(createButton(element).disabled).toBe(false);
    createButton(element).click();
    await flushPromises();

    expect(toasts.filter((toast) => toast.variant === "error")).toEqual([]);
    expect(createBillingScheduleGroupAndScheduleViaAPI).toHaveBeenCalledTimes(
      1
    );
    const args = createBillingScheduleGroupAndScheduleViaAPI.mock.calls[0][0];
    expect(Number.isFinite(args.totalPrice)).toBe(true);
    expect(args.endDate).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });

  it("blocks a termed charge whose total price was cleared and never sends an undefined total", async () => {
    const element = await mount();
    await fillRecurring(element, "Termed");
    change(element, 'lightning-input[name="totalPrice"]', "");
    await flushPromises();

    expect(createButton(element).disabled).toBe(true);
    // The click handler is the backstop for a submit that reaches it anyway.
    const toastHandler = jest.fn();
    element.addEventListener("lightning__showtoast", toastHandler);
    // A real disabled button cannot be clicked; dispatch the event to reach the handler directly.
    createButton(element).dispatchEvent(new CustomEvent("click"));
    await flushPromises();

    expect(createBillingScheduleGroupAndScheduleViaAPI).not.toHaveBeenCalled();
    expect(toastHandler).toHaveBeenCalledTimes(1);
    expect(toastHandler.mock.calls[0][0].detail.message).toBe(
      "Total Price is required."
    );
  });

  it("blocks a termed charge whose term duration was cleared (no end date)", async () => {
    const element = await mount();
    await fillRecurring(element, "Termed");
    change(element, 'lightning-input[name="termDuration"]', "");
    await flushPromises();

    expect(createButton(element).disabled).toBe(true);
    const toastHandler = jest.fn();
    element.addEventListener("lightning__showtoast", toastHandler);
    // A real disabled button cannot be clicked; dispatch the event to reach the handler directly.
    createButton(element).dispatchEvent(new CustomEvent("click"));
    await flushPromises();

    expect(createBillingScheduleGroupAndScheduleViaAPI).not.toHaveBeenCalled();
    expect(toastHandler.mock.calls[0][0].detail.message).toContain("End Date");
  });

  it("recomputes a hidden total price when leaving Termed after the total was cleared", async () => {
    const element = await mount();
    await fillRecurring(element, "Termed");
    change(element, 'lightning-input[name="totalPrice"]', "");
    await flushPromises();
    expect(createButton(element).disabled).toBe(true);

    change(element, 'lightning-radio-group[name="termSetting"]', "Evergreen");
    await flushPromises();

    expect(createButton(element).disabled).toBe(false);
    createButton(element).click();
    await flushPromises();
    expect(
      createBillingScheduleGroupAndScheduleViaAPI.mock.calls[0][0].totalPrice
    ).toBe(10);
  });

  it("sends the one-time total and no end date after switching from a termed charge", async () => {
    const element = await mount();
    await fillRecurring(element, "Termed");
    change(element, 'lightning-radio-group[name="chargeType"]', "OneTime");
    await flushPromises();

    expect(createButton(element).disabled).toBe(false);
    createButton(element).click();
    await flushPromises();

    const args = createBillingScheduleGroupAndScheduleViaAPI.mock.calls[0][0];
    expect(args.billingTermUnitPicklist).toBe("OneTime");
    expect(args.totalPrice).toBe(10);
    expect(args.endDate).toBeNull();
    expect(args.billingTypePicklistTiming).toBeUndefined();
  });

  it("sends the chosen legal entity and timing of a recurring charge", async () => {
    const element = await mount();
    await fillRecurring(element, "Evergreen");
    change(element, 'lightning-radio-group[name="billingTiming"]', "Arrears");
    await flushPromises();

    createButton(element).click();
    await flushPromises();

    const args = createBillingScheduleGroupAndScheduleViaAPI.mock.calls[0][0];
    expect(args.legalEntityId).toBe("0le000000000001AAA");
    expect(args.billingTypePicklistTiming).toBe("Arrears");
  });

  it("recomputes a hidden total price when switching from a termed charge with a cleared total to one time", async () => {
    const element = await mount();
    await fillRecurring(element, "Termed");
    change(element, 'lightning-input[name="totalPrice"]', "");
    await flushPromises();
    expect(createButton(element).disabled).toBe(true);

    change(element, 'lightning-radio-group[name="chargeType"]', "OneTime");
    await flushPromises();

    expect(createButton(element).disabled).toBe(false);
    createButton(element).click();
    await flushPromises();
    expect(
      createBillingScheduleGroupAndScheduleViaAPI.mock.calls[0][0].totalPrice
    ).toBe(10);
  });

  it("warns, not errors, when the Account has no billing account", async () => {
    const element = createElement("c-rlm-billing-schedule-group-modal", {
      is: RlmBillingScheduleGroupModal
    });
    element.recordId = "001000000000001AAA";
    const toasts = recordToasts(element);
    document.body.appendChild(element);
    getAccountBillingInfo.emit({ accountName: "Acme" });
    await flushPromises();

    expect(toasts.map((toast) => [toast.title, toast.variant])).toEqual([
      ["No Billing Account", "warning"]
    ]);
  });

  it("says the billing account could not be read, not that there is none, when the link read is refused", async () => {
    const element = createElement("c-rlm-billing-schedule-group-modal", {
      is: RlmBillingScheduleGroupModal
    });
    element.recordId = "001000000000001AAA";
    const toasts = recordToasts(element);
    document.body.appendChild(element);
    getAccountBillingInfo.emit({
      accountName: "Acme",
      billingLinkUnreadable: true
    });
    await flushPromises();

    expect(toasts.map((toast) => [toast.title, toast.variant])).toEqual([
      ["Billing Account Unavailable", "warning"]
    ]);
    expect(element.shadowRoot.textContent).toContain("could not be read");
    expect(element.shadowRoot.textContent).not.toContain(
      "No Billing Account associated"
    );
    expect(createButton(element).disabled).toBe(true);
  });

  it("forgets the billing account when the account info turns into an error", async () => {
    const element = await mount();
    const toasts = recordToasts(element);
    await fillOneTime(element);
    expect(createButton(element).disabled).toBe(false);

    getAccountBillingInfo.error();
    await flushPromises();

    expect(toasts.map((toast) => [toast.title, toast.variant])).toEqual([
      ["Error loading Account", "error"]
    ]);
    expect(element.shadowRoot.textContent).not.toContain("Acme BA");
    expect(element.shadowRoot.textContent).not.toContain("Acme");
    expect(createButton(element).disabled).toBe(true);
  });

  it("sends a one-time charge with its total price and no end date", async () => {
    const element = await mount();
    await fillOneTime(element);
    const toasts = recordToasts(element);

    expect(createButton(element).disabled).toBe(false);
    createButton(element).click();
    await flushPromises();

    expect(toasts.filter((toast) => toast.variant === "error")).toEqual([]);
    expect(createBillingScheduleGroupAndScheduleViaAPI).toHaveBeenCalledTimes(
      1
    );
    const args = createBillingScheduleGroupAndScheduleViaAPI.mock.calls[0][0];
    expect(args.billingTermUnitPicklist).toBe("OneTime");
    expect(args.totalPrice).toBe(10);
    expect(args.endDate).toBeNull();
  });

  it("blocks Create and explains why when the Account has no Billing City", async () => {
    const element = createElement("c-rlm-billing-schedule-group-modal", {
      is: RlmBillingScheduleGroupModal
    });
    element.recordId = "001000000000001AAA";
    document.body.appendChild(element);
    getAccountBillingInfo.emit({
      accountName: "Acme",
      billingAccountId: "0aa000000000001AAA",
      billingAccountName: "Acme BA",
      billingCity: null
    });
    getLegalEntities.emit([{ id: "0le000000000001AAA", name: "LE" }]);
    getTaxTreatments.emit([{ id: "0tt000000000001AAA", name: "TT" }]);
    getProducts.emit([{ id: "01t000000000001AAA", name: "Product" }]);
    await flushPromises();
    await fillRecurring(element, "Evergreen");

    expect(createButton(element).disabled).toBe(true);
    // The reason is shown next to the button, not only on a click that cannot happen.
    expect(
      element.shadowRoot.querySelector('[role="alert"]').textContent
    ).toContain("Billing City");
    const toasts = recordToasts(element);
    createButton(element).dispatchEvent(new CustomEvent("click"));
    await flushPromises();

    expect(createBillingScheduleGroupAndScheduleViaAPI).not.toHaveBeenCalled();
    expect(toasts).toHaveLength(1);
    expect(toasts[0].message).toContain("Billing City");
  });

  it("drops the tax treatment when the legal entity changes", async () => {
    const element = await mount();
    const treatment = () =>
      Array.from(element.shadowRoot.querySelectorAll("lightning-combobox")).find(
        (candidate) => candidate.name === "taxTreatment"
      );
    change(element, 'lightning-combobox[name="legalEntity"]', "0le000000000001AAA");
    change(element, 'lightning-combobox[name="taxTreatment"]', "0tt000000000001AAA");
    await flushPromises();
    expect(treatment().value).toBe("0tt000000000001AAA");

    change(element, 'lightning-combobox[name="legalEntity"]', "0le000000000002AAA");
    await flushPromises();

    expect(treatment().value).toBeFalsy();
    expect(treatment().options).toHaveLength(0);
  });

  it("asks for the treatments of the chosen legal entity", async () => {
    const element = await mount();
    change(element, 'lightning-combobox[name="legalEntity"]', "0le000000000002AAA");
    await flushPromises();

    expect(getTaxTreatments.getLastConfig()).toEqual({ legalEntityId: "0le000000000002AAA" });
  });

  it("drops a selected treatment the new options no longer offer", async () => {
    const element = await mount();
    const treatment = () =>
      Array.from(element.shadowRoot.querySelectorAll("lightning-combobox")).find(
        (candidate) => candidate.name === "taxTreatment"
      );
    change(element, 'lightning-combobox[name="legalEntity"]', "0le000000000001AAA");
    change(element, 'lightning-combobox[name="taxTreatment"]', "0tt000000000001AAA");
    await flushPromises();
    expect(treatment().value).toBe("0tt000000000001AAA");

    getTaxTreatments.emit([{ id: "0tt000000000002AAA", name: "Other TT" }]);
    await flushPromises();

    expect(treatment().value).toBeFalsy();
    expect(treatment().options).toEqual([{ label: "Other TT", value: "0tt000000000002AAA" }]);
  });

  it("shows no inline reason when the form can be submitted", async () => {
    const element = await mount();
    await fillRecurring(element, "Evergreen");

    expect(element.shadowRoot.querySelector('[role="alert"]')).toBeNull();
  });

  it("recomputes the total when the quantity is zero", async () => {
    const element = await mount();
    await fillRecurring(element, "Evergreen");
    change(element, 'lightning-input[name="quantity"]', "0");
    await flushPromises();

    createButton(element).click();
    await flushPromises();

    const args = createBillingScheduleGroupAndScheduleViaAPI.mock.calls[0][0];
    expect(args.quantity).toBe(0);
    expect(args.totalPrice).toBe(0);
  });

  it("recomputes the total when the unit price is zero", async () => {
    const element = await mount();
    await fillRecurring(element, "Evergreen");
    change(element, 'lightning-input[name="unitPrice"]', "0");
    await flushPromises();

    createButton(element).click();
    await flushPromises();

    const args = createBillingScheduleGroupAndScheduleViaAPI.mock.calls[0][0];
    expect(args.unitPrice).toBe(0);
    expect(args.totalPrice).toBe(0);
  });
});
