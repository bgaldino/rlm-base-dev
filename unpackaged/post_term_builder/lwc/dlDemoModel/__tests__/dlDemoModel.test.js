import {
  hash32,
  mkRng,
  pickInt,
  clamp,
  round1,
  seedTermFlown,
  buildRows,
  seedModel,
  computeUndiscounted,
  edrExisting,
  edrProposed,
  totalsSummary,
  computeTermKpis,
  aggregateKpis,
  finalOfferLineDiscounts,
  termScopeChips,
  toProposalCsvSummary,
  toProposalCsvDetailed,
  currencyCompact,
  int,
  pct1,
  pts,
  formatKpi,
  tone,
  METHOD_PRODUCT,
  METHOD_FARECLASS
} from "c/dlDemoModel";

// A Term shaped like RLM_DeltaTermBuilderController.getBuilderState() emits.
function makeTerm(overrides = {}) {
  return {
    id: "0QL000000000001AAA",
    displayName: "ATL → LHR",
    discount: 12,
    attributes: [
      { code: "DL_Origin", value: "ATL" },
      { code: "DL_Destination", value: "LHR" },
      { code: "DL_Directionality", value: "Between" },
      { code: "DL_Measure", value: "Share Gap" },
      { code: "DL_RequirementValue", value: "5.0" }
    ],
    fares: [
      { id: "0QLfare1", productName: "Delta One", productCode: "DL-J", fareCodes: ["J", "C", "D"], discount: 15 },
      { id: "0QLfare2", productName: "Main", productCode: "DL-M", fareCodes: ["M", "H", "Q"], discount: 8 }
    ],
    ...overrides
  };
}

describe("deterministic primitives", () => {
  it("hash32 is stable and unsigned", () => {
    expect(hash32("ATL>LHR")).toBe(hash32("ATL>LHR"));
    expect(hash32("ATL>LHR")).not.toBe(hash32("LHR>ATL"));
    expect(hash32("anything")).toBeGreaterThanOrEqual(0);
    expect(hash32("")).toBeGreaterThanOrEqual(0);
  });

  it("mkRng replays identical sequences for identical seeds", () => {
    const a = mkRng("seed-1");
    const b = mkRng("seed-1");
    const seqA = [a(), a(), a()];
    const seqB = [b(), b(), b()];
    expect(seqA).toEqual(seqB);
    seqA.forEach((v) => {
      expect(v).toBeGreaterThanOrEqual(0);
      expect(v).toBeLessThan(1);
    });
  });

  it("pickInt stays within inclusive bounds", () => {
    const rng = mkRng("bounds");
    for (let i = 0; i < 50; i++) {
      const v = pickInt(rng, 3, 9);
      expect(v).toBeGreaterThanOrEqual(3);
      expect(v).toBeLessThanOrEqual(9);
    }
  });

  it("clamp and round1 behave", () => {
    expect(clamp(150, 0, 100)).toBe(100);
    expect(clamp(-5, 0, 100)).toBe(0);
    expect(clamp("42", 0, 100)).toBe(42);
    expect(round1(12.345)).toBe(12.3);
    expect(round1("")).toBe(0);
  });
});

describe("seedTermFlown", () => {
  it("is deterministic for the same term", () => {
    const t = makeTerm();
    expect(seedTermFlown(t)).toEqual(seedTermFlown(t));
  });

  it("differs when the route changes but the id is the same", () => {
    const a = seedTermFlown(makeTerm());
    const b = seedTermFlown(
      makeTerm({
        attributes: [
          { code: "DL_Origin", value: "JFK" },
          { code: "DL_Destination", value: "CDG" }
        ]
      })
    );
    expect(a).not.toEqual(b);
  });

  it("keeps FMS above Share so the gap is positive and closeable", () => {
    const f = seedTermFlown(makeTerm());
    expect(f.fmsPts).toBeGreaterThan(f.baseSharePts);
    expect(f.gapPts).toBeGreaterThan(0);
  });

  it("honors an explicit DL_RequirementValue as the gap target", () => {
    const f = seedTermFlown(makeTerm());
    // Requirement 5.0 → gap should equal 5.0 pts.
    expect(f.gapPts).toBeCloseTo(5.0, 1);
    expect(round1(f.fmsPts - f.baseSharePts)).toBeCloseTo(5.0, 1);
  });
});

