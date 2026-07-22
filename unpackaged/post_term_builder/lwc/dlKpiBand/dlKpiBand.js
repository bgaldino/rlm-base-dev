import { LightningElement, api } from "lwc";
import { formatKpi, tone as toneOf, round1 } from "c/dlDemoModel";

// Number-tween duration for the animated headline tiles (Share / Share Gap / EDR).
const ANIM_MS = 650;

/**
 * dlKpiBand — presentational KPI tile band for the Delta Term Builder demo.
 *
 * Renders a row of KPI tiles from a KPI object (as produced by c/dlDemoModel's computeTermKpis or
 * aggregateKpis). Two variants:
 *   - "contract": the full band (Industry/Host Revenue, Industry/Host Passengers, Share, FMS, Gap, EDR).
 *   - "term": a slimmer band (Share, FMS, Share Gap, EDR) shown atop the Term workspace.
 *
 * Owns no data and does no I/O. The only behavior it adds is the headline demo moment: when the KPI
 * object changes, the Share, Share Gap, and proposed EDR values count up/down to their new
 * targets (the other tiles update instantly, to avoid visual noise). Motion is suppressed under
 * prefers-reduced-motion and in environments without requestAnimationFrame.
 */
export default class DlKpiBand extends LightningElement {
  @api variant = "contract"; // "contract" | "term"
  @api currencyCode = "USD";
  @api heading;

  // Animated display values (percentage points). null = not yet painted / no data.
  _dispShare = null;
  _dispGap = null;
  _dispEdr = null;
  _hasPainted = false;
  _rafId = null;
  _tweenStart = null;
  _tweenFrom = null;
  _tweenTo = null;

  _kpis = null;
  @api
  get kpis() {
    return this._kpis;
  }
  set kpis(value) {
    const next = value || null;
    this._kpis = next;
    this._onKpisChange(next);
  }

  disconnectedCallback() {
    this._cancelTween();
  }

  get hasHeading() {
    return !!this.heading;
  }

  get bandClass() {
    return this.variant === "term"
      ? "dl-kpi-band dl-kpi-band_term slds-grid slds-wrap"
      : "dl-kpi-band dl-kpi-band_contract slds-grid slds-wrap";
  }

  get hasKpis() {
    return !!this._kpis;
  }

  // Build the tile view-models for the current variant + (possibly animating) display values.
  get tiles() {
    const k = this._kpis;
    if (!k) {
      return [];
    }
    const tiles = [];
    if (this.variant !== "term") {
      tiles.push(this._staticTile("ind-rev", "Industry Revenue", k.industryRevenue, "currency"));
      tiles.push(this._staticTile("host-rev", "Host Revenue", k.hostRevenue, "currency"));
      tiles.push(this._staticTile("ind-pax", "Industry Passengers", k.industryPassengers, "int"));
      tiles.push(this._staticTile("host-pax", "Host Passengers", k.hostPassengers, "int"));
    }
    tiles.push(this._shareTile(k));
    tiles.push(this._staticTile("fms", "FMS", k.fmsPts, "pct"));
    tiles.push(this._gapTile(k));
    tiles.push(this._edrTile(k));
    return tiles;
  }

  // ---------- tile builders ----------

  _staticTile(key, label, value, kind) {
    return {
      key,
      label,
      value: formatKpi(value, kind, this.currencyCode),
      hasDelta: false,
      caption: "",
      headline: false,
      deltaText: "",
      deltaClass: "dl-kpi-tile__delta",
      valueClass: "dl-kpi-tile__value"
    };
  }

  _shareTile(k) {
    const target = k.projectedSharePts;
    const disp = this._dispShare === null ? target : this._dispShare;
    const lift = target !== null && k.sharePts !== null ? round1(target - k.sharePts) : null;
    return {
      key: "share",
      label: "Share",
      value: formatKpi(disp, "pct"),
      hasDelta: lift !== null && Math.abs(lift) > 0.05,
      ...this._delta(lift, "lift"),
      caption: "",
      headline: true,
      valueClass: "dl-kpi-tile__value dl-kpi-tile__value_headline"
    };
  }

