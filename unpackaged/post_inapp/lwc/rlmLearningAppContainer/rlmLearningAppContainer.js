import { LightningElement, track, wire } from "lwc";
import { NavigationMixin } from "lightning/navigation";
import getSectionsWithBlocksByType from "@salesforce/apex/RLM_Learning_SectionBlockController.getSectionsWithBlocksByType";
import { getPageReferenceByDynamicType } from "c/rlmLearningCommonFunctions";
import { ShowToastEvent } from "lightning/platformShowToastEvent";

export default class Appcontainer extends NavigationMixin(LightningElement) {
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
      console.log("Wired Data:", data);
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
      this.error = error.body.message;
      console.error("Error fetching section and blocks:", error);
    }
  }

  createDynamicLinksMap(data) {
    //got through data array by reading dynamicLinks map value and creating a map of dynamicLink and pageReference
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
      var appNameValue = event.target.dataset.id;
      if (!appNameValue) {
        throw new Error("Action is undefined. Please update a action type");
      }
      var appNameValue = event.target.dataset.id;
      console.log("inside handle on btn click for app = " + appNameValue);
      const dynamicLink = this.dynamicLinksMap[appNameValue];
      console.log("dynamicLink  = " + dynamicLink.RLM_Learning_Link__c);
      const pageRef = await getPageReferenceByDynamicType(dynamicLink);
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

  stripHtmlTags(htmlString) {
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = htmlString;
    return tempDiv.textContent || tempDiv.innerText || "";
  }
}
