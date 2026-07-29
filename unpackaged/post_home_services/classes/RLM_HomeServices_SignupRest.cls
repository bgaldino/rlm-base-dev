/**
 * REST endpoint for signup. Use from LWC when the Apex wire adapter does not pass
 * parameters in Experience Cloud (guest user). POST body = JSON SignupRequest.
 */
@RestResource(urlMapping='/RLM_Signup/*')
global with sharing class RLM_HomeServices_SignupRest {

    @HttpPost
    global static void postSignup() {
        RestRequest req = RestContext.request;
        RLM_HomeServices_CustomerSignupCtrl.SignupResult result;
        try {
            String body = req != null && req.requestBody != null ? req.requestBody.toString() : null;
            if (String.isBlank(body)) {
                result = new RLM_HomeServices_CustomerSignupCtrl.SignupResult();
                result.success = false;
                result.errorMessage = 'Please select at least one product.';
            } else {
                result = RLM_HomeServices_CustomerSignupCtrl.submitSignup(body);
            }
        } catch (Exception e) {
            result = new RLM_HomeServices_CustomerSignupCtrl.SignupResult();
            result.success = false;
            result.errorMessage = e.getMessage();
        }
        if (RestContext.response != null) {
            RestContext.response.statusCode = 200;
            RestContext.response.responseBody = Blob.valueOf(JSON.serialize(result));
            RestContext.response.addHeader('Content-Type', 'application/json');
        }
    }
}