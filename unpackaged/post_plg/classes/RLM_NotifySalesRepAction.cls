public with sharing class RLM_NotifySalesRepAction {

    public class Request {
        @InvocableVariable(label='Record ID (Opportunity or Quote)' required=true)
        public String recordId;
        @InvocableVariable(label='Sales Rep User ID' required=true)
        public String salesRepUserId;
        @InvocableVariable(label='Notification Title')
        public String title;
        @InvocableVariable(label='Notification Body')
        public String body;
    }

    public class Result {
        @InvocableVariable(label='Is Success')
        public Boolean isSuccess;
        @InvocableVariable(label='Error Message')
        public String errorMessage;
    }

    @InvocableMethod(
        label='Notify Sales Rep'
        description='Creates a follow-up Task and sends a Custom Notification to the sales rep'
        category='Revenue Cloud'
    )
    public static List<Result> execute(List<Request> requests) {
        List<Result> results = new List<Result>();
        for (Request req : requests) {
            Result res = new Result();
            try {
                Task followUp = new Task(
                    Subject = String.isNotBlank(req.title) ? req.title : 'New Quote Request — Review Required',
                    Description = String.isNotBlank(req.body) ? req.body
                        : 'A new quote has been requested from the pricing page. Please review and follow up.',
                    WhatId = req.recordId,
                    OwnerId = req.salesRepUserId,
                    Priority = 'High',
                    Status = 'Not Started',
                    ActivityDate = Date.today().addDays(1)
                );
                insert followUp;

                sendCustomNotification(req);
                res.isSuccess = true;
            } catch (Exception e) {
                res.isSuccess = false;
                res.errorMessage = e.getMessage();
            }
            results.add(res);
        }
        return results;
    }

    private static void sendCustomNotification(Request req) {
        try {
            CustomNotificationType notifType = [
                SELECT Id FROM CustomNotificationType
                WHERE DeveloperName = 'RLM_Quote_Request_Notification' LIMIT 1
            ];
            Messaging.CustomNotification notification = new Messaging.CustomNotification();
            notification.setTitle(String.isNotBlank(req.title) ? req.title : 'New Quote Request');
            notification.setBody(String.isNotBlank(req.body) ? req.body
                : 'A prospect requested a quote from the pricing page. Please review.');
            notification.setTargetId(req.recordId);
            notification.setNotificationTypeId(notifType.Id);
            notification.send(new Set<String>{ req.salesRepUserId });
        } catch (Exception e) {
            System.debug(LoggingLevel.WARN, 'Custom notification failed (non-blocking): ' + e.getMessage());
        }
    }
}