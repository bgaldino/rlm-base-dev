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
  edrForRound,
  edrByRound,
  totalsSummary,
  computeTermKpis,
  aggregateKpis,
  finalOfferLineDiscounts,
  termScopeChips,
  scopeLabel,
  scopeTypeRank,
  resolveTermForMarket,
  toProposalCsvSummary,
  toProposalCsvDetailed,
  currencyCompact,
  int,
  pct1,
  pts,
  formatKpi,
  tone,
  CANONICAL_PRODUCTS,
  FARE_CODE_VALUES,
  ALLIANCE_PERMISSIONS,
  METHOD_PRODUCT,
  METHOD_FARECLASS,
  ROUND_COUNT
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

describe("buildRows — Product vs Fare Class", () => {
  it("Product mode renders every canonical product (plus partners)", () => {
    const rows = buildRows(makeTerm(), METHOD_PRODUCT);
    CANONICAL_PRODUCTS.forEach((p) => {
      expect(rows.some((r) => r.label === p && !r.isPartner)).toBe(true);
    });
    // Delta One + Main are backed by real fares; the rest are zero-spend canonical rows.
    const one = rows.find((r) => r.label === "Delta One" && !r.isPartner);
    expect(one.backingFareId).toBe("0QLfare1");
    expect(one.existingDiscountPct).toBe(15);
    const premium = rows.find((r) => r.label === "Premium Select" && !r.isPartner);
    expect(premium.backingFareId).toBeNull();
    expect(premium.zeroSpend).toBe(true);
  });

  it("Fare Class mode explodes fare codes into every canonical booking class", () => {
    const rows = buildRows(makeTerm(), METHOD_FARECLASS);
    FARE_CODE_VALUES.forEach((c) => {
      expect(rows.some((r) => r.label === c && !r.isPartner)).toBe(true);
    });
    const j = rows.find((r) => r.label === "J" && !r.isPartner);
    expect(j.backingFareId).toBe("0QLfare1");
    expect(j.zeroSpend).toBe(false);
    const y = rows.find((r) => r.label === "Y" && !r.isPartner); // not on any fare
    expect(y.zeroSpend).toBe(true);
  });

  it("includes at least one partner-carrier row", () => {
    const rows = buildRows(makeTerm(), METHOD_PRODUCT);
    const partners = rows.filter((r) => r.isPartner);
    expect(partners.length).toBeGreaterThanOrEqual(1);
    partners.forEach((p) => {
      expect(["AF", "KL", "VS"]).toContain(p.carrier);
      expect(p.backingFareId).toBeNull();
    });
  });

  it("seeds one editable lane-fare Compare Fare row", () => {
    const rows = buildRows(makeTerm(), METHOD_PRODUCT);
    const lane = rows.filter((r) => r.isLaneFare);
    expect(lane.length).toBe(1);
    expect(lane[0].compareFare).toBeGreaterThan(0);
  });

  it("Current Existing % sums to exactly 100", () => {
    const rows = buildRows(makeTerm(), METHOD_PRODUCT);
    expect(round1(rows.reduce((a, r) => a + r.currentExistingPct, 0))).toBe(100);
  });

  it("is fully deterministic", () => {
    expect(buildRows(makeTerm(), METHOD_PRODUCT)).toEqual(buildRows(makeTerm(), METHOD_PRODUCT));
  });

  it("proposed round discounts escalate to the Final Offer", () => {
    const rows = buildRows(makeTerm(), METHOD_PRODUCT);
    rows.forEach((r) => {
      expect(r.rounds).toHaveLength(ROUND_COUNT);
      for (let i = 1; i < ROUND_COUNT; i++) {
        expect(r.rounds[i]).toBeGreaterThanOrEqual(r.rounds[i - 1]);
      }
    });
  });

  it("seeds an editable Discount Name and a valid Alliance Permission per row", () => {
    const rows = buildRows(makeTerm(), METHOD_PRODUCT);
    rows.forEach((r) => {
      expect(typeof r.discountName).toBe("string");
      expect(r.discountName.length).toBeGreaterThan(0);
      expect(ALLIANCE_PERMISSIONS).toContain(r.alliancePermission);
    });
  });

  it("defaults the host carrier's Alliance Permission to Allowed", () => {
    const rows = buildRows(makeTerm(), METHOD_PRODUCT);
    rows
      .filter((r) => !r.isPartner)
      .forEach((r) => expect(r.alliancePermission).toBe("Allowed"));
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

  it("surfaces the G2 geography codes when present, ahead of Origin", () => {
    const term = makeTerm({
      attributes: [
        { code: "DL_ScopeType", value: "Market" },
        { code: "DL_MarketGroup", value: "Transatlantic" },
        { code: "DL_Origin", value: "ATL" }
      ]
    });
    const codes = termScopeChips(term).map((c) => c.code);
    expect(codes).toEqual(["DL_ScopeType", "DL_MarketGroup", "DL_Origin"]);
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

describe("geography scope (G2)", () => {
  function scopedTerm(id, scopeType, marketGroup, operator, extra = {}) {
    const attributes = [{ code: "DL_ScopeType", value: scopeType }];
    if (marketGroup !== undefined) {
      attributes.push({ code: "DL_MarketGroup", value: marketGroup });
    }
    if (operator !== undefined) {
      attributes.push({ code: "DL_ScopeOperator", value: operator });
    }
    return { id, displayName: id, attributes, ...extra };
  }

  it("scopeTypeRank orders airport > city > country > region > super-region > custom", () => {
    expect(scopeTypeRank("Airport")).toBeGreaterThan(scopeTypeRank("City"));
    expect(scopeTypeRank("City")).toBeGreaterThan(scopeTypeRank("Country"));
    expect(scopeTypeRank("Country")).toBeGreaterThan(scopeTypeRank("Region"));
    expect(scopeTypeRank("Region")).toBeGreaterThan(scopeTypeRank("Super-region"));
    expect(scopeTypeRank("Super-region")).toBeGreaterThan(scopeTypeRank("Custom"));
    // Unknown value ranks above "no scope type" but below the named tiers.
    expect(scopeTypeRank("Weird")).toBe(0);
    expect(scopeTypeRank(undefined)).toBe(-1);
  });

  it("scopeLabel renders 'Country · Includes GB, FR · Between'", () => {
    const term = {
      attributes: [
        { code: "DL_ScopeType", value: "Country" },
        { code: "DL_ScopeOperator", value: "Equals" },
        { code: "DL_MarketGroup", value: "GB, FR" },
        { code: "DL_Directionality", value: "Between" }
      ]
    };
    expect(scopeLabel(term)).toBe("Country · Includes GB, FR · Between");
  });

  it("scopeLabel reads Not-equals as Excludes and is blank with no scope attrs", () => {
    const excl = {
      attributes: [
        { code: "DL_ScopeType", value: "Region" },
        { code: "DL_ScopeOperator", value: "Not-equals" },
        { code: "DL_MarketGroup", value: "APAC" }
      ]
    };
    expect(scopeLabel(excl)).toBe("Region · Excludes APAC");
    expect(scopeLabel(makeTerm())).toBe("");
  });

  it("resolveTermForMarket picks the most specific matching Term", () => {
    const broad = scopedTerm("broad", "Region", "EMEA");
    const narrow = scopedTerm("narrow", "Country", "GB, FR");
    // "GB" falls inside both EMEA (region) and GB,FR (country) — country is more specific.
    expect(resolveTermForMarket("GB", [broad, narrow]).id).toBe("narrow");
    // A market only the region covers resolves to the region.
    expect(resolveTermForMarket("EMEA", [broad, narrow]).id).toBe("broad");
  });

  it("resolveTermForMarket honors Excludes and returns null when nothing matches", () => {
    const includes = scopedTerm("inc", "Country", "GB, FR", "Equals");
    const excludes = scopedTerm("exc", "Region", "GB", "Not-equals");
    expect(resolveTermForMarket("DE", [includes, excludes]).id).toBe("exc"); // DE not excluded
    expect(resolveTermForMarket("GB", [excludes])).toBeNull(); // GB is excluded
    expect(resolveTermForMarket("ZZ", [includes])).toBeNull(); // ZZ not in GB,FR
  });

  it("resolveTermForMarket keeps input order on equal specificity (stable)", () => {
    const a = scopedTerm("a", "Country", "GB");
    const b = scopedTerm("b", "Country", "GB");
    expect(resolveTermForMarket("GB", [a, b]).id).toBe("a");
    expect(resolveTermForMarket("GB", [b, a]).id).toBe("b");
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
          statusLabel: "Recommended",
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
    expect(csv).toContain("ATL → LHR,Product,Recommended,Yes,42.1,55.5,50.2,5.3,12.4,18.9");
    expect(csv).toContain("Contract (rollup),,,,42.1,55.5,50.2,5.3,12.4,18.9");
    expect(csv).toContain("Projected Host Revenue,123456789");
  });

  it("toProposalCsvSummary renders null KPIs as empty cells (not 0)", () => {
    const p = makeProposal();
    p.terms[0].projectedGapPts = null;
    const csv = toProposalCsvSummary(p);
    expect(csv).toContain("ATL → LHR,Product,Recommended,Yes,42.1,55.5,50.2,,12.4,18.9");
  });

  it("toProposalCsvDetailed emits one row per grid line at the final-offer round", () => {
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
      "Term / Route,Method,Final Offer Round,Value,Carrier,Partner,Discount Name,Alliance Permission,Current Existing %,Undiscounted %,Projected %,Existing Disc %,Prior Disc %,Final Offer Disc %,Compare Fare,Notes"
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
      { currentExistingPct: 50, existingDiscountPct: 100, projectedPct: 50, rounds: [10, 20, 30, 40] },
      { currentExistingPct: 50, existingDiscountPct: 10, projectedPct: 50, rounds: [12, 22, 32, 42] }
    ];
    const ue = computeUndiscounted(rows);
    ue.forEach((v) => expect(Number.isFinite(v)).toBe(true));
    expect(Number.isFinite(edrExisting(rows))).toBe(true);
  });

  it("edrExisting returns null (→ N/A) when there is no weighted spend", () => {
    const rows = [
      { currentExistingPct: 0, existingDiscountPct: 10, projectedPct: 0, rounds: [1, 2, 3, 4] },
      { currentExistingPct: 0, existingDiscountPct: 20, projectedPct: 0, rounds: [1, 2, 3, 4] }
    ];
    expect(edrExisting(rows)).toBeNull();
    expect(edrForRound(rows, 0)).toBeNull();
  });

  it("edrForRound is a projected-weighted mean of proposed discounts", () => {
    const rows = [
      { currentExistingPct: 60, existingDiscountPct: 10, projectedPct: 60, rounds: [20, 25, 30, 40] },
      { currentExistingPct: 40, existingDiscountPct: 5, projectedPct: 40, rounds: [10, 15, 20, 30] }
    ];
    // Final Offer (index 3): (0.6*40 + 0.4*30) = 36
    expect(edrForRound(rows, 3)).toBeCloseTo(36, 1);
  });

  it("edrByRound has one entry per round", () => {
    const rows = buildRows(makeTerm(), METHOD_PRODUCT);
    expect(edrByRound(rows)).toHaveLength(ROUND_COUNT);
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
      { currentExistingPct: 30, existingDiscountPct: 10, projectedPct: 40, rounds: [1, 2, 3, 4] },
      { currentExistingPct: 30, existingDiscountPct: 10, projectedPct: 40, rounds: [1, 2, 3, 4] }
    ];
    const t = totalsSummary(rows);
    expect(t.ceValid).toBe(false); // 60
    expect(t.projectedValid).toBe(false); // 80
  });
});

describe("KPIs", () => {
  it("computeTermKpis projects Share up (and Gap down) when the current round lifts EDR", () => {
    const term = makeTerm();
    const model = seedModel(term, METHOD_PRODUCT);
    // Baseline: current round = Round 1 (default).
    const base = computeTermKpis(term, model);
    // Move the current round to the Final Offer (deeper discounts → higher EDR → higher share).
    model.currentRoundIndex = ROUND_COUNT - 1;
    const projected = computeTermKpis(term, model);
    expect(projected.edrCurrentPts).toBeGreaterThanOrEqual(base.edrCurrentPts);
    expect(projected.projectedSharePts).toBeGreaterThanOrEqual(base.projectedSharePts);
    expect(projected.projectedGapPts).toBeLessThanOrEqual(base.projectedGapPts);
    // Projected share never exceeds FMS (the clamp ceiling).
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
  it("maps Product-mode Final Offer discounts to backing lines, skipping unbacked rows", () => {
    const model = seedModel(makeTerm(), METHOD_PRODUCT);
    const out = finalOfferLineDiscounts(model);
    const ids = out.map((o) => o.id);
    expect(ids).toContain("0QLfare1");
    expect(ids).toContain("0QLfare2");
    // No partner / zero-spend canonical rows leak in (they have no backing line).
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
