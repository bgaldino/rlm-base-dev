import { createElement } from "lwc";
import DlModelingGrid from "c/dlModelingGrid";
import { seedModel, METHOD_PRODUCT, METHOD_FARECLASS } from "c/dlDemoModel";

// eslint-disable-next-line @lwc/lwc/no-async-operation
const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

function makeTerm() {
  return {
    id: "0QL000000000001AAA",
    displayName: "ATL → LHR",
    discount: 12,
    attributes: [
      { code: "DL_Origin", value: "ATL" },
      { code: "DL_Destination", value: "LHR" },
      { code: "DL_Measure", value: "Share Gap" },
      { code: "DL_RequirementValue", value: "5.0" }
    ],
    fares: [
      {
        id: "0QLfare1",
        productName: "Delta One",
        productCode: "DL-J",
        fareCodes: ["J", "C"],
        discount: 15
      },
      {
        id: "0QLfare2",
        productName: "Main",
        productCode: "DL-M",
        fareCodes: ["M", "H"],
        discount: 8
      }
    ]
  };
}

function create(props = {}) {
  const el = createElement("c-dl-modeling-grid", { is: DlModelingGrid });
  Object.assign(el, props);
  document.body.appendChild(el);
  return el;
}

afterEach(() => {
  while (document.body.firstChild) {
    document.body.removeChild(document.body.firstChild);
  }
});

describe("c-dl-modeling-grid", () => {
  it("renders one row per model row with sticky value column", async () => {
    const term = makeTerm();
    const model = seedModel(term, METHOD_PRODUCT);
    const el = create({ term, model, currencyCode: "USD" });
    await flushPromises();
    const rows = el.shadowRoot.querySelectorAll("tbody tr");
    expect(rows.length).toBe(model.rows.length);
    // Value column header reflects the method.
    const valueHeader = el.shadowRoot.querySelector(
      "thead .dl-mg-col_value span"
    );
    expect(valueHeader.textContent.trim()).toBe("Product");
  });

  it("renders four round chips with EDR labels", async () => {
    const term = makeTerm();
    const el = create({ term, model: seedModel(term, METHOD_PRODUCT) });
    await flushPromises();
    const chips = el.shadowRoot.querySelectorAll(".dl-mg-round");
    expect(chips.length).toBe(4);
    // The current round (default Round 1) carries a "Current" badge; final offer carries "Final Offer".
    const badges = [
      ...el.shadowRoot.querySelectorAll(".dl-mg-round__badge")
    ].map((n) => n.textContent.trim());
    expect(badges.join(" ")).toContain("Current");
    expect(badges.join(" ")).toContain("Final Offer");
  });

  it("emits modelchange (coalesced) when a Current Existing % cell is edited", async () => {
    const term = makeTerm();
    const el = create({ term, model: seedModel(term, METHOD_PRODUCT) });
    await flushPromises();
    const handler = jest.fn();
    el.addEventListener("modelchange", handler);

    const input = el.shadowRoot.querySelector(
      "tbody lightning-input[data-key]"
    );
    input.value = 42;
    input.dispatchEvent(new CustomEvent("change", { detail: { value: 42 } }));
    await flushPromises();

    expect(handler).toHaveBeenCalled();
    const detail = handler.mock.calls[0][0].detail;
    expect(detail.termId).toBe(term.id);
    expect(detail.method).toBe(METHOD_PRODUCT);
    expect(detail.model).toBeDefined();
    expect(detail.summary).toBeDefined();
    expect("edrExisting" in detail.summary).toBe(true);
  });

  it("coalesces multiple rapid edits into a single emit per frame", async () => {
    const term = makeTerm();
    const el = create({ term, model: seedModel(term, METHOD_PRODUCT) });
    await flushPromises();
    const handler = jest.fn();
    el.addEventListener("modelchange", handler);

    const inputs = el.shadowRoot.querySelectorAll(
      "tbody lightning-input[data-key]"
    );
    // Fire three changes synchronously — the microtask coalescing should emit once.
    inputs[0].dispatchEvent(
      new CustomEvent("change", { detail: { value: 10 } })
    );
    inputs[0].dispatchEvent(
      new CustomEvent("change", { detail: { value: 11 } })
    );
    inputs[0].dispatchEvent(
      new CustomEvent("change", { detail: { value: 12 } })
    );
    await flushPromises();
    expect(handler).toHaveBeenCalledTimes(1);
  });

  it("emits methodchange when the method toggle flips", async () => {
    const term = makeTerm();
    const el = create({ term, model: seedModel(term, METHOD_PRODUCT) });
    await flushPromises();
    const handler = jest.fn();
    el.addEventListener("methodchange", handler);

    const combo = el.shadowRoot.querySelector("lightning-combobox");
    combo.dispatchEvent(
      new CustomEvent("change", { detail: { value: METHOD_FARECLASS } })
    );
    await flushPromises();

    expect(handler).toHaveBeenCalled();
    expect(handler.mock.calls[0][0].detail.method).toBe(METHOD_FARECLASS);
  });

  it("emits expandtoggle from the Expand Workspace button", async () => {
    const term = makeTerm();
    const el = create({
      term,
      model: seedModel(term, METHOD_PRODUCT),
      expanded: false
    });
    await flushPromises();
    const handler = jest.fn();
    el.addEventListener("expandtoggle", handler);

    // The expand button is the toolbar's lightning-button.
    const btn = el.shadowRoot.querySelector(".dl-mg-toolbar lightning-button");
    btn.dispatchEvent(new CustomEvent("click"));
    await flushPromises();

    expect(handler).toHaveBeenCalled();
    expect(handler.mock.calls[0][0].detail.expanded).toBe(true);
  });

  it("shows a totals warning when a distribution is edited off 100%", async () => {
    const term = makeTerm();
    const el = create({ term, model: seedModel(term, METHOD_PRODUCT) });
    await flushPromises();
    // No warning at the seeded (valid) baseline.
    expect(el.shadowRoot.querySelector(".dl-mg-warn")).toBeNull();
    // Zero out EVERY row's Current Existing % (the first lightning-input in each body row) so the
    // CE total is deterministically 0 — never 100 — regardless of the seeded per-row weights.
    const bodyRows = el.shadowRoot.querySelectorAll("tbody tr");
    bodyRows.forEach((tr) => {
      const ceInput = tr.querySelector("lightning-input");
      ceInput.value = 0;
      ceInput.dispatchEvent(new CustomEvent("change"));
    });
    await flushPromises();
    await flushPromises();
    const warn = el.shadowRoot.querySelector(".dl-mg-warn");
    expect(warn).not.toBeNull();
    expect(warn.textContent).toContain("100%");
  });

  it("renders an empty prompt with no model", async () => {
    const el = create({ term: makeTerm() });
    await flushPromises();
    expect(el.shadowRoot.querySelector(".dl-mg-table")).toBeNull();
    expect(el.shadowRoot.textContent).toContain("Select a Term to model");
  });
});
