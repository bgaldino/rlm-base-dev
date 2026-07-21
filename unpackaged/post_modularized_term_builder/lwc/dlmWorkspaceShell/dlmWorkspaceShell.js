import { LightningElement, api, track, wire } from "lwc";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import {
  publish,
  subscribe,
  unsubscribe,
  MessageContext,
  APPLICATION_SCOPE
} from "lightning/messageService";
import DLM_CHANNEL from "@salesforce/messageChannel/DLM_TermBuilderChannel__c";
import getBuilderState from "@salesforce/apex/RLM_DeltaTermBuilderController.getBuilderState";
import getQuoteLines from "@salesforce/apex/RLM_DeltaLineController.getQuoteLines";
import updateLineDiscountAndDates from "@salesforce/apex/RLM_DeltaLineController.updateLineDiscountAndDates";
import DlProposalSummary from "c/dlProposalSummary";
import {
  METHOD_PRODUCT,
  seedModel,
  computeTermKpis,
  aggregateKpis,
  finalOfferLineDiscounts,
  routeLabel,
  methodLabel
} from "c/dlDemoModel";

// This tile's name, stamped on every published message so it can ignore its own echoes.
const SOURCE = "dlmWorkspaceShell";

/**
 * Modularized Delta Term Builder — the always-mounted "workspace shell" tile.
 *
 * This is the modularized home for the parked negotiation-modeling workbench (see
 * docs/features/delta-negotiation-modeling-demo.md → "Round 2"). It hosts a lightning-tabset with
 * three tabs — Shell Creation (the existing c/dlmTermWorkspace), Modeling (c/dlmModelingWorkspace),
 * and a Performance placeholder — and, as always-visible chrome above the tabs, the contract-wide KPI
 * band + a Proposal Summary action.
 *
 * Ownership (the decided architecture): the SHELL owns the per-Term demo model cache
 * (`_modelsByTermId`, keyed `${termId}::${method}`) and the contract-level KPI aggregation. It must,
 * because the always-visible contract band aggregates across EVERY Term — including Terms the analyst
 * has never opened in the Modeling tab — which only the always-mounted shell can hold. The
 * c/dlmModelingWorkspace tab is a controlled presentational wrapper (props down, events up): it never
 * holds the cache. This mirrors the monolith c/dlTermBuilder orchestrator/grid relationship.
 *
 * The five `dl*` bundles it consumes (dlDemoModel, dlKpiBand, dlModelingGrid, dlProposalSummary via
 * the wrapper) live in post_term_builder/lwc and are reused verbatim in place — never copied here
 * (that would create duplicate c/* components and a deploy conflict).
 *
 * LMC: the shell owns NO account/quote/term selection UI (that's c/dlmNegotiationContext +
 * c/dlmTermsRail). It learns the open negotiation from `context`, the chosen Term from
 * `termSelected` / `termsChanged`, and reloads on `linesChanged` / `fareAdded` / `contractCreated`.
 * It publishes `linesChanged` after an Apply-Final-Offer write-back so the other tiles refetch.
 *
 * All modeled numbers are mock, deterministic, and client-only (see c/dlDemoModel). The single server
 * write is the reused RLM_DeltaLineController.updateLineDiscountAndDates; getBuilderState +
 * getQuoteLines are read-only.
 */
export default class DlmWorkspaceShell extends LightningElement {
  // Design-time configuration (see .js-meta.xml). Left undefined unless the admin sets them so the
  // getters can treat "unset" as on-by-default without tripping the LWC boolean-default-true lint rule.
  @api headingLabel;
  @api showContractBand;
  @api showProposalAction;
  @api shellCreationLabel;
  @api modelingLabel;
  @api performanceLabel;

  @track terms = [];

  quoteId;
  selectedTermId;
  quoteName = "";
  accountName = "";
  currencyCode = "USD";

  // Which tab is active ("creation" | "modeling" | "performance"). Shell Creation is the default.
  activeTab = "creation";

  // Per-(term, method) client-only demo model cache, keyed `${termId}::${method}`; seeded lazily,
  // pruned on refresh, cleared on quote/account switch. The shell — not the Modeling tab — owns it.
  _modelsByTermId = {};
  selectedMethod = METHOD_PRODUCT;
  // Reactive mirror of the selected Term + method's model, handed to the Modeling workspace.
  @track activeModel = null;
  // When the Modeling tab requests it, the workspace expands (the host page can react via the event).
  workspaceExpanded = false;
  applyingOffer = false;
  loadingState = false;
  errorMessage = "";

  // line id → prior-cycle discount %, harvested from getQuoteLines. Enriches term.fares[*].priorDiscount
  // before seeding so the modeling grid can show a read-only Prior Discount column. getBuilderState's
  // fare payload doesn't carry it, so this is the (read-only, no-Apex-change) source.
  _priorByLineId = {};

