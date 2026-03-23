import { LightningElement, api, track } from 'lwc';
import { publish, subscribe, unsubscribe, MessageContext } from 'lightning/messageService';
import { wire } from 'lwc';
import RLM_RAMP_SCHEDULE_CHANNEL from '@salesforce/messageChannel/RLM_RampScheduleChannel__c';

export default class RlmRampScheduleForm extends LightningElement {
    // Admin-configurable properties
    @api quoteStartDate = '';
    @api defaultScheduleName = '3 Year Ramp Schedule';
    @api defaultDuration = 40;
    @api defaultScheduleType = 'Annual';

    // Form state
    @track scheduleName = '';
    @track scheduleType = 'Annual';
    @track startDate = '';
    @track durationMonths = 40;
    @track numberOfCustomSegments = 4;
    @track proRataPosition = 'End';

    @wire(MessageContext)
    messageContext;

    subscription = null;

    // Options
    typeOptions = [
        { label: 'Annual', value: 'Annual' },
        { label: 'Custom', value: 'Custom' }
    ];

    proRataOptions = [
        { label: 'Beginning', value: 'Start' },
        { label: 'End', value: 'End' }
    ];

    _initialized = false;
    _lastDefaultDuration = null;
    _lastDefaultScheduleName = null;
    _lastDefaultScheduleType = null;
    _lastQuoteStartDate = null;

    connectedCallback() {
        // Subscribe to messages (to receive start date updates from preview table)
        this.subscribeToChannel();
    }

    // Initialize component state from Flow properties
    initializeFromProperties() {
        // Get current values (handle undefined/null)
        const currentDuration = this.defaultDuration != null ? this.defaultDuration : 40;
        const currentName = this.defaultScheduleName || '3 Year Ramp Schedule';
        const currentType = this.defaultScheduleType || 'Annual';
        const currentStartDate = this.quoteStartDate || '';
        
        // Check if Flow properties have changed (using strict comparison)
        const durationChanged = this._lastDefaultDuration !== currentDuration;
        const nameChanged = this._lastDefaultScheduleName !== currentName;
        const typeChanged = this._lastDefaultScheduleType !== currentType;
        const startDateChanged = this._lastQuoteStartDate !== currentStartDate;
        
        // Only update if not initialized or if properties have changed
        if (!this._initialized || durationChanged || nameChanged || typeChanged || startDateChanged) {
            
            // Update values from Flow properties
            if (nameChanged || !this._initialized) {
                this.scheduleName = currentName;
            }
            if (typeChanged || !this._initialized) {
                this.scheduleType = currentType;
            }
            if (durationChanged || !this._initialized) {
                this.durationMonths = currentDuration;
            }
            
            // Handle start date
            if (currentStartDate && (startDateChanged || !this.startDate)) {
                this.startDate = currentStartDate;
            } else if (!this.startDate) {
                // Only set default date if startDate is not already set
                const today = new Date();
                today.setDate(today.getDate() + 10);
                this.startDate = this.formatDateForInput(today);
            }
            
            // Track last values (store the actual values, not the @api properties)
            this._lastDefaultDuration = currentDuration;
            this._lastDefaultScheduleName = currentName;
            this._lastDefaultScheduleType = currentType;
            this._lastQuoteStartDate = currentStartDate;
            
            if (!this._initialized) {
                this._initialized = true;
            }
            
            // Publish state after initialization or property change
            this.publishState();
        }
    }

    renderedCallback() {
        // Flow sets @api properties after connectedCallback, so check here
        // Initialize from Flow properties if they're available
        this.initializeFromProperties();
        
        // Subscribe to channel after component is rendered and messageContext is available
        if (this.messageContext && !this.subscription) {
            this.subscribeToChannel();
        }
    }

    // Getters to ensure reactive updates when @api properties change
    get effectiveDefaultDuration() {
        return this.defaultDuration || 40;
    }

    get effectiveDefaultScheduleName() {
        return this.defaultScheduleName || '3 Year Ramp Schedule';
    }

    get effectiveDefaultScheduleType() {
        return this.defaultScheduleType || 'Annual';
    }


    disconnectedCallback() {
        this.unsubscribeFromChannel();
    }

    subscribeToChannel() {
        if (this.messageContext && !this.subscription) {
            try {
                this.subscription = subscribe(
                    this.messageContext,
                    RLM_RAMP_SCHEDULE_CHANNEL,
                    (message) => this.handleMessage(message)
                );
            } catch (error) {
                console.error('Error subscribing to message channel:', error);
            }
        }
    }

    unsubscribeFromChannel() {
        if (this.subscription) {
            unsubscribe(this.subscription);
            this.subscription = null;
        }
    }

    handleMessage(message) {
        // Listen for start date updates from preview table
        if (message.source === 'preview' && message.startDate) {
            // Reactive binding (value={startDate}) updates the input automatically.
            this.startDate = message.startDate;
        }
    }

    // Computed properties
    get isCustomType() {
        return this.scheduleType === 'Custom';
    }

    get showProRataPosition() {
        const duration = parseInt(this.durationMonths) || 0;
        if (this.scheduleType === 'Annual') {
            return duration % 12 !== 0;
        } else {
            const numSegments = parseInt(this.numberOfCustomSegments) || 1;
            return duration % numSegments !== 0;
        }
    }

    get durationMessage() {
        const duration = parseInt(this.durationMonths) || 0;
        if (this.scheduleType === 'Annual') {
            const years = Math.floor(duration / 12);
            const remainingMonths = duration % 12;
            if (remainingMonths > 0) {
                return `Will generate ${years} segments with 1 year duration and 1 pro-rata segment of ${remainingMonths} months`;
            }
            return `Will generate ${years} segments with 1 year duration each`;
        } else {
            const numSegments = parseInt(this.numberOfCustomSegments) || 1;
            const monthsPerSegment = Math.floor(duration / numSegments);
            const remainingMonths = duration % numSegments;
            if (remainingMonths > 0) {
                return `Will generate ${numSegments} segments of ${monthsPerSegment} months each and 1 pro-rata segment of ${remainingMonths} months`;
            }
            return `Will generate ${numSegments} segments of ${monthsPerSegment} months each`;
        }
    }

    // Event Handlers
    handleNameChange(event) {
        this.scheduleName = event.target.value;
        this.publishState();
    }

    handleTypeChange(event) {
        this.scheduleType = event.detail.value;
        this.publishState();
    }

    handleStartDateChange(event) {
        this.startDate = event.target.value;
        this.publishState();
    }

    handleDurationChange(event) {
        this.durationMonths = parseInt(event.target.value) || 1;
        this.publishState();
    }

    handleCustomSegmentsChange(event) {
        this.numberOfCustomSegments = parseInt(event.target.value) || 1;
        this.publishState();
    }

    handleProRataPositionChange(event) {
        this.proRataPosition = event.detail.value;
        this.publishState();
    }

    // Publish state to LMS
    publishState() {
        if (!this.messageContext) {
            // MessageContext not available yet, skip publishing
            return;
        }
        
        const payload = {
            scheduleName: this.scheduleName,
            scheduleType: this.scheduleType,
            startDate: this.startDate,
            durationMonths: this.durationMonths,
            numberOfCustomSegments: this.numberOfCustomSegments,
            proRataPosition: this.proRataPosition,
            source: 'form'
        };
        
        publish(this.messageContext, RLM_RAMP_SCHEDULE_CHANNEL, payload);
    }

    formatDateForInput(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
}