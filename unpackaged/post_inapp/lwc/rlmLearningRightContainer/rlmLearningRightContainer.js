import { LightningElement, track, wire, api } from "lwc";
import { NavigationMixin } from "lightning/navigation";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import getSectionsWithBlocksByType from "@salesforce/apex/RLM_Learning_SectionBlockController.getSectionsWithBlocksByType";
import getSectionsWithBlocksByPageId from "@salesforce/apex/RLM_Learning_SectionBlockController.getSectionsWithBlocksByPageId";
import { getPageReferenceByDynamicType } from "c/rlmLearningCommonFunctions";

export default class RlmLearningRightContainer extends NavigationMixin(
  LightningElement
) {
  @track sectionsWithBlocks = [];
  @track error;

  @api isHome;
  _pageId;
  @api
  get pageId() {
    return this._pageId;
  }
  set pageId(value) {
    this._pageId = value;
    if (value) {
      getSectionsWithBlocksByPageId({
        sectionType: "Right",
        pageId: value
      })
        .then((data) => {
          this.sectionsWithBlocks = data;
          this.createDynamicLinksMap(data);
        })
        .catch((error) => {
          this.showToast(error, error.message);
        });
    }
  }
  dynamicLinksMap = {};

  connectedCallback() {
    if (this.isHome) {
      getSectionsWithBlocksByType({
        sectionType: "Right",
        pageType: "Home"
      })
        .then((data) => {
          this.sectionsWithBlocks = data;
          this.createDynamicLinksMap(data);
        })
        .catch((error) => {
          this.showToast(error, error.message);
        });
    }
  }

  createDynamicLinksMap(data) {
    // Go through the data array, building a map of dynamicLink id -> dynamicLink.
    // Reset first so a wire re-run (e.g. a new pageId) doesn't retain stale entries.
    this.dynamicLinksMap = {};
    data.forEach((sectionWithBlocks) => {
      sectionWithBlocks.dynamicLinks.forEach((dynamicLink) => {
        this.dynamicLinksMap[dynamicLink.Id] = JSON.parse(
          JSON.stringify(dynamicLink)
        );
      });
    });
  }

  async handleClick(event) {
    const appNameValue = event.currentTarget.dataset.id;
    try {
      if (!appNameValue) {
        throw new Error("Application name is not defined");
      }
      const dynamicLink = this.dynamicLinksMap[appNameValue];
      if (!dynamicLink) {
        throw new Error("No dynamic link found for " + appNameValue);
      }
      const pageRef = await getPageReferenceByDynamicType(dynamicLink);
      try {
        let url = await this[NavigationMixin.GenerateUrl](pageRef);
        if (dynamicLink.RecordType.DeveloperName === "SetupPage") {
          url = pageRef.attributes.url;
        }
        if (!url) {
          throw new Error("Unable to generate URL. Possibly an invalid link");
        }
        // In-app SPA navigation only for the in-app detail page (or links not
        // flagged for a new tab); everything else — including external WebPage /
        // CommunityPage links — opens a new tab with noopener/noreferrer to
        // prevent reverse-tabnabbing.
        const openInNewTab =
          dynamicLink.RLM_Learning_Open_in_new_tab__c === true ||
          dynamicLink.RecordType.DeveloperName !== "InAppDetailsPage";
        if (openInNewTab) {
          window.open(url, "_blank", "noopener,noreferrer");
        } else {
          this[NavigationMixin.Navigate](pageRef);
        }
      } catch (error) {
        this.showToast(error, error.message);
      }
    } catch (error) {
      this.showToast(error, error.message);
    }
  }

  showToast(error, errorMessage) {
    const toastEvent = new ShowToastEvent({
      title: "Error",
      message: error.body ? error.body.message : errorMessage,
      variant: "error"
    });
    this.dispatchEvent(toastEvent);
  }
}
