import { LightningElement, api, wire } from 'lwc';
import { refreshApex } from '@salesforce/apex';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import { CloseActionScreenEvent } from 'lightning/actions';
import getBundleFulfillment from '@salesforce/apex/RLM_ShipmentFulfillmentService.getBundleFulfillment';
import holdBillingForBundle from '@salesforce/apex/RLM_ShipmentFulfillmentService.holdBillingForBundle';
import confirmShipment from '@salesforce/apex/RLM_ShipmentFulfillmentService.confirmShipment';

/**
 * Asset record-page screen action: "Confirm Shipment (Simulate EBS)".
 * Placed on a one-time hardware asset. Simulates the inbound shipment / serial
 * mapping event that releases the bundled software subscriptions from billing
 * hold. Provides a demo-setup "Apply billing hold" step so the whole gate is
 * demoable from the record page without an external integration.
 */
export default class RlmConfirmShipment extends LightningElement {
    @api recordId;

    view;
    loadError;
    working = false;
    serialText = '';
    shipmentDate = new Date().toISOString().slice(0, 10);
    amendmentQuoteId;
    _wired;

    @wire(getBundleFulfillment, { hardwareAssetId: '$recordId' })
    wired(value) {
        this._wired = value;
        const { data, error } = value;
        if (data) {
            this.view = data;
            this.loadError = undefined;
        } else if (error) {
            this.loadError = this.reduce(error);
        }
    }

    // ---- derived state ----
    get hasView() {
        return !!this.view && !!this.view.hardwareAssetId;
    }
    get isHardware() {
        return this.hasView && this.view.isOneTimeHardware === true;
    }
    get software() {
        return (this.view && this.view.software) || [];
    }
    get hasSoftware() {
        return this.software.length > 0;
    }
    get anyHeld() {
        return this.hasView && this.view.softwareHeldCount > 0;
    }
    get alreadyShipped() {
        return this.hasView && this.view.hardwareStatus === 'Shipped';
    }
    // Show the demo-setup hold button when there is software but nothing is held yet.
    get canHold() {
        return this.isHardware && this.hasSoftware && !this.anyHeld;
    }
    // Show the shipment form once something is on hold.
    get canConfirm() {
        return this.isHardware && this.anyHeld;
    }
    get notApplicable() {
        return this.hasView && (!this.isHardware || !this.hasSoftware);
    }
    get isSerialized() {
        return this.hasView && this.view.isSerialized === true;
    }
    get serialPlaceholder() {
        const n = (this.view && this.view.expectedUnits) || 1;
        return `Enter ${n} serial number(s), one per line`;
    }
    get confirmDisabled() {
        if (this.working || !this.shipmentDate) return true;
        // Serials are only required when the hardware product is serialized.
        return this.isSerialized && !this.serialText.trim();
    }
    // A start-date amendment quote was produced on shipment (bundle was
    // future-dated). Surface it so the rep can review + activate to regenerate
    // billing from the ship date.
    get hasAmendmentQuote() {
        return !!this.amendmentQuoteId;
    }
    get amendmentQuoteUrl() {
        return this.amendmentQuoteId
            ? `/lightning/r/Quote/${this.amendmentQuoteId}/view`
            : null;
    }

    // ---- handlers ----
    handleSerial(e) {
        this.serialText = e.detail.value;
    }
    handleDate(e) {
        this.shipmentDate = e.detail.value;
    }

    async applyHold() {
        this.working = true;
        try {
            const res = await holdBillingForBundle({ assetIds: [this.recordId] });
            if (res.isSuccess) {
                this.toast('Billing held', (res.messages || []).join(' '), 'success');
                await refreshApex(this._wired);
            } else {
                this.toast('Could not hold billing', (res.messages || []).join(' '), 'error');
            }
        } catch (e) {
            this.toast('Error', this.reduce(e), 'error');
        } finally {
            this.working = false;
        }
    }

    async confirm() {
        this.working = true;
        try {
            const serials = this.serialText
                .split(/[\n,]/)
                .map((s) => s.trim())
                .filter((s) => s.length > 0);
            const res = await confirmShipment({
                hardwareAssetId: this.recordId,
                serialNumbers: serials,
                shipmentDate: this.shipmentDate
            });
            if (res.isSuccess) {
                this.amendmentQuoteId = res.amendmentQuoteId;
                this.toast('Shipment confirmed', (res.messages || []).join(' '), 'success');
                await refreshApex(this._wired);
                // If a re-anchor amendment quote was produced, keep the panel open
                // so the rep can review + activate it; otherwise close.
                if (!this.amendmentQuoteId) {
                    this.close();
                }
            } else {
                this.toast('Shipment failed', (res.messages || []).join(' '), 'error');
            }
        } catch (e) {
            this.toast('Error', this.reduce(e), 'error');
        } finally {
            this.working = false;
        }
    }

    close() {
        this.dispatchEvent(new CloseActionScreenEvent());
    }

    // ---- helpers ----
    toast(title, message, variant) {
        this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
    }
    reduce(error) {
        if (!error) return 'Unknown error';
        if (Array.isArray(error.body)) return error.body.map((e) => e.message).join(', ');
        if (error.body && error.body.message) return error.body.message;
        if (typeof error.message === 'string') return error.message;
        return JSON.stringify(error);
    }
}
