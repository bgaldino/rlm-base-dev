public with sharing class RLM_Learning_SectionBlockSequence {
  @AuraEnabled(cacheable=true)
  public static List<RLM_Learning_Block__c> getAllBlocks() {
    return [SELECT Id, Name FROM RLM_Learning_Block__c WITH USER_MODE];
  }

  //get blocks for a section from the sectionblock entity
  @AuraEnabled(cacheable=false)
  public static List<RLM_Learning_SectionBlock__c> getBlocksForSection(String sectionId) {
    if (String.isEmpty(sectionId)) {
      throw new AuraHandledException('Section Id cannot be null or empty.');
    }
    return [
      SELECT Id, RLM_Learning_Block__c
      FROM RLM_Learning_SectionBlock__c
      WHERE RLM_Learning_Section__c = :sectionId
      WITH USER_MODE
      ORDER BY RLM_Learning_Order_Sequence__c ASC
    ];
  }

  @AuraEnabled
  public static void updateSectionBlocks(
    String sectionId,
    List<String> blockIds
  ) {
    if (String.isEmpty(sectionId)) {
      throw new AuraHandledException('Section Id cannot be null or empty.');
    }
    if (blockIds == null) {
      throw new AuraHandledException('Block Ids cannot be null.');
    }
    try {
      List<RLM_Learning_SectionBlock__c> recordsToDelete = [
        SELECT Id
        FROM RLM_Learning_SectionBlock__c
        WHERE RLM_Learning_Section__c = :sectionId
        WITH USER_MODE
      ];

      if (!recordsToDelete.isEmpty()) {
        // allOrNone = true: any delete failure throws and rolls back, so we never
        // leave stale junction rows behind and then insert a duplicate set.
        Database.delete(recordsToDelete, true, AccessLevel.USER_MODE);
      }

      List<RLM_Learning_SectionBlock__c> junctionRecords = new List<RLM_Learning_SectionBlock__c>();
      for (Integer i = 0; i < blockIds.size(); i++) {
        RLM_Learning_SectionBlock__c record = new RLM_Learning_SectionBlock__c();
        record.RLM_Learning_Section__c = sectionId;
        record.RLM_Learning_Block__c = blockIds[i];
        record.RLM_Learning_Order_Sequence__c = i + 1;
        junctionRecords.add(record);
      }
      // These are always new rows (no Id / external id), so insert.
      insert as user junctionRecords;
    } catch (Exception e) {
      throw new AuraHandledException(e.getMessage());
    }
  }
}
