import { LightningElement, track, wire, api } from "lwc";
import { NavigationMixin, CurrentPageReference } from "lightning/navigation";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import rlmLearningSectionDetailModal from "c/rlmLearningSectionDetailModal";
import getSectionsWithBlocksByPageId from "@salesforce/apex/RLM_Learning_SectionBlockController.getSectionsWithBlocksByPageId";
import {
  findDynamicLinkIdentifier,
  getDynamicLinkByIdentifier,
  getPageReferenceByDynamicType
} from "c/rlmLearningCommonFunctions";
import getSectionWithBlockBySectionId from "@salesforce/apex/RLM_Learning_SectionBlockController.getSectionWithBlockBySectionId";

export default class Setupconfiglwc extends NavigationMixin(LightningElement) {
  @track sectionsWithBlocks = [];

  sectionType = "Left_Bottom";
  @api pageId = "";
  dynamicLinksMap = {};

  @wire(getSectionsWithBlocksByPageId, {
    sectionType: "$sectionType",
    pageId: "$pageId"
  })
  wiredSections({ error, data }) {
    if (data) {
      this.sectionsWithBlocks = data;
      this.createDynamicLinksMap(data);
    } else if (error) {
      console.error("Error fetching section and blocks:", error);
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
    var appNameValue = event.target.dataset.id;
    try {
      if (!appNameValue) {
        throw new Error("Application name is not defined");
      }
      const dynamicLink = this.dynamicLinksMap[appNameValue];
      if (
        dynamicLink.RLM_Learning_Section__c != null &&
        dynamicLink.RLM_Learning_Section__c !== undefined
      ) {
        const data = await getSectionWithBlockBySectionId({
          sectionId: dynamicLink.RLM_Learning_Section__c
        });
        const sectionWithBlock = data[0];
        const description = await this.replaceDynamicLinks(
          sectionWithBlock.block.description
        );
        const result = await rlmLearningSectionDetailModal.open({
          // `label` is not included here in this example.
          // it is set on lightning-modal-header instead
          size: "medium",
          header: sectionWithBlock.section.RLM_Learning_Header__c,
          subHeader: sectionWithBlock.section.RLM_Learning_Sub_Header__c,
          description: description
        });
      } else {
        try {
          const pageRef = await getPageReferenceByDynamicType(dynamicLink);
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
      }
    } catch (error) {
      this.showToast(error, error.message);
    }
  }

  async replaceDynamicLinks(content) {
    // Step 1: Identify all dynamic link identifiers
    const identifiers = [];
    let searchIndex = 0;

    while (true) {
      const startIndex = content.indexOf("DYN_LINK", searchIndex);
      if (startIndex === -1) break;

      const identifier = findDynamicLinkIdentifier(content, startIndex);
      identifiers.push(identifier);

      // Move the search index past the current identifier
      searchIndex = startIndex + identifier.length;
    }

    // Step 2: Process each identifier in a for loop with try-catch
    for (const identifier of identifiers) {
      try {
        const dynamicLink = await getDynamicLinkByIdentifier(identifier);
        let url = "";
        if (dynamicLink.RecordType.DeveloperName === "WebPage") {
          url = dynamicLink.RLM_Learning_Link__c;
        } else {
          const pageRef = await getPageReferenceByDynamicType(dynamicLink);
          if (
            dynamicLink.RecordType.DeveloperName === "SetupPage" ||
            dynamicLink.RecordType.DeveloperName == "CommunityPage"
          ) {
            url = pageRef.attributes.url;
          } else {
            url = await this[NavigationMixin.GenerateUrl](pageRef);
          }
          try {
            if (!url) {
              throw new Error(
                "Unable to generate URL. Possibly an invalid link"
              );
            }
          } catch (error) {
            this.showToast(error, error.message);
          }
        }
        const replaceString =
          "<a href='" +
          url +
          "' target='_blank' style='color: rgb(0,0,238);'>" +
          dynamicLink.RLM_Learning_Text_Value__c +
          "</a>";
        content = content.replace(identifier, replaceString);
      } catch (error) {
        console.error(`Error processing identifier "${identifier}":`, error);
        // Skip this identifier and continue
      }
    }
    return content;
  }

  hideModalBox() {
    this.isShowModal = false;
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
