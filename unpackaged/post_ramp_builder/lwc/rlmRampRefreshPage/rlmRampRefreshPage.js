import { LightningElement, api } from 'lwc';

/**
 * @description Renders a "View Quote" button on the Flow success screen.
 *
 * Quick Actions run at a URL like:
 *   /lightning/action/quick/Quote.RLM_Create_Ramp_Schedule_V4?...&backgroundContext=%2Flightning%2Fr%2F...
 *
 * window.location.reload() reloads that action URL (re-opens the modal).
 * Instead, we extract the backgroundContext parameter and navigate there,
 * which closes the action and lands on the refreshed record page.
 */
export default class RlmRampRefreshPage extends LightningElement {
    // Kept for Flow schema compatibility; not used at runtime.
    @api recordId;

    handleDone() {
        try {
            // eslint-disable-next-line @lwc/lwc/no-window-object-usage
            const params = new URLSearchParams(window.location.search);
            const backgroundContext = params.get('backgroundContext');
            // Validate that backgroundContext is a same-origin Lightning path before
            // trusting it, to avoid open-redirect from a tampered URL parameter.
            if (backgroundContext && backgroundContext.startsWith('/lightning/')) {
                // URLSearchParams.get() already decodes once; backgroundContext
                // is a relative /lightning/r/... path — navigate there directly.
                // eslint-disable-next-line @lwc/lwc/no-window-object-usage
                window.location.href = backgroundContext;
            } else {
                // eslint-disable-next-line @lwc/lwc/no-window-object-usage
                window.location.reload();
            }
        } catch (e) {
            // eslint-disable-next-line @lwc/lwc/no-window-object-usage
            window.location.reload();
        }
    }
}
