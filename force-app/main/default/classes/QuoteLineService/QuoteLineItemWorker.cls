public with sharing class QuoteLineItemWorker implements IQuoteLineItemWorker {
    private IQuoteLineDAO quoteLineDAO = (IQuoteLineDAO) ServiceRegistry.getInstance('IQuoteLineDAO');
    private Map<String, List<QuoteLineItem>> newListByType = new Map<String, List<QuoteLineItem>>();
    private Map<String, Map<Id, QuoteLineItem>> dirtyMapByType = new Map<String, Map<Id, QuoteLineItem>>();
    private Map<String, Map<Id, QuoteLineItem>> deletedMapByType = new Map<String, Map<Id, QuoteLineItem>>();
    public QuoteLineItemWorker() {
        String sObjectName = QuoteLineItem.SObjectType.getDescribe().getName();
        newListByType.put(sObjectName, new List<QuoteLineItem>());
        dirtyMapByType.put(sObjectName, new Map<Id, QuoteLineItem>());
        deletedMapByType.put(sObjectName, new Map<Id, QuoteLineItem>());

    }

    public void registerNew(QuoteLineItem record) {
        if (String.isNotBlank(record.Id)) {
            throw new QuoteLineItemWorkerException('Only new records can be registered as new');
        }
        String sObjectType = record.getSObjectType().getDescribe().getName();
        newListByType.get(sObjectType).add(record);
    }

    public void registerNew(List<QuoteLineItem> records) {
        for (QuoteLineItem record : records) {
            registerNew(record);
        }
    }

    public void registerDeleted(QuoteLineItem record) {
        if (String.isBlank(record.Id)) {
            throw new QuoteLineItemWorkerException('New records cannot be registered for deletion');
        }
        String sObjectType = record.getSObjectType().getDescribe().getName();
        deletedMapByType.get(sObjectType).put(record.Id, record);
    }

    public void registerDeleted(List<QuoteLineItem> records) {
        for (QuoteLineItem record : records) {
            registerDeleted(record);
        }
    }

    public void registerDirty(QuoteLineItem record) {
        registerDirty(record, new List<SObjectField>());
    }

    public void registerDirty(QuoteLineItem record, List<SObjectField> dirtyFields) {
        if (String.isBlank(record.Id)) {
            throw new QuoteLineItemWorkerException('New records cannot be registered as dirty');
        }
        String sObjectType = record.getSObjectType().getDescribe().getName();
        QuoteLineItem registeredRecord = dirtyMapByType.get(sObjectType).get(record.Id);
        if (registeredRecord == null) {
            registeredRecord = new QuoteLineItem(Id = record.Id);
            dirtyMapByType.get(sObjectType).put(record.Id, registeredRecord);
        }
        for (SObjectField dirtyField : dirtyFields) {
        	registeredRecord.put(dirtyField, record.get(dirtyField));
        }
    }

    public void registerDirty(List<QuoteLineItem> records) {
        for (QuoteLineItem record : records) {
            registerDirty(record);
        }
    }

    public void registerDirty(List<QuoteLineItem> records, List<SObjectField> dirtyFields) {
        for (QuoteLineItem record : records) {
            registerDirty(record, dirtyFields);
        }
    }

    public void commitWork() {
        Savepoint sp = Database.setSavepoint();
        try {
            doCommitWork();
        } catch (Exception e) {
            Database.rollback(sp);
            throw e;
        }
    }

    private void doCommitWork() {
        insertDmlByType();
        updateDmlByType();
        deleteDmlByType();
    }

    private void insertDmlByType() {
        for (String sObjectType : newListByType.keySet()) {            
            quoteLineDAO.insertLines(newListByType.get(sObjectType));
        }
    }

    private void updateDmlByType() {
        for (String sObjectType : dirtyMapByType.keySet()) {
            quoteLineDAO.updateLines(dirtyMapByType.get(sObjectType).values());
        }
    }
    private void deleteDmlByType() {
        for (String sObjectType : dirtyMapByType.keySet()) {
            quoteLineDAO.deleteLines(deletedMapByType.get(sObjectType).values());
        }
    }

    @TestVisible
    private List<QuoteLineItem> getDirtyQuoteLineItems() {
        return dirtyMapByType.get('QuoteLineItem').values();
    }

    public class QuoteLineItemWorkerException extends Exception {}
}