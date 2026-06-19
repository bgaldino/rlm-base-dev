import { LightningElement, track, wire, api } from "lwc";
import { CurrentPageReference, NavigationMixin } from "lightning/navigation";
import getSectionsWithBlocksByPageId from "@salesforce/apex/SectionBlockController.getSectionsWithBlocksByPageId";
import {
  findDynamicLinkIdentifier,
  getDynamicLinkByIdentifier,
  getPageReferenceByDynamicType
} from "c/commonFunctions";

export default class AppOverviewLWC extends NavigationMixin(LightningElement) {
  @track sectionsWithBlocks = [];

  sectionType = "Left_Top";
  @api pageId = "";

  @wire(getSectionsWithBlocksByPageId, {
    sectionType: "$sectionType",
    pageId: "$pageId"
  })
  wiredSections({ error, data }) {
    if (data) {
      console.log("Wired Data:", data);
      this.sectionsWithBlocks = [...data];
      this.checkForDynamicLinks();
    } else if (error) {
      this.error = error.body.message;
      console.error("Error fetching section and blocks:", error);
    }
  }

  async checkForDynamicLinks() {
    const newBlocks = [];
    for (let i = 0; i < this.sectionsWithBlocks[0].blocks.length; i++) {
      let description = this.sectionsWithBlocks[0].blocks[i].description;
      newBlocks.push({ ...this.sectionsWithBlocks[0].blocks[i] });
      if (description.includes("DYN_LINK")) {
        newBlocks[i].description = await this.replaceDynamicLinks(description);
      }
    }
    this.sectionsWithBlocks[0] = {
      ...this.sectionsWithBlocks[0],
      blocks: newBlocks
    };
  }

  async replaceDynamicLinks(content) {
    while (content.includes("DYN_LINK")) {
      const identifier = findDynamicLinkIdentifier(
        content,
        content.indexOf("DYN_LINK")
      );
      try {
        const dynamicLink = await getDynamicLinkByIdentifier(identifier);
        let url = "";
        if (dynamicLink.RecordType.DeveloperName == "WebPage") {
          url = dynamicLink.Link__c;
        } else {
          const pageRef = await getPageReferenceByDynamicType(dynamicLink);
          if (
            dynamicLink.RecordType.DeveloperName == "SetupPage" ||
            dynamicLink.RecordType.DeveloperName == "CommunityPage"
          ) {
            url = pageRef.attributes.url;
          } else {
            url = await this[NavigationMixin.GenerateUrl](pageRef);
          }
        }
        const replaceString =
          "<a href='" +
          url +
          "' target='_blank' style='color: rgb(0,0,238);'>" +
          dynamicLink.Text_Value__c +
          "</a>";
        content = content.replace(identifier, replaceString);
      } catch (error) {
        return content;
      }
    }
    return content;
  }

  @wire(CurrentPageReference)
  getStateParameters(currentPageReference) {
    if (currentPageReference) {
      this.appNameValue = currentPageReference.state?.c__appName;
    }
  }
}