  _subscription = null;

  @wire(MessageContext)
  messageContext;

  connectedCallback() {
    this._subscribe();
  }

  disconnectedCallback() {
    this._unsubscribe();
  }

  // ---------- LMC wiring ----------

  _subscribe() {
    if (this._subscription) {
      return;
    }
    this._subscription = subscribe(
      this.messageContext,
      DLM_CHANNEL,
      (message) => this.handleMessage(message),
      { scope: APPLICATION_SCOPE }
    );
  }

  _unsubscribe() {
    if (this._subscription) {
      unsubscribe(this._subscription);
      this._subscription = null;
    }
  }

  handleMessage(message) {
    if (!message || message.source === SOURCE) {
      return;
    }
    switch (message.type) {
      case "context":
        // A different negotiation was opened/created: adopt it, abandon the prior quote's client-only
        // demo models, and reload. A repeat of the current quote (e.g. a header date edit) is ignored.
        if (message.quoteId && message.quoteId !== this.quoteId) {
          this.quoteId = message.quoteId;
          this.selectedTermId = null;
          this._resetDemoModels();
          this.loadState();
        }
        break;
      case "termSelected":
        // The rail selected a Term that already exists in our loaded set: adopt it and point the
        // active model at it (seeding on demand). No refetch needed.
        if (message.quoteId === this.quoteId) {
          this.selectedTermId = message.selectedTermId || null;
          this._syncActiveModel();
        }
        break;
      case "termsChanged":
        // A Term was just added: adopt the newest selection and refetch (our term set is stale).
        if (message.quoteId === this.quoteId) {
          this.selectedTermId = message.selectedTermId || this.selectedTermId;
          this.loadState();
        }
        break;
      case "linesChanged":
      case "fareAdded":
      case "contractCreated":
        // Line data / fares / downstream state changed elsewhere: refetch. A fare change means new
        // backing rows, so loadState reseeds the affected Term's model from the refreshed payload.
        if (message.quoteId === this.quoteId) {
          this.loadState(message.type === "fareAdded" ? this.selectedTermId : null);
        }
        break;
      default:
        break;
    }
  }

  _publishLinesChanged() {
    publish(this.messageContext, DLM_CHANNEL, {
      type: "linesChanged",
      quoteId: this.quoteId,
      source: SOURCE
    });
  }

  // ---------- state load + prior-discount enrichment ----------

  // Reload the shell's own view of the negotiation: getBuilderState (terms + quote + currency) and
  // getQuoteLines (prior-discount enrichment). When reseedTermId is set (a fare was added), that
  // Term's cached models are dropped so they re-seed from the refreshed, enriched payload.
  async loadState(reseedTermId) {
    if (!this.quoteId) {
      return;
    }
    this.loadingState = true;
    this.errorMessage = "";
    try {
      const [stateRes, linesRes] = await Promise.all([
        getBuilderState({ quoteId: this.quoteId }).then((j) => this._parse(j)),
        getQuoteLines({ quoteId: this.quoteId })
          .then((j) => this._parse(j))
          .catch(() => ({}))
      ]);
      if (stateRes.isSuccess === false) {
        this.errorMessage = stateRes.errorMessage || "Unable to load the negotiation.";
        return;
      }
      const quote = stateRes.quote || {};
      this.quoteName = quote.name || this.quoteName;
      this.accountName = quote.accountName || this.accountName;
      this.currencyCode =
        stateRes.currencyCode || quote.currencyCode || this.currencyCode || "USD";

      // Harvest prior discounts before enriching so the seed sees them.
      this._priorByLineId = this._collectPriorDiscounts(linesRes);
      const terms = this._enrichTerms(stateRes.terms || []);
      this.terms = terms;

      // Drop models for Terms that no longer exist, then (if a fare was added) drop the edited Term's
      // models so they re-seed with the new backing fare.
      this._pruneDemoModels();
      if (reseedTermId) {
        this._reseedModelsForTerm(reseedTermId);
      }

      // Resolve the selection: keep the current Term if still present, else fall back to the server
      // default / first. (The rail owns selection, but the shell needs a resolved id for activeModel.)
      const ids = new Set(this.terms.map((t) => t.id));
      if (!this.selectedTermId || !ids.has(this.selectedTermId)) {
        this.selectedTermId =
          stateRes.selectedTermId || (this.terms[0] && this.terms[0].id) || null;
      }
      this._syncActiveModel();
    } catch (e) {
      this.errorMessage = this._errMessage(e);
    } finally {
      this.loadingState = false;
    }
  }

