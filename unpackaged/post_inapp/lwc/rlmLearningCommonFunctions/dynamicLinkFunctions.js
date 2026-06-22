import getObjectIdFromQuery from "@salesforce/apex/RLM_Learning_DynamicLinkHelper.getObjectIdFromQuery";
import getDynamicLinkByIdentity from "@salesforce/apex/RLM_Learning_DynamicLinkHelper.getDynamicLinkByIdentity";
import getRecordIdFromDynamicLinkType from "@salesforce/apex/RLM_Learning_DynamicLinkHelper.getRecordIdFromDynamicLinkType";
import getSiteUrl from "@salesforce/apex/RLM_Learning_DynamicLinkHelper.getSiteUrl";
import getSetupPageLink from "@salesforce/apex/RLM_Learning_DynamicLinkHelper.getSetupPageLink";

// Apex lookups can legitimately return no rows when an admin-authored
// whereCondition / name matches nothing. Throw a clear, actionable error
// instead of a cryptic "cannot read property Id of undefined".
const firstOrThrow = (rows, label) => {
  if (!rows || rows.length === 0) {
    throw new Error("No record found for " + label);
  }
  return rows[0];
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
    case "RecordPage":
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
    case "RecordRelationshipPage":
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
    case "WebPage":
      pageReference = {
        type: "standard__webPage",
        attributes: {
          url: dynamicLink.RLM_Learning_Link__c
        }
      };
      break;
    case "CommunityPage":
      const communityPage = await getRecordIdFromDynamicLinkType({
        dyanmicLinkType: dynamicLink.RecordType.DeveloperName,
        whereCondition: "Name='" + dynamicLink.RLM_Learning_Site_Name__c + "'"
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
          url: siteUrl
        }
      };
      break;
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
    case "SurveyRecordPage":
      const survey = await getRecordIdFromDynamicLinkType({
        dyanmicLinkType: dynamicLink.RecordType.DeveloperName,
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
    case "DPERecordPage":
      const dpeRecord = await getRecordIdFromDynamicLinkType({
        dyanmicLinkType: dynamicLink.RecordType.DeveloperName,
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
    case "FlowRecordPage":
      const flowActiveVersion = await getRecordIdFromDynamicLinkType({
        dyanmicLinkType: dynamicLink.RecordType.DeveloperName,
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
    case "SetupPage":
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
    default:
      pageReference = {
        type: "standard__webPage",
        attributes: {
          url: dynamicLink.RLM_Learning_Link__c
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
  // identifier (A-Z or "_"), stopping at the first character that is not (or the
  // start of the string). "DYN_LINK" is 8 chars, hence the +8 upper bound.
  const isIdentifierChar = (code) =>
    (code >= 65 && code <= 90) || code === 95;
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
  findDynamicLinkIdentifier
};
