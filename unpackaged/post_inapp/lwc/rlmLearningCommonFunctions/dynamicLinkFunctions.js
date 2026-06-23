import getObjectIdFromQuery from "@salesforce/apex/RLM_Learning_DynamicLinkHelper.getObjectIdFromQuery";
import getDynamicLinkByIdentity from "@salesforce/apex/RLM_Learning_DynamicLinkHelper.getDynamicLinkByIdentity";
import getRecordIdFromDynamicLinkType from "@salesforce/apex/RLM_Learning_DynamicLinkHelper.getRecordIdFromDynamicLinkType";
import getSiteUrl from "@salesforce/apex/RLM_Learning_DynamicLinkHelper.getSiteUrl";
import getSetupPageLink from "@salesforce/apex/RLM_Learning_DynamicLinkHelper.getSetupPageLink";

// Escape a value for safe inclusion in HTML built by string concatenation
// (attribute values and text content) before it is rendered as rich text.
const escapeHtml = (value) =>
  String(value == null ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");

// Allowlist for embedded video <iframe> src values: only https URLs from known
// video hosts may be embedded, so admin-authored / mis-imported data can't embed
// an arbitrary origin. Returns the url when allowed, otherwise null.
const ALLOWED_VIDEO_HOSTS = new Set([
  "play.vidyard.com",
  "vidyard.com",
  "www.youtube.com",
  "youtube.com",
  "www.youtube-nocookie.com",
  "youtube-nocookie.com",
  "player.vimeo.com",
  "vimeo.com"
]);

const safeVideoUrl = (url) => {
  if (!url) {
    return null;
  }
  let parsed;
  try {
    parsed = new URL(url);
  } catch {
    return null;
  }
  if (parsed.protocol !== "https:") {
    return null;
  }
  return ALLOWED_VIDEO_HOSTS.has(parsed.host.toLowerCase()) ? url : null;
};

// Validate a URL before it becomes a standard__webPage navigation target: allow
// only http(s) absolute URLs or app-relative paths, blocking unsafe schemes
// (javascript:, data:, vbscript:, ...). Throws on anything else so the caller's
// try/catch surfaces it instead of navigating somewhere unsafe.
const requireSafeUrl = (url) => {
  const trimmed = String(url == null ? "" : url).trim();
  if (/^https?:\/\//i.test(trimmed) || trimmed.startsWith("/")) {
    return trimmed;
  }
  throw new Error("Unsafe or invalid link URL: " + url);
};

// Apex lookups can legitimately return no rows when an admin-authored
// whereCondition / name matches nothing. Throw a clear, actionable error
// instead of a cryptic "cannot read property Id of undefined".
const firstOrThrow = (rows, label) => {
  if (!rows || rows.length === 0) {
    throw new Error("No record found for " + label);
  }
  return rows[0];
};

// Salesforce wire/Apex/LDS errors arrive in several shapes: { body: { message } },
// { body: [{ message }, ...] } (FIELD_/DML errors), or a plain { message }. Reduce any
// of them to one human-readable string so a toast never renders blank, falling back to
// `fallback` when nothing usable is present.
const reduceErrorMessage = (error, fallback = "Unknown error") => {
  if (!error) {
    return fallback;
  }
  const body = error.body;
  if (Array.isArray(body)) {
    const joined = body
      .map((e) => e && e.message)
      .filter(Boolean)
      .join(", ");
    return joined || fallback;
  }
  return (body && body.message) || error.message || fallback;
};

const getPageReferenceByDynamicType = async (dynamicLink) => {
  var pageReference;
  switch (dynamicLink.RecordType.DeveloperName) {
    case "NamedPage":
      pageReference = {
        type: "standard__app",
        attributes: {
          appTarget: dynamicLink.RLM_Learning_App_API_Name__c,
          pageRef: {
            type: "standard__namedPage",
            attributes: {
              pageName: dynamicLink.RLM_Learning_Page_Name__c
            }
          }
        }
      };
      break;
    case "APINamePage":
      pageReference = {
        type: "standard__app",
        attributes: {
          appTarget: dynamicLink.RLM_Learning_App_API_Name__c,
          pageRef: {
            type: "standard__navItemPage",
            attributes: {
              apiName: dynamicLink.RLM_Learning_Page_Name__c
            }
          }
        }
      };
      break;
    case "AppPage":
      pageReference = {
        type: "standard__app",
        attributes: {
          appTarget: dynamicLink.RLM_Learning_App_API_Name__c
        }
      };
      break;
    case "ObjectPage":
      pageReference = {
        type: "standard__app",
        attributes: {
          appTarget: dynamicLink.RLM_Learning_App_API_Name__c,
          pageRef: {
            type: "standard__objectPage",
            attributes: {
              objectApiName: dynamicLink.RLM_Learning_Object__c,
              actionName: "list"
            }
          }
        }
      };
      if (dynamicLink.RLM_Learning_Filter_Name__c) {
        pageReference.attributes.pageRef.state = {
          filterName: dynamicLink.RLM_Learning_Filter_Name__c
        };
      }
      break;
    case "RecordPage": {
      // execute select query and get the id
      const SELECTQUERYRESULT = await getObjectIdFromQuery({
        objectAPIName: dynamicLink.RLM_Learning_Object__c,
        whereCondition: dynamicLink.RLM_Learning_Where_Condition__c
      });
      // get the id from the result
      const objectId = firstOrThrow(
        SELECTQUERYRESULT,
        "RecordPage: " + dynamicLink.RLM_Learning_Object__c
      ).Id;

      pageReference = {
        type: "standard__app",
        attributes: {
          appTarget: dynamicLink.RLM_Learning_App_API_Name__c,
          pageRef: {
            type: "standard__recordPage",
            attributes: {
              objectApiName: dynamicLink.RLM_Learning_Object__c,
              actionName: "view",
              recordId: objectId
            }
          }
        }
      };
      break;
    }
    case "RecordRelationshipPage": {
      // execute select query and get the id
      const SELECTRESULT = await getObjectIdFromQuery({
        objectAPIName: dynamicLink.RLM_Learning_Object__c,
        whereCondition: dynamicLink.RLM_Learning_Where_Condition__c
      });
      // get the id from the result
      const objectResultId = firstOrThrow(
        SELECTRESULT,
        "RecordRelationshipPage: " + dynamicLink.RLM_Learning_Object__c
      ).Id;

      pageReference = {
        type: "standard__app",
        attributes: {
          appTarget: dynamicLink.RLM_Learning_App_API_Name__c,
          pageRef: {
            type: "standard__recordRelationshipPage",
            attributes: {
              objectApiName: dynamicLink.RLM_Learning_Object__c,
              actionName: "view",
              recordId: objectResultId,
              relationshipApiName: dynamicLink.RLM_Learning_Relationship_API_Name__c
            }
          }
        }
      };
      break;
    }
    case "WebPage":
      pageReference = {
        type: "standard__webPage",
        attributes: {
          url: requireSafeUrl(dynamicLink.RLM_Learning_Link__c)
        }
      };
      break;
    case "CommunityPage": {
      const communityPage = await getRecordIdFromDynamicLinkType({
        dynamicLinkType: dynamicLink.RecordType.DeveloperName,
        // Escape single quotes so a site name like "Bob's Portal" can't break the
        // SOQL literal (USER_MODE on the Apex side already bounds the query).
        whereCondition:
          "Name='" +
          String(dynamicLink.RLM_Learning_Site_Name__c || "").replace(
            /'/g,
            "\\'"
          ) +
          "'"
      });
      let siteUrl = await getSiteUrl({
        networkId: firstOrThrow(
          communityPage,
          "CommunityPage: " + dynamicLink.RLM_Learning_Site_Name__c
        ).Id
      });
      if (dynamicLink.RLM_Learning_Relative_Url__c) {
        siteUrl += dynamicLink.RLM_Learning_Relative_Url__c;
      }
      pageReference = {
        type: "standard__webPage",
        attributes: {
          url: requireSafeUrl(siteUrl)
        }
      };
      break;
    }
    case "InAppDetailsPage":
      pageReference = {
        type: "standard__app",
        attributes: {
          appTarget: "c__RLM_Learning_Home",
          pageRef: {
            type: "standard__navItemPage",
            attributes: {
              apiName: "RLM_Learning_Application_Details_Page"
            }
          }
        }
      };
      break;
    case "SurveyRecordPage": {
      const survey = await getRecordIdFromDynamicLinkType({
        dynamicLinkType: dynamicLink.RecordType.DeveloperName,
        whereCondition: dynamicLink.RLM_Learning_Where_Condition__c
      });
      pageReference = {
        type: "standard__webPage",
        attributes: {
          url:
            "/survey/builderApp.app?surveyId=" +
            firstOrThrow(survey, "SurveyRecordPage").Id
        }
      };
      break;
    }
    case "DPERecordPage": {
      const dpeRecord = await getRecordIdFromDynamicLinkType({
        dynamicLinkType: dynamicLink.RecordType.DeveloperName,
        whereCondition: dynamicLink.RLM_Learning_Where_Condition__c
      });
      pageReference = {
        type: "standard__webPage",
        attributes: {
          url:
            "/builder_industries_dataprocessingengine/dataProcessingEngine.app?dataProcessingEngineId=" +
            firstOrThrow(dpeRecord, "DPERecordPage").Id
        }
      };
      break;
    }
    case "FlowRecordPage": {
      const flowActiveVersion = await getRecordIdFromDynamicLinkType({
        dynamicLinkType: dynamicLink.RecordType.DeveloperName,
        whereCondition: dynamicLink.RLM_Learning_Where_Condition__c
      });
      pageReference = {
        type: "standard__webPage",
        attributes: {
          url:
            "/builder_platform_interaction/flowBuilder.app?flowId=" +
            firstOrThrow(flowActiveVersion, "FlowRecordPage").ActiveVersionId
        }
      };
      break;
    }
    case "SetupPage": {
      const records = await getObjectIdFromQuery({
        objectAPIName: dynamicLink.RLM_Learning_Setup_Page__c,
        whereCondition: dynamicLink.RLM_Learning_Where_Condition__c
      });
      const setupPage = await getSetupPageLink({
        objectAPIName: dynamicLink.RLM_Learning_Setup_Page__c,
        record: firstOrThrow(records, "SetupPage").Id
      });

      pageReference = {
        type: "standard__webPage",
        attributes: {
          url: setupPage
        }
      };
      break;
    }
    default:
      pageReference = {
        type: "standard__webPage",
        attributes: {
          url: requireSafeUrl(dynamicLink.RLM_Learning_Link__c)
        }
      };
      break;
  }
  // Only page references that carry a pageRef (standard__app navItem/named/object/record
  // pages) can take a state. WebPage/CommunityPage/etc. references have only `url`, so
  // guard against writing state onto a missing pageRef (would throw a TypeError).
  if (
    dynamicLink.RLM_Learning_Page__c != null &&
    dynamicLink.RLM_Learning_Page__c !== undefined &&
    pageReference.attributes.pageRef
  ) {
    pageReference.attributes.pageRef.state = {
      c__pageId: dynamicLink.RLM_Learning_Page__c
    };
  }
  return pageReference;
};

const getDynamicLinkByIdentifier = async (identifier) => {
  const SELECTQUERYRESULT = await getDynamicLinkByIdentity({
    identifier: identifier
  });
  return SELECTQUERYRESULT;
};

const findDynamicLinkIdentifier = (input, middlePosition) => {
  // Walk backwards from middlePosition while the character is part of the
  // identifier (A-Z, a-z, 0-9 or "_"), stopping at the first character that is not
  // (or the start of the string). Identity values are mixed-case (e.g.
  // "PriceManagement_Getstarted_DYN_LINK"). "DYN_LINK" is 8 chars, hence the +8.
  const isIdentifierChar = (code) =>
    (code >= 48 && code <= 57) || // 0-9
    (code >= 65 && code <= 90) || // A-Z
    (code >= 97 && code <= 122) || // a-z
    code === 95; // _
  let spacePosition = middlePosition;
  while (
    spacePosition >= 0 &&
    isIdentifierChar(input.charCodeAt(spacePosition))
  ) {
    spacePosition--;
  }
  return input.substring(spacePosition + 1, middlePosition + 8);
};
export {
  getDynamicLinkByIdentifier,
  getPageReferenceByDynamicType,
  findDynamicLinkIdentifier,
  escapeHtml,
  safeVideoUrl,
  requireSafeUrl,
  reduceErrorMessage
};
