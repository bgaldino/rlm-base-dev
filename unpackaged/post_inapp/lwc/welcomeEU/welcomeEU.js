import { LightningElement, wire, track } from "lwc";
import getSectionsWithBlocksByType from '@salesforce/apex/SectionBlockController.getSectionsWithBlocksByType';
import getName from '@salesforce/apex/UserInformation.getName';
import getTiming from '@salesforce/apex/UserInformation.getTiming';
import getExpiryDays from '@salesforce/apex/UserInformation.getExpiryDays';

export default class WelcomeEU extends LightningElement {

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
