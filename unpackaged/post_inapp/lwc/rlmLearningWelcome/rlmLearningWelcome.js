import { LightningElement, wire, track } from "lwc";
import getSectionsWithBlocksByType from '@salesforce/apex/RLM_Learning_SectionBlockController.getSectionsWithBlocksByType';
import getName from '@salesforce/apex/RLM_Learning_UserInformation.getName';
import getTiming from '@salesforce/apex/RLM_Learning_UserInformation.getTiming';
import getExpiryDays from '@salesforce/apex/RLM_Learning_UserInformation.getExpiryDays';

export default class RlmLearningWelcome extends LightningElement {

  @track sectionsWithBlocks = [];
  @track error;

  sectionType = 'Top';
  pageType = 'Home';

  @wire(getName)
  getName;

  @wire(getTiming)
  getTiming;

  @wire(getExpiryDays)
  getExpiryDays;

  // Normalize the wire result: null on non-trial orgs (countdown hidden), but
  // keep 0 visible (an expired trial should still render "remaining 0 days").
  get expiryDaysDisplay() {
    const days = this.getExpiryDays && this.getExpiryDays.data;
    return days === null || days === undefined ? null : days;
  }

  get hasExpiryDays() {
    return this.expiryDaysDisplay !== null;
  }

  @wire(getSectionsWithBlocksByType, { sectionType: '$sectionType', pageType: '$pageType' })
  wiredSections({ error, data }) {
    if (data) {
      console.log('Wired Data:', data);
      this.sectionsWithBlocks = data;
    } else if (error) {
      this.error = error.body.message;
      console.error('Error fetching section and blocks:', error);
    }
  }
}
