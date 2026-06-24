import { LightningElement, wire, track } from "lwc";
import getSectionsWithBlocksByType from "@salesforce/apex/RLM_Learning_SectionBlockController.getSectionsWithBlocksByType";
import getName from "@salesforce/apex/RLM_Learning_UserInformation.getName";
import getExpiryDays from "@salesforce/apex/RLM_Learning_UserInformation.getExpiryDays";

export default class RlmLearningWelcome extends LightningElement {

  @track sectionsWithBlocks = [];
  @track error;

  sectionType = "Top";
  pageType = "Home";

  @wire(getName)
  getName;

  @wire(getExpiryDays)
  getExpiryDays;

  // Part-of-day is derived from the browser's local time rather than a cacheable
  // Apex wire: a cacheable Apex method must be deterministic, and one built on
  // System.now() can be cached and go stale (e.g. still "Morning" in the afternoon).
  // The client clock is always fresh and already in the user's local timezone.
  get timing() {
    const hour = new Date().getHours();
    if (hour < 12) {
      return "Morning";
    }
    if (hour < 17) {
      return "Afternoon";
    }
    return "Evening";
  }

  // Build the greeting; `timing` is always present (client-computed), so the title
  // never flashes "undefined undefined!" — it shows e.g. "Morning!" until the wired
  // name resolves, then "Morning <name>!".
  get greeting() {
    const name = this.getName && this.getName.data;
    const text = `${this.timing} ${name || ""}`.trim();
    return text ? `${text}!` : "";
  }

  // Normalize the wire result: null on non-trial orgs (countdown hidden), but
  // keep 0 visible (an expired trial should still render "remaining 0 days").
  get expiryDaysDisplay() {
    const days = this.getExpiryDays && this.getExpiryDays.data;
    return days === null || days === undefined ? null : days;
  }

  get hasExpiryDays() {
    return this.expiryDaysDisplay !== null;
  }

  @wire(getSectionsWithBlocksByType, {
    sectionType: "$sectionType",
    pageType: "$pageType"
  })
  wiredSections({ error, data }) {
    if (data) {
      this.sectionsWithBlocks = data;
    } else if (error) {
      this.error = error?.body?.message || error?.message || "Unknown error";
    }
  }
}
