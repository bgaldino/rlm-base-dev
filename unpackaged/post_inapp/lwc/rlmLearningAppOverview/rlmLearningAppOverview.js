import { LightningElement, track, wire, api } from "lwc";
import { NavigationMixin } from "lightning/navigation";
import getSectionsWithBlocksByPageId from "@salesforce/apex/RLM_Learning_SectionBlockController.getSectionsWithBlocksByPageId";
import {
  findDynamicLinkIdentifier,
  getDynamicLinkByIdentifier,
  getPageReferenceByDynamicType,
  escapeHtml,
  safeVideoUrl
} from "c/rlmLearningCommonFunctions";

export default class RlmLearningAppOverview extends NavigationMixin(
  LightningElement
) {
  @track sectionsWithBlocks = [];

  sectionType = "Left_Top";
  // Left undefined so the wire doesn't fire (and the controller doesn't throw on a
  // blank id) until a real page id is set by the parent.
  @api pageId;

  @wire(getSectionsWithBlocksByPageId, {
    sectionType: "$sectionType",
    pageId: "$pageId"
  })
  wiredSections({ error, data }) {
    if (data) {
      // Only embed an allowlisted https video host; otherwise no iframe is rendered.
      this.sectionsWithBlocks = data.map((s) => ({
        ...s,
        section: {
          ...s.section,
          safeVideoLink: safeVideoUrl(s.section.RLM_Learning_Video_Link__c)
        }
      }));
      this.checkForDynamicLinks();
    } else if (error) {
      this.error = error?.body?.message || error?.message || "Unknown error";
    }
  }

  async checkForDynamicLinks() {
    // The wire fires with `data` truthy even when it's an empty array, so guard
    // against a missing first section / blocks before dereferencing.
    if (
      !this.sectionsWithBlocks.length ||
      !this.sectionsWithBlocks[0].blocks
    ) {
      return;
    }
    const newBlocks = [];
    for (let i = 0; i < this.sectionsWithBlocks[0].blocks.length; i++) {
      let description = this.sectionsWithBlocks[0].blocks[i].description;
      newBlocks.push({ ...this.sectionsWithBlocks[0].blocks[i] });
      if (description && description.includes("DYN_LINK")) {
        newBlocks[i].description = await this.replaceDynamicLinks(description);
      }
    }
    this.sectionsWithBlocks[0] = {
      ...this.sectionsWithBlocks[0],
      blocks: newBlocks
    };
  }

  async replaceDynamicLinks(content) {
    if (!content) {
      return content;
    }
    while (content.includes("DYN_LINK")) {
      const identifier = findDynamicLinkIdentifier(
        content,
        content.indexOf("DYN_LINK")
      );
      try {
        const dynamicLink = await getDynamicLinkByIdentifier(identifier);
        let url = "";
        if (dynamicLink.RecordType.DeveloperName === "WebPage") {
          url = dynamicLink.RLM_Learning_Link__c;
        } else {
          const pageRef = await getPageReferenceByDynamicType(dynamicLink);
          if (
            dynamicLink.RecordType.DeveloperName === "SetupPage" ||
            dynamicLink.RecordType.DeveloperName === "CommunityPage"
          ) {
            url = pageRef.attributes.url;
          } else {
            url = await this[NavigationMixin.GenerateUrl](pageRef);
          }
        }
        if (!url) {
          // No URL resolved — replace the placeholder with plain text instead of
          // injecting a broken <a href="">, and let the loop progress.
          content = content.replace(
            identifier,
            escapeHtml(dynamicLink.RLM_Learning_Text_Value__c)
          );
          continue;
        }
        const replaceString =
          "<a href='" +
          escapeHtml(url) +
          "' target='_blank' rel='noopener noreferrer' style='color: rgb(0,0,238);'>" +
          escapeHtml(dynamicLink.RLM_Learning_Text_Value__c) +
          "</a>";
        content = content.replace(identifier, replaceString);
      } catch {
        // Couldn't resolve this identifier — drop the placeholder so a raw
        // DYN_LINK token isn't left visible, and keep processing the rest.
        content = content.replace(identifier, "");
      }
    }
    return content;
  }
}
