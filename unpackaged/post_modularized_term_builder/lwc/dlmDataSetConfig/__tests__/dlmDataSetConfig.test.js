// The sfdx-lwc-jest stubs expose the standard uiRecordApi / uiObjectInfoApi adapters as test wire
// adapters whose `.emit()` feeds the component's @wire — the sanctioned way to drive these wires in a
// unit test. The lint rule that guards against calling wire adapters outside @wire is a false positive
// for that (test-only) usage, so it is disabled for this spec file.
/* eslint-disable @lwc/lwc/no-unexpected-wire-adapter-usages */
import { createElement } from "lwc";
import DlmDataSetConfig from "c/dlmDataSetConfig";
import { getRecord, updateRecord } from "lightning/uiRecordApi";
import { getPicklistValues } from "lightning/uiObjectInfoApi";

// Real timers: flushPromises leans on setTimeout(0), so we deliberately do NOT fake-timer this suite.
// eslint-disable-next-line @lwc/lwc/no-async-operation
const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

const QUOTE_ID = "0Q0000000000001AAA";
const ACCOUNT_ID = "001000000000001AAA";

function pad(n) {
  return `${n}`.padStart(2, "0");
}

// Mirror the component's _prefillPeriod / _toIsoDate exactly (today, and same month/day one year out),
// computed in-test so the assertion tracks whatever "today" is when the suite runs.
function expectedPrefill() {
  const d = new Date();
  const start = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const end = `${d.getFullYear() + 1}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  return { start, end };
}

// A Quote record shaped for the uiRecordApi.getFieldValue stub (reads record.fields[name].value).
function quoteData(fields = {}) {
  return {
    id: QUOTE_ID,
    apiName: "Quote",
    fields: {
      DL_AnalysisPeriodStart__c: { value: null },
      DL_AnalysisPeriodEnd__c: { value: null },
      DL_ParticipatingCarriers__c: { value: null },
      ...fields
    }
  };
}

function accountData(name) {
  return { id: ACCOUNT_ID, apiName: "Account", fields: { Name: { value: name } } };
}

function carrierPicklist() {
  return {
    values: [
      { label: "Air France", value: "Air France" },
      { label: "KLM Royal Dutch Airlines", value: "KLM Royal Dutch Airlines" }
    ]
  };
}

function create(props = {}) {
  const el = createElement("c-dlm-data-set-config", { is: DlmDataSetConfig });
  Object.assign(el, props);
  document.body.appendChild(el);
  return el;
}

function saveButton(el) {
  return [...el.shadowRoot.querySelectorAll("lightning-button")].find(
    (b) => b.label === "Save"
  );
}

afterEach(() => {
  while (document.body.firstChild) {
    document.body.removeChild(document.body.firstChild);
  }
  jest.clearAllMocks();
});

describe("c-dlm-data-set-config", () => {
  it("pre-fills a blank analysis period today → +1yr", async () => {
    const el = create({ quoteId: QUOTE_ID, accountId: ACCOUNT_ID });
    getRecord.emit(quoteData());
    await flushPromises();

    const { start, end } = expectedPrefill();
    const dateInputs = el.shadowRoot.querySelectorAll(
      "lightning-input"
    );
    expect(dateInputs.length).toBe(2);
    expect(dateInputs[0].value).toBe(start);
    expect(dateInputs[1].value).toBe(end);
  });

  it("adopts a persisted period without pre-filling and starts collapsed", async () => {
    const el = create({ quoteId: QUOTE_ID, accountId: ACCOUNT_ID });
    getRecord.emit(
      quoteData({
        DL_AnalysisPeriodStart__c: { value: "2026-01-01" },
        DL_AnalysisPeriodEnd__c: { value: "2027-01-01" }
      })
    );
    await flushPromises();

    // Collapsed on first load of an already-configured Quote → the body (date inputs) is not rendered.
    expect(
      el.shadowRoot.querySelectorAll("lightning-input").length
    ).toBe(0);
  });

  it("emits configchange with the expected periodFactor when the period changes", async () => {
    const el = create({ quoteId: QUOTE_ID, accountId: ACCOUNT_ID });
    getRecord.emit(quoteData());
    await flushPromises();

    const events = [];
    el.addEventListener("configchange", (e) => events.push(e.detail));

    const [startInput, endInput] = el.shadowRoot.querySelectorAll(
      "lightning-input"
    );
    // 2026-01-01 → 2028-01-01 spans 730 days → factor 2.
    startInput.dispatchEvent(
      new CustomEvent("change", { detail: { value: "2026-01-01" } })
    );
    endInput.dispatchEvent(
      new CustomEvent("change", { detail: { value: "2028-01-01" } })
    );
    await flushPromises();

    expect(events.length).toBeGreaterThan(0);
    const last = events[events.length - 1];
    expect(last.periodFactor).toBeCloseTo(2, 5);
    expect(last.analysisStartDate).toBe("2026-01-01");
    expect(last.analysisEndDate).toBe("2028-01-01");
  });

  it("saves selected participating carriers to the Quote via updateRecord", async () => {
    const el = create({ quoteId: QUOTE_ID, accountId: ACCOUNT_ID });
    getRecord.emit(quoteData());
    getPicklistValues.emit(carrierPicklist());
    await flushPromises();

    const group = el.shadowRoot.querySelector("lightning-checkbox-group");
    expect(group).not.toBeNull();
    group.dispatchEvent(
      new CustomEvent("change", { detail: { value: ["Air France"] } })
    );
    await flushPromises();

    saveButton(el).dispatchEvent(new CustomEvent("click"));
    await flushPromises();

    expect(updateRecord).toHaveBeenCalledTimes(1);
    const { fields } = updateRecord.mock.calls[0][0];
    expect(fields.Id).toBe(QUOTE_ID);
    expect(fields.DL_ParticipatingCarriers__c).toBe("Air France");
  });

  it("keeps subsidiary picks client-only — chips render but nothing is written", async () => {
    const el = create({ quoteId: QUOTE_ID, accountId: ACCOUNT_ID });
    getRecord.emit(quoteData());
    await flushPromises();

    const picker = el.shadowRoot.querySelector("lightning-record-picker");
    picker.dispatchEvent(
      new CustomEvent("change", { detail: { recordId: ACCOUNT_ID } })
    );
    await flushPromises();

    // The single-record wire resolves the picked account's Name → a removable chip.
    getRecord.emit(accountData("Delta Subsidiary Co"));
    await flushPromises();

    const chipLabels = [
      ...el.shadowRoot.querySelectorAll(".dlm-dsc__chip-label")
    ].map((n) => n.textContent.trim());
    expect(chipLabels).toContain("Delta Subsidiary Co");
    // Subsidiaries are surfaced scope only — never persisted.
    expect(updateRecord).not.toHaveBeenCalled();
  });
});
