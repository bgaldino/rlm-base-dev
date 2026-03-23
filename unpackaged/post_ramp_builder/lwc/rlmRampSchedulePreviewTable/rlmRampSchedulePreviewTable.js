import { LightningElement, api, track, wire } from 'lwc';
import { subscribe, unsubscribe, publish, MessageContext } from 'lightning/messageService';
import RLM_RAMP_SCHEDULE_CHANNEL from '@salesforce/messageChannel/RLM_RampScheduleChannel__c';

export default class RlmRampSchedulePreviewTable extends LightningElement {
    // Admin-configurable properties
    @api hideDiscountColumn = false;
    @api hideUpliftColumn = false;
    /** Default trial discount (%) from parent/Flow; used for initial preview before LMS message arrives */
    @api defaultTrialDiscount;
    /** Default schedule name from parent/Flow for initial preview */
    @api defaultScheduleName;
    /** Default duration in months from parent/Flow for initial preview */
    @api defaultDuration;
    /** Default trial duration (e.g. days) from parent/Flow for initial preview */
    @api defaultTrialDuration;
    /** Default start date (YYYY-MM-DD) from parent/Flow for initial preview */
    @api defaultStartDate;

    // Output property for Flow to check validation status
    @api validationStatus = false;
    
    // Output properties for Flow to read segment data
    @api 
    get segmentsJson() {
        return JSON.stringify(this.getSegmentsForApi());
    }
    
    @api
    get scheduleNameOutput() {
        return this.scheduleName;
    }
    
    @api
    get scheduleTypeOutput() {
        return this.scheduleType === 'Annual' ? 'YEARLY' : 'CUSTOM';
    }

    // State from LMS
    @track scheduleName = '3 Year Ramp Schedule';
    @track scheduleType = 'Annual';
    @track startDate = '';
    @track durationMonths = 40;
    @track numberOfCustomSegments = 4;
    @track proRataPosition = 'End';
    @track includeTrialSegment = 'No';
    @track trialDurationValue = 30;
    @track trialDurationUnit = 'Days'; // Fixed to Days
    @track trialDiscountPercent = 100;

    // Segments
    @track segments = [];
    
    // Validation
    @track validationErrors = [];
    @track isValid = true;
    
    // Track if Custom segments have been manually edited (to prevent regeneration from form inputs)
    @track customSegmentsManuallyEdited = false;
    
    subscription = null;

    @wire(MessageContext)
    messageContext;

    connectedCallback() {
        // Initialize default date immediately
        this.initializeDefaultDate();
        // Apply parent/Flow defaults so preview matches form on first load (avoids race with LMS)
        if (this.defaultTrialDiscount != null && this.defaultTrialDiscount !== undefined) {
            this.trialDiscountPercent = this.defaultTrialDiscount;
        }
        if (this.defaultScheduleName != null && this.defaultScheduleName !== undefined && this.defaultScheduleName !== '') {
            this.scheduleName = this.defaultScheduleName;
        }
        if (this.defaultDuration != null && this.defaultDuration !== undefined) {
            const d = parseInt(this.defaultDuration, 10);
            if (!isNaN(d)) this.durationMonths = d;
        }
        // Do not set trialDurationValue from defaultTrialDuration here - let trial section be source of truth via LMS.
        // Preview will request current trial state after subscribing so it gets the form's value (including user edits).
        if (this.defaultStartDate != null && this.defaultStartDate !== undefined && this.defaultStartDate !== '') {
            this.startDate = this.defaultStartDate;
        }
        // Generate segments with defaults - will be updated when messages arrive
        this.generateSegments();
    }

