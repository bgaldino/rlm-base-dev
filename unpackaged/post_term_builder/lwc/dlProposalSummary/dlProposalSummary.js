import { api } from "lwc";
import LightningModal from "lightning/modal";
import {
  formatKpi,
  pct1,
  pts,
  toProposalCsvSummary,
  toProposalCsvDetailed
} from "c/dlDemoModel";

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
 * Presentational + client-only exports: the analyst reviews the recommended Final Offer here and can
 * export it three ways — Summary CSV, Detailed CSV (per-Term grid rows at each Term's final-offer
 * round), and Print / Save as PDF (browser print of the modal). The header's Apply Final Offer /
 * Create Contract actions perform the actual write-back. `proposal.models` (termId → demo model) is
 * passed by the shell and feeds the Detailed CSV.
 */
export default class DlProposalSummary extends LightningModal {
  @api proposal;

  get hasProposal() {
    return !!(this.proposal && this.proposal.contract);
  }

  // Export buttons are disabled until there's a modeled proposal to export.
  get hasNoProposal() {
    return !this.hasProposal;
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

  // ---------- exports ----------

  handleDownloadSummary() {
    this._download(this._fileBase("summary"), toProposalCsvSummary(this.proposal));
  }

  handleDownloadDetailed() {
    const models = (this.proposal && this.proposal.models) || {};
    this._download(
      this._fileBase("detailed"),
      toProposalCsvDetailed(this.proposal, models)
    );
  }

  // Browser print → Save as PDF. The scoped @media print block widens the table and hides the
  // action buttons; hiding the surrounding Lightning chrome is environment-dependent (verified live).
  handlePrint() {
    window.print();
  }

  // Sanitize the negotiation name into a filename stem, e.g. "Delta ATL-LHR" → delta-atl-lhr-summary.csv
  _fileBase(kind) {
    const stem = `${this.negotiationName || "proposal"}`
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 60);
    return `${stem || "proposal"}-${kind}.csv`;
  }

  // Trigger a client-side CSV download via Blob + object URL + a transient anchor. Prepend a UTF-8
  // BOM (U+FEFF) so Excel opens the file as UTF-8 (renders the em-dash and arrow glyphs correctly).
  _download(filename, csv) {
    const blob = new Blob(["﻿", csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.style.display = "none";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  handleClose() {
    this.close({ status: "close" });
  }
}
