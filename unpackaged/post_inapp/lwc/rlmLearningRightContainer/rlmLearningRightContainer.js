import { LightningElement, track, wire, api } from "lwc";
import { NavigationMixin } from "lightning/navigation";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import getSectionsWithBlocksByType from "@salesforce/apex/RLM_Learning_SectionBlockController.getSectionsWithBlocksByType";
import getSectionsWithBlocksByPageId from "@salesforce/apex/RLM_Learning_SectionBlockController.getSectionsWithBlocksByPageId";
import { getPageReferenceByDynamicType } from "c/rlmLearningCommonFunctions";

export default class RightContainer extends NavigationMixin(LightningElement) {
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
          console.log("Learning Data:", data);
          this.sectionsWithBlocks = data;
          this.createDynamicLinksMap(data);
        })
        .catch((error) => {
          console.error("Error fetching section and blocks:", error);
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
          console.log("Learning Data:", data);
          this.sectionsWithBlocks = data;
          this.createDynamicLinksMap(data);
        })
        .catch((error) => {
          console.error("Error fetching section and blocks:", error);
        });
    }
  }

  createDynamicLinksMap(data) {
    //got through data array by reading dynamicLinks map value and creating a map of dynamicLink and pageReference
    data.forEach((sectionWithBlocks) => {
      sectionWithBlocks.dynamicLinks.forEach((dynamicLink) => {
        this.dynamicLinksMap[dynamicLink.Id] = JSON.parse(
          JSON.stringify(dynamicLink)
        );
      });
    });
  }

  async handleClick(event) {
    // Wired to an <a href="#">; prevent the default anchor jump.
    event.preventDefault();
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
      console.log("pageRef: " + JSON.stringify(pageRef));
      try {
        let url = await this[NavigationMixin.GenerateUrl](pageRef);
        if (dynamicLink.RecordType.DeveloperName == "SetupPage") {
          url = pageRef.attributes.url;
        }
        console.log("url: " + url);
        if (!url) {
          throw new Error("Unable to generate URL. Possibly an invalid link");
        }
        if (
          dynamicLink.RecordType.DeveloperName == "InAppDetailsPage" ||
          dynamicLink.RecordType.DeveloperName == "WebPage" ||
          dynamicLink.RecordType.DeveloperName == "CommunityPage"
        ) {
          this[NavigationMixin.Navigate](pageRef);
        } else {
          // Open external links in a new tab with noopener/noreferrer to prevent
          // reverse-tabnabbing (the opened page can't reach window.opener).
          window.open(url, "_blank", "noopener,noreferrer");
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
