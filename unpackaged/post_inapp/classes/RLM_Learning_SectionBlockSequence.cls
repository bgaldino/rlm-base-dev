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
        // Using Database.delete for finer error control
        Database.DeleteResult[] results = Database.delete(
          recordsToDelete,
          false,
          AccessLevel.USER_MODE
        );

        // Handle errors
        for (Integer i = 0; i < results.size(); i++) {
          if (!results[i].isSuccess()) {
            // Log the error details
            System.debug(
              'Error deleting record with Id: ' + recordsToDelete[i].Id
            );
            System.debug(
              'Error message: ' + results[i].getErrors()[0].getMessage()
            );
          }
        }
      }
      List<RLM_Learning_SectionBlock__c> junctionRecords = new List<RLM_Learning_SectionBlock__c>();

      // Create or update a record
      for (Integer i = 0; i < blockIds.size(); i++) {
        RLM_Learning_SectionBlock__c record = new RLM_Learning_SectionBlock__c();
        record.RLM_Learning_Section__c = sectionId;
        record.RLM_Learning_Block__c = blockIds[i];
        record.RLM_Learning_Order_Sequence__c = i + 1;
        junctionRecords.add(record);
      }
      // Perform the upsert
      upsert as user junctionRecords;
    } catch (Exception e) {
      throw new AuraHandledException(e.getMessage());
    }
  }
}
