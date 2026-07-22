import { createElement } from "lwc";
import DlmTermsRail from "c/dlmTermsRail";
import { subscribe, publish } from "lightning/messageService";
import DlmTermLibraryModal from "c/dlmTermLibraryModal";
import getBuilderState from "@salesforce/apex/RLM_DeltaTermBuilderController.getBuilderState";
import addTerm from "@salesforce/apex/RLM_DeltaTermBuilderController.addTerm";

// The rail opens the Term Library as a LightningModal via its static open(); mock the whole module so
// the test controls the returned result (finished / cancel) without mounting a real modal.
jest.mock(
  "c/dlmTermLibraryModal",
  () => ({ __esModule: true, default: { open: jest.fn() } }),
  { virtual: true }
);

jest.mock(
  "@salesforce/apex/RLM_DeltaTermBuilderController.getBuilderState",
  () => ({ __esModule: true, default: jest.fn() }),
  { virtual: true }
);
jest.mock(
  "@salesforce/apex/RLM_DeltaTermBuilderController.addTerm",
  () => ({ __esModule: true, default: jest.fn() }),
  { virtual: true }
);

const QUOTE_ID = "0Q0000000000001AAA";

// eslint-disable-next-line @lwc/lwc/no-async-operation
const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

function createRail() {
  const element = createElement("c-dlm-term-rail", { is: DlmTermsRail });
  document.body.appendChild(element);
  return element;
}

// The rail adopts a quote from a `context` message on the DLM channel; grab the subscribe handler and
// drive it exactly as the header would.
function sendMessage(message) {
  const handler = subscribe.mock.calls[0][2];
  handler(message);
}

function libraryButton(element) {
  return element.shadowRoot.querySelector(".dl-tb-add-term__library");
}

function publishesOfType(type) {
  return publish.mock.calls.filter((c) => c[2] && c[2].type === type);
}

describe("c-dlm-term-rail — Add from Library", () => {
  afterEach(() => {
    while (document.body.firstChild) {
      document.body.removeChild(document.body.firstChild);
    }
    jest.clearAllMocks();
  });

  it("renders an Add from Library button", () => {
    const element = createRail();
    expect(libraryButton(element)).not.toBeNull();
  });

  it("opens the library modal and refreshes on a finished result", async () => {
    getBuilderState
      .mockResolvedValueOnce(
        JSON.stringify({
          isSuccess: true,
          terms: [{ id: "t1", name: "Existing" }],
          selectedTermId: "t1"
        })
      )
      .mockResolvedValueOnce(
        JSON.stringify({
          isSuccess: true,
          terms: [
            { id: "t1", name: "Existing" },
            { id: "t2", name: "From Library" }
          ],
          selectedTermId: "t1"
        })
      );
    DlmTermLibraryModal.open.mockResolvedValue({
      status: "finished",
      termLineId: "0QL000000000002AAA",
      addedFareCount: 2
    });

    const element = createRail();
    sendMessage({ type: "context", quoteId: QUOTE_ID, source: "header" });
    await flushPromises();
    expect(getBuilderState).toHaveBeenCalledTimes(1);

    libraryButton(element).dispatchEvent(new CustomEvent("click"));
    await flushPromises();

    expect(DlmTermLibraryModal.open).toHaveBeenCalledWith({
      quoteId: QUOTE_ID,
      size: "medium",
      label: "Term Library"
    });
    // handleTermAdded reloaded (2nd getBuilderState) and broadcast termsChanged for the workspace/header.
    expect(getBuilderState).toHaveBeenCalledTimes(2);
    expect(publishesOfType("termsChanged").length).toBe(1);
    expect(addTerm).not.toHaveBeenCalled();
  });

  it("does not refresh when the modal is cancelled", async () => {
    getBuilderState.mockResolvedValue(
      JSON.stringify({
        isSuccess: true,
        terms: [{ id: "t1", name: "Existing" }],
        selectedTermId: "t1"
      })
    );
    DlmTermLibraryModal.open.mockResolvedValue({ status: "cancel" });

    const element = createRail();
    sendMessage({ type: "context", quoteId: QUOTE_ID, source: "header" });
    await flushPromises();

    libraryButton(element).dispatchEvent(new CustomEvent("click"));
    await flushPromises();

    expect(DlmTermLibraryModal.open).toHaveBeenCalledTimes(1);
    // Only the initial load ran; no reload and no termsChanged broadcast.
    expect(getBuilderState).toHaveBeenCalledTimes(1);
    expect(publishesOfType("termsChanged").length).toBe(0);
  });
});
