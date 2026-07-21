import { api } from "lwc";
import LightningModal from "lightning/modal";

// API name of the DL contract-creation flow hosted in this modal. It is a headless (autolaunched)
// flow: it takes the source Quote Id as its `recordId` input, creates the Contract, always saves the
// negotiated discounts as contract item prices, and returns isSuccess / errorMessage /
// outputContractId. All confirmation UI lives here in the modal, not in the flow.
const CREATE_CONTRACT_FLOW = "DL_CreateContractFromQuote";

/**
 * Delta "Create Contract" modal. The Term Builder header opens this with
 * DlCreateContractModal.open({ quoteId, summary, size: 'small' }). The modal shows a summary of the
 * Terms (and their fares) that will be contracted, then — on Create — mounts the headless
 * DL_CreateContractFromQuote flow, which runs to completion with no screens of its own. On FINISHED we
 * read the flow's output variables and close with a structured payload so the parent can toast +
 * deep-link to the new Contract.
 */
export default class DlCreateContractModal extends LightningModal {
  @api quoteId;
  // { quoteName, termCount, lineCount, terms: [{ id, name, discountText, fares: [...] , hasFares }] }
  @api summary;

  flowApiName = CREATE_CONTRACT_FLOW;
  running = false;
  errorMessage = "";

  get hasQuote() {
    return !!this.quoteId;
  }

  get terms() {
    return (this.summary && this.summary.terms) || [];
  }

  get hasTerms() {
    return this.terms.length > 0;
  }

  get createDisabled() {
    return !this.hasQuote || this.running;
  }

  // Single input the flow declares: the source Quote Id, bound to its `recordId` input variable.
  get inputVariables() {
    if (!this.quoteId) {
      return [];
    }
    return [{ name: "recordId", type: "String", value: this.quoteId }];
  }

  // Create pressed: mount the headless flow (it auto-runs on render). A spinner replaces the footer
  // buttons while it runs; completion arrives via handleStatusChange.
  handleCreate() {
    if (!this.hasQuote) {
      return;
    }
    this.errorMessage = "";
    this.running = true;
  }

  handleCancel() {
    this.close({ status: "cancel" });
  }

  // The autolaunched flow surfaces terminal state via statuschange. On FINISHED we harvest its output
  // variables (isSuccess / errorMessage / outputContractId) and close with them so the parent decides
  // whether to toast success + link to the new Contract or surface the flow's error. On ERROR we drop
  // back to the summary so the user can retry or cancel.
  handleStatusChange(event) {
    const status = event.detail?.status;
    if (status === "ERROR") {
      this.running = false;
      this.errorMessage =
        "The contract could not be created. Please try again.";
      return;
    }
    if (status !== "FINISHED" && status !== "FINISHED_SCREEN") {
      return;
    }
    const outputs = event.detail?.outputVariables || [];
    const byName = {};
    outputs.forEach((v) => {
      byName[v.name] = v.value;
    });
    this.close({
      status: "finished",
      isSuccess: byName.isSuccess === true || byName.isSuccess === "true",
      contractId: byName.outputContractId || null,
      errorMessage: byName.errorMessage || null
    });
  }
}
