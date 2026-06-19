public with sharing class SectionBlockSequence {
  @AuraEnabled(cacheable=true)
  public static List<Block__c> getAllBlocks() {
    return [SELECT Id, Name FROM Block__c WITH USER_MODE];
  }

  //get blocks for a section from the sectionblock entity
  @AuraEnabled(cacheable=false)
  public static List<SectionBlock__c> getBlocksForSection(String sectionId) {
    if (String.isEmpty(sectionId)) {
      throw new AuraHandledException('Section Id cannot be null or empty.');
    }
    return [
      SELECT Id, Block__c
      FROM SectionBlock__c
      WHERE Section__c = :sectionId
      WITH USER_MODE
      ORDER BY Order_Sequence__c ASC
    ];
  }

  @AuraEnabled
  public static void updateSectionBlocks(
    String sectionId,
    List<String> blockIds
  ) {
    try {
      List<SectionBlock__c> recordsToDelete = [
        SELECT Id
        FROM SectionBlock__c
        WHERE Section__c = :sectionId
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
      List<SectionBlock__c> junctionRecords = new List<SectionBlock__c>();

      // Create or update a record
      for (Integer i = 0; i < blockIds.size(); i++) {
        SectionBlock__c record = new SectionBlock__c();
        record.Section__c = sectionId;
        record.Block__c = blockIds[i];
        record.Order_Sequence__c = i + 1;
        junctionRecords.add(record);
      }
      // Perform the upsert
      upsert as user junctionRecords;
    } catch (Exception e) {
      throw new AuraHandledException(e.getMessage());
    }
  }
}
