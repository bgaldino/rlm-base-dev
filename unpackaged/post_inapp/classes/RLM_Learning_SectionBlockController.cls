public with sharing class RLM_Learning_SectionBlockController {
  @AuraEnabled(cacheable=true)
  public static List<RLM_Learning_Section__c> getSectionsByType(
    String sectionType,
    String pageType
  ) {
    if (String.isEmpty(sectionType)) {
      throw new AuraHandledException('Section type cannot be null or empty.');
    }

    if (String.isEmpty(pageType)) {
      throw new AuraHandledException('Page type cannot be null or empty.');
    }
    List<RLM_Learning_Page__c> result = [
      SELECT Id FROM RLM_Learning_Page__c WHERE RLM_Learning_Type__c = :pageType WITH USER_MODE
    ];
    if (result.isEmpty()) {
      throw new AuraHandledException('No Page type is available.');
    }
    String pageId = result[0].Id;
    return getSectionsByPageId(sectionType, pageId);
  }

  @AuraEnabled(cacheable=true)
  public static List<RLM_Learning_Section__c> getSectionsByPageId(
    String sectionType,
    String pageId
  ) {
    if (String.isEmpty(sectionType)) {
      throw new AuraHandledException('Section type cannot be null or empty.');
    }

    if (String.isEmpty(pageId)) {
      throw new AuraHandledException('Page type cannot be null or empty.');
    }

    List<RLM_Learning_Section__c> sections = [
      SELECT
        Id,
        RLM_Learning_Header__c,
        RLM_Learning_Sub_Header__c,
        RLM_Learning_Video_Link__c,
        RLM_Learning_Icon__r.RLM_Learning_Type__c,
        RLM_Learning_Icon__r.RLM_Learning_Size__c,
        (
          SELECT
            Id,
            RLM_Learning_Order_Sequence__c,
            RLM_Learning_Block__r.Id,
            RLM_Learning_Block__r.Name,
            RLM_Learning_Block__r.RLM_Learning_Header__c,
            RLM_Learning_Block__r.RLM_Learning_Sub_Header__c,
            RLM_Learning_Block__r.RLM_Learning_Icon__r.RLM_Learning_Type__c,
            RLM_Learning_Block__r.RLM_Learning_Icon__r.RLM_Learning_Size__c,
            RLM_Learning_Block__r.RLM_Learning_Action__c,
            RLM_Learning_Block__r.RLM_Learning_ActionText__c,
            RLM_Learning_Block__r.RLM_Learning_Description__c
          FROM SectionBlocks__r
          WHERE RLM_Learning_Block__r.RLM_Learning_Active__c = TRUE
          ORDER BY RLM_Learning_Order_Sequence__c ASC
        )
      FROM RLM_Learning_Section__c
      WHERE
        RecordType.DeveloperName = :sectionType
        AND RLM_Learning_Active__c = TRUE
        AND RLM_Learning_Page__c = :pageId
      WITH USER_MODE
    ];
    return sections;
  }
  public static List<RLM_Learning_DynamicLink__c> getDynamicLinks(
    List<String> dynamicLinkIds
  ) {
    if (dynamicLinkIds.isEmpty()) {
      return new List<RLM_Learning_DynamicLink__c>();
    } else {
      return [
        SELECT
          Id,
          Name,
          RLM_Learning_App_API_Name__c,
          RLM_Learning_Identity__c,
          RLM_Learning_Object__c,
          RLM_Learning_Filter_Name__c,
          RLM_Learning_Page_Name__c,
          RLM_Learning_Relationship_API_Name__c,
          RLM_Learning_Text_Value__c,
          RLM_Learning_Where_Condition__c,
          RecordType.DeveloperName,
          RLM_Learning_Page__c,
          RLM_Learning_Section__c,
          RLM_Learning_Link__c,
          RLM_Learning_Relative_Url__c,
          RLM_Learning_Setup_Page__c,
          RLM_Learning_Site_Name__c
        FROM RLM_Learning_DynamicLink__c
        WHERE Id IN :dynamicLinkIds
        WITH USER_MODE
      ];
    }
  }

  @AuraEnabled(cacheable=true)
  public static List<Map<String, Object>> getSectionWithBlockBySectionId(
    String sectionId
  ) {
    if (String.isEmpty(sectionId)) {
      throw new AuraHandledException('Section id cannot be null or empty.');
    }

    List<RLM_Learning_Section__c> sections = [
      SELECT
        Id,
        RLM_Learning_Header__c,
        RLM_Learning_Sub_Header__c,
        RLM_Learning_Video_Link__c,
        RLM_Learning_Icon__r.RLM_Learning_Type__c,
        RLM_Learning_Icon__r.RLM_Learning_Size__c,
        (
          SELECT
            Id,
            RLM_Learning_Order_Sequence__c,
            RLM_Learning_Block__r.Id,
            RLM_Learning_Block__r.Name,
            RLM_Learning_Block__r.RLM_Learning_Header__c,
            RLM_Learning_Block__r.RLM_Learning_Sub_Header__c,
            RLM_Learning_Block__r.RLM_Learning_Icon__r.RLM_Learning_Type__c,
            RLM_Learning_Block__r.RLM_Learning_Icon__r.RLM_Learning_Size__c,
            RLM_Learning_Block__r.RLM_Learning_Action__c,
            RLM_Learning_Block__r.RLM_Learning_ActionText__c,
            RLM_Learning_Block__r.RLM_Learning_Description__c
          FROM SectionBlocks__r
          WHERE RLM_Learning_Block__r.RLM_Learning_Active__c = TRUE
          ORDER BY RLM_Learning_Order_Sequence__c ASC
        )
      FROM RLM_Learning_Section__c
      WHERE Id = :sectionId AND RLM_Learning_Active__c = TRUE
      WITH USER_MODE
    ];
    List<Map<String, Object>> result = new List<Map<String, Object>>();

    Map<String, Object> sectionMap = new Map<String, Object>();
    List<String> dynamicLinkIds = new List<String>();
    sectionMap.put('section', sections[0]);

    RLM_Learning_SectionBlock__c sectionBlock = sections[0].SectionBlocks__r[0];
    Map<String, Object> blockMap = new Map<String, Object>();
    blockMap.put('blockId', sectionBlock.RLM_Learning_Block__r.Id);
    blockMap.put('header', sectionBlock.RLM_Learning_Block__r.RLM_Learning_Header__c);
    blockMap.put('subHeader', sectionBlock.RLM_Learning_Block__r.RLM_Learning_Sub_Header__c);
    blockMap.put('icon', sectionBlock.RLM_Learning_Block__r.RLM_Learning_Icon__r.RLM_Learning_Type__c);
    blockMap.put('iconSize', sectionBlock.RLM_Learning_Block__r.RLM_Learning_Icon__r.RLM_Learning_Size__c);
    blockMap.put('action', sectionBlock.RLM_Learning_Block__r.RLM_Learning_Action__c);
    blockMap.put('actionText', sectionBlock.RLM_Learning_Block__r.RLM_Learning_ActionText__c);
    blockMap.put('description', sectionBlock.RLM_Learning_Block__r.RLM_Learning_Description__c);
    if (sectionBlock.RLM_Learning_Block__r.RLM_Learning_Action__c != null) {
      dynamicLinkIds.add(sectionBlock.RLM_Learning_Block__r.RLM_Learning_Action__c);
    }

    sectionMap.put('dynamicLinks', getDynamicLinks(dynamicLinkIds));
    sectionMap.put('block', blockMap);
    result.add(sectionMap);

    return result;
  }

  @AuraEnabled(cacheable=true)
  public static List<Map<String, Object>> getSectionsWithBlocksByType(
    String sectionType,
    String pageType
  ) {
    if (String.isEmpty(sectionType)) {
      throw new AuraHandledException('Section type cannot be null or empty.');
    }
    if (String.isEmpty(pageType)) {
      throw new AuraHandledException('Page type cannot be null or empty.');
    }

    return getResultFromSections(getSectionsByType(sectionType, pageType));
  }

  @AuraEnabled(cacheable=true)
  public static List<Map<String, Object>> getSectionsWithBlocksByPageId(
    String sectionType,
    String pageId
  ) {
    if (String.isEmpty(sectionType)) {
      throw new AuraHandledException('Section type cannot be null or empty.');
    }
    if (String.isEmpty(pageId)) {
      throw new AuraHandledException('Page type cannot be null or empty.');
    }

    return getResultFromSections(getSectionsByPageId(sectionType, pageId));
  }
  private static List<Map<String, Object>> getResultFromSections(
    List<RLM_Learning_Section__c> sections
  ) {
    // First pass: collect every referenced DynamicLink id across all sections/blocks
    // so the lookup query runs ONCE, instead of once per block inside the loops.
    Set<String> allDynamicLinkIds = new Set<String>();
    for (RLM_Learning_Section__c section : sections) {
      for (RLM_Learning_SectionBlock__c sectionBlock : section.SectionBlocks__r) {
        String action = sectionBlock.RLM_Learning_Block__r.RLM_Learning_Action__c;
        if (action != null) {
          allDynamicLinkIds.add(action);
        }
      }
    }

    // Single bulk query, keyed by Id for per-section mapping below.
    Map<String, RLM_Learning_DynamicLink__c> dynamicLinksById = new Map<String, RLM_Learning_DynamicLink__c>();
    for (
      RLM_Learning_DynamicLink__c link : getDynamicLinks(
        new List<String>(allDynamicLinkIds)
      )
    ) {
      dynamicLinksById.put(String.valueOf(link.Id), link);
    }

    List<Map<String, Object>> result = new List<Map<String, Object>>();

    for (RLM_Learning_Section__c section : sections) {
      Map<String, Object> sectionMap = new Map<String, Object>();
      List<Map<String, Object>> blocks = new List<Map<String, Object>>();
      // De-duplicated set of this section's action ids, so each section carries only
      // its own dynamic links (preserves the prior per-section grouping).
      Set<String> sectionActionIds = new Set<String>();
      sectionMap.put('section', section);

      for (RLM_Learning_SectionBlock__c sectionBlock : section.SectionBlocks__r) {
        Map<String, Object> blockMap = new Map<String, Object>();
        blockMap.put('blockId', sectionBlock.RLM_Learning_Block__r.Id);
        blockMap.put('header', sectionBlock.RLM_Learning_Block__r.RLM_Learning_Header__c);
        blockMap.put('subHeader', sectionBlock.RLM_Learning_Block__r.RLM_Learning_Sub_Header__c);
        blockMap.put('icon', sectionBlock.RLM_Learning_Block__r.RLM_Learning_Icon__r.RLM_Learning_Type__c);
        blockMap.put('iconSize', sectionBlock.RLM_Learning_Block__r.RLM_Learning_Icon__r.RLM_Learning_Size__c);
        blockMap.put('action', sectionBlock.RLM_Learning_Block__r.RLM_Learning_Action__c);
        blockMap.put('actionText', sectionBlock.RLM_Learning_Block__r.RLM_Learning_ActionText__c);
        blockMap.put('description', sectionBlock.RLM_Learning_Block__r.RLM_Learning_Description__c);

        String action = sectionBlock.RLM_Learning_Block__r.RLM_Learning_Action__c;
        if (action != null) {
          sectionActionIds.add(action);
        }
        blocks.add(blockMap);
      }

      List<RLM_Learning_DynamicLink__c> sectionDynamicLinks = new List<RLM_Learning_DynamicLink__c>();
      for (String linkId : sectionActionIds) {
        if (dynamicLinksById.containsKey(linkId)) {
          sectionDynamicLinks.add(dynamicLinksById.get(linkId));
        }
      }

      sectionMap.put('blocks', blocks);
      sectionMap.put('dynamicLinks', sectionDynamicLinks);
      result.add(sectionMap);
    }

    return result;
  }
}