  _gapTile(k) {
    const target = k.projectedGapPts;
    const disp = this._dispGap === null ? target : this._dispGap;
    const closed = target !== null && target <= 0.05;
    const closing = k.gapPts !== null && target !== null && target < k.gapPts - 0.05;
    return {
      key: "gap",
      label: "Share Gap",
      value: formatKpi(disp, "pts"),
      hasDelta: !!(closed || closing),
      deltaText: closed ? "closed" : closing ? "closing" : "",
      deltaClass:
        "dl-kpi-tile__delta " +
        (toneOf(target, "gap") === "positive"
          ? "dl-kpi-tile__delta_positive"
          : "dl-kpi-tile__delta_negative"),
      caption: "",
      headline: true,
      valueClass:
        "dl-kpi-tile__value dl-kpi-tile__value_headline " +
        (toneOf(target, "gap") === "positive" ? "dl-kpi-tile__value_good" : "dl-kpi-tile__value_gap")
    };
  }

  _edrTile(k) {
    const target = k.edrCurrentPts;
    const disp = this._dispEdr === null ? target : this._dispEdr;
    const lift = k.edrLiftPts;
    return {
      key: "edr",
      label: "Proposed EDR",
      value: formatKpi(disp, "pct"),
      hasDelta: lift !== null && lift !== undefined && Math.abs(lift) > 0.05,
      ...this._delta(lift, "lift"),
      caption: "",
      headline: true,
      valueClass: "dl-kpi-tile__value dl-kpi-tile__value_headline"
    };
  }

  // Directional delta chip (caret + magnitude) for a signed pts value.
  _delta(value, kind) {
    if (value === null || value === undefined) {
      return { deltaText: "", deltaClass: "dl-kpi-tile__delta" };
    }
    const t = toneOf(value, kind);
    const caret = value > 0.05 ? "▲" : value < -0.05 ? "▼" : "";
    const cls =
      t === "positive"
        ? "dl-kpi-tile__delta_positive"
        : t === "negative"
          ? "dl-kpi-tile__delta_negative"
          : "";
    return {
      deltaText: caret ? `${caret} ${Math.abs(round1(value)).toFixed(1)} pts` : "",
      deltaClass: `dl-kpi-tile__delta ${cls}`
    };
  }

  // ---------- animation ----------

  _onKpisChange(next) {
    const targets = {
      share: next ? next.projectedSharePts : null,
      gap: next ? next.projectedGapPts : null,
      edr: next ? next.edrCurrentPts : null
    };
    if (!next || !this._hasPainted || this._reducedMotion || !this._canAnimate) {
      this._cancelTween();
      this._dispShare = targets.share;
      this._dispGap = targets.gap;
      this._dispEdr = targets.edr;
    } else {
      this._startTween(targets);
    }
    if (next) {
      this._hasPainted = true;
    }
  }

  _startTween(targets) {
    this._cancelTween();
    this._tweenFrom = { share: this._dispShare, gap: this._dispGap, edr: this._dispEdr };
    this._tweenTo = targets;
    this._tweenStart = null;
    // eslint-disable-next-line @lwc/lwc/no-async-operation
    this._rafId = requestAnimationFrame(this._step);
  }

  // Arrow fn so `this` binds to the component inside requestAnimationFrame.
  _step = (ts) => {
    if (this._tweenStart === null) {
      this._tweenStart = ts;
    }
    const p = Math.min(1, (ts - this._tweenStart) / ANIM_MS);
    const e = 1 - Math.pow(1 - p, 3); // ease-out cubic
    this._dispShare = this._lerp(this._tweenFrom.share, this._tweenTo.share, e);
    this._dispGap = this._lerp(this._tweenFrom.gap, this._tweenTo.gap, e);
    this._dispEdr = this._lerp(this._tweenFrom.edr, this._tweenTo.edr, e);
    if (p < 1) {
      // eslint-disable-next-line @lwc/lwc/no-async-operation
      this._rafId = requestAnimationFrame(this._step);
    } else {
      this._rafId = null;
    }
  };

  _lerp(from, to, e) {
    if (to === null || to === undefined) {
      return null;
    }
    if (from === null || from === undefined) {
      return to; // snap in when a value appears (e.g. EDR crossing from N/A to a number)
    }
    return round1(from + (to - from) * e);
  }

  _cancelTween() {
    if (this._rafId && this._canAnimate) {
      cancelAnimationFrame(this._rafId);
    }
    this._rafId = null;
  }

  // requestAnimationFrame is unavailable in some test environments (jsdom); guard so the band still
  // renders (snaps to target values) there.
  get _canAnimate() {
    return typeof requestAnimationFrame === "function" && typeof cancelAnimationFrame === "function";
  }

  get _reducedMotion() {
    try {
      return (
        typeof window !== "undefined" &&
        typeof window.matchMedia === "function" &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches
      );
    } catch {
      return false;
    }
  }
}
