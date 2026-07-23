/**
 * dlDemoModel — the pure, deterministic mock-data + KPI/EDR engine for the Delta Term Builder demo.
 *
 * This is an LWC *service module* (no template, no LightningElement): it exports plain functions that
 * the orchestrator (c/dlTermBuilder), the modeling grid (c/dlModelingGrid), and the proposal summary
 * (c/dlProposalSummary) all import so the negotiation math lives in exactly one place.
 *
 * Everything here is a pure function of its inputs — NO Math.random(), NO Date, NO I/O. "Randomness"
 * is a stable hash of the Term's identity + route, so the demo reproduces identical baseline numbers
 * across refreshes (clean, repeatable demo runs) while still looking varied route-to-route. Only the
 * analyst's in-session edits change the numbers.
 *
 * Units: every internal percentage is carried in **percentage points** (e.g. Share = 42.3 means
 * 42.3%). Discounts and spend-mix percentages are likewise 0–100. The two conventions are never mixed.
 *
 * Consumed data comes straight from RLM_DeltaTermBuilderController.getBuilderState(): a `term` carries
 * `{ id, displayName, discount, attributes[{code,value}], fares[{id, productName, productCode,
 * fareCodes[], discount}] }`. We only READ it — the demo model never writes back here (the
 * Apply-Final-Offer handoff does that through existing Apex).
 */

// ---------- discounting method ----------

// Discounting methods (the Term's modeling method). Product and Fare Class are genuinely different row
// builders, not two views of one row set — see buildRows(). Both render the Term's REAL fares only —
// there is no canonical-product padding, no unflown fare-class rows, and no injected partner rows.
export const METHOD_PRODUCT = "product";
export const METHOD_FARECLASS = "fareclass";

// Route-attribute codes (must match the PC-DL-TERM attribute defs + c/dlTermCard's lookup).
const ORIGIN_CODE = "DL_Origin";
const DESTINATION_CODE = "DL_Destination";
const DIRECTIONALITY_CODE = "DL_Directionality";
const MEASURE_CODE = "DL_Measure";
const REQUIREMENT_CODE = "DL_RequirementValue";

// ---------- deterministic primitives (no Math.random / no Date) ----------

