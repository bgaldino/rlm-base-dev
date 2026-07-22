import { createElement } from "lwc";
import DlKpiBand from "c/dlKpiBand";

// eslint-disable-next-line @lwc/lwc/no-async-operation
const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

function contractKpis(overrides = {}) {
  return {
    scope: "contract",
    termCount: 2,
    industryRevenue: 412_600_000,
    hostRevenue: 150_000_000,
    industryPassengers: 30000,
    hostPassengers: 12000,
    negotiatedSpendUSD: 200_000_000,
    projectedHostRevenue: 160_000_000,
    sharePts: 36.4,
    fmsPts: 40.0,
    gapPts: 3.6,
    projectedSharePts: 38.8,
    projectedGapPts: 1.2,
    edrExistingPts: 12.0,
    edrCurrentPts: 18.5,
    edrLiftPts: 6.5,
    ...overrides
  };
}

function create(props = {}) {
  const el = createElement("c-dl-kpi-band", { is: DlKpiBand });
  Object.assign(el, props);
  document.body.appendChild(el);
  return el;
}

afterEach(() => {
  while (document.body.firstChild) {
    document.body.removeChild(document.body.firstChild);
  }
});

describe("c-dl-kpi-band", () => {
  it("renders the full contract band with all tiles", async () => {
    const el = create({ variant: "contract", kpis: contractKpis() });
    await flushPromises();
    const labels = [...el.shadowRoot.querySelectorAll(".dl-kpi-tile__label")].map((n) =>
      n.textContent.trim()
    );
    expect(labels).toEqual(
      expect.arrayContaining([
        "Industry Revenue",
        "Host Revenue",
        "Industry Passengers",
        "Host Passengers",
        "Share",
        "FMS",
        "Share Gap",
        "Proposed EDR"
      ])
    );
  });

  it("renders the slimmer term band without revenue/passenger tiles", async () => {
    const el = create({ variant: "term", kpis: contractKpis() });
    await flushPromises();
    const labels = [...el.shadowRoot.querySelectorAll(".dl-kpi-tile__label")].map((n) =>
      n.textContent.trim()
    );
    expect(labels).toEqual(["Share", "FMS", "Share Gap", "Proposed EDR"]);
  });

  it("formats headline values and snaps (no rAF in jsdom)", async () => {
    const el = create({ variant: "term", kpis: contractKpis() });
    await flushPromises();
    const values = [...el.shadowRoot.querySelectorAll(".dl-kpi-tile__value")].map((n) =>
      n.textContent.trim()
    );
    // Share (projected) = 38.8%, FMS 40.0%, Gap 1.2 pts, EDR 18.5%.
    expect(values).toContain("38.8%");
    expect(values).toContain("40.0%");
    expect(values).toContain("1.2 pts");
    expect(values).toContain("18.5%");
  });

  it("labels a closed gap as closed and colors it good", async () => {
    const el = create({
      variant: "term",
      kpis: contractKpis({ projectedGapPts: 0, gapPts: 3.6 })
    });
    await flushPromises();
    const gapValue = el.shadowRoot.querySelector(".dl-kpi-tile__value_good");
    expect(gapValue).not.toBeNull();
    expect(gapValue.textContent.trim()).toBe("0.0 pts");
    const delta = [...el.shadowRoot.querySelectorAll(".dl-kpi-tile__delta")].map((n) =>
      n.textContent.trim()
    );
    expect(delta).toContain("closed");
  });

  it("shows N/A for EDR when there is no weighted spend", async () => {
    const el = create({
      variant: "term",
      kpis: contractKpis({ edrCurrentPts: null, edrLiftPts: null })
    });
    await flushPromises();
    const values = [...el.shadowRoot.querySelectorAll(".dl-kpi-tile__value")].map((n) =>
      n.textContent.trim()
    );
    expect(values).toContain("N/A");
  });

  it("renders an empty state with no kpis", async () => {
    const el = create({ variant: "contract" });
    await flushPromises();
    expect(el.shadowRoot.querySelector(".dl-kpi-band__empty")).not.toBeNull();
    expect(el.shadowRoot.querySelectorAll(".dl-kpi-tile")).toHaveLength(0);
  });
});
