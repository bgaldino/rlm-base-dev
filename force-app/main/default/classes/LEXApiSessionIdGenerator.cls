/*
This class is used to generate Session Id for Lightning Experience. 
Using UserInfo.getSessionId() in REST Callouts returns 
'INVALID_SESSION_ID: This session is not valid for use with the API' 
error if request is originated from Lightning page. 
A sessionId returned from below method would address above issue.
*/

public class LEXApiSessionIdGenerator{
    public static String generateSessionId(){
        String sessionId='';
        PageReference sessionPage = Page.LEXApiSessionIdGeneratorVF;
        String vfContent = Test.isRunningTest()?'Start_Of_Session_Id12345End_Of_Session_Id':sessionPage.getContent().toString();
        Integer startP = vfContent.indexOf('Start_Of_Session_Id')+'Start_Of_Session_Id'.length();
        Integer endP = vfContent.indexOf('End_Of_Session_Id');
        sessionId = vfContent.subString(startP, endP);
        return sessionId;
    }

}