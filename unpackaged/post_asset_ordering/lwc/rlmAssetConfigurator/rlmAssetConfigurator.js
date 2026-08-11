import { LightningElement, api } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import startConfiguration from '@salesforce/apex/RLM_AssetConfiguratorService.startConfiguration';

/**
 * Phase 2 guided-reconfiguration embed. Scoped to a consolidated transaction
 * (the Quote produced by the console). Starts a native Product Configurator
 * session for a chosen product and renders the returned instance so an agent can
 * review the guided configuration in-flow. Node-level edits are driven through
 * RLM_AssetConfiguratorService.applyConfiguratorAction (follow-up UI).
 */
export default class RlmAssetConfigurator extends LightningElement {
    @api transactionId; // consolidated Quote/Order id

    productId;
    quantity = 1;
    working = false;
    configurationId;
    nodes = [];
    rawResponse;

    get startDisabled() {
        return this.working || !this.productId;
    }
    get hasResult() {
        return !!this.configurationId || !!this.rawResponse;
    }
    get nodeCount() {
        return this.nodes ? this.nodes.length : 0;
    }

    handleProductId(e) {
        this.productId = e.detail.value;
    }
    handleQuantity(e) {
        this.quantity = e.detail.value;
    }

    async handleStart() {
        this.working = true;
        this.configurationId = undefined;
        this.nodes = [];
        this.rawResponse = undefined;
        try {
            const body = await startConfiguration({
                productId: this.productId,
                transactionId: this.transactionId,
                quantity: this.quantity ? Number(this.quantity) : 1
            });
            this.rawResponse = body;
            try {
                const parsed = JSON.parse(body);
                this.configurationId = parsed.configurationId || parsed.id;
                this.nodes = Array.isArray(parsed.nodes) ? parsed.nodes : [];
            } catch (parseErr) {
                // Non-JSON body: leave raw response for display.
            }
            this.dispatchEvent(
                new ShowToastEvent({
                    title: 'Configuration started',
                    message: 'Guided configuration session opened.',
                    variant: 'success'
                })
            );
        } catch (e) {
            const msg =
                e && e.body && e.body.message ? e.body.message : 'Unable to start configuration.';
            this.dispatchEvent(
                new ShowToastEvent({ title: 'Configurator error', message: msg, variant: 'error' })
            );
        } finally {
            this.working = false;
        }
    }
}
