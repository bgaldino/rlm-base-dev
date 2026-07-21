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

// ---------- canonical demo catalog ----------

// Branded products, in the order the requirements list them. Product mode renders one row per product
// (including zero-flown-spend products so the analyst can still propose a discount).
export const CANONICAL_PRODUCTS = [
  "Delta One",
  "Premium Select",
  "Comfort",
  "Main",
  "Main Basic"
];

// Booking / fare classes (mirrors DL_FareCodes__c in dlQuoteLineGrid). Fare Class mode explodes the
// Term's fares into these rows, adding any not-yet-flown codes as zero-spend rows.
export const FARE_CODE_VALUES = [
  "J", "C", "D", "I", "Z", "P", "A", "G", "W", "S", "Y",
  "B", "M", "H", "Q", "K", "L", "U", "T", "X", "V", "E"
];

// Joint-venture partner carriers surfaced as extra rows so partner spend shows up in the grid and the
// proposal. Deterministically chosen per Term; they carry spend but have no backing Quote line, so the
// Apply-Final-Offer handoff skips them.
export const PARTNER_CARRIERS = ["AF", "KL", "VS"];

export const HOST_CARRIER = "DL";

// Discounting methods (the Term's modeling method). Product and Fare Class are genuinely different row
// builders, not two views of one row set — see buildRows().
export const METHOD_PRODUCT = "product";
export const METHOD_FARECLASS = "fareclass";

// Four explicit negotiation rounds. The active (current) round drives KPIs; the final-offer round
// drives the proposal + the Apply-to-Quote handoff. Both are explicit, never inferred from "highest
// populated" (a stray Round 4 edit must not silently move every KPI).
export const ROUND_LABELS = ["Round 1", "Round 2", "Round 3", "Final Offer"];
export const ROUND_COUNT = ROUND_LABELS.length;
export const DEFAULT_CURRENT_ROUND = 0;
export const DEFAULT_FINAL_OFFER_ROUND = ROUND_COUNT - 1;

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

