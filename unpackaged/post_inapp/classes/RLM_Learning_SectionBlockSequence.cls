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
    Id sectionIdValue = toId(sectionId, 'Section Id');
    return [
      SELECT Id, RLM_Learning_Block__c
      FROM RLM_Learning_SectionBlock__c
      WHERE RLM_Learning_Section__c = :sectionIdValue
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
    // Validate every String -> Id up front (repo apex-classes rule) so a malformed
    // value fails fast with a clear error instead of a raw DML/SOQL exception.
    Id sectionIdValue = toId(sectionId, 'Section Id');
    List<Id> blockIdValues = new List<Id>();
    for (String blockId : blockIds) {
      blockIdValues.add(toId(blockId, 'Block Id'));
    }
    try {
      List<RLM_Learning_SectionBlock__c> recordsToDelete = [
        SELECT Id
        FROM RLM_Learning_SectionBlock__c
        WHERE RLM_Learning_Section__c = :sectionIdValue
        WITH USER_MODE
      ];

      if (!recordsToDelete.isEmpty()) {
        // allOrNone = true: any delete failure throws and rolls back, so we never
        // leave stale junction rows behind and then insert a duplicate set.
        Database.delete(recordsToDelete, true, AccessLevel.USER_MODE);
      }

      List<RLM_Learning_SectionBlock__c> junctionRecords = new List<RLM_Learning_SectionBlock__c>();
      for (Integer i = 0; i < blockIdValues.size(); i++) {
        RLM_Learning_SectionBlock__c record = new RLM_Learning_SectionBlock__c();
        record.RLM_Learning_Section__c = sectionIdValue;
        record.RLM_Learning_Block__c = blockIdValues[i];
        record.RLM_Learning_Order_Sequence__c = i + 1;
        junctionRecords.add(record);
      }
      // These are always new rows (no Id / external id), so insert.
      insert as user junctionRecords;
    } catch (Exception e) {
      throw new AuraHandledException(e.getMessage());
    }
  }

  // Validate a String -> Id before binding it into SOQL/DML (apex-classes rule).
  private static Id toId(String value, String label) {
    try {
      return Id.valueOf(value);
    } catch (Exception e) {
      throw new AuraHandledException(label + ' is not a valid id.');
    }
  }
}
