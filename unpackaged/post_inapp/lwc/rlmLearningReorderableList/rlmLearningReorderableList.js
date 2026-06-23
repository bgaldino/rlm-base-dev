import { LightningElement, track, api } from "lwc";
import { CloseActionScreenEvent } from "lightning/actions";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import getAllBlocks from "@salesforce/apex/RLM_Learning_SectionBlockSequence.getAllBlocks";
import getBlocksForSection from "@salesforce/apex/RLM_Learning_SectionBlockSequence.getBlocksForSection";
import updateSectionBlocks from "@salesforce/apex/RLM_Learning_SectionBlockSequence.updateSectionBlocks";

export default class RlmLearningReorderableList extends LightningElement {
  @api objectApiName;
  @track blocks = [];
  @track selectedBlocks = [];

  _recordId;

  @api set recordId(value) {
    this._recordId = value;
    this.getData().catch((error) => {
      this.showToast("Couldn't load blocks", error);
    });
  }

  get recordId() {
    return this._recordId;
  }

  async getData() {
    const [availableBlocks, initialSelectedBlocks] = await Promise.all([
      getAllBlocks(),
      getBlocksForSection({ sectionId: this.recordId })
    ]);

    this.blocks = availableBlocks.map((block) => {
      return {
        label: block.Name,
        value: block.Id
      };
    });
    // Assign (don't push) so re-opening the quick action / re-setting recordId
    // doesn't accumulate duplicate selections.
    this.selectedBlocks = initialSelectedBlocks.map(
      (block) => block.RLM_Learning_Block__c
    );
  }

  handleOptionChange(event) {
    this.selectedBlocks = event.detail.value;
  }

  handleCancel() {
    this.dispatchEvent(new CloseActionScreenEvent());
  }

  async handleSave() {
    try {
      await updateSectionBlocks({
        sectionId: this.recordId,
        blockIds: this.selectedBlocks
      });
      // Close the quick action only after a successful save.
      this.dispatchEvent(new CloseActionScreenEvent());
    } catch (error) {
      this.showToast("Couldn't save blocks", error);
    }
  }

  showToast(title, error) {
    const message =
      error && error.body && error.body.message
        ? error.body.message
        : (error && error.message) || "Unknown error";
    this.dispatchEvent(
      new ShowToastEvent({ title, message, variant: "error" })
    );
  }
}
