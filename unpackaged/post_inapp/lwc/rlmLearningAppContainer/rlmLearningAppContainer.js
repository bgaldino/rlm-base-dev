import { LightningElement, track, wire } from "lwc";
import { NavigationMixin } from "lightning/navigation";
import getSectionsWithBlocksByType from "@salesforce/apex/RLM_Learning_SectionBlockController.getSectionsWithBlocksByType";
import { getPageReferenceByDynamicType } from "c/rlmLearningCommonFunctions";
import { ShowToastEvent } from "lightning/platformShowToastEvent";

export default class RlmLearningAppContainer extends NavigationMixin(
  LightningElement
) {
  @track sectionsWithBlocks = [];
  @track error;

  sectionType = "Left_Bottom";
  pageType = "Home";

  dynamicLinksMap = {};

  @wire(getSectionsWithBlocksByType, {
    sectionType: "$sectionType",
    pageType: "$pageType"
  })
  wiredSections({ error, data }) {
    if (data) {
      this.sectionsWithBlocks = JSON.parse(JSON.stringify(data)).map(
        (section) => {
          // Process SectionBlocks__r
          if (section.section && section.section.SectionBlocks__r) {
            section.section.SectionBlocks__r =
              section.section.SectionBlocks__r.map((block) => {
                if (block.RLM_Learning_Block__r && block.RLM_Learning_Block__r.RLM_Learning_Description__c) {
                  block.RLM_Learning_Block__r.PlainDescription__c = this.stripHtmlTags(
                    block.RLM_Learning_Block__r.RLM_Learning_Description__c
                  );
                }
                return block;
              });
          }

          // Process blocks array
          if (section.blocks) {
            section.blocks = section.blocks.map((block) => {
              if (block.description) {
                block.plainDescription = this.stripHtmlTags(block.description);
              }
              return block;
            });
          }
          return section;
        }
      );
      this.createDynamicLinksMap(data);
    } else if (error) {
      this.error = error?.body?.message || error?.message || "Unknown error";
    }
  }

  createDynamicLinksMap(data) {
    // Go through the data array, building a map of dynamicLink id -> dynamicLink.
    data.forEach((sectionWithBlocks) => {
      if (sectionWithBlocks.dynamicLinks) {
        sectionWithBlocks.dynamicLinks.forEach((dynamicLink) => {
          this.dynamicLinksMap[dynamicLink.Id] = JSON.parse(
            JSON.stringify(dynamicLink)
          );
        });
      }
    });
  }

  async handleClick(event) {
    try {
      // currentTarget = the element the handler is bound to (carries data-id);
      // event.target may be an internal node of the base component.
      const appNameValue = event.currentTarget.dataset.id;
      if (!appNameValue) {
        throw new Error("Action is undefined. Please update an action type.");
      }
      const dynamicLink = this.dynamicLinksMap[appNameValue];
      if (!dynamicLink) {
        throw new Error("No dynamic link found for " + appNameValue);
      }
      const pageRef = await getPageReferenceByDynamicType(dynamicLink);
      try {
        let url = await this[NavigationMixin.GenerateUrl](pageRef);
        if (dynamicLink.RecordType.DeveloperName == "SetupPage") {
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

  stripHtmlTags(htmlString) {
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = htmlString;
    return tempDiv.textContent || tempDiv.innerText || "";
  }
}