    renderedCallback() {
        // Subscribe to channel after component is rendered and messageContext is available
        // This ensures subscription happens when messageContext becomes available via @wire
        if (this.messageContext && !this.subscription) {
            this.subscribeToChannel();
        }
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
                // Request current trial state so we get the form's value (e.g. 60) even if we mounted before user edited
                this.requestTrialState();
            } catch (error) {
                console.error('Error subscribing to message channel:', error);
            }
        }
    }

    requestTrialState() {
        if (this.messageContext) {
            publish(this.messageContext, RLM_RAMP_SCHEDULE_CHANNEL, {
                source: 'preview',
                requestTrialState: true
            });
        }
    }

    unsubscribeFromChannel() {
        unsubscribe(this.subscription);
        this.subscription = null;
    }

    handleMessage(message) {
        // Ignore validation messages to prevent infinite loops
        if (message.source === 'validation') {
            return;
        }
        
        // Ignore preview messages (start date updates from preview table)
        if (message.source === 'preview') {
            return;
        }
        
        // Track significant form changes that require regeneration
        let requiresRegeneration = false;
        let scheduleTypeChanged = false;
        let significantChange = false;
        
        // Update state based on message source
        if (message.source === 'form') {
            if (message.scheduleType !== undefined && message.scheduleType !== this.scheduleType) {
                scheduleTypeChanged = true;
                significantChange = true;
                this.scheduleType = message.scheduleType;
            } else if (message.scheduleType !== undefined) {
                this.scheduleType = message.scheduleType;
            }
            
            if (message.scheduleName !== undefined) this.scheduleName = message.scheduleName;
            
            // Start date changes from form
            if (message.startDate !== undefined) {
                // For Annual, always update. For Custom, only update if segments haven't been manually edited
                if (this.scheduleType === 'Annual') {
                    this.startDate = message.startDate;
                } else if (this.scheduleType === 'Custom' && !this.customSegmentsManuallyEdited) {
                    this.startDate = message.startDate;
                }
            }
            
            if (message.durationMonths !== undefined && message.durationMonths !== this.durationMonths) {
                significantChange = true;
                this.durationMonths = message.durationMonths;
            } else if (message.durationMonths !== undefined) {
                this.durationMonths = message.durationMonths;
            }
            
            if (message.numberOfCustomSegments !== undefined && message.numberOfCustomSegments !== this.numberOfCustomSegments) {
                significantChange = true;
                this.numberOfCustomSegments = message.numberOfCustomSegments;
            } else if (message.numberOfCustomSegments !== undefined) {
                this.numberOfCustomSegments = message.numberOfCustomSegments;
            }
            
            if (message.proRataPosition !== undefined && message.proRataPosition !== this.proRataPosition) {
                significantChange = true;
                this.proRataPosition = message.proRataPosition;
            } else if (message.proRataPosition !== undefined) {
                this.proRataPosition = message.proRataPosition;
            }
        } else if (message.source === 'trial') {
            if (message.includeTrialSegment !== undefined && message.includeTrialSegment !== this.includeTrialSegment) {
                significantChange = true;
                this.includeTrialSegment = message.includeTrialSegment;
            } else if (message.includeTrialSegment !== undefined) {
                this.includeTrialSegment = message.includeTrialSegment;
            }
            if (message.trialDurationValue !== undefined) {
                const newVal = parseInt(message.trialDurationValue, 10);
                const numVal = (isNaN(newVal) || newVal < 1) ? 1 : newVal;
                if (numVal !== this.trialDurationValue) significantChange = true;
                this.trialDurationValue = numVal;
            }
            if (message.trialDurationUnit !== undefined) {
                if (message.trialDurationUnit !== this.trialDurationUnit) significantChange = true;
                this.trialDurationUnit = message.trialDurationUnit;
            }
            if (message.trialDiscountPercent !== undefined) this.trialDiscountPercent = message.trialDiscountPercent;
            // Safeguard: always regenerate when trial duration/unit is updated so segment and calculated duration stay in sync
            if (message.trialDurationValue !== undefined || message.trialDurationUnit !== undefined) {
                requiresRegeneration = true;
            }
        }
        
        // Determine if regeneration is needed
        if (scheduleTypeChanged) {
            // Schedule type changed - always regenerate and reset manual edit flag
            this.customSegmentsManuallyEdited = false;
            requiresRegeneration = true;
        } else if (this.scheduleType === 'Annual') {
            // Annual schedule - always regenerate from form inputs
            requiresRegeneration = true;
        } else if (this.scheduleType === 'Custom') {
            // Custom schedule - only regenerate if:
            // 1. Segments haven't been manually edited, OR
            // 2. There was a significant change (duration, number of segments, pro-rata position, trial settings)
            if (!this.customSegmentsManuallyEdited || significantChange) {
                if (significantChange) {
                    // Reset manual edit flag on significant changes
                    this.customSegmentsManuallyEdited = false;
                }
                requiresRegeneration = true;
            }
        }
        
        // Only regenerate segments if required
        if (requiresRegeneration) {
            this.generateSegments();
        }
    }

    initializeDefaultDate() {
        if (!this.startDate) {
            const today = new Date();
            today.setDate(today.getDate() + 10);
            this.startDate = this.formatDateForInput(today);
        }
    }

    get hasSegments() {
        return this.segments && this.segments.length > 0;
    }

    handleSegmentFieldChange(event) {
        const segmentId = parseInt(event.target.dataset.id);
        const field = event.target.dataset.field;
        const value = event.target.value;
        
        // For Annual schedule: if first editable segment's start date changes, recalculate all segments
        if (field === 'startDate' && this.scheduleType === 'Annual') {
            const changedSegment = this.segments.find(s => s.id === segmentId);
            if (changedSegment && changedSegment.isStartDateEditable) {
                // This is the first editable segment (trial or first non-trial)
                const dateParts = value.split('-');
                if (dateParts.length === 3) {
                    const newStartDate = new Date(parseInt(dateParts[0]), parseInt(dateParts[1]) - 1, parseInt(dateParts[2]));
                    // Update the startDate property
                    this.startDate = this.formatDateForInput(newStartDate);
                    
                    // Publish the new start date back to the form component
                    this.publishStartDateUpdate(this.startDate);
                    
                    // Recalculate all segments from the new start date
                    this.recalculateSegmentsFromNewStartDate(newStartDate);
                    
                    // Validate after recalculation
                    this.validateSegments();
                    return;
                }
            }
        }
        
        // For Custom schedule: any date change only updates that segment and recalculates duration
        if (this.scheduleType === 'Custom' && (field === 'startDate' || field === 'endDate')) {
            // Mark that segments have been manually edited
            this.customSegmentsManuallyEdited = true;
            
            this.segments = this.segments.map(segment => {
                if (segment.id === segmentId) {
                    const updated = { ...segment };
                    if (field === 'startDate') {
                        updated.startDateValue = value;
                        const dateParts = value.split('-');
                        if (dateParts.length === 3) {
                            const newDate = new Date(parseInt(dateParts[0]), parseInt(dateParts[1]) - 1, parseInt(dateParts[2]));
                            updated.startDateDisplay = this.formatDateForDisplay(newDate);
                            updated.startDateObj = newDate;
                        }
                    } else if (field === 'endDate') {
                        updated.endDateValue = value;
                        const dateParts = value.split('-');
                        if (dateParts.length === 3) {
                            const newDate = new Date(parseInt(dateParts[0]), parseInt(dateParts[1]) - 1, parseInt(dateParts[2]));
                            updated.endDateDisplay = this.formatDateForDisplay(newDate);
                            updated.endDateObj = newDate;
                        }
                    }
                    
                    // Recalculate duration for this segment
                    if (updated.startDateObj && updated.endDateObj) {
                        if (updated.isTrialSegment) {
                            updated.durationDisplay = this.formatTrialDurationDisplay(updated.startDateObj, updated.endDateObj);
                        } else {
                            updated.durationDisplay = this.formatDurationDisplay(updated.startDateObj, updated.endDateObj);
                        }
                    }
                    
                    return updated;
                }
                return segment;
            });
            
            // Validate after date changes (will show gaps/overlaps if any)
            this.validateSegments();
            return;
        }
        
        // For other changes (Annual end dates, name, discount, uplift, etc.), update only the changed segment
        this.segments = this.segments.map(segment => {
            if (segment.id === segmentId) {
                const updated = { ...segment };
                if (field === 'name') {
                    updated.name = value;
                } else if (field === 'startDate') {
                    updated.startDateValue = value;
                    const dateParts = value.split('-');
                    if (dateParts.length === 3) {
                        const newDate = new Date(parseInt(dateParts[0]), parseInt(dateParts[1]) - 1, parseInt(dateParts[2]));
                        updated.startDateDisplay = this.formatDateForDisplay(newDate);
                        updated.startDateObj = newDate;
                    }
                } else if (field === 'endDate') {
                    updated.endDateValue = value;
                    const dateParts = value.split('-');
                    if (dateParts.length === 3) {
                        const newDate = new Date(parseInt(dateParts[0]), parseInt(dateParts[1]) - 1, parseInt(dateParts[2]));
                        updated.endDateDisplay = this.formatDateForDisplay(newDate);
                        updated.endDateObj = newDate;
                        // Make end date editable if start date is editable
                        updated.isEndDateEditable = updated.isStartDateEditable;
                    }
                } else if (field === 'discount') {
                    updated.discount = parseInt(value) || 0;
                    updated.discountDisplay = value;
                } else if (field === 'uplift') {
                    updated.uplift = parseInt(value) || 0;
                }
                return updated;
            }
            return segment;
        });
        
        // Validate after date changes
        if (field === 'startDate' || field === 'endDate') {
            this.validateSegments();
        }
    }

    // Publish start date update back to form component
    publishStartDateUpdate(newStartDate) {
        if (this.messageContext) {
            const payload = {
                startDate: newStartDate,
                source: 'preview'
            };
            publish(this.messageContext, RLM_RAMP_SCHEDULE_CHANNEL, payload);
        }
    }

    // Recalculate all segments from a new start date (for Custom schedules)
    recalculateCustomSegmentsFromNewStartDate(newStartDate) {
        if (this.scheduleType !== 'Custom') {
            // This method is only for Custom schedules
            return;
        }
        
        if (this.segments.length === 0) {
            return;
        }
        
        // Find the first editable segment (trial or first non-trial)
        const firstEditableSegment = this.segments.find(s => s.isStartDateEditable);
        if (!firstEditableSegment) {
            return;
        }
        
        // Calculate the offset (difference between old and new start date)
        const oldStartDate = firstEditableSegment.startDateObj;
        if (!oldStartDate) {
            return;
        }
        
        const offsetDays = Math.floor((newStartDate.getTime() - oldStartDate.getTime()) / (1000 * 60 * 60 * 24));
        
        // Apply the offset to all segments
        this.segments = this.segments.map(segment => {
            const updated = { ...segment };
            
            if (segment.startDateObj) {
                const newStartDateObj = this.addDays(segment.startDateObj, offsetDays);
                updated.startDateValue = this.formatDateForInput(newStartDateObj);
                updated.startDateDisplay = this.formatDateForDisplay(newStartDateObj);
                updated.startDateObj = newStartDateObj;
            }
            
            if (segment.endDateObj) {
                const newEndDateObj = this.addDays(segment.endDateObj, offsetDays);
                updated.endDateValue = this.formatDateForInput(newEndDateObj);
                updated.endDateDisplay = this.formatDateForDisplay(newEndDateObj);
                updated.endDateObj = newEndDateObj;
                
                // Recalculate duration
                if (updated.startDateObj && updated.endDateObj) {
                    if (segment.isTrialSegment) {
                        updated.durationDisplay = this.formatTrialDurationDisplay(updated.startDateObj, updated.endDateObj);
                    } else {
                        updated.durationDisplay = this.formatDurationDisplay(updated.startDateObj, updated.endDateObj);
                    }
                }
            }
            
            return updated;
        });
    }

    // Recalculate all segments from a new start date (for Annual schedules)
    recalculateSegmentsFromNewStartDate(newStartDate) {
        const newSegments = [];
        let segmentId = 1;
        
        let currentDate = newStartDate;
        const hasTrial = this.includeTrialSegment === 'Yes';
        const totalDuration = parseInt(this.durationMonths) || 40;
        const isAnnual = this.scheduleType === 'Annual';
        
        if (!isAnnual) {
            // This method is only for Annual schedules
            return;
        }
        
        // Trial Segment
        if (hasTrial) {
            const trialEndDate = this.calculateTrialEndDate(currentDate);
            const trialDurationDisplay = this.formatTrialDurationDisplay(currentDate, trialEndDate);
            newSegments.push({
                id: segmentId++,
                name: 'Trial',
                type: 'TRIAL',
                typeLabel: 'TRIAL',
                badgeClass: 'badge badge-trial',
                durationDisplay: trialDurationDisplay,
                startDateValue: this.formatDateForInput(currentDate),
                startDateDisplay: this.formatDateForDisplay(currentDate),
                endDateValue: this.formatDateForInput(trialEndDate),
                endDateDisplay: this.formatDateForDisplay(trialEndDate),
                discount: this.trialDiscountPercent || 100,
                discountDisplay: `${this.trialDiscountPercent || 100}%`,
                uplift: 0,
                isTrialSegment: true,
                isStartDateEditable: true,
                isEndDateEditable: false
            });
            
            currentDate = this.addDays(trialEndDate, 1);
        }
        
        // Generate Annual segments
        const fullYears = Math.floor(totalDuration / 12);
        const remainingMonths = totalDuration % 12;
        const proRataAtStart = this.proRataPosition === 'Start' && remainingMonths > 0;
        let segmentIndex = 0;
        
        if (proRataAtStart) {
            const proRataAnniversary = this.addMonths(currentDate, remainingMonths);
            const proRataEndDate = this.addDays(proRataAnniversary, -1);
            const isFirstSegment = !hasTrial && segmentIndex === 0;
            newSegments.push(this.createProRataSegment(segmentId++, currentDate, proRataEndDate, isFirstSegment, false));
            currentDate = this.addDays(proRataEndDate, 1);
            segmentIndex++;
        }
        
        for (let i = 0; i < fullYears; i++) {
            const yearAnniversary = this.addMonths(currentDate, 12);
            const yearEndDate = this.addDays(yearAnniversary, -1);
            const isFirstSegment = !hasTrial && segmentIndex === 0;
            
            newSegments.push({
                id: segmentId++,
                name: `Year ${i + 1}`,
                type: 'YEARLY',
                typeLabel: 'YEARLY',
                badgeClass: 'badge badge-yearly',
                durationDisplay: this.formatDurationDisplay(currentDate, yearEndDate),
                startDateValue: this.formatDateForInput(currentDate),
                startDateDisplay: this.formatDateForDisplay(currentDate),
                endDateValue: this.formatDateForInput(yearEndDate),
                endDateDisplay: this.formatDateForDisplay(yearEndDate),
                discount: 0,
                discountDisplay: '0',
                uplift: 0,
                isTrialSegment: false,
                isStartDateEditable: isFirstSegment,
                isEndDateEditable: false
            });
            
            currentDate = this.addDays(yearEndDate, 1);
            segmentIndex++;
        }
        
        if (!proRataAtStart && remainingMonths > 0) {
            const proRataAnniversary = this.addMonths(currentDate, remainingMonths);
            const proRataEndDate = this.addDays(proRataAnniversary, -1);
            const isFirstSegment = !hasTrial && segmentIndex === 0;
            newSegments.push(this.createProRataSegment(segmentId++, currentDate, proRataEndDate, isFirstSegment, false));
        }
        
        // Store date objects for validation
        this.segments = newSegments.map(segment => {
            const startDateObj = this.parseDateFromInput(segment.startDateValue);
            const endDateObj = this.parseDateFromInput(segment.endDateValue) || this.parseDateFromDisplay(segment.endDateDisplay);
            return {
                ...segment,
                startDateObj: startDateObj,
                endDateObj: endDateObj
            };
        });
    }

    generateSegments() {
        const newSegments = [];
        let segmentId = 1;
        
        let currentDate = this.parseStartDate();
        const hasTrial = this.includeTrialSegment === 'Yes';
        const totalDuration = parseInt(this.durationMonths) || 40;
        const isAnnual = this.scheduleType === 'Annual';
        const isCustom = this.scheduleType === 'Custom';
        
        // Trial Segment
        if (hasTrial) {
            const trialEndDate = this.calculateTrialEndDate(currentDate);
            const trialDurationDisplay = this.formatTrialDurationDisplay(currentDate, trialEndDate);
            // For Annual: only start date editable. For Custom: both dates editable
            const isTrialStartEditable = true; // Always editable (first segment)
            const isTrialEndEditable = isCustom; // Only editable for Custom type
            newSegments.push({
                id: segmentId++,
                name: 'Trial',
                type: 'TRIAL',
                typeLabel: 'TRIAL',
                badgeClass: 'badge badge-trial',
                durationDisplay: trialDurationDisplay,
                startDateValue: this.formatDateForInput(currentDate),
                startDateDisplay: this.formatDateForDisplay(currentDate),
                endDateValue: this.formatDateForInput(trialEndDate),
                endDateDisplay: this.formatDateForDisplay(trialEndDate),
                discount: this.trialDiscountPercent || 100,
                discountDisplay: `${this.trialDiscountPercent || 100}%`,
                uplift: 0,
                isTrialSegment: true,
                isStartDateEditable: isTrialStartEditable,
                isEndDateEditable: isTrialEndEditable
            });
            
            currentDate = this.addDays(trialEndDate, 1);
        }
        
        // For Annual: only first segment (or trial if exists) start date is editable
        // For Custom: all dates are editable
        let firstNonTrialSegmentIndex = hasTrial ? 1 : 0;
        
        if (isAnnual) {
            const fullYears = Math.floor(totalDuration / 12);
            const remainingMonths = totalDuration % 12;
            const proRataAtStart = this.proRataPosition === 'Start' && remainingMonths > 0;
            
            // For Annual: only first non-trial segment's start date is editable (if no trial exists)
            let segmentIndex = 0;
            
            if (proRataAtStart) {
                // Anniversary-based: end date is one day before the anniversary
                const proRataAnniversary = this.addMonths(currentDate, remainingMonths);
                const proRataEndDate = this.addDays(proRataAnniversary, -1);
                
                // First non-trial segment: start date editable only if no trial exists
                const isFirstSegment = !hasTrial && segmentIndex === 0;
                newSegments.push(this.createProRataSegment(segmentId++, currentDate, proRataEndDate, isFirstSegment));
                currentDate = this.addDays(proRataEndDate, 1);
                segmentIndex++;
            }
            
            for (let i = 0; i < fullYears; i++) {
                // Anniversary-based: 12 months from start date, end date is one day before anniversary
                const yearAnniversary = this.addMonths(currentDate, 12);
                const yearEndDate = this.addDays(yearAnniversary, -1);
                
                // First non-trial segment: start date editable only if no trial exists
                const isFirstSegment = !hasTrial && segmentIndex === 0;
                
                newSegments.push({
                    id: segmentId++,
                    name: `Year ${i + 1}`,
                    type: 'YEARLY',
                    typeLabel: 'YEARLY',
                    badgeClass: 'badge badge-yearly',
                    durationDisplay: this.formatDurationDisplay(currentDate, yearEndDate),
                    startDateValue: this.formatDateForInput(currentDate),
                    startDateDisplay: this.formatDateForDisplay(currentDate),
                    endDateValue: this.formatDateForInput(yearEndDate),
                    endDateDisplay: this.formatDateForDisplay(yearEndDate),
                    discount: 0,
                    discountDisplay: '0',
                    uplift: 0,
                    isTrialSegment: false,
                    isStartDateEditable: isFirstSegment,
                    isEndDateEditable: false
                });
                
                currentDate = this.addDays(yearEndDate, 1);
                segmentIndex++;
            }
            
            if (!proRataAtStart && remainingMonths > 0) {
                // Anniversary-based: end date is one day before the anniversary
                const proRataAnniversary = this.addMonths(currentDate, remainingMonths);
                const proRataEndDate = this.addDays(proRataAnniversary, -1);
                // First non-trial segment: start date editable only if no trial exists
                const isFirstSegment = !hasTrial && segmentIndex === 0;
                newSegments.push(this.createProRataSegment(segmentId++, currentDate, proRataEndDate, isFirstSegment));
            }
        } else {
            // Custom type: all dates are editable
            const numSegments = parseInt(this.numberOfCustomSegments) || 4;
            const monthsPerSegment = Math.floor(totalDuration / numSegments);
            const remainingMonths = totalDuration % numSegments;
            const hasProRata = remainingMonths > 0;
            const proRataAtStart = this.proRataPosition === 'Start' && hasProRata;
            
            if (proRataAtStart) {
                // Anniversary-based: end date is one day before the anniversary
                const proRataAnniversary = this.addMonths(currentDate, remainingMonths);
                const proRataEndDate = this.addDays(proRataAnniversary, -1);
                // For Custom: all dates editable
                newSegments.push(this.createProRataSegment(segmentId++, currentDate, proRataEndDate, true));
                currentDate = this.addDays(proRataEndDate, 1);
            }
            
            for (let i = 0; i < numSegments; i++) {
                // Anniversary-based: end date is one day before the anniversary
                const segmentAnniversary = this.addMonths(currentDate, monthsPerSegment);
                const segmentEndDate = this.addDays(segmentAnniversary, -1);
                
                // For Custom: all dates are editable
                newSegments.push({
                    id: segmentId++,
                    name: `Segment ${i + 1}`,
                    type: 'CUSTOM',
                    typeLabel: 'CUSTOM',
                    badgeClass: 'badge badge-custom',
                    durationDisplay: this.formatDurationDisplay(currentDate, segmentEndDate),
                    startDateValue: this.formatDateForInput(currentDate),
                    startDateDisplay: this.formatDateForDisplay(currentDate),
                    endDateValue: this.formatDateForInput(segmentEndDate),
                    endDateDisplay: this.formatDateForDisplay(segmentEndDate),
                    discount: 0,
                    discountDisplay: '0',
                    uplift: 0,
                    isTrialSegment: false,
                    isStartDateEditable: true, // All dates editable for Custom
                    isEndDateEditable: true     // All dates editable for Custom
                });
                
                currentDate = this.addDays(segmentEndDate, 1);
            }
            
            if (!proRataAtStart && hasProRata) {
                // Anniversary-based: end date is one day before the anniversary
                const proRataAnniversary = this.addMonths(currentDate, remainingMonths);
                const proRataEndDate = this.addDays(proRataAnniversary, -1);
                // For Custom: all dates editable
                newSegments.push(this.createProRataSegment(segmentId++, currentDate, proRataEndDate, true));
            }
        }
        
        // Store date objects for validation
        this.segments = newSegments.map(segment => {
            const startDateObj = this.parseDateFromInput(segment.startDateValue);
            const endDateObj = this.parseDateFromInput(segment.endDateValue) || this.parseDateFromDisplay(segment.endDateDisplay);
            return {
                ...segment,
                startDateObj: startDateObj,
                endDateObj: endDateObj
            };
        });
        
        // Validate after generation
        this.validateSegments();
    }

    createProRataSegment(id, startDate, endDate, isStartDateEditable = false, isEndDateEditable = false) {
        // For Custom type, all dates are editable
        if (this.scheduleType === 'Custom') {
            isEndDateEditable = true;
        }
        return {
            id: id,
            name: 'Pro Rate Segment',
            type: 'PRO-RATA',
            typeLabel: 'PRO-RATA',
            badgeClass: 'badge badge-prorata',
            durationDisplay: this.formatDurationDisplay(startDate, endDate),
            startDateValue: this.formatDateForInput(startDate),
            startDateDisplay: this.formatDateForDisplay(startDate),
            endDateValue: this.formatDateForInput(endDate),
            endDateDisplay: this.formatDateForDisplay(endDate),
            discount: 0,
            discountDisplay: '0',
            uplift: 0,
            isTrialSegment: false,
            isStartDateEditable: isStartDateEditable,
            isEndDateEditable: isEndDateEditable
        };
    }

    parseStartDate() {
        if (this.startDate) {
            const parts = this.startDate.split('-');
            if (parts.length === 3) {
                return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
            }
        }
        const date = new Date();
        date.setDate(date.getDate() + 10);
        return date;
    }

    /** Display trial segment duration calculated from its start and end dates */
    formatTrialDurationDisplay(startDate, endDate) {
        const unit = this.trialDurationUnit || 'Days';
        if (unit === 'Days') {
            const duration = this.calculateDuration(startDate, endDate);
            return `${duration.days} Day${duration.days !== 1 ? 's' : ''}`;
        }
        return this.formatDurationDisplay(startDate, endDate);
    }

    calculateTrialEndDate(startDate) {
        const value = parseInt(this.trialDurationValue) || 1;
        const unit = this.trialDurationUnit || 'Months';
        
        if (unit === 'Days') {
            // For days, add the number of days (inclusive of start date)
            const endDate = new Date(startDate);
            endDate.setDate(endDate.getDate() + value - 1);
            return endDate;
        } else {
            // For months, use anniversary-based calculation
            // End date is one day before the anniversary
            const anniversary = this.addMonths(startDate, value);
            return this.addDays(anniversary, -1);
        }
    }

    // Anniversary-based month addition (e.g., Feb 12 + 1 month = March 12)
    addMonths(date, months) {
        const result = new Date(date);
        const originalDay = result.getDate();
        const originalMonth = result.getMonth();
        const originalYear = result.getFullYear();
        
        // Calculate target month and year
        let targetMonth = originalMonth + months;
        let targetYear = originalYear;
        
        while (targetMonth < 0) {
            targetMonth += 12;
            targetYear--;
        }
        while (targetMonth >= 12) {
            targetMonth -= 12;
            targetYear++;
        }
        
        // Set the target month and year
        result.setFullYear(targetYear, targetMonth, 1);
        
        // Handle end-of-month cases (e.g., Jan 31 -> Feb 28/29)
        const daysInTargetMonth = new Date(targetYear, targetMonth + 1, 0).getDate();
        const dayToSet = Math.min(originalDay, daysInTargetMonth);
        result.setDate(dayToSet);
        
        return result;
    }

    addDays(date, days) {
        const result = new Date(date);
        result.setDate(result.getDate() + days);
        return result;
    }

    // Calculate actual duration between two dates (inclusive of both dates)
    // Uses anniversary-based month counting (e.g., Feb 12 to Feb 11 = 12 months)
    calculateDuration(startDate, endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        // Calculate total days (inclusive)
        const timeDiff = end.getTime() - start.getTime();
        const totalDays = Math.floor(timeDiff / (1000 * 60 * 60 * 24)) + 1;
        
        // For short durations (< 60 days), return days only
        if (totalDays < 60) {
            return { days: totalDays, months: 0 };
        }
        
        // Calculate months using anniversary-based logic
        // Find the highest anniversary date that is <= end date, or one day after end date
        let months = 0;
        
        // Check each month anniversary
        for (let m = 1; m <= 120; m++) { // Max 10 years
            const anniversary = this.addMonths(start, m);
            const oneDayBeforeAnniversary = this.addDays(anniversary, -1);
            
            // If end date is exactly one day before anniversary, count as full month
            if (oneDayBeforeAnniversary.getTime() === end.getTime()) {
                months = m;
                return { days: 0, months: months };
            }
            
            // If end date is before the anniversary, we've found the last full month
            if (anniversary > end) {
                // The last full month period ended at (anniversary - 1 day)
                const lastFullMonthEnd = this.addDays(anniversary, -1);
                
                // If end is exactly at lastFullMonthEnd, we have m months with 0 days
                if (lastFullMonthEnd.getTime() === end.getTime()) {
                    months = m;
                    return { days: 0, months: months };
                }
                
                // Otherwise, we have (m-1) full months, plus remaining days
                months = m - 1;
                if (months > 0) {
                    const prevAnniversary = this.addMonths(start, months);
                    const prevFullMonthEnd = this.addDays(prevAnniversary, -1);
                    const daysDiff = end.getTime() - prevFullMonthEnd.getTime();
                    const remainingDays = Math.floor(daysDiff / (1000 * 60 * 60 * 24));
                    return { days: remainingDays, months: months };
                } else {
                    // No full months, return total days
                    return { days: totalDays, months: 0 };
                }
            }
        }
        
        // If we get here, it's a very long duration (> 10 years)
        // Just return total days
        return { days: totalDays, months: 0 };
    }

    // Format duration display based on rules
    formatDurationDisplay(startDate, endDate) {
        const duration = this.calculateDuration(startDate, endDate);
        
        // Short durations (< 60 days) show as "X Days"
        if (duration.months === 0) {
            return `${duration.days} Day${duration.days !== 1 ? 's' : ''}`;
        }
        
        // Mixed durations show as "X Months, Y Days"
        if (duration.days === 0) {
            return `${duration.months} Month${duration.months !== 1 ? 's' : ''}`;
        }
        
        return `${duration.months} Month${duration.months !== 1 ? 's' : ''}, ${duration.days} Day${duration.days !== 1 ? 's' : ''}`;
    }

    formatDateForInput(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    formatDateForDisplay(date) {
        // Format: "MMM, dd, yyyy" (e.g., "Jan 22, 2026")
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const month = monthNames[date.getMonth()];
        const day = date.getDate();
        const year = date.getFullYear();
        return `${month} ${day}, ${year}`;
    }

    parseDateFromInput(dateString) {
        if (!dateString) return null;
        const parts = dateString.split('-');
        if (parts.length === 3) {
            return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
        }
        return null;
    }

    parseDateFromDisplay(dateString) {
        if (!dateString) return null;
        // Try parsing "MMM dd, yyyy" format (e.g., "Jan 22, 2026")
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const match = dateString.match(/(\w+)\s+(\d+),\s+(\d+)/);
        if (match) {
            const monthName = match[1];
            const day = parseInt(match[2]);
            const year = parseInt(match[3]);
            const monthIndex = monthNames.indexOf(monthName);
            if (monthIndex !== -1) {
                return new Date(year, monthIndex, day);
            }
        }
        // Fallback: try old format "MM/DD/YYYY"
        const parts = dateString.split('/');
        if (parts.length === 3) {
            return new Date(parseInt(parts[2]), parseInt(parts[0]) - 1, parseInt(parts[1]));
        }
        return null;
    }

    // Validate segments for gaps, overlaps, and segment limit
    validateSegments() {
        const errors = [];
        
        // Check segment count (excluding trial) - only validate if segments exist
        if (this.segments && this.segments.length > 0) {
            const nonTrialSegments = this.segments.filter(s => !s.isTrialSegment);
            if (nonTrialSegments.length > 12) {
                errors.push({
                    type: 'segmentLimit',
                    message: `Maximum 12 segments allowed (excluding Trial). Current: ${nonTrialSegments.length} segments.`
                });
            }
        }
        
        // Check continuity (gaps and overlaps)
        if (this.segments.length > 1) {
            for (let i = 0; i < this.segments.length - 1; i++) {
                const currentSegment = this.segments[i];
                const nextSegment = this.segments[i + 1];
                
                const currentEndDate = currentSegment.endDateObj || 
                    this.parseDateFromInput(currentSegment.endDateValue) || 
                    this.parseDateFromDisplay(currentSegment.endDateDisplay);
                const nextStartDate = nextSegment.startDateObj || 
                    this.parseDateFromInput(nextSegment.startDateValue);
                
                if (!currentEndDate || !nextStartDate) {
                    continue; // Skip if dates are invalid
                }
                
                // Calculate expected next start date (current end date + 1 day)
                const expectedNextStart = this.addDays(currentEndDate, 1);
                
                // Check for gap or overlap
                if (nextStartDate.getTime() < expectedNextStart.getTime()) {
                    // Overlap detected
                    errors.push({
                        type: 'overlap',
                        message: `Segments cannot have gaps or overlaps between them. Segment "${nextSegment.name}" starts before "${currentSegment.name}" ends.`
                    });
                } else if (nextStartDate.getTime() > expectedNextStart.getTime()) {
                    // Gap detected
                    errors.push({
                        type: 'gap',
                        message: `Segments cannot have gaps or overlaps between them. Gap detected between "${currentSegment.name}" and "${nextSegment.name}".`
                    });
                }
            }
        }
        
        this.validationErrors = errors;
        this.isValid = errors.length === 0;
        this.validationStatus = this.isValid; // Update @api property for Flow
        
        // Publish validation status via LMS
        this.publishValidationStatus();
        
        // Dispatch custom event for Flow to listen to
        this.dispatchEvent(new CustomEvent('validationchange', {
            detail: {
                isValid: this.isValid,
                errors: this.validationErrors
            },
            bubbles: true,
            composed: true
        }));
    }

    // Publish validation status to Flow
    publishValidationStatus() {
        if (this.messageContext) {
            const payload = {
                isValid: this.isValid,
                validationErrors: this.validationErrors,
                source: 'validation'
            };
            
            publish(this.messageContext, RLM_RAMP_SCHEDULE_CHANNEL, payload);
        }
    }

    get hasValidationErrors() {
        return this.validationErrors && this.validationErrors.length > 0;
    }

    get validationErrorMessage() {
        if (this.hasValidationErrors) {
            // Prioritize segment limit errors, then gap/overlap errors
            const segmentLimitError = this.validationErrors.find(e => e.type === 'segmentLimit');
            if (segmentLimitError) {
                return segmentLimitError.message;
            }
            const gapOrOverlapError = this.validationErrors.find(e => e.type === 'gap' || e.type === 'overlap');
            if (gapOrOverlapError) {
                return 'Segments cannot have gaps or overlaps between them';
            }
            return this.validationErrors[0].message;
        }
        return '';
    }

    /**
     * @api method to get segments data for the API
     * Returns array of segment definitions formatted for the Apex API
     */
    @api
    getSegmentsForApi() {
        return this.segments.map((segment, index) => {
            // Map internal segment type to API segment type
            const segmentTypeMapping = {
                'TRIAL': 'TRIAL',
                'YEARLY': 'YEARLY',
                'CUSTOM': 'CUSTOM',
                'PRO-RATA': 'PRO-RATED'
            };
            
            return {
                sequence: index + 1,
                name: segment.name,
                segmentType: segmentTypeMapping[segment.type] || segment.type,
                startDate: segment.startDateValue,
                endDate: segment.endDateValue,
                discountPercent: segment.discount || 0,
                upliftPercent: segment.uplift || 0
            };
        });
    }

    /**
     * @api method to get schedule metadata
     * Returns schedule name and type
     */
    @api
    getScheduleMetadata() {
        return {
            scheduleName: this.scheduleName,
            scheduleType: this.scheduleType === 'Annual' ? 'YEARLY' : 'CUSTOM',
            startDate: this.startDate
        };
    }

    /**
     * @api method to check if segments are valid
     */
    @api
    isScheduleValid() {
        return this.isValid;
    }
}