describe("analysis-period scaling (periodFactor)", () => {
  it("a factor of 1 — or an omitted / invalid factor — is byte-identical to the unscaled baseline", () => {
    const t = makeTerm();
    const base = seedTermFlown(t);
    expect(seedTermFlown(t, undefined, 1)).toEqual(base);
    expect(seedTermFlown(t, undefined, -3)).toEqual(base); // negative → coerced to 1
    expect(seedTermFlown(t, undefined, NaN)).toEqual(base); // NaN → coerced to 1
  });

  it("a factor of 2 doubles every absolute magnitude and leaves the percentage KPIs put", () => {
    const t = makeTerm();
    const one = seedTermFlown(t, undefined, 1);
    const two = seedTermFlown(t, undefined, 2);
    // Base magnitudes scale exactly; host figures within ±rounding of double.
    expect(two.industryRevenue).toBe(2 * one.industryRevenue);
    expect(two.industryPassengers).toBe(2 * one.industryPassengers);
    expect(two.negotiatedSpendUSD).toBe(2 * one.negotiatedSpendUSD);
    expect(two.hostRevenue).toBeCloseTo(2 * one.hostRevenue, -1);
    expect(two.hostPassengers).toBeCloseTo(2 * one.hostPassengers, -1);
    // Percentage KPIs are ratios of co-scaled magnitudes → invariant.
    expect(two.baseSharePts).toBe(one.baseSharePts);
    expect(two.fmsPts).toBe(one.fmsPts);
    expect(two.gapPts).toBe(one.gapPts);
    expect(two.beta).toBe(one.beta);
  });

  it("a factor of 0 zeroes the absolute magnitudes but preserves the percentage KPIs", () => {
    const t = makeTerm();
    const zero = seedTermFlown(t, undefined, 0);
    const base = seedTermFlown(t);
    expect(zero.industryRevenue).toBe(0);
    expect(zero.hostRevenue).toBe(0);
    expect(zero.industryPassengers).toBe(0);
    expect(zero.hostPassengers).toBe(0);
    expect(zero.negotiatedSpendUSD).toBe(0);
    expect(zero.baseSharePts).toBe(base.baseSharePts);
    expect(zero.fmsPts).toBe(base.fmsPts);
  });

  it("computeTermKpis threads periodFactor into the magnitudes only", () => {
    const t = makeTerm();
    const model = seedModel(t, METHOD_PRODUCT);
    const one = computeTermKpis(t, model); // default factor 1
    const two = computeTermKpis(t, model, 2);
    expect(two.industryRevenue).toBe(2 * one.industryRevenue);
    expect(two.industryPassengers).toBe(2 * one.industryPassengers);
    expect(two.negotiatedSpendUSD).toBe(2 * one.negotiatedSpendUSD);
    expect(two.hostRevenue).toBeCloseTo(2 * one.hostRevenue, -1);
    expect(two.hostPassengers).toBeCloseTo(2 * one.hostPassengers, -1);
    expect(two.projectedHostRevenue).toBeCloseTo(2 * one.projectedHostRevenue, -1);
    // Percentage KPIs unchanged under scaling.
    expect(two.sharePts).toBe(one.sharePts);
    expect(two.fmsPts).toBe(one.fmsPts);
    expect(two.gapPts).toBe(one.gapPts);
    expect(two.projectedSharePts).toBe(one.projectedSharePts);
    expect(two.projectedGapPts).toBe(one.projectedGapPts);
    expect(two.edrExistingPts).toBe(one.edrExistingPts);
    expect(two.edrCurrentPts).toBe(one.edrCurrentPts);
  });
});

