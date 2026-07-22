/* global require */
import { createElement } from "lwc";
import DlmTermLibraryModal from "c/dlmTermLibraryModal";
import getTermLibrary from "@salesforce/apex/RLM_DeltaTermBuilderController.getTermLibrary";
import addTermFromTemplate from "@salesforce/apex/RLM_DeltaTermBuilderController.addTermFromTemplate";

// The component extends LightningModal, which sfdx-lwc-jest does not stub. Mock it as a plain
// LightningElement whose close() records its payload so the tests can assert the finished contract.
// (The lightning-modal-header/body/footer children DO have stubs.)
const mockClose = jest.fn();
jest.mock(
  "lightning/modal",
  () => {
    const { LightningElement } = require("lwc");
    return {
      __esModule: true,
      default: class extends LightningElement {
        close(payload) {
          mockClose(payload);
        }
      }
    };
  },
  { virtual: true }
);

jest.mock(
  "@salesforce/apex/RLM_DeltaTermBuilderController.getTermLibrary",
  () => ({ __esModule: true, default: jest.fn() }),
  { virtual: true }
);
jest.mock(
  "@salesforce/apex/RLM_DeltaTermBuilderController.addTermFromTemplate",
  () => ({ __esModule: true, default: jest.fn() }),
  { virtual: true }
);

const QUOTE_ID = "0Q0000000000001AAA";
const PRODUCT_ID = "01t000000000001AAA";
const TERM_LINE_ID = "0QL000000000009AAA";

const TEMPLATES = [
  {
    productId: PRODUCT_ID,
    name: "ATL Hub Volume",
    description: "ATL hub programme",
    scopeChips: [
      { code: "DL_Origin", label: "Origin", value: "ATL" },
      { code: "DL_Destination", label: "Destination", value: "US50 Display" }
    ],
    fareNames: ["Main", "Comfort", "Delta One"]
  }
];

// eslint-disable-next-line @lwc/lwc/no-async-operation
const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

async function createModal() {
  const element = createElement("c-dlm-term-library-modal", {
    is: DlmTermLibraryModal
  });
  element.quoteId = QUOTE_ID;
  document.body.appendChild(element);
  await flushPromises();
  return element;
}

function items(element) {
  return element.shadowRoot.querySelectorAll(".dl-tl-item");
}

function addButton(element, productId) {
  return [...element.shadowRoot.querySelectorAll("lightning-button")].find(
    (b) => b.dataset.id === productId
  );
}

