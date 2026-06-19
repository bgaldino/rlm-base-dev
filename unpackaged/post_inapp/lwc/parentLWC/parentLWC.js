import { LightningElement } from "lwc";

export default class ParentLWC extends LightningElement {
  isHome = true;
  hasNoData = false;
  handleHasNoData() {
    this.hasNoData = true;
  }
}
