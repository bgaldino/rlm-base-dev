import { LightningElement } from "lwc";

export default class RlmLearningParent extends LightningElement {
  isHome = true;
  hasNoData = false;
  handleHasNoData() {
    this.hasNoData = true;
  }
}