  // Flatten the nested getQuoteLines tree ({ groups:[{ lines, children }], ungrouped }) into a
  // line id → priorDiscount map. Walks group lines + nested child groups + ungrouped lines.
  _collectPriorDiscounts(linesRes) {
    const map = {};
    if (!linesRes) {
      return map;
    }
    const takeLines = (lines) => {
      (lines || []).forEach((l) => {
        if (l && l.id !== undefined && l.id !== null) {
          map[l.id] = l.priorDiscount;
        }
      });
    };
    const walkGroup = (g) => {
      if (!g) {
        return;
      }
      takeLines(g.lines);
      (g.children || []).forEach(walkGroup);
    };
    (linesRes.groups || []).forEach(walkGroup);
    takeLines(linesRes.ungrouped);
    return map;
  }

  // Copy each Term's fares with priorDiscount filled from the harvested map (when the line was found).
  // Returns fresh objects so seeding sees the enriched fares; leaves getBuilderState's shape otherwise
  // untouched, and only sets priorDiscount when we actually have a value for that line id.
  _enrichTerms(terms) {
    const prior = this._priorByLineId;
    return terms.map((t) => {
      const fares = (t.fares || []).map((f) => {
        const p = prior[f.id];
        return p === undefined ? f : { ...f, priorDiscount: p };
      });
      return { ...t, fares };
    });
  }

  // ---------- demo modeling: KPIs ----------

  // Per-Term KPI objects for every Term (baseline flown data + the active-method model's current
  // round). Terms without a seeded model still get baseline KPIs (seeded on demand), so the contract
  // band is populated even before the analyst opens the Modeling tab.
  get _termKpiList() {
    return this.terms.map((t) => computeTermKpis(t, this._modelFor(t, this.selectedMethod)));
  }

  get contractKpis() {
    return aggregateKpis(this._termKpiList);
  }

  get selectedTermKpis() {
    const t = this.selectedTerm;
    return t ? computeTermKpis(t, this._modelFor(t, this.selectedMethod)) : null;
  }

  // ---------- getters: selection, tabs, visibility ----------

  get selectedTerm() {
    return this.terms.find((t) => t.id === this.selectedTermId) || null;
  }

  get hasQuote() {
    return !!this.quoteId;
  }

  get hasTerms() {
    return this.terms.length > 0;
  }

  get effectiveHeading() {
    return this.headingLabel || "Negotiation Workbench";
  }

  get contractBandVisible() {
    return this.showContractBand !== false;
  }

  get proposalActionVisible() {
    return this.showProposalAction !== false;
  }

  get hasContractKpis() {
    return this.hasTerms;
  }

  get shellCreationTabLabel() {
    return this.shellCreationLabel || "Shell Creation";
  }

  get modelingTabLabel() {
    return this.modelingLabel || "Modeling";
  }

  get performanceTabLabel() {
    return this.performanceLabel || "Performance";
  }

  get proposalDisabled() {
    return !this.quoteId || !this.hasTerms;
  }

  get applyOfferDisabled() {
    return !this.quoteId || !this.activeModel || this.applyingOffer;
  }

  handleTabActive(event) {
    const value = event.target && event.target.value;
    this.activeTab = value || "creation";
  }

  // ---------- events up from the Modeling workspace ----------

  // The grid recomputed its model after an edit → adopt it, so the KPI getters (and the contract band
  // they feed) recompute + animate. The grid coalesces edits, so this fires at most once per frame.
  handleModelChange(event) {
    const { termId, method, model } = event.detail;
    if (!termId || !model) {
      return;
    }
    this._modelsByTermId[this._modelKey(termId, method)] = model;
    if (termId === this.selectedTermId && method === this.selectedMethod) {
      this.activeModel = model;
    }
  }

  // The grid's method toggle flipped → swap in (seed if needed) that method's model for the Term.
  handleMethodChange(event) {
    const { termId, method } = event.detail;
    if (!termId || termId !== this.selectedTermId) {
      return;
    }
    this.selectedMethod = method;
    this._syncActiveModel();
  }

  handleExpandToggle(event) {
    this.workspaceExpanded = !!event.detail.expanded;
  }

  handleResetModel() {
    this._resetDemoModels();
    this._syncActiveModel();
    this._toast("Demo model reset", "Modeled rounds were cleared for this session.", "info");
  }

