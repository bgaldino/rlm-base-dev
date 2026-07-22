import { LightningElement, api, wire, track } from "lwc";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import { getRecord, getFieldValue, updateRecord } from "lightning/uiRecordApi";
import { getPicklistValues } from "lightning/uiObjectInfoApi";
import ID_FIELD from "@salesforce/schema/Quote.Id";
import ANALYSIS_START from "@salesforce/schema/Quote.DL_AnalysisPeriodStart__c";
import ANALYSIS_END from "@salesforce/schema/Quote.DL_AnalysisPeriodEnd__c";
import CARRIERS from "@salesforce/schema/Quote.DL_ParticipatingCarriers__c";
import ACCOUNT_NAME from "@salesforce/schema/Account.Name";

const QUOTE_FIELDS = [ANALYSIS_START, ANALYSIS_END, CARRIERS];
// Quote carries no record types in this app, so the picklist reads against the master record type.
const MASTER_RECORD_TYPE_ID = "012000000000000AAA";
// MultiselectPicklist values round-trip as a ';'-delimited string via uiRecordApi.
const MS_DELIM = ";";
const DAY_MS = 24 * 60 * 60 * 1000;

/**
 * Modularized Delta Term Builder — the "Configure Data Set" pre-term panel (Shell Creation tab).
 *
 * Captures Wesley M's "Pre-Term Building Requirements" BEFORE term building begins:
 *   - Analysis Period (Quote.DL_AnalysisPeriodStart__c / DL_AnalysisPeriodEnd__c) — DRIVES the
 *     analytics. Pre-filled today → today + 1yr when unset. Its length yields a `periodFactor`
 *     (days / 365, clamped ≥ 0) the shell uses to scale the fabricated absolute KPI magnitudes.
 *   - Participating (partner) Carriers (Quote.DL_ParticipatingCarriers__c multiselect) — capture &
 *     surface only; the shell shows them as chips above the Modeling grid, never as grid rows.
 *   - Subsidiary Accounts — CLIENT-ONLY scope, pulled live from the native Account hierarchy
 *     (direct children of the negotiation's Account). NOT persisted to the Quote.
 *
 * A CONTROLLED CHILD of c/dlmWorkspaceShell (props down, events up), mirroring c/dlmModelingWorkspace.
 * It does its own I/O through STANDARD uiRecordApi — getRecord / updateRecord for the three Quote
 * fields and a lightning-record-picker for subsidiaries — so it never touches
 * RLM_DeltaTermBuilderController or the LMC. It emits a composed `configchange` on load and on every
 * change/save; the shell consumes it to re-scale the KPI bands and re-pass the carriers.
 *
 * `Date` is used here (allowed in an LWC) ONLY to compute the period factor + the today→+1yr default;
 * the deterministic c/dlDemoModel engine stays Date-free and receives the factor as a plain number.
 */
export default class DlmDataSetConfig extends LightningElement {
  @api quoteId;
  @api accountId;

  @track startDate;
  @track endDate;
  @track selectedCarriers = [];
  // Client-only subsidiary scope (never written to the Quote): parallel id list + {id,label} chips.
  @track subsidiaryIds = [];
  @track subsidiaryChips = [];

  carrierOptions = [];
  expanded = true;
  saving = false;
  errorMessage = "";
  // Guards so we pre-fill / adopt the persisted period exactly once, and only auto-collapse on first
  // load of an already-configured Quote.
  _prefilled = false;
  _appliedRecord = false;
  // The most recently picked subsidiary account id, resolved to a name by a single-record wire.
  _pendingSubsidiaryId;

  // ---------- wires ----------

  @wire(getRecord, { recordId: "$quoteId", fields: QUOTE_FIELDS })
  wiredQuote({ data, error }) {
    if (data) {
      // Clear any transient read error (e.g. LDS not-yet-cached miss on a just-created renewal quote):
      // the record loaded, so a stale banner from an earlier emission must not linger.
      this.errorMessage = "";
      const start = getFieldValue(data, ANALYSIS_START);
      const end = getFieldValue(data, ANALYSIS_END);
      const carriers = getFieldValue(data, CARRIERS);
      this.selectedCarriers = carriers
        ? `${carriers}`.split(MS_DELIM).filter(Boolean)
        : [];
      if (start || end) {
        // Already configured: adopt the persisted period and start collapsed.
        this.startDate = start || null;
        this.endDate = end || null;
        if (!this._appliedRecord) {
          this.expanded = false;
        }
      } else if (!this._prefilled) {
        // Fresh negotiation: default the period to today → +1yr (unsaved until the analyst hits Save).
        this._prefillPeriod();
      }
      this._appliedRecord = true;
      // Publish the initial factor + carriers so the KPI bands scale from first render.
      this._emitConfig();
    } else if (error) {
      this.errorMessage = this._errMessage(error);
    }
  }

  @wire(getPicklistValues, {
    recordTypeId: MASTER_RECORD_TYPE_ID,
    fieldApiName: CARRIERS
  })
  wiredCarrierPicklist({ data }) {
    if (data) {
      this.carrierOptions = (data.values || []).map((v) => ({
        label: v.label,
        value: v.value
      }));
    }
  }

