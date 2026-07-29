import { LightningElement, wire, track } from "lwc";
import basePath from "@salesforce/community/basePath";
import getProducts from "@salesforce/apex/RLM_HomeServices_ProductCarouselCtrl.getProducts";
import submitSignup from "@salesforce/apex/RLM_HomeServices_CustomerSignupCtrl.submitSignup";
import { resolveProductImageUrl } from "c/rlmHomeServicesImageUrl";

const FORM_FIELDS = [
  { name: "firstName", label: "First Name", type: "text", required: true },
  { name: "lastName", label: "Last Name", type: "text", required: true },
  { name: "street", label: "Street", type: "text", required: false },
  { name: "city", label: "City", type: "text", required: false },
  { name: "state", label: "State / Province", type: "text", required: false },
  { name: "postalCode", label: "Postal Code", type: "text", required: false },
  { name: "country", label: "Country", type: "text", required: false },
  { name: "phone", label: "Phone", type: "tel", required: false },
  { name: "email", label: "Email", type: "email", required: false }
];

export default class RlmHomeServicesCustSignUp extends LightningElement {
  // Product carousel state (selectedPricebookEntryIds is source of truth for submit; wire re-runs won't clear it)
  @track productCards = [];
  @track hasProducts = false;
  @track selectedPricebookEntryIds = [];

  // Form state
  form = Object.fromEntries(FORM_FIELDS.map(({ name }) => [name, ""]));
  @track message = "";
  @track messageClass = "slds-m-top_medium slds-text-color_success";
  @track submitDisabled = false;

  get formFields() {
    return FORM_FIELDS.map((field) => ({
      ...field,
      value: this.form[field.name]
    }));
  }

  @wire(getProducts)
  wiredProducts({ error, data }) {
    if (data) {
      const selectedSet = new Set(
        (this.selectedPricebookEntryIds || []).filter(Boolean)
      );
      this.productCards = data.map((p) => {
        const imageUrl = resolveProductImageUrl(p.displayUrl, basePath);
        const pricebookEntryId = p.pricebookEntryId;
        return {
          ...p,
          productId: p.productId,
          pricebookEntryId,
          formattedPrice: this.formatCurrency(p.listPrice),
          displayUrl: imageUrl || "",
          showImage: this.isValidImageUrl(imageUrl),
          selectLabel: `Select ${p.name}`,
          selected: selectedSet.has(pricebookEntryId)
        };
      });
      this.hasProducts = this.productCards.length > 0;
    } else if (error) {
      this.hasProducts = false;
      console.error("Error loading products:", error);
    }
  }

  formatCurrency(value) {
    if (value == null) return "$0.00";
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD"
    }).format(value);
  }

  isValidImageUrl(url) {
    if (!url || typeof url !== "string") return false;
    const t = url.trim();
    return (
      t.length > 0 &&
      (t.startsWith("http://") || t.startsWith("https://") || t.startsWith("/"))
    );
  }

  handleImageError(event) {
    const productId = event.target?.dataset?.cardId;
    if (productId) {
      this.productCards = this.productCards.map((card) => {
        return card.productId === productId
          ? { ...card, showImage: false }
          : card;
      });
    }
  }

  handleSelect(event) {
    const pricebookEntryId = event.currentTarget.dataset.pricebookEntryId;
    const checked = event.detail.checked;
    if (!pricebookEntryId) return;
    // Update source-of-truth list (survives wire re-runs)
    if (checked) {
      if (!this.selectedPricebookEntryIds.includes(pricebookEntryId)) {
        this.selectedPricebookEntryIds = [
          ...this.selectedPricebookEntryIds,
          pricebookEntryId
        ];
      }
    } else {
      this.selectedPricebookEntryIds = (
        this.selectedPricebookEntryIds || []
      ).filter((id) => id !== pricebookEntryId);
    }
    // Keep UI in sync
    this.productCards = this.productCards.map((card) => {
      return card.pricebookEntryId === pricebookEntryId
        ? { ...card, selected: checked }
        : card;
    });
  }

  get scrollStep() {
    return 320;
  }

  handleScrollLeft() {
    const el = this.refs.cardsContainer;
    if (el) el.scrollBy({ left: -this.scrollStep, behavior: "smooth" });
  }

  handleScrollRight() {
    const el = this.refs.cardsContainer;
    if (el) el.scrollBy({ left: this.scrollStep, behavior: "smooth" });
  }

  handleFormChange(event) {
    const fieldName = event.currentTarget.dataset.field;
    this.form = {
      ...this.form,
      [fieldName]: event.target.value
    };
  }

  normalizedFormValue(fieldName) {
    return (this.form[fieldName] || "").trim();
  }

  async handleSubmit() {
    this.message = "";
    // Use selectedPricebookEntryIds (source of truth; survives wire re-runs)
    const pricebookEntryIds = Array.isArray(this.selectedPricebookEntryIds)
      ? [...this.selectedPricebookEntryIds].filter(Boolean)
      : [];
    if (pricebookEntryIds.length === 0) {
      this.messageClass = "slds-m-top_medium slds-text-color_error";
      this.message =
        "Please select at least one product from the Products section.";
      return;
    }
    const first = this.normalizedFormValue("firstName");
    const last = this.normalizedFormValue("lastName");
    if (!first || !last) {
      this.messageClass = "slds-m-top_medium slds-text-color_error";
      this.message = "First name and last name are required.";
      return;
    }
    this.submitDisabled = true;
    let submissionSucceeded = false;
    try {
      const requestJson = JSON.stringify({
        firstName: first,
        lastName: last,
        street: this.normalizedFormValue("street"),
        city: this.normalizedFormValue("city"),
        state: this.normalizedFormValue("state"),
        postalCode: this.normalizedFormValue("postalCode"),
        country: this.normalizedFormValue("country"),
        phone: this.normalizedFormValue("phone"),
        email: this.normalizedFormValue("email"),
        pricebookEntryIds
      });
      const result = await submitSignup({ requestJson });
      if (result.success) {
        submissionSucceeded = true;
        this.messageClass = "slds-m-top_medium slds-text-color_success";
        this.message =
          "Thank you! Your account and opportunity have been created successfully.";
      } else {
        this.messageClass = "slds-m-top_medium slds-text-color_error";
        this.message = result.errorMessage || "An error occurred.";
      }
    } catch (e) {
      this.messageClass = "slds-m-top_medium slds-text-color_error";
      this.message = e.body?.message || e.message || "An error occurred.";
    } finally {
      this.submitDisabled = submissionSucceeded;
    }
  }
}
