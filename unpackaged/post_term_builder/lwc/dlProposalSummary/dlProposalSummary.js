import { api } from "lwc";
import LightningModal from "lightning/modal";
import { formatKpi, pct1, pts } from "c/dlDemoModel";

/**
 * dlProposalSummary — an on-screen (LightningModal) rollup of the modeled negotiation.
 *
 * Opened from the Term Builder header with:
 *   DlProposalSummary.open({ size: 'large', label, proposal })
 * where `proposal` = {
 *   negotiationName, accountName, currencyCode,
 *   contract: <aggregate KPI object>,
 *   terms: [{ termId, route, method, methodLabel, statusLabel, isRecommended,
 *             sharePts, fmsPts, projectedSharePts, projectedGapPts,
 *             edrExistingPts, edrFinalOfferPts }]
 * }
 *
 * Presentational only — it reads the already-computed demo model and formats it. No export in this
 * phase (CSV/PDF deferred); the analyst reviews the recommended Final Offer here, then closes and uses
 * the header's Apply Final Offer / Create Contract actions to hand it off.
 */
export default class DlProposalSummary extends LightningModal {
  @api proposal;

  get hasProposal() {
    return !!(this.proposal && this.proposal.contract);
  }

  get negotiationName() {
    return (this.proposal && this.proposal.negotiationName) || "Negotiation";
  }

  get accountName() {
    return (this.proposal && this.proposal.accountName) || "";
  }

  get currencyCode() {
    return (this.proposal && this.proposal.currencyCode) || "USD";
  }

  // Contract-level KPI rollup tiles.
  get contractTiles() {
    const c = this.proposal && this.proposal.contract;
    if (!c) {
      return [];
    }
    return [
      { key: "share", label: "Projected Share", value: pct1(c.projectedSharePts), tone: "" },
      { key: "fms", label: "FMS", value: pct1(c.fmsPts), tone: "" },
      {
        key: "gap",
        label: "Projected Gap",
        value: pts(c.projectedGapPts),
        tone: c.projectedGapPts !== null && c.projectedGapPts <= 0.05 ? "good" : "gap"
      },
      { key: "edr-ex", label: "Existing EDR", value: pct1(c.edrExistingPts), tone: "" },
      { key: "edr-cur", label: "Final Offer EDR", value: pct1(c.edrCurrentPts), tone: "" },
      {
        key: "host-rev",
        label: "Projected Host Revenue",
        value: formatKpi(c.projectedHostRevenue, "currency", this.currencyCode),
        tone: ""
      }
    ];
  }

  // Per-term rows for the summary table.
  get termRows() {
    const terms = (this.proposal && this.proposal.terms) || [];
    return terms.map((t) => ({
      key: t.termId,
      route: t.route || "—",
      methodLabel: t.methodLabel,
      statusLabel: t.statusLabel || "Draft",
      share: pct1(t.sharePts),
      fms: pct1(t.fmsPts),
      projectedShare: pct1(t.projectedSharePts),
      gap: pts(t.projectedGapPts),
      gapClass:
        t.projectedGapPts !== null && t.projectedGapPts <= 0.05
          ? "dl-ps-gap dl-ps-gap_good"
          : "dl-ps-gap dl-ps-gap_open",
      edrExisting: pct1(t.edrExistingPts),
      edrFinal: pct1(t.edrFinalOfferPts),
      recommendedClass: t.isRecommended ? "dl-ps-row dl-ps-row_recommended" : "dl-ps-row",
      isRecommended: !!t.isRecommended
    }));
  }

  get hasTerms() {
    return this.termRows.length > 0;
  }

  get contractTileClass() {
    return "dl-ps-tile";
  }

  handleClose() {
    this.close({ status: "close" });
  }
}
