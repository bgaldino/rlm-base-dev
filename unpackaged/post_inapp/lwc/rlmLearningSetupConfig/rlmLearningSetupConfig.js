import { LightningElement, track, wire, api } from "lwc";
import { NavigationMixin } from "lightning/navigation";
import { ShowToastEvent } from "lightning/platformShowToastEvent";
import rlmLearningSectionDetailModal from "c/rlmLearningSectionDetailModal";
import getSectionsWithBlocksByPageId from "@salesforce/apex/RLM_Learning_SectionBlockController.getSectionsWithBlocksByPageId";
import {
  findDynamicLinkIdentifier,
  getDynamicLinkByIdentifier,
  getPageReferenceByDynamicType,
  escapeHtml,
  requireSafeUrl
} from "c/rlmLearningCommonFunctions";
import getSectionWithBlockBySectionId from "@salesforce/apex/RLM_Learning_SectionBlockController.getSectionWithBlockBySectionId";

export default class RlmLearningSetupConfig extends NavigationMixin(
  LightningElement
) {
  @track sectionsWithBlocks = [];

  sectionType = "Left_Bottom";
  // Left undefined so the wire doesn't fire (and the controller doesn't throw on a
  // blank id) until a real page id is set by the parent.
  @api pageId;
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
      this.showToast(error, error.message);
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
        await rlmLearningSectionDetailModal.open({
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
      }
    } catch (error) {
      this.showToast(error, error.message);
    }
  }

  async replaceDynamicLinks(content) {
    if (!content) {
      return content;
    }
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
          url = requireSafeUrl(dynamicLink.RLM_Learning_Link__c);
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
          // Couldn't resolve a URL — show the link text as plain text rather than
          // a broken <a href=""> or the raw DYN_LINK token.
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
        // DYN_LINK token isn't left visible in the modal body.
        content = content.replace(identifier, "");
      }
    }
    return content;
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
