import { getPageReferenceByDynamicType } from "c/rlmLearningCommonFunctions";
import getRecordIdFromDynamicLinkType from "@salesforce/apex/RLM_Learning_DynamicLinkHelper.getRecordIdFromDynamicLinkType";
import getSiteUrl from "@salesforce/apex/RLM_Learning_DynamicLinkHelper.getSiteUrl";

jest.mock(
  "@salesforce/apex/RLM_Learning_DynamicLinkHelper.getObjectIdFromQuery",
  () => ({ default: jest.fn() }),
  { virtual: true }
);
jest.mock(
  "@salesforce/apex/RLM_Learning_DynamicLinkHelper.getDynamicLinkByIdentity",
  () => ({ default: jest.fn() }),
  { virtual: true }
);
jest.mock(
  "@salesforce/apex/RLM_Learning_DynamicLinkHelper.getRecordIdFromDynamicLinkType",
  () => ({ default: jest.fn() }),
  { virtual: true }
);
jest.mock(
  "@salesforce/apex/RLM_Learning_DynamicLinkHelper.getSiteUrl",
  () => ({ default: jest.fn() }),
  { virtual: true }
);
jest.mock(
  "@salesforce/apex/RLM_Learning_DynamicLinkHelper.getSetupPageLink",
  () => ({ default: jest.fn() }),
  { virtual: true }
);

const communityLink = (siteName) => ({
  RecordType: { DeveloperName: "CommunityPage" },
  RLM_Learning_Site_Name__c: siteName
});

// The SOQL literal the Apex helper receives for a CommunityPage site name.
const whereFor = async (siteName) => {
  await getPageReferenceByDynamicType(communityLink(siteName));
  return getRecordIdFromDynamicLinkType.mock.calls.at(-1)[0].whereCondition;
};

describe("CommunityPage site-name escaping", () => {
  beforeEach(() => {
    getRecordIdFromDynamicLinkType.mockReset();
    getRecordIdFromDynamicLinkType.mockResolvedValue([
      { Id: "0DB000000000001" }
    ]);
    getSiteUrl.mockReset();
    getSiteUrl.mockResolvedValue("https://example.my.site.com/portal");
  });

  it("passes a plain name through unchanged", async () => {
    expect(await whereFor("Partner Portal")).toBe("Name='Partner Portal'");
  });

  it("escapes a single quote", async () => {
    expect(await whereFor("Bob's Portal")).toBe("Name='Bob\\'s Portal'");
  });

  it("escapes a trailing backslash so it cannot consume the closing quote", async () => {
    expect(await whereFor("Portal\\")).toBe("Name='Portal\\\\'");
  });

  it("escapes the backslash before the quote, not the quote's own escape", async () => {
    // Raw: x\' OR Name != '  — quote-only escaping yields x\\' which closes the literal.
    expect(await whereFor("x\\' OR Name != '")).toBe(
      "Name='x\\\\\\' OR Name != \\''"
    );
  });

  it("treats a missing site name as empty", async () => {
    expect(await whereFor(undefined)).toBe("Name=''");
  });

  it("still navigates to the site URL", async () => {
    const ref = await getPageReferenceByDynamicType(
      communityLink("Partner Portal")
    );
    expect(ref).toEqual({
      type: "standard__webPage",
      attributes: { url: "https://example.my.site.com/portal" }
    });
  });
});