  // The Modeling workspace's "Apply Final Offer to Quote" button. Applies the active Term's Final
  // Offer discounts to its backing Quote fare lines via the reused line-update Apex (no new Apex).
  // Product rows map 1:1; Fare-Class rows roll up to the parent fare line (spend-weighted, in the
  // demo model). Then broadcast linesChanged so the other tiles refetch the now-persisted values,
  // ready for the existing Create Contract handoff.
  async handleApplyOfferRequest() {
    if (this.applyOfferDisabled) {
      return;
    }
    const lines = finalOfferLineDiscounts(this.activeModel);
    if (!lines.length) {
      this._toast(
        "Nothing to apply",
        "The Final Offer has no rows backed by a Quote fare line.",
        "info"
      );
      return;
    }
    this.applyingOffer = true;
    this.errorMessage = "";
    try {
      const res = this._parse(
        await updateLineDiscountAndDates({
          inputJson: JSON.stringify({ quoteId: this.quoteId, lines })
        })
      );
      if (res.isSuccess === false) {
        this.errorMessage = res.errorMessage || "Unable to apply the Final Offer.";
        return;
      }
      const updatedCount = res.updatedCount || lines.length;
      this._toast(
        "Final Offer applied",
        `Updated ${updatedCount} fare line${updatedCount === 1 ? "" : "s"}.`,
        "success"
      );
      // Refetch our own state, then tell the other tiles their line data changed.
      await this.loadState();
      this._publishLinesChanged();
    } catch (e) {
      this.errorMessage = this._errMessage(e);
    } finally {
      this.applyingOffer = false;
    }
  }

  // ---------- proposal summary ----------

  // Open the on-screen proposal summary. Projects each Term at its own model's FINAL OFFER round (not
  // the live current round), so the summary reflects the recommended offer regardless of which round
  // currently drives the live bands.
  async handleOpenProposal() {
    if (this.proposalDisabled) {
      return;
    }
    const perTermForContract = [];
    const termRows = this.terms.map((t) => {
      const model = this._modelFor(t, this.selectedMethod);
      const finalRound = model ? model.finalOfferRoundIndex : undefined;
      const kpi = computeTermKpis(t, model, finalRound);
      perTermForContract.push(kpi);
      return {
        termId: t.id,
        route: routeLabel(t),
        method: model ? model.method : this.selectedMethod,
        methodLabel: methodLabel(model ? model.method : this.selectedMethod),
        statusLabel: model
          ? (model.roundStatuses || [])[model.finalOfferRoundIndex] || "Draft"
          : "Draft",
        isRecommended: t.id === this.selectedTermId,
        sharePts: kpi.sharePts,
        fmsPts: kpi.fmsPts,
        projectedSharePts: kpi.projectedSharePts,
        projectedGapPts: kpi.projectedGapPts,
        edrExistingPts: kpi.edrExistingPts,
        edrFinalOfferPts: kpi.edrCurrentPts // computed at the final-offer round above
      };
    });
    const proposal = {
      negotiationName: this.quoteName,
      accountName: this.accountName,
      currencyCode: this.currencyCode,
      contract: aggregateKpis(perTermForContract),
      terms: termRows
    };
    try {
      await DlProposalSummary.open({
        size: "large",
        label: "Proposal Summary",
        proposal
      });
    } catch (e) {
      this.errorMessage = this._errMessage(e);
    }
  }

  // ---------- model lifecycle helpers (owned here, mirrored from the monolith orchestrator) ----------

  _modelKey(termId, method) {
    return `${termId}::${method}`;
  }

  // Get the model for a (term, method), seeding it on demand. Returns a live reference held in the map.
  _modelFor(term, method) {
    if (!term || !term.id) {
      return null;
    }
    const key = this._modelKey(term.id, method);
    if (!this._modelsByTermId[key]) {
      this._modelsByTermId[key] = seedModel(term, method);
    }
    return this._modelsByTermId[key];
  }

  // Point activeModel at the selected Term + method's model (seeding if needed) so the workspace grid
  // + bands stay in sync after a selection, method flip, or refresh.
  _syncActiveModel() {
    const t = this.selectedTerm;
    this.activeModel = t ? this._modelFor(t, this.selectedMethod) : null;
  }

  // Drop all models for one Term (both methods) so they re-seed from the updated term payload.
  _reseedModelsForTerm(termId) {
    Object.keys(this._modelsByTermId).forEach((key) => {
      if (key.startsWith(`${termId}::`)) {
        delete this._modelsByTermId[key];
      }
    });
  }

  // Remove models whose Term no longer exists after a state refresh.
  _pruneDemoModels() {
    const ids = new Set(this.terms.map((t) => t.id));
    Object.keys(this._modelsByTermId).forEach((key) => {
      const termId = key.split("::")[0];
      if (!ids.has(termId)) {
        delete this._modelsByTermId[key];
      }
    });
  }

  // Clear all demo models (quote/account switch, or explicit reset).
  _resetDemoModels() {
    this._modelsByTermId = {};
    this.activeModel = null;
    this.selectedMethod = METHOD_PRODUCT;
    this.workspaceExpanded = false;
  }

  // ---------- helpers ----------

  _parse(json) {
    try {
      return json ? JSON.parse(json) : {};
    } catch {
      return { isSuccess: false, errorMessage: "Unexpected response from server." };
    }
  }

  _errMessage(e) {
    return (e && e.body && e.body.message) || (e && e.message) || "Unexpected error.";
  }

  _toast(title, message, variant) {
    this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
  }
}
