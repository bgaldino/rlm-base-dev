/**
 * @description Exception thrown when ramp schedule creation/validation fails in Flow,
 * so the Flow fault connector runs and the user sees the Error screen with the message.
 */
public class RLM_RampScheduleFlowException extends Exception {
    public RLM_RampScheduleFlowException(String message, String details) {
        setMessage(String.isNotBlank(details) ? message + ' ' + details : message);
    }
}