describe("buildRows — real fares only (Product vs Fare Class)", () => {
  it("Product mode yields one row per real fare product, seeded to the fare's discount", () => {
    const rows = buildRows(makeTerm(), METHOD_PRODUCT);
    expect(rows.map((r) => r.label)).toEqual(["Delta One", "Main"]);
    const one = rows.find((r) => r.label === "Delta One");
    expect(one.backingFareId).toBe("0QLfare1");
    expect(one.existingDiscountPct).toBe(15);
    const main = rows.find((r) => r.label === "Main");
    expect(main.backingFareId).toBe("0QLfare2");
    expect(main.existingDiscountPct).toBe(8);
  });

  it("Fare Class mode explodes only the fare codes present on the Term's fares", () => {
    const rows = buildRows(makeTerm(), METHOD_FARECLASS);
    expect(rows.map((r) => r.label)).toEqual(["J", "C", "D", "M", "H", "Q"]);
    const j = rows.find((r) => r.label === "J");
    expect(j.backingFareId).toBe("0QLfare1");
    expect(j.existingDiscountPct).toBe(15);
    const q = rows.find((r) => r.label === "Q");
    expect(q.backingFareId).toBe("0QLfare2");
  });

  it("yields no rows for a Term with no fares (grid empty-state)", () => {
    expect(buildRows(makeTerm({ fares: [] }), METHOD_PRODUCT)).toEqual([]);
    expect(buildRows({ id: "t", attributes: [] }, METHOD_FARECLASS)).toEqual([]);
  });

  it("pre-fills proposedDiscountPct to existingDiscountPct on every row", () => {
    [METHOD_PRODUCT, METHOD_FARECLASS].forEach((method) => {
      buildRows(makeTerm(), method).forEach((r) => {
        expect(r.proposedDiscountPct).toBe(r.existingDiscountPct);
      });
    });
  });

  it("carries no round / partner / alliance / compare-fare scaffolding on a row", () => {
    const r = buildRows(makeTerm(), METHOD_PRODUCT)[0];
    expect(r.rounds).toBeUndefined();
    expect(r.isPartner).toBeUndefined();
    expect(r.carrier).toBeUndefined();
    expect(r.discountName).toBeUndefined();
    expect(r.alliancePermission).toBeUndefined();
    expect(r.compareFare).toBeUndefined();
    expect(r.isLaneFare).toBeUndefined();
  });

  it("Current Existing % sums to exactly 100", () => {
    const rows = buildRows(makeTerm(), METHOD_PRODUCT);
    expect(round1(rows.reduce((a, r) => a + r.currentExistingPct, 0))).toBe(100);
  });

  it("is fully deterministic", () => {
    expect(buildRows(makeTerm(), METHOD_PRODUCT)).toEqual(buildRows(makeTerm(), METHOD_PRODUCT));
  });

  it("carries priorDiscountPct: null when the fare wasn't enriched, else the clamped value", () => {
    const plain = buildRows(makeTerm(), METHOD_FARECLASS);
    plain.forEach((r) => expect(r.priorDiscountPct).toBeNull());

    const enriched = makeTerm({
      fares: [
        { id: "0QLfare1", productName: "Delta One", productCode: "DL-J", fareCodes: ["J"], discount: 15, priorDiscount: 9.25 }
      ]
    });
    const rows = buildRows(enriched, METHOD_FARECLASS);
    const withPrior = rows.filter((r) => r.priorDiscountPct !== null);
    expect(withPrior.length).toBeGreaterThan(0);
    withPrior.forEach((r) => expect(r.priorDiscountPct).toBeCloseTo(9.3, 1));
  });
});

describe("termScopeChips", () => {
  it("returns curated geography chips in display order, only for present values", () => {
    const chips = termScopeChips(makeTerm());
    const codes = chips.map((c) => c.code);
    expect(codes).toEqual([
      "DL_Origin",
      "DL_Destination",
      "DL_Directionality",
      "DL_Measure",
      "DL_RequirementValue"
    ]);
    const origin = chips.find((c) => c.code === "DL_Origin");
    expect(origin).toEqual({ code: "DL_Origin", label: "Origin", value: "ATL" });
  });

  it("skips blank / whitespace-only attribute values", () => {
    const term = makeTerm({
      attributes: [
        { code: "DL_Origin", value: "ATL" },
        { code: "DL_Destination", value: "  " },
        { code: "DL_Directionality", value: "" }
      ]
    });
    expect(termScopeChips(term).map((c) => c.code)).toEqual(["DL_Origin"]);
  });

  it("returns [] for a term with no attributes", () => {
    expect(termScopeChips({ attributes: [] })).toEqual([]);
    expect(termScopeChips(null)).toEqual([]);
  });
});

