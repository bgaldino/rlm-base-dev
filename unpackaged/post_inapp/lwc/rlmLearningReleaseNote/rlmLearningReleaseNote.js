import { LightningElement, track, wire } from "lwc";
import getSectionsWithBlocksByType from "@salesforce/apex/RLM_Learning_SectionBlockController.getSectionsWithBlocksByType";

export default class RlmLearningReleaseNote extends LightningElement {
  @track sectionsWithBlocks = [];
  @track error;

  sectionType = "Left_Top";
  pageType = "Home";

  @wire(getSectionsWithBlocksByType, {
    sectionType: "$sectionType",
    pageType: "$pageType"
  })
  wiredSections({ error, data }) {
    if (data) {
      this.sectionsWithBlocks = data.map(section => ({
        ...section,
        contentSize: section.section.RLM_Learning_Video_Link__c ? 7 : 12,
        // Full width for a video with no accompanying blocks; otherwise share the row.
        videoSize: section.blocks && section.blocks.length > 0 ? 5 : 12
      }));
      if (this.sectionsWithBlocks.length === 0) {
        this.dispatchEvent(new CustomEvent("hasnodata"));
      }
    } else if (error) {
      this.error = error?.body?.message || error?.message || "Unknown error";
    }
  }
}
