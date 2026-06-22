import { LightningElement, track, api } from "lwc";
import { CloseActionScreenEvent } from "lightning/actions";
import getAllBlocks from "@salesforce/apex/RLM_Learning_SectionBlockSequence.getAllBlocks";
import getBlocksForSection from "@salesforce/apex/RLM_Learning_SectionBlockSequence.getBlocksForSection";
import updateSectionBlocks from "@salesforce/apex/RLM_Learning_SectionBlockSequence.updateSectionBlocks";

export default class ReorderableList extends LightningElement {
  @api objectApiName;
  @track blocks = [];
  @track selectedBlocks = [];

  _recordId;

  @api set recordId(value) {
    this._recordId = value;
    this.getData().then();
  }

  get recordId() {
    return this._recordId;
  }

  async getData() {
    var [availableBlocks, intialSelectedBlocks] = await Promise.all([
      getAllBlocks(),
      getBlocksForSection({ sectionId: this.recordId })
    ]);

    this.blocks = availableBlocks.map((block) => {
      return {
        label: block.Name,
        value: block.Id
      };
    });
    this.selectedBlocks.push(
      ...intialSelectedBlocks.map((block) => block.RLM_Learning_Block__c)
    );
  }

  handleOptionChange(event) {
    this.selectedBlocks = event.detail.value;
  }

  handleCancel(event) {
    // Add your cancel button implementation here
    this.dispatchEvent(new CloseActionScreenEvent());
  }

  async handleSave(e) {
    await updateSectionBlocks({
      sectionId: this.recordId,
      blockIds: this.selectedBlocks
    });
    // Close the modal window and display a success toast
    this.dispatchEvent(new CloseActionScreenEvent());
  }
}