describe("proposal CSV exports (G3)", () => {
  function makeProposal() {
    return {
      negotiationName: "Delta ATL → LHR",
      accountName: "Acme, Inc.", // comma → must be quoted
      currencyCode: "USD",
      contract: {
        sharePts: 42.1,
        fmsPts: 55.5,
        projectedSharePts: 50.2,
        projectedGapPts: 5.3,
        edrExistingPts: 12.4,
        edrCurrentPts: 18.9,
        projectedHostRevenue: 123456789
      },
      terms: [
        {
          termId: "0QLterm1",
          route: "ATL → LHR",
          methodLabel: "Product",
          statusLabel: "Proposed",
          isRecommended: true,
          sharePts: 42.1,
          fmsPts: 55.5,
          projectedSharePts: 50.2,
          projectedGapPts: 5.3,
          edrExistingPts: 12.4,
          edrFinalOfferPts: 18.9
        }
      ]
    };
  }

  it("toProposalCsvSummary emits metadata, a term row, and a contract rollup row", () => {
    const csv = toProposalCsvSummary(makeProposal());
    const lines = csv.split("\n");
    expect(lines[0]).toBe("Delta Negotiation Proposal — Summary");
    expect(csv).toContain("Negotiation,Delta ATL → LHR");
    // Comma-bearing account name is quoted per RFC-4180.
    expect(csv).toContain('Account,"Acme, Inc."');
    expect(csv).toContain(
      "Term / Route,Method,Status,Recommended,Share %,FMS %,Projected Share %,Projected Gap (pts),Existing EDR %,Final Offer EDR %"
    );
    expect(csv).toContain("ATL → LHR,Product,Proposed,Yes,42.1,55.5,50.2,5.3,12.4,18.9");
    expect(csv).toContain("Contract (rollup),,,,42.1,55.5,50.2,5.3,12.4,18.9");
    expect(csv).toContain("Projected Host Revenue,123456789");
  });

  it("toProposalCsvSummary renders null KPIs as empty cells (not 0)", () => {
    const p = makeProposal();
    p.terms[0].projectedGapPts = null;
    const csv = toProposalCsvSummary(p);
    expect(csv).toContain("ATL → LHR,Product,Proposed,Yes,42.1,55.5,50.2,,12.4,18.9");
  });

  it("toProposalCsvDetailed emits one row per grid line at its single proposed discount", () => {
    const model = seedModel(makeTerm(), METHOD_PRODUCT);
    const proposal = {
      negotiationName: "N",
      accountName: "A",
      currencyCode: "USD",
      terms: [{ termId: "t1", route: "ATL → LHR" }]
    };
    const csv = toProposalCsvDetailed(proposal, { t1: model });
    const lines = csv.split("\n");
    expect(lines[0]).toBe("Delta Negotiation Proposal — Detailed");
    expect(csv).toContain(
      "Term / Route,Method,Value,Spend %,Undiscounted %,Projected %,Existing Disc %,Prior Disc %,Proposed Disc %"
    );
    // Header (1) + metadata (3) + blank (1) + column header (1) = 6 lines before data.
    const dataLines = lines.slice(6).filter((l) => l.startsWith("ATL → LHR,"));
    expect(dataLines.length).toBe(model.rows.length);
  });

  it("toProposalCsvDetailed skips terms with no model, tolerates empty input", () => {
    const proposal = { terms: [{ termId: "t1", route: "R1" }, { termId: "t2", route: "R2" }] };
    const model = seedModel(makeTerm(), METHOD_PRODUCT);
    const csv = toProposalCsvDetailed(proposal, { t1: model }); // t2 has no model
    expect(csv).toContain("R1,");
    expect(csv).not.toContain("R2,");
    expect(() => toProposalCsvSummary(undefined)).not.toThrow();
    expect(() => toProposalCsvDetailed(undefined, undefined)).not.toThrow();
  });
});

