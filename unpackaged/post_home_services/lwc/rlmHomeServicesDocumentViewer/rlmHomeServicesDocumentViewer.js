import { LightningElement, api } from "lwc";
import ABOUT_URL from "@salesforce/resourceUrl/RLM_HomeServices_About";
import DEMO_SCRIPT_URL from "@salesforce/resourceUrl/RLM_HomeServices_DemoScript";
import SETUP_STEPS_URL from "@salesforce/resourceUrl/RLM_HomeServices_SetupSteps";

const DOCUMENTS = {
  about: {
    url: ABOUT_URL,
    filename: "HomeServices-Demo-Guide.html"
  },
  demoScript: {
    url: DEMO_SCRIPT_URL,
    filename: "HomeServices-Demo-Script.html"
  },
  setupSteps: {
    url: SETUP_STEPS_URL,
    filename: "HomeServices-Setup-Steps.html"
  }
};

export default class RlmHomeServicesDocumentViewer extends LightningElement {
  @api cardTitle = "Home Services Document";
  @api iconName = "standard:document";
  @api documentKey = "about";
  @api allowDownload = false;
  @api downloadLabel = "Download Document";
  @api downloadFilename;

  get document() {
    return DOCUMENTS[this.documentKey] || DOCUMENTS.about;
  }

  get documentUrl() {
    return this.document.url;
  }

  downloadDocument() {
    const link = document.createElement("a");
    link.href = this.documentUrl;
    link.download = this.downloadFilename || this.document.filename;
    link.target = "_blank";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}
