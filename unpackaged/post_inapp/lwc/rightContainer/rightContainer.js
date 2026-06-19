import { LightningElement, track, wire, api } from "lwc";
import { NavigationMixin } from "lightning/navigation";
import getSectionsWithBlocksByType from "@salesforce/apex/SectionBlockController.getSectionsWithBlocksByType";
import getSectionsWithBlocksByPageId from "@salesforce/apex/SectionBlockController.getSectionsWithBlocksByPageId";
import { getPageReferenceByDynamicType } from "c/commonFunctions";

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
    const appNameValue = event.target.dataset.id;
    try {
      console.log("inside handle on btn click for app = " + appNameValue);
      if (!appNameValue) {
        throw new Error("Application name is not defined");
      }
      const dynamicLink = this.dynamicLinksMap[appNameValue];
      console.log("dynamicLink = " + dynamicLink.Link__c);
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
          const windowContextNameUniqueStr = Math.random()
            .toString(36)
            .substring(2, 7);
          console.log(windowContextNameUniqueStr);
          const windowContextNameUUID = crypto.randomUUID();
          window.open("", windowContextNameUUID);
          window.open(url, windowContextNameUUID);
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
