import { LightningElement, api, track, wire } from 'lwc';
import { publish, subscribe, unsubscribe, MessageContext } from 'lightning/messageService';
import RLM_RAMP_SCHEDULE_CHANNEL from '@salesforce/messageChannel/RLM_RampScheduleChannel__c';

export default class RlmRampScheduleTrialSection extends LightningElement {
    // Admin-configurable properties
    @api defaultTrialDiscount = 100;
    @api defaultTrialDuration = 30;
    @api lockTrialDuration = false;
    @api lockTrialDiscount = false;

    // Form state
    @track includeTrialSegment = 'No';
    @track trialDurationValue = 30;
    @track trialDurationUnit = 'Days'; // Fixed to Days
    @track trialDiscountPercent = 100;

    @wire(MessageContext)
    messageContext;

    _channelSubscription = null;

    // Options
    yesNoOptions = [
        { label: 'Yes', value: 'Yes' },
        { label: 'No', value: 'No' }
    ];

    trialDurationUnitOptions = [
        { label: 'Days', value: 'Days' },
        { label: 'Months', value: 'Months' }
    ];

    _initialized = false;
    _lastDefaultTrialDuration = null;
    _lastDefaultTrialDiscount = null;
    _lastLockTrialDuration = null;
    _lastLockTrialDiscount = null;

    connectedCallback() {}

    ensureSubscribed() {
        if (this.messageContext && !this._channelSubscription) {
            this._channelSubscription = subscribe(
                this.messageContext,
                RLM_RAMP_SCHEDULE_CHANNEL,
                (message) => this.handleChannelMessage(message)
            );
        }
    }

    disconnectedCallback() {
        if (this._channelSubscription) {
            unsubscribe(this._channelSubscription);
            this._channelSubscription = null;
        }
    }

    handleChannelMessage(message) {
        if (message && message.source === 'preview' && message.requestTrialState) {
            this.publishState();
        }
    }

    // Initialize component state from Flow properties
    initializeFromProperties() {
        // Get current values (handle undefined/null)
        const currentDuration = this.defaultTrialDuration != null ? this.defaultTrialDuration : 30;
        const currentDiscount = this.defaultTrialDiscount != null ? this.defaultTrialDiscount : 100;
        const currentLockDuration = this.lockTrialDuration === true;
        const currentLockDiscount = this.lockTrialDiscount === true;
        
        // Check if Flow properties have changed (using strict comparison)
        const durationChanged = this._lastDefaultTrialDuration !== currentDuration;
        const discountChanged = this._lastDefaultTrialDiscount !== currentDiscount;
        const lockDurationChanged = this._lastLockTrialDuration !== currentLockDuration;
        const lockDiscountChanged = this._lastLockTrialDiscount !== currentLockDiscount;
        
        // Only update if not initialized or if properties have changed
        if (!this._initialized || durationChanged || discountChanged || lockDurationChanged || lockDiscountChanged) {
            
            // Update values from Flow properties
            // Only update if not locked (to preserve user changes) OR if this is initial load
            if ((!currentLockDuration || !this._initialized) && (durationChanged || !this._initialized)) {
                this.trialDurationValue = currentDuration;
            }
            if ((!currentLockDiscount || !this._initialized) && (discountChanged || !this._initialized)) {
                this.trialDiscountPercent = currentDiscount;
            }
            
            if (!this._initialized) {
                this.trialDurationUnit = 'Days';
            }
            
            // Track last values (store the actual values)
            this._lastDefaultTrialDuration = currentDuration;
            this._lastDefaultTrialDiscount = currentDiscount;
            this._lastLockTrialDuration = currentLockDuration;
            this._lastLockTrialDiscount = currentLockDiscount;
            
            if (!this._initialized) {
                this._initialized = true;
            }
            
            // Publish state after initialization or property change
            this.publishState();
        }
    }

    renderedCallback() {
        this.initializeFromProperties();
        this.ensureSubscribed();
    }


    // Computed properties
    get hasTrialSegment() {
        return this.includeTrialSegment === 'Yes';
    }

    // Event Handlers
    handleTrialSegmentChange(event) {
        this.includeTrialSegment = event.detail.value;
        this.publishState();
    }

    handleTrialDurationValueChange(event) {
        const raw = parseInt(event.target.value, 10);
        this.trialDurationValue = (isNaN(raw) || raw < 1) ? 1 : raw;
        this.publishState();
    }

    handleTrialDurationUnitChange(event) {
        this.trialDurationUnit = event.detail.value || 'Days';
        this.publishState();
    }

    handleTrialDiscountChange(event) {
        this.trialDiscountPercent = parseInt(event.target.value) || 0;
        this.publishState();
    }

    // Publish state to LMS
    publishState() {
        if (!this.messageContext) {
            // MessageContext not available yet, skip publishing
            return;
        }
        
        const payload = {
            includeTrialSegment: this.includeTrialSegment,
            trialDurationValue: this.trialDurationValue,
            trialDurationUnit: this.trialDurationUnit,
            trialDiscountPercent: this.trialDiscountPercent,
            source: 'trial'
        };
        
        publish(this.messageContext, RLM_RAMP_SCHEDULE_CHANNEL, payload);
    }
}