// Deterministic subset of `arr` of length `count` (stable order), using the rng as a Fisher-Yates
// source. Used to pick partner carriers without repeats.
export function pickSome(rng, arr, count) {
  const pool = [...arr];
  for (let i = pool.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }
  return pool.slice(0, Math.max(0, Math.min(count, pool.length)));
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
 * (today's behavior), the deterministic seed is used verbatim — this function stays byte-identical.
 */
export function seedTermFlown(term, modeling = term && term.modeling) {
  const id = (term && term.id) || "term";
  const m = attrMap(term);
  const seed = `${id}|${routeSignature(term)}|${m[MEASURE_CODE] || ""}|${m[REQUIREMENT_CODE] || ""}`;
  const rng = mkRng(seed);

  const industryRevenue = pickInt(rng, 80, 520) * 1_000_000; // $80M–$520M addressable
  const baseSharePts = round1(18 + rng() * 40); // current revenue share 18–58%

  // Prefer the Term's stated requirement (gap target) when present & sensible; else a seeded 3–12 pts.
  const requirement = parseFloat(m[REQUIREMENT_CODE]);
  const gapPts =
    Number.isFinite(requirement) && requirement > 0 && requirement <= 40
      ? round1(requirement)
      : round1(3 + rng() * 9);
  const fmsPts = clamp(round1(baseSharePts + gapPts), 0, 95);

  // "Passengers" carry the flight-capacity metric that FMS is derived from (labelled Passengers in the
  // KPI band; FMS itself stays flight-capacity based).
  const industryPassengers = pickInt(rng, 4000, 26000);
  const hostRevenue = Math.round((industryRevenue * baseSharePts) / 100);
  const hostPassengers = Math.round((industryPassengers * fmsPts) / 100);

  // Elasticity: pts of Share gained per pt of EDR lift. 0.25–0.60 so a realistic ~8–15 pt EDR lift
  // meaningfully — but not always fully — closes the gap.
  const beta = 0.25 + rng() * 0.35;

  // Customer's negotiated spend on this Term's routes — the natural weight for rolling per-Term EDR up
  // to the contract (spend-weighted, distinct from the revenue-share aggregation).
  const negotiatedSpendUSD = pickInt(rng, 40, 300) * 1_000_000;

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

// Product-mode entries: one per canonical product (matched to a real fare when the Term has one), plus
// any extra real fare products the Term carries that aren't in the canonical list.
function productEntries(term) {
  const fares = (term && term.fares) || [];
  const byName = new Map();
  fares.forEach((f) => {
    const key = normName(f.productName);
    if (key && !byName.has(key)) {
      byName.set(key, f);
    }
  });
  const entries = CANONICAL_PRODUCTS.map((p) => {
    const fare = byName.get(normName(p));
    return {
      key: `P:${p}`,
      label: p,
      product: p,
      backingFareId: fare ? fare.id : null,
      hasFlown: !!fare,
      existingDiscount: fare ? num(fare.discount) : null,
      priorDiscount: priorOf(fare)
    };
  });
  // Append real fare products not in the canonical list (keeps a hand-built demo catalog honest).
  const canonical = new Set(CANONICAL_PRODUCTS.map(normName));
  fares.forEach((f) => {
    if (!canonical.has(normName(f.productName)) && f.productName) {
      entries.push({
        key: `P:${f.productName}`,
        label: f.productName,
        product: f.productName,
        backingFareId: f.id,
        hasFlown: true,
        existingDiscount: num(f.discount),
        priorDiscount: priorOf(f)
      });
    }
  });
  return entries;
}

// Fare-Class-mode entries: explode each fare's fareCodes[] into booking-class rows (first fare to use a
// code owns the backing line + existing discount), then add the remaining canonical codes as zero-spend
// rows so the analyst can propose on unflown classes.
function fareClassEntries(term) {
  const fares = (term && term.fares) || [];
  const codeInfo = {};
  fares.forEach((f) => {
    (f.fareCodes || []).forEach((c) => {
      if (c && !codeInfo[c]) {
        codeInfo[c] = {
          fareId: f.id,
          discount: num(f.discount),
          product: f.productName,
          priorDiscount: priorOf(f)
        };
      }
    });
  });
  return FARE_CODE_VALUES.map((c) => {
    const info = codeInfo[c];
    return {
      key: `F:${c}`,
      label: c,
      product: info ? info.product : null,
      backingFareId: info ? info.fareId : null,
      hasFlown: !!info,
      existingDiscount: info ? info.discount : null,
      priorDiscount: info ? info.priorDiscount : null
    };
  });
}

// Add 1–2 deterministic partner-carrier rows mirroring flown host rows. Partners carry spend (so they
// show up in the mix + proposal) but have no backing Quote line, so Apply-Final-Offer skips them.
function withPartnerRows(term, method, entries) {
  const flown = entries.filter((e) => e.hasFlown);
  if (flown.length === 0) {
    return entries;
  }
  const seed = `${term && term.id}|${method}|partners`;
  const rng = mkRng(seed);
  const count = 1 + (hash32(seed) % 2); // 1 or 2
  const carriers = pickSome(rng, PARTNER_CARRIERS, count);
  const partners = carriers.map((carrier, i) => {
    const mirror = flown[i % flown.length];
    return {
      key: `${carrier}:${mirror.label}`,
      label: mirror.label,
      product: mirror.product,
      carrier,
      isPartner: true,
      backingFareId: null,
      hasFlown: true,
      // Partners negotiate their own discount — seed rather than inherit the host's.
      existingDiscount: null,
      notes: "JV partner spend"
    };
  });
  return [...entries, ...partners];
}

/**
 * Build the full editable row set for a Term under a discounting method. Each row's seeded values
 * (spend mix, existing discount, per-round proposals) are stable functions of the Term id + method +
 * row key, so rows are independently reproducible.
 */
export function buildRows(term, method) {
  const base = method === METHOD_FARECLASS ? fareClassEntries(term) : productEntries(term);
  const entries = withPartnerRows(term, method, base);
  const termId = (term && term.id) || "term";

  // First pass: seed each row's raw spend weight + existing discount + escalating round proposals.
  const rows = entries.map((e) => {
    const rng = mkRng(`${termId}|${method}|${e.key}`);
    const rawWeight = e.hasFlown ? 0.15 + rng() * 1.0 : 0; // zero-spend rows carry no weight
    const existingDiscountPct =
      e.existingDiscount !== null && e.existingDiscount !== undefined
        ? clamp(round1(e.existingDiscount), 0, 100)
        : round1(4 + rng() * 18); // 4–22% seeded when no real fare backs the row

    // Proposed discounts escalate round over round; the Final Offer is the deepest.
    const r1 = clamp(round1(existingDiscountPct + 1 + rng() * 3), 0, 100);
    const r2 = clamp(round1(r1 + 1 + rng() * 3), 0, 100);
    const r3 = clamp(round1(r2 + 1 + rng() * 3), 0, 100);
    const r4 = clamp(round1(r3 + 1 + rng() * 4), 0, 100);

    return {
      key: e.key,
      label: e.label,
      product: e.product || null,
      carrier: e.carrier || HOST_CARRIER,
      isPartner: !!e.isPartner,
      isLaneFare: false,
      backingFareId: e.backingFareId || null,
      zeroSpend: !e.hasFlown,
      _rawWeight: rawWeight,
      currentExistingPct: 0, // filled after normalization below
      existingDiscountPct,
      // Read-only prior-cycle discount context (null unless the fare was enriched from getQuoteLines).
      priorDiscountPct:
        e.priorDiscount !== null && e.priorDiscount !== undefined
          ? clamp(round1(e.priorDiscount), 0, 100)
          : null,
      projectedPct: 0, // starts equal to currentExistingPct
      compareFare: null,
      rounds: [r1, r2, r3, r4],
      notes: e.notes || ""
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

  // One seeded lane-fare row carries an editable Compare Fare benchmark (informational, not in EDR).
  const laneRow = rows.find((r) => !r.zeroSpend && !r.isPartner) || rows.find((r) => !r.zeroSpend);
  if (laneRow) {
    const rng = mkRng(`${termId}|${method}|${laneRow.key}|compare`);
    laneRow.isLaneFare = true;
    laneRow.compareFare = pickInt(rng, 800, 3200);
    if (!laneRow.notes) {
      laneRow.notes = "Lane fare benchmark";
    }
  }

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
 * per (term, method) in `_modelsByTermId`; the grid mutates its rows/rounds in place across the session.
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
    roundLabels: [...ROUND_LABELS],
    roundCount: ROUND_COUNT,
    currentRoundIndex: DEFAULT_CURRENT_ROUND,
    finalOfferRoundIndex: DEFAULT_FINAL_OFFER_ROUND,
    // Optional per-round status chips (Draft / Sent / Countered / Recommended) for storytelling.
    roundStatuses: ROUND_LABELS.map(() => "Draft"),
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
 * Proposed EDR for a given round = projected-spend-weighted average of that round's proposed discounts.
 * Uses a true weighted mean (normalized by total projected weight) so it stays sane even while the
 * projected distribution is temporarily off 100% mid-edit. Returns null when projected spend is zero.
 */
export function edrForRound(rows, roundIndex) {
  const list = rows || [];
  const totalWeight = sum(list.map((r) => num(r.projectedPct)));
  if (totalWeight <= 0) {
    return null;
  }
  const weighted = list.reduce((acc, r) => {
    const w = num(r.projectedPct);
    const proposed = clamp((r.rounds || [])[roundIndex], 0, 100);
    return acc + w * proposed;
  }, 0);
  return round1(weighted / totalWeight);
}

// EDR for every round (parallel to roundLabels); null entries render as N/A.
export function edrByRound(rows, roundCount = ROUND_COUNT) {
  const out = [];
  for (let i = 0; i < roundCount; i++) {
    out.push(edrForRound(rows, i));
  }
  return out;
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
 * Full KPI object for a Term, combining its flown-data baseline with the model's active-round EDR to
 * project Share and Share Gap. Shape is identical to aggregateKpis()'s output so c/dlKpiBand renders
 * Term and Contract bands uniformly. Absolute magnitudes are included so the contract rollup can sum
 * them metric-by-metric.
 */
export function computeTermKpis(term, model, roundIndexOverride, modeling = term && term.modeling) {
  const flown = seedTermFlown(term, modeling);
  const rows = (model && model.rows) || [];
  const round =
    roundIndexOverride === undefined || roundIndexOverride === null
      ? model
        ? model.currentRoundIndex
        : DEFAULT_CURRENT_ROUND
      : roundIndexOverride;

  const edrEx = edrExisting(rows);
  const edrCur = edrForRound(rows, round);
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
 * Reduce a model's Final Offer proposals to per-backing-line discounts for the Apply-to-Quote handoff.
 * Product rows map 1:1 to their backing fare line. Fare Class rows are rolled up to the parent fare
 * line, spend-weighted by projected mix, since the Quote/Contract carry product-level discounts. Rows
 * with no backing line (zero-spend canonical rows, partner rows) are skipped.
 *
 * Returns [{ id, discount }] ready for RLM_DeltaLineController.updateLineDiscountAndDates.
 */
export function finalOfferLineDiscounts(model) {
  if (!model || !model.rows) {
    return [];
  }
  const round = model.finalOfferRoundIndex;
  const byLine = new Map(); // lineId → { wSum, wvSum, fallback }
  model.rows.forEach((r) => {
    if (!r.backingFareId) {
      return;
    }
    const proposed = clamp((r.rounds || [])[round], 0, 100);
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
