public with sharing class SectionBlockController {
  @AuraEnabled(cacheable=true)
  public static List<Section__c> getSectionsByType(
    String sectionType,
    String pageType
  ) {
    if (String.isEmpty(sectionType)) {
      throw new AuraHandledException('Section type cannot be null or empty.');
    }

    if (String.isEmpty(pageType)) {
      throw new AuraHandledException('Page type cannot be null or empty.');
    }
    List<Page__c> result = [
      SELECT Id FROM Page__c WHERE Type__c = :pageType WITH USER_MODE
    ];
    if (result.isEmpty()) {
      throw new AuraHandledException('No Page type is available.');
    }
    String pageId = result[0].Id;
    return getSectionsByPageId(sectionType, pageId);
  }

  @AuraEnabled(cacheable=true)
  public static List<Section__c> getSectionsByPageId(
    String sectionType,
    String pageId
  ) {
    if (String.isEmpty(sectionType)) {
      throw new AuraHandledException('Section type cannot be null or empty.');
    }

    if (String.isEmpty(pageId)) {
      throw new AuraHandledException('Page type cannot be null or empty.');
    }

    List<Section__c> sections = [
      SELECT
        Id,
        Header__c,
        Sub_Header__c,
        Video_Link__c,
        Icon__r.Type__c,
        Icon__r.Size__c,
        (
          SELECT
            Id,
            Order_Sequence__c,
            Block__r.Id,
            Block__r.Name,
            Block__r.Header__c,
            Block__r.Sub_Header__c,
            Block__r.Icon__r.Type__c,
            Block__r.Icon__r.Size__c,
            Block__r.Action__c,
            Block__r.ActionText__c,
            Block__r.Description__c
          FROM SectionBlocks__r
          WHERE Block__r.Active__c = TRUE
          ORDER BY Order_Sequence__c ASC
        )
      FROM Section__c
      WHERE
        RecordType.DeveloperName = :sectionType
        AND Active__c = TRUE
        AND Page__c = :pageId
      WITH USER_MODE
    ];
    return sections;
  }
  public static List<DynamicLink__c> getDynamicLinks(
    List<String> dynamicLinkIds
  ) {
    if (dynamicLinkIds.isEmpty()) {
      return new List<DynamicLink__c>();
    } else {
      return [
        SELECT
          Id,
          Name,
          App_API_Name__c,
          Identity__c,
          Object__c,
          Filter_Name__c,
          Page_Name__c,
          Relationship_API_Name__c,
          Text_Value__c,
          Where_Condition__c,
          RecordType.DeveloperName,
          Page__c,
          Section__c,
          Link__c,
          Relative_Url__c,
          Setup_Page__c,
          Site_Name__c
        FROM DynamicLink__c
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

    List<Section__c> sections = [
      SELECT
        Id,
        Header__c,
        Sub_Header__c,
        Video_Link__c,
        Icon__r.Type__c,
        Icon__r.Size__c,
        (
          SELECT
            Id,
            Order_Sequence__c,
            Block__r.Id,
            Block__r.Name,
            Block__r.Header__c,
            Block__r.Sub_Header__c,
            Block__r.Icon__r.Type__c,
            Block__r.Icon__r.Size__c,
            Block__r.Action__c,
            Block__r.ActionText__c,
            Block__r.Description__c
          FROM SectionBlocks__r
          WHERE Block__r.Active__c = TRUE
          ORDER BY Order_Sequence__c ASC
        )
      FROM Section__c
      WHERE Id = :sectionId AND Active__c = TRUE
      WITH USER_MODE
    ];
    List<Map<String, Object>> result = new List<Map<String, Object>>();

    Map<String, Object> sectionMap = new Map<String, Object>();
    List<String> dynamicLinkIds = new List<String>();
    sectionMap.put('section', sections[0]);

    SectionBlock__c sectionBlock = sections[0].SectionBlocks__r[0];
    Map<String, Object> blockMap = new Map<String, Object>();
    blockMap.put('blockId', sectionBlock.Block__r.Id);
    blockMap.put('header', sectionBlock.Block__r.Header__c);
    blockMap.put('subHeader', sectionBlock.Block__r.Sub_Header__c);
    blockMap.put('icon', sectionBlock.Block__r.Icon__r.Type__c);
    blockMap.put('iconSize', sectionBlock.Block__r.Icon__r.Size__c);
    blockMap.put('action', sectionBlock.Block__r.Action__c);
    blockMap.put('actionText', sectionBlock.Block__r.ActionText__c);
    blockMap.put('description', sectionBlock.Block__r.Description__c);
    if (sectionBlock.Block__r.Action__c != null) {
      dynamicLinkIds.add(sectionBlock.Block__r.Action__c);
    }

    sectionMap.put('dynamicLinks', getDynamicLinks(dynamicLinkIds));
    sectionMap.put('block', blockMap);
    result.add(sectionMap);

    System.debug('Result being returned: ' + JSON.serialize(result));
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
    List<Section__c> sections
  ) {
    List<Map<String, Object>> result = new List<Map<String, Object>>();

    for (Section__c section : sections) {
      Map<String, Object> sectionMap = new Map<String, Object>();
      List<String> dynamicLinkIds = new List<String>();
      sectionMap.put('section', section);
      sectionMap.put('blocks', new List<Map<String, Object>>());

      for (SectionBlock__c sectionBlock : section.SectionBlocks__r) {
        Map<String, Object> blockMap = new Map<String, Object>();
        blockMap.put('blockId', sectionBlock.Block__r.Id);
        blockMap.put('header', sectionBlock.Block__r.Header__c);
        blockMap.put('subHeader', sectionBlock.Block__r.Sub_Header__c);
        blockMap.put('icon', sectionBlock.Block__r.Icon__r.Type__c);
        blockMap.put('iconSize', sectionBlock.Block__r.Icon__r.Size__c);
        blockMap.put('action', sectionBlock.Block__r.Action__c);
        blockMap.put('actionText', sectionBlock.Block__r.ActionText__c);
        blockMap.put('description', sectionBlock.Block__r.Description__c);
        if (sectionBlock.Block__r.Action__c != null) {
          dynamicLinkIds.add(sectionBlock.Block__r.Action__c);
        }

        sectionMap.put('dynamicLinks', getDynamicLinks(dynamicLinkIds));
        ((List<Map<String, Object>>) sectionMap.get('blocks')).add(blockMap);
      }
      result.add(sectionMap);
    }

    System.debug('Result being returned: ' + JSON.serialize(result));
    return result;
  }
}
