import { api } from "lwc";
import LightningModal from "lightning/modal";

export default class RlmLearningSectionDetailModal extends LightningModal {
  @api header = "";
  @api subHeader = "";
  @api description = "";

  handleOkay() {
    this.close();
  }
}
