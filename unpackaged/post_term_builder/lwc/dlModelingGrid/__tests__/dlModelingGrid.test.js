import { createElement } from "lwc";
import DlModelingGrid from "c/dlModelingGrid";
import { seedModel, METHOD_PRODUCT } from "c/dlDemoModel";

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
        alliancePartners: ["Air France", "KLM Royal Dutch Airlines"],
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
    expect(valueHeader.textContent.trim()).toBe("Discount Name");
  });

  it("renders six columns and no totals/EDR footer (no round chips)", async () => {
    const term = makeTerm();
    const el = create({ term, model: seedModel(term, METHOD_PRODUCT) });
    await flushPromises();
    // Round chips are gone post-collapse.
    expect(el.shadowRoot.querySelector(".dl-mg-round")).toBeNull();
    const headers = [...el.shadowRoot.querySelectorAll("thead th")].map((n) =>
      n.textContent.trim()
    );
    expect(headers).toEqual([
      "Discount Name",
      "Fare Codes",
      "Historic Projected Share %",
      "Projected Share %",
      "Prior Disc %",
      "Proposed Disc %"
    ]);
    // The Existing Disc % column and the totals/EDR footer were removed — discount is negotiated
    // solely via the Proposed Disc % column.
    expect(el.shadowRoot.querySelector("tfoot")).toBeNull();
    expect(el.shadowRoot.querySelector(".dl-mg-edr")).toBeNull();
  });

  it("renders the Prior Disc % column as a read-only lightning-input (aligned with Proposed), not editable text", async () => {
    const term = makeTerm();
    const model = seedModel(term, METHOD_PRODUCT);
    // Enrich the first row with a prior-cycle discount (as getQuoteLines would).
    model.rows[0].priorDiscountPct = 5;
    const el = create({ term, model });
    await flushPromises();

    const firstRow = el.shadowRoot.querySelector("tbody tr");
    // The prior cell is read-only (no data-key handler); the editable cells all carry data-key.
    const readOnly = firstRow.querySelector("lightning-input:not([data-key])");
    expect(readOnly).not.toBeNull();
    expect(readOnly.readOnly).toBe(true);
    expect(Number(readOnly.value)).toBe(5);
    // The editable inputs (Projected Share %, Proposed Disc %) are unaffected — two, none read-only.
    // Historic Projected Share % is a read-only display and Fare Codes is plain text — neither is an input.
    const editable = firstRow.querySelectorAll("lightning-input[data-key]");
    expect(editable.length).toBe(2);
  });

  it("emits modelchange with an updated proposed discount when the Proposed % cell is edited", async () => {
    const term = makeTerm();
    const el = create({ term, model: seedModel(term, METHOD_PRODUCT) });
    await flushPromises();
    const handler = jest.fn();
    el.addEventListener("modelchange", handler);

    // The Proposed Disc % input is the last lightning-input in the first body row.
    const firstRow = el.shadowRoot.querySelector("tbody tr");
    const inputs = firstRow.querySelectorAll("lightning-input[data-key]");
    const proposed = inputs[inputs.length - 1];
    proposed.value = 25;
    proposed.dispatchEvent(new CustomEvent("change", { detail: { value: 25 } }));
    await flushPromises();

    expect(handler).toHaveBeenCalled();
    const detail = handler.mock.calls[0][0].detail;
    expect(detail.model.rows[0].proposedDiscountPct).toBe(25);
    expect("edrProposed" in detail.summary).toBe(true);
  });

  it("emits modelchange (coalesced) when the Projected Share % cell is edited", async () => {
    const term = makeTerm();
    const el = create({ term, model: seedModel(term, METHOD_PRODUCT) });
    await flushPromises();
    const handler = jest.fn();
    el.addEventListener("modelchange", handler);

    // Historic Projected Share % is read-only display, so the first editable input in a row is
    // Projected Share %.
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
    // The edited value landed on the row's Projected Share % (projectedPct), not the read-only historic.
    expect(detail.model.rows[0].projectedPct).toBe(42);
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

  it("has no method toggle (grid is locked to the Product view)", async () => {
    const term = makeTerm();
    const el = create({ term, model: seedModel(term, METHOD_PRODUCT) });
    await flushPromises();
    expect(el.shadowRoot.querySelector("lightning-combobox")).toBeNull();
    expect(el.shadowRoot.querySelector(".dl-mg-toolbar")).toBeNull();
  });

  it("labels each product row with its bare product name and its fare codes in the Fare Codes column", async () => {
    const term = makeTerm();
    const el = create({ term, model: seedModel(term, METHOD_PRODUCT) });
    await flushPromises();
    const labels = [...el.shadowRoot.querySelectorAll("tbody .dl-mg-value")].map(
      (n) => n.textContent.trim()
    );
    // Product name only — no parenthesized fare codes.
    expect(labels).toContain("Delta One");
    expect(labels).toContain("Main");
    // Fare codes render in the dedicated Fare Codes column, space-separated.
    const fareCodes = [
      ...el.shadowRoot.querySelectorAll("tbody .dl-mg-fare-codes")
    ].map((n) => n.textContent.trim());
    expect(fareCodes).toContain("J C");
    expect(fareCodes).toContain("M H");
  });

  it("shows a collapsed alliance-partner summary for a fare that has partners", async () => {
    const term = makeTerm();
    const el = create({ term, model: seedModel(term, METHOD_PRODUCT) });
    await flushPromises();
    const summaries = [
      ...el.shadowRoot.querySelectorAll("tbody .dl-mg-alliance")
    ].map((n) => n.textContent.trim());
    // Delta One carries two partners; Main carries none (em dash).
    expect(summaries).toContain("Air France · KLM Royal Dutch Airlines");
    expect(summaries).toContain("—");
  });

  it("expands a row to reveal the alliance-partner dual-listbox, then collapses it", async () => {
    const term = makeTerm();
    const model = seedModel(term, METHOD_PRODUCT);
    const el = create({ term, model });
    await flushPromises();
    // Collapsed: no detail editor yet.
    expect(el.shadowRoot.querySelector("lightning-dual-listbox")).toBeNull();
    const baseRows = el.shadowRoot.querySelectorAll("tbody tr").length;

    const expander = el.shadowRoot.querySelector(".dl-mg-expander");
    expander.click();
    await flushPromises();
    expect(el.shadowRoot.querySelector("lightning-dual-listbox")).not.toBeNull();
    // A detail row was inserted beneath the base row.
    expect(el.shadowRoot.querySelectorAll("tbody tr").length).toBe(baseRows + 1);

    // Collapse again.
    el.shadowRoot.querySelector(".dl-mg-expander").click();
    await flushPromises();
    expect(el.shadowRoot.querySelector("lightning-dual-listbox")).toBeNull();
    expect(el.shadowRoot.querySelectorAll("tbody tr").length).toBe(baseRows);
  });

  it("emits alliancechange with { backingFareId, alliancePartners } when a row's dual-listbox changes", async () => {
    const term = makeTerm();
    const el = create({ term, model: seedModel(term, METHOD_PRODUCT) });
    await flushPromises();
    const handler = jest.fn();
    el.addEventListener("alliancechange", handler);

    // Expand the first row (Delta One, backingFareId 0QLfare1).
    el.shadowRoot.querySelector(".dl-mg-expander").click();
    await flushPromises();

    const dual = el.shadowRoot.querySelector("lightning-dual-listbox");
    dual.dispatchEvent(
      new CustomEvent("change", { detail: { value: ["Virgin Atlantic"] } })
    );
    await flushPromises();

    expect(handler).toHaveBeenCalled();
    const detail = handler.mock.calls[0][0].detail;
    expect(detail.backingFareId).toBe("0QLfare1");
    expect(detail.alliancePartners).toEqual(["Virgin Atlantic"]);
  });

  it("renders an empty prompt with no model", async () => {
    const el = create({ term: makeTerm() });
    await flushPromises();
    expect(el.shadowRoot.querySelector(".dl-mg-table")).toBeNull();
    expect(el.shadowRoot.textContent).toContain("Select a Term to model");
  });
});