describe("spend normalization + EDR", () => {
  it("computeUndiscounted sums to ~100 when there is spend", () => {
    const rows = buildRows(makeTerm(), METHOD_PRODUCT);
    const ue = computeUndiscounted(rows);
    expect(round1(ue.reduce((a, v) => a + v, 0))).toBeCloseTo(100, 0);
  });

  it("guards a 100% existing discount (no Infinity/NaN)", () => {
    const rows = [
      { currentExistingPct: 50, existingDiscountPct: 100, projectedPct: 50, proposedDiscountPct: 100 },
      { currentExistingPct: 50, existingDiscountPct: 10, projectedPct: 50, proposedDiscountPct: 10 }
    ];
    const ue = computeUndiscounted(rows);
    ue.forEach((v) => expect(Number.isFinite(v)).toBe(true));
    expect(Number.isFinite(edrExisting(rows))).toBe(true);
  });

  it("edrExisting / edrProposed return null (→ N/A) when there is no weighted spend", () => {
    const rows = [
      { currentExistingPct: 0, existingDiscountPct: 10, projectedPct: 0, proposedDiscountPct: 10 },
      { currentExistingPct: 0, existingDiscountPct: 20, projectedPct: 0, proposedDiscountPct: 20 }
    ];
    expect(edrExisting(rows)).toBeNull();
    expect(edrProposed(rows)).toBeNull();
  });

  it("edrProposed is a projected-weighted mean of the proposed discounts", () => {
    const rows = [
      { currentExistingPct: 60, existingDiscountPct: 10, projectedPct: 60, proposedDiscountPct: 40 },
      { currentExistingPct: 40, existingDiscountPct: 5, projectedPct: 40, proposedDiscountPct: 30 }
    ];
    // Projected-weighted: (0.6*40 + 0.4*30) = 36.
    expect(edrProposed(rows)).toBeCloseTo(36, 1);
  });
});

describe("totalsSummary", () => {
  it("flags a valid seeded distribution as valid", () => {
    const rows = buildRows(makeTerm(), METHOD_PRODUCT);
    const t = totalsSummary(rows);
    expect(t.ceValid).toBe(true);
    expect(t.projectedValid).toBe(true);
  });

  it("flags an off-100 distribution as invalid", () => {
    const rows = [
      { currentExistingPct: 30, existingDiscountPct: 10, projectedPct: 40 },
      { currentExistingPct: 30, existingDiscountPct: 10, projectedPct: 40 }
    ];
    const t = totalsSummary(rows);
    expect(t.ceValid).toBe(false); // 60
    expect(t.projectedValid).toBe(false); // 80
  });
});

describe("KPIs", () => {
  it("computeTermKpis projects Share up (and Gap down) when the proposed discounts lift EDR", () => {
    const term = makeTerm();
    const model = seedModel(term, METHOD_PRODUCT);
    // Baseline: proposed == existing (as seeded).
    const base = computeTermKpis(term, model);
    // Deepen every proposed discount → higher proposed EDR → higher projected share, smaller gap.
    model.rows.forEach((r) => {
      r.proposedDiscountPct = clamp(r.existingDiscountPct + 20, 0, 100);
    });
    const projected = computeTermKpis(term, model);
    expect(projected.edrCurrentPts).toBeGreaterThanOrEqual(base.edrCurrentPts);
    expect(projected.projectedSharePts).toBeGreaterThanOrEqual(base.projectedSharePts);
    expect(projected.projectedGapPts).toBeLessThanOrEqual(base.projectedGapPts);
    // Projected share never exceeds FMS (the clamp ceiling); gap never goes negative.
    expect(projected.projectedSharePts).toBeLessThanOrEqual(projected.fmsPts);
    expect(projected.projectedGapPts).toBeGreaterThanOrEqual(0);
  });

  it("aggregateKpis rolls each metric up by its own meaning", () => {
    const t1 = {
      industryRevenue: 100, hostRevenue: 40, industryPassengers: 1000, hostPassengers: 500,
      negotiatedSpendUSD: 100, projectedHostRevenue: 45,
      edrExistingPts: 10, edrCurrentPts: 20
    };
    const t2 = {
      industryRevenue: 300, hostRevenue: 60, industryPassengers: 3000, hostPassengers: 900,
      negotiatedSpendUSD: 300, projectedHostRevenue: 90,
      edrExistingPts: 14, edrCurrentPts: 26
    };
    const agg = aggregateKpis([t1, t2]);
    // Share = 100/400 = 25%; FMS = 1400/4000 = 35%; Gap = 10 pts.
    expect(agg.sharePts).toBeCloseTo(25, 1);
    expect(agg.fmsPts).toBeCloseTo(35, 1);
    expect(agg.gapPts).toBeCloseTo(10, 1);
    // Projected share = 135/400 = 33.75%.
    expect(agg.projectedSharePts).toBeCloseTo(33.8, 1);
    // EDR spend-weighted: existing (100*10 + 300*14)/400 = 13; current (100*20+300*26)/400 = 24.5.
    expect(agg.edrExistingPts).toBeCloseTo(13, 1);
    expect(agg.edrCurrentPts).toBeCloseTo(24.5, 1);
    expect(agg.edrLiftPts).toBeCloseTo(11.5, 1);
  });

  it("aggregateKpis is null-safe on an empty contract", () => {
    const agg = aggregateKpis([]);
    expect(agg.sharePts).toBeNull();
    expect(agg.fmsPts).toBeNull();
    expect(agg.gapPts).toBeNull();
    expect(agg.edrExistingPts).toBeNull();
  });
});

