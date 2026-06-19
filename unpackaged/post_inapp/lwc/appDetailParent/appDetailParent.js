import { LightningElement, wire } from "lwc";
import { CurrentPageReference } from "lightning/navigation";
export default class AppDetailParent extends LightningElement {
  isHome = false;
  pageId;
  @wire(CurrentPageReference)
  getStateParameters(currentPageReference) {
    if (currentPageReference) {
      this.pageId = currentPageReference.state?.c__pageId;
    }
  }
}