// FNV-1a 32-bit hash of a string → unsigned int. Stable across runs and environments.
export function hash32(str) {
  let h = 0x811c9dc5;
  const s = String(str == null ? "" : str);
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    // h *= 16777619, kept in 32-bit range via Math.imul.
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

// Seeded LCG → a function returning floats in [0, 1). Numerical Recipes constants. Deterministic given
// the seed, so identical seeds always replay the identical sequence.
export function mkRng(seed) {
  let state = (hash32(seed) ^ 0x9e3779b9) >>> 0;
  return function next() {
    state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
    return state / 4294967296;
  };
}

// Integer in [min, max] inclusive from a seeded rng.
export function pickInt(rng, min, max) {
  return Math.floor(rng() * (max - min + 1)) + min;
}

// ---------- small numeric helpers ----------

export function clamp(value, lo, hi) {
  const n = num(value);
  return Math.min(hi, Math.max(lo, n));
}

// Coerce an editable/string value to a finite number, defaulting to 0 for blank/NaN so the compute
// functions never emit NaN.
export function num(value) {
  if (value === "" || value === null || value === undefined) {
    return 0;
  }
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
}

// Round to one decimal place (all demo percentages carry one decimal).
export function round1(value) {
  return Math.round(num(value) * 10) / 10;
}

function sum(arr) {
  return arr.reduce((acc, v) => acc + num(v), 0);
}

// ---------- term attribute lookup ----------

// Map a Term's attribute list (code → value), same shape c/dlTermCard reads.
function attrMap(term) {
  const map = {};
  const attrs = (term && term.attributes) || [];
  attrs.forEach((a) => {
    if (a && a.code) {
      map[a.code] = a.value;
    }
  });
  return map;
}

// A short, stable route signature ("ATL>LHR>Between") used as part of the seed so two Terms with the
// same route but different ids still differ, and the same Term is stable across refreshes.
function routeSignature(term) {
  const m = attrMap(term);
  return [m[ORIGIN_CODE] || "", m[DESTINATION_CODE] || "", m[DIRECTIONALITY_CODE] || ""].join(">");
}

// Human route label ("ATL → LHR", or "ATL ↔ LHR" when directionality is Between). Same derivation
// c/dlTermCard uses; empty until at least one endpoint is set (falls back to the Term's displayName).
export function routeLabel(term) {
  const m = attrMap(term);
  const origin = m[ORIGIN_CODE];
  const destination = m[DESTINATION_CODE];
  if (!origin && !destination) {
    return (term && term.displayName) || "";
  }
  const arrow = m[DIRECTIONALITY_CODE] === "Between" ? " ↔ " : " → ";
  return `${origin || "—"}${arrow}${destination || "—"}`;
}

// Display label for a discounting method value.
export function methodLabel(method) {
  return method === METHOD_FARECLASS ? "Fare Class" : "Product";
}

// Geography scope attribute codes (definitions live in the org as data — AttributeDefinition +
// AttributePicklistValue — so these are wired by allow-list, not repo metadata).
const TICKETING_REGION_CODE = "DL_TicketingRegion";

// Curated geography/scope attribute codes → human labels, in banner display order. The Modeling tab's
// Term scope banner surfaces the Term-level geography ONCE above the grid (never per-row). Only codes
// with a value render.
const SCOPE_LABELS = [
  [ORIGIN_CODE, "Origin"],
  [DESTINATION_CODE, "Destination"],
  [DIRECTIONALITY_CODE, "Directionality"],
  [MEASURE_CODE, "Measure"],
  [TICKETING_REGION_CODE, "Ticketing Region"],
  [REQUIREMENT_CODE, "Requirement"]
];

// ---------- proposal CSV exports (pure formatters) ----------

// RFC-4180-ish escaping: wrap in quotes and double interior quotes when the cell has a comma, quote,
// or newline. null/undefined → empty cell.
function csvCell(v) {
  if (v === null || v === undefined) {
    return "";
  }
  const s = `${v}`;
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

function csvLine(cells) {
  return cells.map(csvCell).join(",");
}

// A point value rounded to 1 decimal for CSV; null/undefined → "" (not "0").
function num1(v) {
  return v === null || v === undefined ? "" : round1(v);
}

/**
 * Summary CSV: negotiation metadata header + one row per Term (recommended Final Offer KPIs) + a
 * contract rollup row. Pure — returns the CSV text; the caller handles the Blob/anchor download.
 * `proposal` is the payload dlmWorkspaceShell builds for the Proposal Summary modal.
 */
export function toProposalCsvSummary(proposal) {
  const p = proposal || {};
  const terms = p.terms || [];
  const c = p.contract || {};
  const lines = [];
  lines.push("Delta Negotiation Proposal — Summary");
  lines.push(csvLine(["Negotiation", p.negotiationName || ""]));
  lines.push(csvLine(["Account", p.accountName || ""]));
  lines.push(csvLine(["Currency", p.currencyCode || "USD"]));
  lines.push("");
  lines.push(
    csvLine([
      "Term / Route",
      "Method",
      "Status",
      "Recommended",
      "Share %",
      "FMS %",
      "Projected Share %",
      "Projected Gap (pts)",
      "Existing EDR %",
      "Final Offer EDR %"
    ])
  );
  terms.forEach((t) => {
    lines.push(
      csvLine([
        t.route || "",
        t.methodLabel || "",
        t.statusLabel || "",
        t.isRecommended ? "Yes" : "",
        num1(t.sharePts),
        num1(t.fmsPts),
        num1(t.projectedSharePts),
        num1(t.projectedGapPts),
        num1(t.edrExistingPts),
        num1(t.edrFinalOfferPts)
      ])
    );
  });
  lines.push("");
  lines.push(
    csvLine([
      "Contract (rollup)",
      "",
      "",
      "",
      num1(c.sharePts),
      num1(c.fmsPts),
      num1(c.projectedSharePts),
      num1(c.projectedGapPts),
      num1(c.edrExistingPts),
      num1(c.edrCurrentPts)
    ])
  );
  if (c.projectedHostRevenue !== null && c.projectedHostRevenue !== undefined) {
    lines.push(csvLine(["Projected Host Revenue", c.projectedHostRevenue]));
  }
  return lines.join("\n");
}

/**
 * Detailed CSV: one flat row per modeled grid line across all Terms, at its single proposed discount.
 * `modelsByTermId` maps termId → the demo model (rows[]). Pure — returns the CSV text; the caller
 * handles the Blob/anchor download.
 */
export function toProposalCsvDetailed(proposal, modelsByTermId) {
  const p = proposal || {};
  const terms = p.terms || [];
  const models = modelsByTermId || {};
  const lines = [];
  lines.push("Delta Negotiation Proposal — Detailed");
  lines.push(csvLine(["Negotiation", p.negotiationName || ""]));
  lines.push(csvLine(["Account", p.accountName || ""]));
  lines.push(csvLine(["Currency", p.currencyCode || "USD"]));
  lines.push("");
  lines.push(
    csvLine([
      "Term / Route",
      "Method",
      "Value",
      "Spend %",
      "Undiscounted %",
      "Projected %",
      "Existing Disc %",
      "Prior Disc %",
      "Proposed Disc %"
    ])
  );
  terms.forEach((t) => {
    const model = models[t.termId];
    if (!model || !Array.isArray(model.rows)) {
      return;
    }
    const ue = computeUndiscounted(model.rows);
    model.rows.forEach((r, i) => {
      lines.push(
        csvLine([
          t.route || "",
          methodLabel(model.method),
          r.label,
          num1(r.currentExistingPct),
          num1(ue[i]),
          num1(r.projectedPct),
          num1(r.existingDiscountPct),
          num1(r.priorDiscountPct),
          num1(r.proposedDiscountPct)
        ])
      );
    });
  });
  return lines.join("\n");
}

// Compact scope chips for the Term scope banner. Returns [{ code, label, value }] for the curated scope
// attributes that carry a value on this Term, in display order.
export function termScopeChips(term) {
  const m = attrMap(term);
  const chips = [];
  SCOPE_LABELS.forEach(([code, label]) => {
    const value = m[code];
    if (value !== null && value !== undefined && `${value}`.trim() !== "") {
      chips.push({ code, label, value: `${value}` });
    }
  });
  return chips;
}

// ---------- flown-data seed (per Term) ----------

/**
 * Derive a Term's simulated flown-data baseline from its identity + route. Deterministic. All the
 * absolute magnitudes ($ revenue, flight counts) that the contract rollup sums live here; the
 * percentage KPIs (Share, FMS, Gap) are derived from them.
 *
 * FMS (fair market share, flight-capacity based) is kept strictly above Share (revenue based) so the
 * Share Gap is positive and closeable — the headline demo moment. When the Term carries an explicit
 * DL_RequirementValue (the "Share Gap: 5.0" the rail chip shows), that value is honored as the target
 * gap so the KPI band matches the chip.
 *
 * Data-provider seam: when a Term carries a `modeling` blob (see the data-contract doc,
 * docs/features/delta-negotiation-modeling-demo.md — populated server-side in a future round), any
 * finite numeric field on `modeling.flown` overrides the corresponding seeded baseline. Absent
 * (today's behavior) with a `periodFactor` of 1, the deterministic seed is used verbatim — this
 * function stays byte-identical.
 *
 * Analysis-period scaling: `periodFactor` (days-in-window ÷ 365, computed by the Configure Data Set
 * panel where `Date` is allowed — this module stays `Date`-free) multiplies the three absolute
 * magnitudes (industry revenue, industry passengers, negotiated spend) BEFORE the host derivations, so
 * host revenue / host passengers scale with them. All percentage KPIs (Share, FMS, Gap) are ratios of
 * co-scaled magnitudes and are therefore invariant under a uniform factor. An invalid/blank factor
 * coerces to 1 (no scaling), keeping every existing call site back-compatible.
 */
export function seedTermFlown(term, modeling = term && term.modeling, periodFactor = 1) {
  const id = (term && term.id) || "term";
  const m = attrMap(term);
  const seed = `${id}|${routeSignature(term)}|${m[MEASURE_CODE] || ""}|${m[REQUIREMENT_CODE] || ""}`;
  const rng = mkRng(seed);

  const pf = Number.isFinite(periodFactor) && periodFactor >= 0 ? periodFactor : 1;

  const industryRevenue = Math.round(pickInt(rng, 80, 520) * 1_000_000 * pf); // $80M–$520M addressable, period-scaled
  const baseSharePts = round1(18 + rng() * 40); // current revenue share 18–58% (invariant under pf)

  // Prefer the Term's stated requirement (gap target) when present & sensible; else a seeded 3–12 pts.
  const requirement = parseFloat(m[REQUIREMENT_CODE]);
  const gapPts =
    Number.isFinite(requirement) && requirement > 0 && requirement <= 40
      ? round1(requirement)
      : round1(3 + rng() * 9);
  const fmsPts = clamp(round1(baseSharePts + gapPts), 0, 95);

  // "Passengers" carry the flight-capacity metric that FMS is derived from (labelled Passengers in the
  // KPI band; FMS itself stays flight-capacity based). Period-scaled like revenue.
  const industryPassengers = Math.round(pickInt(rng, 4000, 26000) * pf);
  const hostRevenue = Math.round((industryRevenue * baseSharePts) / 100);
  const hostPassengers = Math.round((industryPassengers * fmsPts) / 100);

  // Elasticity: pts of Share gained per pt of EDR lift. 0.25–0.60 so a realistic ~8–15 pt EDR lift
  // meaningfully — but not always fully — closes the gap.
  const beta = 0.25 + rng() * 0.35;

  // Customer's negotiated spend on this Term's routes — the natural weight for rolling per-Term EDR up
  // to the contract (spend-weighted, distinct from the revenue-share aggregation). Period-scaled.
  const negotiatedSpendUSD = Math.round(pickInt(rng, 40, 300) * 1_000_000 * pf);

  const baseline = {
    industryRevenue,
    hostRevenue,
    industryPassengers,
    hostPassengers,
    negotiatedSpendUSD,
    baseSharePts,
    fmsPts,
    gapPts: round1(fmsPts - baseSharePts),
    beta
  };
  return overlayFinite(baseline, modeling && modeling.flown);
}

// Shallow-overlay only the finite-number own keys of `override` onto a copy of `base`. Used by the
// data-provider seam so a partial `modeling.flown` blob can pin some magnitudes while the rest stay
// seeded; when `override` is absent the base object is returned unchanged.
function overlayFinite(base, override) {
  if (!override || typeof override !== "object") {
    return base;
  }
  const out = { ...base };
  Object.keys(override).forEach((k) => {
    const v = override[k];
    if (typeof v === "number" && Number.isFinite(v)) {
      out[k] = v;
    }
  });
  return out;
}

// ---------- row builders (Product vs Fare Class are genuinely different) ----------

// Normalize a product name for matching a canonical product to a real fare (case/space-insensitive).
function normName(name) {
  return String(name || "").trim().toLowerCase();
}

// A fare's prior-cycle discount, when the caller enriched the fare with it (from getQuoteLines'
// priorDiscount, keyed by line id). Read-only context in the grid; never affects any KPI. null when
// absent (today's getBuilderState fares don't carry it).
function priorOf(fare) {
  return fare && fare.priorDiscount !== null && fare.priorDiscount !== undefined
    ? num(fare.priorDiscount)
    : null;
}

// Product-mode entries: one row per REAL fare product the Term carries (deduped by product name, first
// fare wins). No canonical-product padding — a Term with no fares yields no rows (grid empty-state).
function productEntries(term) {
  const fares = (term && term.fares) || [];
  const byName = new Map();
  fares.forEach((f) => {
    const key = normName(f.productName);
    if (key && !byName.has(key)) {
      byName.set(key, f);
    }
  });
  const entries = [];
  byName.forEach((fare) => {
    entries.push({
      key: `P:${fare.productName}`,
      label: fare.productName,
      product: fare.productName,
      backingFareId: fare.id,
      hasFlown: true,
      existingDiscount: num(fare.discount),
      priorDiscount: priorOf(fare),
      // Per-fare context forwarded to the row so the grid can label with fare codes and edit the
      // per-line Alliance Partner multiselect. Source lists come from getBuilderState's fareDto.
      fareCodes: Array.isArray(fare.fareCodes) ? fare.fareCodes : [],
      alliancePartners: Array.isArray(fare.alliancePartners) ? fare.alliancePartners : []
    });
  });
  return entries;
}

// Fare-Class-mode entries: explode each fare's fareCodes[] into booking-class rows (first fare to use a
// code owns the backing line + existing discount), in first-seen order. Only codes actually present on
// the Term's fares become rows — no unflown-code padding.
function fareClassEntries(term) {
  const fares = (term && term.fares) || [];
  const codeInfo = {};
  const order = [];
  fares.forEach((f) => {
    (f.fareCodes || []).forEach((c) => {
      if (c && !codeInfo[c]) {
        codeInfo[c] = {
          fareId: f.id,
          discount: num(f.discount),
          product: f.productName,
          priorDiscount: priorOf(f)
        };
        order.push(c);
      }
    });
  });
  return order.map((c) => {
    const info = codeInfo[c];
    return {
      key: `F:${c}`,
      label: c,
      product: info.product,
      backingFareId: info.fareId,
      hasFlown: true,
      existingDiscount: info.discount,
      priorDiscount: info.priorDiscount
    };
  });
}

/**
 * Build the editable row set for a Term under a discounting method. Each row's seeded spend weight and
 * existing discount are stable functions of the Term id + method + row key, so rows are independently
 * reproducible. Rows are the Term's REAL fares only (no partner rows, no canonical/unflown padding), and
 * each carries a single analyst-editable `proposedDiscountPct` (pre-filled to the existing discount) —
 * the negotiation collapsed to one proposed set, no per-round history.
 */
export function buildRows(term, method) {
  const entries = method === METHOD_FARECLASS ? fareClassEntries(term) : productEntries(term);
  const termId = (term && term.id) || "term";

  // First pass: seed each row's raw spend weight + existing discount.
  const rows = entries.map((e) => {
    const rng = mkRng(`${termId}|${method}|${e.key}`);
    const rawWeight = e.hasFlown ? 0.15 + rng() * 1.0 : 0;
    const existingDiscountPct =
      e.existingDiscount !== null && e.existingDiscount !== undefined
        ? clamp(round1(e.existingDiscount), 0, 100)
        : round1(4 + rng() * 18); // 4–22% seeded when the fare carries no discount

    return {
      key: e.key,
      label: e.label,
      product: e.product || null,
      backingFareId: e.backingFareId || null,
      // Per-fare context carried onto the row: fare codes decorate the row label; alliance partners
      // are edited per row in the modeling grid. Both default to [] for non-product row sets.
      fareCodes: Array.isArray(e.fareCodes) ? e.fareCodes : [],
      alliancePartners: Array.isArray(e.alliancePartners) ? e.alliancePartners : [],
      _rawWeight: rawWeight,
      currentExistingPct: 0, // filled after normalization below
      existingDiscountPct,
      // Read-only prior-cycle discount context (null unless the fare was enriched from getQuoteLines).
      priorDiscountPct:
        e.priorDiscount !== null && e.priorDiscount !== undefined
          ? clamp(round1(e.priorDiscount), 0, 100)
          : null,
      // Single analyst-editable proposed discount; pre-fills to the existing discount, drives the KPIs,
      // and is what Apply-Final-Offer writes back to the Quote.
      proposedDiscountPct: existingDiscountPct,
      projectedPct: 0 // starts equal to currentExistingPct
    };
  });

  // Second pass: normalize raw weights → Current Existing % summing to ~100 (rounded), then fix the
  // rounding residual on the largest row so the seeded distribution sums to exactly 100.
  const totalRaw = sum(rows.map((r) => r._rawWeight));
  rows.forEach((r) => {
    r.currentExistingPct = totalRaw > 0 ? round1((r._rawWeight / totalRaw) * 100) : 0;
    r.projectedPct = r.currentExistingPct; // projected starts at the current mix
    delete r._rawWeight;
  });
  fixTo100(rows, "currentExistingPct");
  // Keep projected in lockstep with the corrected current mix.
  rows.forEach((r) => {
    r.projectedPct = r.currentExistingPct;
  });

  return rows;
}

// Nudge the largest row so a one-decimal distribution sums to exactly 100 (only when the column has any
// weight at all — an all-zero-spend set legitimately sums to 0).
function fixTo100(rows, field) {
  const total = round1(sum(rows.map((r) => r[field])));
  if (total <= 0 || total === 100) {
    return;
  }
  let largest = null;
  rows.forEach((r) => {
    if (!largest || r[field] > largest[field]) {
      largest = r;
    }
  });
  if (largest) {
    largest[field] = round1(largest[field] + (100 - total));
  }
}

// ---------- model assembly ----------

/**
 * Seed a fresh client-only model for a Term + discounting method. The orchestrator caches one of these
 * per (term, method) in `_modelsByTermId`; the grid mutates its rows in place across the session. The
 * negotiation is a single proposed set (one `proposedDiscountPct` per row) — no round metadata.
 */
export function seedModel(term, method, modeling = term && term.modeling) {
  const resolved = method === METHOD_FARECLASS ? METHOD_FARECLASS : METHOD_PRODUCT;
  // Data-provider seam: a `modeling.rows` array (already in row shape) is honored verbatim; otherwise
  // rows are seeded deterministically. Absent (today), behavior is byte-identical.
  const seededRows =
    modeling && Array.isArray(modeling.rows)
      ? JSON.parse(JSON.stringify(modeling.rows))
      : buildRows(term, resolved);
  return {
    termId: (term && term.id) || null,
    method: resolved,
    rows: seededRows
  };
}

// ---------- spend normalization + EDR ----------

/**
 * Undiscounted Existing spend mix (UE_i), in percentage points summing to 100. Each row's undiscounted
 * weight is CE_i / (1 − ED_i/100) — grossing the discounted current spend back up — then renormalized.
 * A 100% (or invalid) discount is guarded so it never produces Infinity. Returns all-zero when there is
 * no weighted spend.
 */
export function computeUndiscounted(rows) {
  const raw = (rows || []).map((r) => {
    const ce = num(r.currentExistingPct);
    const ed = clamp(r.existingDiscountPct, 0, 100);
    const denom = 1 - ed / 100;
    return denom > 0 ? ce / denom : ce; // ED≥100 → fall back to CE (avoid divide-by-zero)
  });
  const total = sum(raw);
  return raw.map((v) => (total > 0 ? round1((v / total) * 100) : 0));
}

/**
 * Existing EDR = spend-weighted average existing discount, weighted by the undiscounted spend mix.
 * Returns null (→ "N/A") when no row carries weighted spend.
 */
export function edrExisting(rows) {
  const ue = computeUndiscounted(rows);
  const totalWeight = sum(ue);
  if (totalWeight <= 0) {
    return null;
  }
  const weighted = (rows || []).reduce(
    (acc, r, i) => acc + (ue[i] / 100) * clamp(r.existingDiscountPct, 0, 100),
    0
  );
  return round1(weighted);
}

/**
 * Proposed EDR = projected-spend-weighted average of each row's single proposed discount. Uses a true
 * weighted mean (normalized by total projected weight) so it stays sane even while the projected
 * distribution is temporarily off 100% mid-edit. Returns null when projected spend is zero.
 */
export function edrProposed(rows) {
  const list = rows || [];
  const totalWeight = sum(list.map((r) => num(r.projectedPct)));
  if (totalWeight <= 0) {
    return null;
  }
  const weighted = list.reduce((acc, r) => {
    const w = num(r.projectedPct);
    const proposed = clamp(r.proposedDiscountPct, 0, 100);
    return acc + w * proposed;
  }, 0);
  return round1(weighted / totalWeight);
}

// ---------- totals / validation (for the sticky totals row) ----------

/**
 * Totals + validity for the grid's sticky totals row. CE and Projected must each sum to ~100 (a small
 * tolerance absorbs one-decimal rounding); temporarily-invalid totals are allowed while editing but the
 * caller should not present the KPI as final until valid.
 */
export function totalsSummary(rows) {
  const list = rows || [];
  const ceTotal = round1(sum(list.map((r) => r.currentExistingPct)));
  const projectedTotal = round1(sum(list.map((r) => r.projectedPct)));
  const ueTotal = round1(sum(computeUndiscounted(list)));
  const near100 = (v) => Math.abs(v - 100) <= 0.2;
  return {
    ceTotal,
    ueTotal,
    projectedTotal,
    ceValid: near100(ceTotal),
    projectedValid: near100(projectedTotal)
  };
}

// ---------- KPIs ----------

/**
 * Full KPI object for a Term, combining its flown-data baseline with the model's proposed EDR to project
 * Share and Share Gap. Shape is identical to aggregateKpis()'s output so c/dlKpiBand renders Term and
 * Contract bands uniformly. Absolute magnitudes are included so the contract rollup can sum them
 * metric-by-metric. `periodFactor` (analysis-window ÷ 365, default 1) scales those magnitudes via
 * seedTermFlown; the percentage KPIs stay invariant.
 */
export function computeTermKpis(term, model, periodFactor = 1, modeling = term && term.modeling) {
  const flown = seedTermFlown(term, modeling, periodFactor);
  const rows = (model && model.rows) || [];

  const edrEx = edrExisting(rows);
  const edrCur = edrProposed(rows);
  const edrLift = edrEx === null || edrCur === null ? 0 : round1(edrCur - edrEx);

  const projectedSharePts = clamp(round1(flown.baseSharePts + flown.beta * edrLift), 0, flown.fmsPts);
  const projectedGapPts = round1(flown.fmsPts - projectedSharePts);

  return {
    scope: "term",
    termId: (term && term.id) || null,
    // absolute magnitudes (summed at the contract level)
    industryRevenue: flown.industryRevenue,
    hostRevenue: flown.hostRevenue,
    industryPassengers: flown.industryPassengers,
    hostPassengers: flown.hostPassengers,
    negotiatedSpendUSD: flown.negotiatedSpendUSD,
    projectedHostRevenue: Math.round((flown.industryRevenue * projectedSharePts) / 100),
    // percentage KPIs (percentage points)
    sharePts: flown.baseSharePts,
    fmsPts: flown.fmsPts,
    gapPts: flown.gapPts,
    projectedSharePts,
    projectedGapPts,
    edrExistingPts: edrEx,
    edrCurrentPts: edrCur,
    edrLiftPts: edrLift
  };
}

// Spend-weighted mean over per-Term KPI objects for a null-aware accessor (used for contract EDR).
function spendWeightedMean(perTerm, accessor) {
  let wSum = 0;
  let vSum = 0;
  (perTerm || []).forEach((t) => {
    const v = accessor(t);
    if (v === null || v === undefined) {
      return;
    }
    const w = num(t.negotiatedSpendUSD);
    wSum += w;
    vSum += w * v;
  });
  return wSum > 0 ? round1(vSum / wSum) : null;
}

/**
 * Contract-wide rollup from per-Term KPI objects. Each metric is aggregated by its own meaning — Share
 * from summed revenue, FMS from summed flights, Gap from those — never one blanket revenue weighting.
 * EDR rolls up spend-weighted (by negotiated spend), consistent with the per-Term definition.
 */
export function aggregateKpis(perTerm) {
  const list = perTerm || [];
  const industryRevenue = sum(list.map((t) => t.industryRevenue));
  const hostRevenue = sum(list.map((t) => t.hostRevenue));
  const industryPassengers = sum(list.map((t) => t.industryPassengers));
  const hostPassengers = sum(list.map((t) => t.hostPassengers));
  const negotiatedSpendUSD = sum(list.map((t) => t.negotiatedSpendUSD));
  const projectedHostRevenue = sum(list.map((t) => t.projectedHostRevenue));

  const sharePts = industryRevenue > 0 ? round1((hostRevenue / industryRevenue) * 100) : null;
  // FMS stays flight-capacity based: host ÷ industry passengers (the capacity metric).
  const fmsPts = industryPassengers > 0 ? round1((hostPassengers / industryPassengers) * 100) : null;
  const gapPts = sharePts !== null && fmsPts !== null ? round1(fmsPts - sharePts) : null;
  const projectedSharePts =
    industryRevenue > 0 ? round1((projectedHostRevenue / industryRevenue) * 100) : null;
  const projectedGapPts =
    projectedSharePts !== null && fmsPts !== null ? round1(fmsPts - projectedSharePts) : null;

  const edrExistingPts = spendWeightedMean(list, (t) => t.edrExistingPts);
  const edrCurrentPts = spendWeightedMean(list, (t) => t.edrCurrentPts);
  const edrLiftPts =
    edrExistingPts !== null && edrCurrentPts !== null ? round1(edrCurrentPts - edrExistingPts) : null;

  return {
    scope: "contract",
    termCount: list.length,
    industryRevenue,
    hostRevenue,
    industryPassengers,
    hostPassengers,
    negotiatedSpendUSD,
    projectedHostRevenue,
    sharePts,
    fmsPts,
    gapPts,
    projectedSharePts,
    projectedGapPts,
    edrExistingPts,
    edrCurrentPts,
    edrLiftPts
  };
}

// ---------- Apply-Final-Offer roll-up (Fare Class → product line) ----------

/**
 * Reduce a model's proposed discounts to per-backing-line discounts for the Apply-to-Quote handoff.
 * Product rows map 1:1 to their backing fare line. Fare Class rows are rolled up to the parent fare
 * line, spend-weighted by projected mix, since the Quote/Contract carry product-level discounts. Rows
 * with no backing line are skipped.
 *
 * Returns [{ id, discount }] ready for RLM_DeltaLineController.updateLineDiscountAndDates.
 */
export function finalOfferLineDiscounts(model) {
  if (!model || !model.rows) {
    return [];
  }
  const byLine = new Map(); // lineId → { wSum, wvSum, fallback }
  model.rows.forEach((r) => {
    if (!r.backingFareId) {
      return;
    }
    const proposed = clamp(r.proposedDiscountPct, 0, 100);
    const weight = num(r.projectedPct);
    const entry = byLine.get(r.backingFareId) || { wSum: 0, wvSum: 0, fallback: proposed };
    entry.wSum += weight;
    entry.wvSum += weight * proposed;
    entry.fallback = proposed; // last-seen, used if every contributing row has zero projected weight
    byLine.set(r.backingFareId, entry);
  });
  const out = [];
  byLine.forEach((entry, id) => {
    const discount = entry.wSum > 0 ? round1(entry.wvSum / entry.wSum) : round1(entry.fallback);
    out.push({ id, discount });
  });
  return out;
}

// ---------- formatting ----------

const CURRENCY_SYMBOLS = { USD: "$", EUR: "€", GBP: "£", CAD: "$", AUD: "$" };

function currencySymbol(code) {
  return CURRENCY_SYMBOLS[code] || "";
}

// Compact currency, e.g. $412.6M / $1.2B. Falls back to the ISO code as a prefix when no symbol maps.
export function currencyCompact(value, currencyCode = "USD") {
  const n = num(value);
  const sym = currencySymbol(currencyCode);
  const prefix = sym || `${currencyCode} `;
  const abs = Math.abs(n);
  let scaled;
  let suffix;
  if (abs >= 1_000_000_000) {
    scaled = n / 1_000_000_000;
    suffix = "B";
  } else if (abs >= 1_000_000) {
    scaled = n / 1_000_000;
    suffix = "M";
  } else if (abs >= 1_000) {
    scaled = n / 1_000;
    suffix = "K";
  } else {
    return `${prefix}${Math.round(n)}`;
  }
  return `${prefix}${round1(scaled)}${suffix}`;
}

// Integer with grouping separators (e.g. 24,600).
export function int(value) {
  return Math.round(num(value)).toLocaleString("en-US");
}

// One-decimal percentage. Null → "N/A".
export function pct1(value) {
  return value === null || value === undefined ? "N/A" : `${round1(value).toFixed(1)}%`;
}

// One-decimal percentage points. Null → "N/A".
export function pts(value) {
  return value === null || value === undefined ? "N/A" : `${round1(value).toFixed(1)} pts`;
}

/**
 * Format a KPI value by kind: "currency" | "int" | "pct" | "pts". Currency accepts a currencyCode.
 */
export function formatKpi(value, kind, currencyCode = "USD") {
  switch (kind) {
    case "currency":
      return currencyCompact(value, currencyCode);
    case "int":
      return int(value);
    case "pct":
      return pct1(value);
    case "pts":
    default:
      return pts(value);
  }
}

/**
 * A tone token ("positive" | "negative" | "neutral") for a value, so the KPI band can color trends
 * without hardcoding thresholds in the template. `kind`:
 *  - "gap": smaller is better (closing the gap is positive).
 *  - "lift": larger is better (a positive delta is positive).
 */
export function tone(value, kind = "lift") {
  if (value === null || value === undefined) {
    return "neutral";
  }
  const n = num(value);
  if (kind === "gap") {
    if (n <= 0.05) {
      return "positive"; // gap effectively closed
    }
    return "negative";
  }
  // lift / delta
  if (n > 0.05) {
    return "positive";
  }
  if (n < -0.05) {
    return "negative";
  }
  return "neutral";
}