describe("finalOfferLineDiscounts", () => {
  it("maps Product-mode proposed discounts to backing lines, skipping unbacked rows", () => {
    const model = seedModel(makeTerm(), METHOD_PRODUCT);
    const out = finalOfferLineDiscounts(model);
    const ids = out.map((o) => o.id);
    expect(ids).toContain("0QLfare1");
    expect(ids).toContain("0QLfare2");
    // Every emitted line is a real backing fare id (no unbacked rows leak in).
    expect(out.every((o) => typeof o.id === "string" && o.id.startsWith("0QL"))).toBe(true);
    out.forEach((o) => {
      expect(o.discount).toBeGreaterThanOrEqual(0);
      expect(o.discount).toBeLessThanOrEqual(100);
    });
  });

  it("rolls Fare-Class rows up to the parent fare line (spend-weighted)", () => {
    const model = seedModel(makeTerm(), METHOD_FARECLASS);
    // Codes J,C,D back fare1; M,H,Q back fare2 — both should appear once each.
    const out = finalOfferLineDiscounts(model);
    const ids = out.map((o) => o.id);
    expect(ids.filter((id) => id === "0QLfare1")).toHaveLength(1);
    expect(ids.filter((id) => id === "0QLfare2")).toHaveLength(1);
  });
});

describe("formatting", () => {
  it("currencyCompact scales and prefixes", () => {
    expect(currencyCompact(412_600_000, "USD")).toBe("$412.6M");
    expect(currencyCompact(1_200_000_000, "USD")).toBe("$1.2B");
    expect(currencyCompact(24_600, "USD")).toBe("$24.6K");
    expect(currencyCompact(950, "USD")).toBe("$950");
    expect(currencyCompact(5_000_000, "EUR")).toBe("€5M");
    expect(currencyCompact(5_000_000, "XYZ")).toContain("XYZ ");
  });

  it("int / pct1 / pts format and null-guard", () => {
    expect(int(24600)).toBe("24,600");
    expect(pct1(42.34)).toBe("42.3%");
    expect(pct1(null)).toBe("N/A");
    expect(pts(5)).toBe("5.0 pts");
    expect(pts(undefined)).toBe("N/A");
  });

  it("formatKpi dispatches by kind", () => {
    expect(formatKpi(412_600_000, "currency", "USD")).toBe("$412.6M");
    expect(formatKpi(24600, "int")).toBe("24,600");
    expect(formatKpi(42.3, "pct")).toBe("42.3%");
    expect(formatKpi(5, "pts")).toBe("5.0 pts");
    expect(formatKpi(null, "pct")).toBe("N/A");
  });

  it("tone reflects gap-closing vs lift direction", () => {
    expect(tone(0, "gap")).toBe("positive"); // gap closed
    expect(tone(4.2, "gap")).toBe("negative"); // gap remains
    expect(tone(3, "lift")).toBe("positive"); // positive lift
    expect(tone(-2, "lift")).toBe("negative");
    expect(tone(0, "lift")).toBe("neutral");
    expect(tone(null, "gap")).toBe("neutral");
  });
});