describe("c-dlm-term-library-modal", () => {
  afterEach(() => {
    while (document.body.firstChild) {
      document.body.removeChild(document.body.firstChild);
    }
    jest.clearAllMocks();
  });

  it("lists templates with their scope chips and fare classes", async () => {
    getTermLibrary.mockResolvedValue(
      JSON.stringify({ isSuccess: true, templates: TEMPLATES })
    );
    const element = await createModal();

    expect(getTermLibrary).toHaveBeenCalledTimes(1);
    const rows = items(element);
    expect(rows.length).toBe(1);
    expect(rows[0].textContent).toContain("ATL Hub Volume");

    const badges = element.shadowRoot.querySelectorAll("lightning-badge");
    expect(badges.length).toBe(2);
    expect([...badges].map((b) => b.label)).toEqual(["ATL", "US50 Display"]);
    expect(rows[0].textContent).toContain("Main, Comfort, Delta One");
  });

  it("filters the list by the search box (name / scope / fares)", async () => {
    const TWO = [
      TEMPLATES[0],
      {
        productId: "01t000000000002AAA",
        name: "JFK-LHR Directional",
        description: "",
        scopeChips: [{ code: "DL_Origin", label: "Origin", value: "JFK" }],
        fareNames: ["Delta One"]
      }
    ];
    getTermLibrary.mockResolvedValue(
      JSON.stringify({ isSuccess: true, templates: TWO })
    );
    const element = await createModal();
    expect(items(element).length).toBe(2);

    const search = element.shadowRoot.querySelector("lightning-input");
    // Matches the second template's name only.
    search.value = "jfk";
    search.dispatchEvent(new CustomEvent("change"));
    await flushPromises();
    expect(items(element).length).toBe(1);
    expect(items(element)[0].textContent).toContain("JFK-LHR Directional");

    // A miss shows the no-matches note and no rows.
    search.value = "nope";
    search.dispatchEvent(new CustomEvent("change"));
    await flushPromises();
    expect(items(element).length).toBe(0);
    expect(
      element.shadowRoot.querySelector('[role="status"]').textContent
    ).toContain("No terms match");
  });

  it("stays open across adds and reports the running totals on close", async () => {
    getTermLibrary.mockResolvedValue(
      JSON.stringify({ isSuccess: true, templates: TEMPLATES })
    );
    addTermFromTemplate.mockResolvedValue(
      JSON.stringify({
        isSuccess: true,
        termLineId: TERM_LINE_ID,
        addedFareCount: 3
      })
    );
    const element = await createModal();

    addButton(element, PRODUCT_ID).dispatchEvent(new CustomEvent("click"));
    await flushPromises();

    expect(addTermFromTemplate).toHaveBeenCalledWith({
      inputJson: JSON.stringify({
        quoteId: QUOTE_ID,
        templateProductId: PRODUCT_ID
      })
    });
    // The modal stays open after an add and shows a running tally.
    expect(mockClose).not.toHaveBeenCalled();
    expect(
      element.shadowRoot.querySelector('[role="status"]').textContent
    ).toContain("1 Term added");

    // Adding again climbs the tally instead of closing.
    addButton(element, PRODUCT_ID).dispatchEvent(new CustomEvent("click"));
    await flushPromises();
    expect(addTermFromTemplate).toHaveBeenCalledTimes(2);
    expect(
      element.shadowRoot.querySelector('[role="status"]').textContent
    ).toContain("2 Terms added");

    // The footer button (now "Done") reports the accumulated totals to the rail.
    element.shadowRoot
      .querySelector("lightning-modal-footer lightning-button")
      .dispatchEvent(new CustomEvent("click"));
    expect(mockClose).toHaveBeenCalledWith({
      status: "finished",
      addedCount: 2,
      addedFareCount: 6,
      lastTermLineId: TERM_LINE_ID
    });
  });

  it("closes with a cancel payload when nothing was added", async () => {
    getTermLibrary.mockResolvedValue(
      JSON.stringify({ isSuccess: true, templates: TEMPLATES })
    );
    const element = await createModal();

    element.shadowRoot
      .querySelector("lightning-modal-footer lightning-button")
      .dispatchEvent(new CustomEvent("click"));

    expect(mockClose).toHaveBeenCalledWith({ status: "cancel" });
  });

  it("surfaces a library-load failure and renders no rows", async () => {
    getTermLibrary.mockResolvedValue(
      JSON.stringify({ isSuccess: false, errorMessage: "Library unavailable." })
    );
    const element = await createModal();

    expect(items(element).length).toBe(0);
    expect(element.shadowRoot.querySelector('[role="alert"]').textContent).toContain(
      "Library unavailable."
    );
  });

  it("keeps the modal open and shows the error when the add fails", async () => {
    getTermLibrary.mockResolvedValue(
      JSON.stringify({ isSuccess: true, templates: TEMPLATES })
    );
    addTermFromTemplate.mockResolvedValue(
      JSON.stringify({ isSuccess: false, errorMessage: "No price book entry." })
    );
    const element = await createModal();

    addButton(element, PRODUCT_ID).dispatchEvent(new CustomEvent("click"));
    await flushPromises();

    expect(mockClose).not.toHaveBeenCalled();
    expect(element.shadowRoot.querySelector('[role="alert"]').textContent).toContain(
      "No price book entry."
    );
  });
});
