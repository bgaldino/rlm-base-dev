import { LightningElement, api } from 'lwc';
import { FlowNavigationNextEvent, FlowAttributeChangeEvent } from 'lightning/flowSupport';

export default class AppointmentSelector extends LightningElement {
    // --- All Inputs ---
    @api salesTransactionItems = [];
    @api productClassification;
    @api qualificationContext;
    @api transactionRecord;
    @api summary;
    // The duplicate "@api slotsText;" has been removed from here.
    
    // --- Original properties for appointment slot selection ---
    @api selectedStartTime;
    @api selectedFinishTime;
    @api selectedGrade;
    selectedSlotId = null;
    _slotsText = '';
    groupedSlots = [];
    allSlots = [];
    hasSlots = false;

    // --- SAFER Debugging Logic ---
    connectedCallback() {
        console.log('--- COMPONENT DEBUG START ---');
        console.log('salesTransactionItems:', this.salesTransactionItems);
        console.log('productClassification:', this.productClassification);
        console.log('qualificationContext:', this.qualificationContext);
        console.log('transactionRecord:', this.transactionRecord);
        console.log('summary:', this.summary);
        console.log('slotsText:', this._slotsText);
        console.log('--- COMPONENT DEBUG END ---');
    }

    get debugData() {
        return [
            { label: 'salesTransactionItems', value: JSON.stringify(this.salesTransactionItems, null, 2) },
            { label: 'productClassification', value: JSON.stringify(this.productClassification, null, 2) },
            { label: 'qualificationContext', value: JSON.stringify(this.qualificationContext, null, 2) },
            { label: 'transactionRecord', value: JSON.stringify(this.transactionRecord, null, 2) },
            { label: 'summary', value: JSON.stringify(this.summary, null, 2) }
        ];
    }
    
    // Original logic continues below...
    
    // This is the correct declaration for slotsText, using a getter and setter
    @api
    get slotsText() { return this._slotsText; }
    set slotsText(value) {
        this._slotsText = value;
        this.processSlots();
    }

    get isNextDisabled() { return !this.selectedSlotId; }

    processSlots() {
        if (!this._slotsText) { this.hasSlots = false; this.groupedSlots = []; return; }
        this.allSlots = [];
        const cleanedText = this._slotsText.replace('null', '').trim();
        const slotChunks = cleanedText.split('Slot:').slice(1);
        slotChunks.forEach(chunk => {
            const idMatch = chunk.match(/^(\d+)/);
            const startMatch = chunk.match(/Start:\s*([\d-]+\s[\d:]+)/);
            const finishMatch = chunk.match(/Finish:\s*([\d-]+\s[\d:]+)/);
            const gradeMatch = chunk.match(/Grade:\s*(\d+)/);
            if (idMatch && startMatch && finishMatch && gradeMatch) {
                const grade = parseInt(gradeMatch[1], 10);
                this.allSlots.push({ id: idMatch[1], start: new Date(startMatch[1]), finish: new Date(finishMatch[1]), grade: grade });
            }
        });
        this.hasSlots = this.allSlots.length > 0;
        if (!this.hasSlots) { this.groupedSlots = []; return; }
        const slotsByDate = this.allSlots.reduce((acc, slot) => {
            const date = slot.start.toISOString().split('T')[0];
            if (!acc[date]) acc[date] = [];
            acc[date].push(slot);
            return acc;
        }, {});
        this.groupedSlots = Object.keys(slotsByDate).map(date => ({
            date: date,
            formattedDate: new Date(date).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' }),
            slots: slotsByDate[date].map(slot => {
                const isSelected = this.selectedSlotId === slot.id;
                return { ...slot, timeRange: `${this.formatTime(slot.start)} - ${this.formatTime(slot.finish)}`, badgeClass: slot.grade >= 90 ? 'slds-badge slds-badge_lightest badge-gold' : 'slds-badge slds-badge_lightest', isSelected: isSelected, itemClass: isSelected ? 'slot-item slds-is-selected' : 'slot-item' }
            })
        }));
    }

    formatTime(date) { return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'UTC' }); }

    handleSlotSelection(event) {
        this.selectedSlotId = event.currentTarget.dataset.slotId;
        const selectedSlot = this.allSlots.find(slot => slot.id === this.selectedSlotId);
        if (selectedSlot) {
            this.selectedStartTime = selectedSlot.start.toISOString();
            this.selectedFinishTime = selectedSlot.finish.toISOString();
            this.selectedGrade = selectedSlot.grade;
            this.dispatchEvent(new FlowAttributeChangeEvent('selectedStartTime', this.selectedStartTime));
            this.dispatchEvent(new FlowAttributeChangeEvent('selectedFinishTime', this.selectedFinishTime));
            this.dispatchEvent(new FlowAttributeChangeEvent('selectedGrade', this.selectedGrade));
            this.processSlots();
        }
    }

    handleNextClick() { if (!this.isNextDisabled) { this.dispatchEvent(new FlowNavigationNextEvent()); } }
}