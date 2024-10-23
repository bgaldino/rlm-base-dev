public with sharing class NotificationQuery implements INotificationQuery {
    
    private static INotificationQuery instance = null;
    private static AccessLevel accessLevelMode = AccessLevel.USER_MODE;
    public static INotificationQuery getInstance() {
        if (instance == null) {
            instance = new NotificationQuery();
        }
        return instance;
    }

    public static void setInstance(INotificationQuery existingInstance) {
        instance = existingInstance;
    }
    
    public NotificationQuery() {
        if(Test.isRunningTest()) {
            accessLevelMode = AccessLevel.SYSTEM_MODE;
        }
    }

    public Id getEmailTemplateId(String emailTemplateName){

        List<EmailTemplate> eTemplates = Database.queryWithBinds(
            'SELECT Id FROM EmailTemplate WHERE DeveloperName =:emailTemplateName',
            new Map<String,Object>{'emailTemplateName' => emailTemplateName},
            accessLevelMode
        );
        
        return eTemplates.size() > 0 ? eTemplates[0].Id : null;
    }
}