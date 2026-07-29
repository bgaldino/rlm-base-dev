import { LightningElement, api, wire, track } from "lwc";
import { getRecord, getFieldValue } from "lightning/uiRecordApi";
import getProspectData from "@salesforce/apex/RLM_HomeServices_ProspectValueCardCtrl.getProspectData";
import { resolveProductImageUrl } from "c/rlmHomeServicesImageUrl";

import ACCOUNT_NAME_FIELD from "@salesforce/schema/Account.Name";
import ACCOUNT_PHONE_FIELD from "@salesforce/schema/Account.Phone";

// Only standard fields in the wire — custom RLM fields come through Apex
const ACCOUNT_FIELDS = [ACCOUNT_NAME_FIELD, ACCOUNT_PHONE_FIELD];

const STAGE_LABELS = [
  "New Inquiry",
  "On-site Assessment",
  "Contracted",
  "Active Customer"
];

export default class RlmHomeServicesProspectValueCard extends LightningElement {
  @api recordId;

  @wire(getRecord, { recordId: "$recordId", fields: ACCOUNT_FIELDS })
  account;

  @track _prospectData = {};

  @wire(getProspectData, { accountId: "$recordId" })
  wiredProspectData({ data, error }) {
    if (data) {
      this._prospectData = data;
    } else if (error) {
      console.error(
        "rlmHomeServicesProspectValueCard: getProspectData error",
        error
      );
      this._prospectData = {};
    }
  }

  // ── Account fields ────────────────────────────────────────────────────────

  get fullName() {
    const first = this._prospectData.firstName;
    const last = this._prospectData.lastName;
    if (first || last) {
      return [first, last].filter(Boolean).join(" ");
    }
    return getFieldValue(this.account.data, ACCOUNT_NAME_FIELD) || "";
  }

  get initials() {
    const first = this._prospectData.firstName || "";
    const last = this._prospectData.lastName || "";
    if (first || last) {
      return (first.charAt(0) + last.charAt(0)).toUpperCase();
    }
    const name = getFieldValue(this.account.data, ACCOUNT_NAME_FIELD) || "";
    const parts = name.trim().split(/\s+/);
    return parts.length > 1
      ? (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase()
      : name.substring(0, 2).toUpperCase();
  }

  get email() {
    return this._prospectData.email || "";
  }

  get phone() {
    return getFieldValue(this.account.data, ACCOUNT_PHONE_FIELD) || "";
  }

  // ── Value stats ───────────────────────────────────────────────────────────

  get monthlyValue() {
    return this._prospectData.opportunityAmount || 0;
  }

  get annualValue() {
    return this.monthlyValue * 12;
  }

  get ltv() {
    return this.monthlyValue * 36;
  }

  // ── Journey stage ─────────────────────────────────────────────────────────

  get journeyStageIndex() {
    if (this._prospectData.hasOrders) return 3;
    if (this._prospectData.hasContracts) return 2;
    const stage = (this._prospectData.opportunityStage || "").toLowerCase();
    if (stage === "closed won") return 2;
    if (this._prospectData.lineItems && this._prospectData.lineItems.length > 0)
      return 1;
    return 0;
  }

  get journeySteps() {
    const active = this.journeyStageIndex;
    return STAGE_LABELS.map((label, i) => {
      const isComplete = i < active;
      const isActive = i === active;
      const isLast = i === STAGE_LABELS.length - 1;
      let nodeClass = "stage-node";
      if (isComplete) nodeClass += " stage-node_complete";
      else if (isActive) nodeClass += " stage-node_active";
      const labelClass = isActive
        ? "stage-label stage-label_active"
        : "stage-label";
      return {
        label,
        key: label,
        isComplete,
        isActive,
        isUpcoming: i > active,
        isLast,
        nodeClass,
        labelClass
      };
    });
  }

  // ── Service tiles ─────────────────────────────────────────────────────────

  get hasLineItems() {
    return (
      this._prospectData.lineItems && this._prospectData.lineItems.length > 0
    );
  }

  get lineItemsWithImage() {
    if (!this._prospectData.lineItems) return [];
    return this._prospectData.lineItems.map((item) => {
      const imageUrl = resolveProductImageUrl(item.displayUrl);
      return {
        ...item,
        key: item.lineItemId,
        imageUrl,
        hasImage: !!imageUrl
      };
    });
  }

  // ── Loading state ─────────────────────────────────────────────────────────
  // Render as soon as the standard Account wire resolves (data OR error)
  get isLoaded() {
    return !!(this.account.data || this.account.error);
  }
}