  // Resolve each picked subsidiary account to its Name, then add it as a removable client-only chip.
  @wire(getRecord, { recordId: "$_pendingSubsidiaryId", fields: [ACCOUNT_NAME] })
  wiredSubsidiary({ data }) {
    const id = this._pendingSubsidiaryId;
    if (data && id && !this.subsidiaryIds.includes(id)) {
      const label = getFieldValue(data, ACCOUNT_NAME) || id;
      this.subsidiaryIds = [...this.subsidiaryIds, id];
      this.subsidiaryChips = [...this.subsidiaryChips, { id, label }];
      this._emitConfig();
    }
  }

  // ---------- derived state ----------

  // Analysis-period factor: fraction of a year the period spans (days / 365), clamped ≥ 0. Defaults to
  // 1 (no scaling) when either bound is blank/unparseable, so the shell + engine stay back-compatible.
  get periodFactor() {
    const s = this._parseDate(this.startDate);
    const e = this._parseDate(this.endDate);
    if (s === null || e === null) {
      return 1;
    }
    const factor = (e - s) / DAY_MS / 365;
    return Number.isFinite(factor) && factor >= 0 ? factor : 1;
  }

  get hasCarrierOptions() {
    return this.carrierOptions.length > 0;
  }

  get hasSubsidiaries() {
    return this.subsidiaryChips.length > 0;
  }

  get subsidiaryFilter() {
    return this.accountId
      ? {
          criteria: [
            { fieldPath: "ParentId", operator: "eq", value: this.accountId }
          ]
        }
      : undefined;
  }

  get subsidiaryPickerDisabled() {
    return !this.accountId;
  }

  get accountMatchingInfo() {
    return { primaryField: { fieldPath: "Name" } };
  }

  get accountDisplayInfo() {
    return { primaryField: "Name" };
  }

  get toggleLabel() {
    return this.expanded ? "Hide" : "Configure Data Set";
  }

  get toggleIcon() {
    return this.expanded ? "utility:chevrondown" : "utility:chevronright";
  }

  get saveDisabled() {
    return this.saving || !this.quoteId;
  }

  // ---------- handlers ----------

  handleToggle() {
    this.expanded = !this.expanded;
  }

  handleStartChange(event) {
    this.startDate = event.detail.value || null;
    this._emitConfig();
  }

  handleEndChange(event) {
    this.endDate = event.detail.value || null;
    this._emitConfig();
  }

  handleCarrierChange(event) {
    this.selectedCarriers = event.detail.value || [];
    this._emitConfig();
  }

  handleSubsidiarySelect(event) {
    const recordId = event.detail && event.detail.recordId;
    if (recordId && !this.subsidiaryIds.includes(recordId)) {
      // The name resolves via the $_pendingSubsidiaryId wire, which then pushes the chip.
      this._pendingSubsidiaryId = recordId;
    }
    // Clear the picker so the next child can be chosen.
    const picker = this.refs && this.refs.subsidiaryPicker;
    if (picker && picker.clearSelection) {
      picker.clearSelection();
    }
  }

  handleRemoveSubsidiary(event) {
    const id = event.currentTarget.dataset.id;
    this.subsidiaryIds = this.subsidiaryIds.filter((x) => x !== id);
    this.subsidiaryChips = this.subsidiaryChips.filter((c) => c.id !== id);
    this._emitConfig();
  }

  async handleSave() {
    if (this.saveDisabled) {
      return;
    }
    this.saving = true;
    this.errorMessage = "";
    const fields = {};
    fields[ID_FIELD.fieldApiName] = this.quoteId;
    fields[ANALYSIS_START.fieldApiName] = this.startDate || null;
    fields[ANALYSIS_END.fieldApiName] = this.endDate || null;
    // Subsidiaries are deliberately NOT written — they are client-only scope this round.
    fields[CARRIERS.fieldApiName] = this.selectedCarriers.join(MS_DELIM);
    try {
      await updateRecord({ fields });
      this.expanded = false;
      this._emitConfig();
      this._toast(
        "Data set saved",
        "Analysis period and participating carriers saved to the negotiation.",
        "success"
      );
    } catch (e) {
      this.errorMessage = this._errMessage(e);
    } finally {
      this.saving = false;
    }
  }

  // ---------- helpers ----------

  _emitConfig() {
    this.dispatchEvent(
      new CustomEvent("configchange", {
        bubbles: true,
        composed: true,
        detail: {
          periodFactor: this.periodFactor,
          analysisStartDate: this.startDate || null,
          analysisEndDate: this.endDate || null,
          carriers: [...this.selectedCarriers],
          subsidiaryAccountIds: [...this.subsidiaryIds]
        }
      })
    );
  }

  _prefillPeriod() {
    this._prefilled = true;
    const today = new Date();
    const plusYear = new Date(
      today.getFullYear() + 1,
      today.getMonth(),
      today.getDate()
    );
    this.startDate = this._toIsoDate(today);
    this.endDate = this._toIsoDate(plusYear);
  }

  _toIsoDate(d) {
    const mm = `${d.getMonth() + 1}`.padStart(2, "0");
    const dd = `${d.getDate()}`.padStart(2, "0");
    return `${d.getFullYear()}-${mm}-${dd}`;
  }

  // Parse a "YYYY-MM-DD" date input value to epoch ms; null when blank/unparseable.
  _parseDate(value) {
    if (!value) {
      return null;
    }
    const ms = Date.parse(value);
    return Number.isFinite(ms) ? ms : null;
  }

  _errMessage(e) {
    return (
      (e && e.body && e.body.message) || (e && e.message) || "Unexpected error."
    );
  }

  _toast(title, message, variant) {
    this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
  }
}
