import { LightningElement, api, wire } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';
import getBillingScheduleGroupData from '@salesforce/apex/RLM_BSGTimelineController.getBillingScheduleGroupData';

export default class RlmBsgSchedulesTimeline extends NavigationMixin(LightningElement) {
    @api recordId;
    
    bsgData;
    billingSchedules = [];
    monthLabels = [];
    selectedSchedule;
    isLoading = true;
    error;
    
    @wire(getBillingScheduleGroupData, { recordId: '$recordId' })
    wiredBSGData({ error, data }) {
        this.isLoading = true;
        if (data) {
            this.bsgData = data;
            this.processSchedules();
            this.error = undefined;
            this.isLoading = false;
        } else if (error) {
            this.error = error.body?.message || 'An error occurred loading the data';
            this.bsgData = undefined;
            this.isLoading = false;
        }
    }
    
    get hasData() {
        return !this.isLoading && this.billingSchedules && this.billingSchedules.length > 0;
    }
    
    get scheduleCount() {
        return this.billingSchedules ? this.billingSchedules.length : 0;
    }
    
    get selectedScheduleTitle() {
        return this.selectedSchedule ? 
            `${this.selectedSchedule.scheduleNumber} - ${this.selectedSchedule.status} - ${this.selectedSchedule.category}` : '';
    }
    
    processSchedules() {
        if (!this.bsgData || !this.bsgData.billingSchedules) {
            return;
        }
        
        const schedules = this.bsgData.billingSchedules;
        
        // Find min and max dates for timeline
        let minDate = null;
        let maxDate = null;
        
        schedules.forEach(bs => {
            const start = new Date(bs.startDate);
            const end = new Date(bs.endDate);
            
            if (!minDate || start < minDate) minDate = start;
            if (!maxDate || end > maxDate) maxDate = end;
        });
        
        // Generate month labels
        this.generateMonthLabels(minDate, maxDate);
        
        // Process each schedule for display
        this.billingSchedules = schedules.map(bs => {
            const startDate = new Date(bs.startDate);
            const endDate = new Date(bs.endDate);
            
            // Calculate position and width
            const totalDays = this.daysBetween(minDate, maxDate);
            const startOffset = this.daysBetween(minDate, startDate);
            const duration = this.daysBetween(startDate, endDate);
            
            const leftPercent = (startOffset / totalDays) * 100;
            const widthPercent = (duration / totalDays) * 100;
            
            // Determine status class
            let statusClass = 'active';
            if (bs.category === 'Cancellation' || bs.status === 'Cancelled') {
                statusClass = 'cancelled';
            } else if (bs.status === 'Completely Billed') {
                statusClass = 'billed';
            } else if (bs.status === 'Planned') {
                statusClass = 'planned';
            }
            
            // Category badge class
            let categoryClass = 'category-original';
            if (bs.category === 'Amendment') {
                categoryClass = 'category-amendment';
            } else if (bs.category === 'Cancellation') {
                categoryClass = 'category-cancellation';
            }
            
            // Fix #7: pick the right value first, then format (avoid double-negating)
            const rawAmount = (bs.billingPeriodAmount != null) ? bs.billingPeriodAmount : bs.totalAmount;
            const displayAmount = this.formatCurrency(rawAmount);

            // Fix #1: append billing frequency suffix based on billingTermUnit
            const termUnit = (bs.billingTermUnit || '').toLowerCase().replace(/-/g, '').replace(/ /g, '');
            let frequencyLabel = '';
            if (termUnit === 'onetime' || termUnit === 'one-time') {
                frequencyLabel = ' (One-Time)';
            } else if (termUnit === 'month') {
                frequencyLabel = '/mo';
            } else if (termUnit === 'year') {
                frequencyLabel = '/yr';
            } else if (termUnit === 'semiannual') {
                frequencyLabel = '/semi-annual';
            } else if (termUnit === 'quarterly') {
                frequencyLabel = '/qtr';
            } else if (termUnit && termUnit !== '') {
                frequencyLabel = ' (' + bs.billingTermUnit + ')';
            }
            const displayAmountWithFreq = displayAmount + frequencyLabel;

            return {
                ...bs,
                barStyle: `left: ${leftPercent}%; width: ${widthPercent}%;`,
                barClass: `timeline-bar ${statusClass}`,
                categoryClass: categoryClass,
                displayAmount: displayAmountWithFreq
            };
        });
    }
    
    generateMonthLabels(minDate, maxDate) {
        const labels = [];
        let current = new Date(minDate.getFullYear(), minDate.getMonth(), 1);
        const end = new Date(maxDate.getFullYear(), maxDate.getMonth(), 1);
        
        const totalDays = this.daysBetween(minDate, maxDate);
        
        while (current <= end) {
            const monthStart = new Date(current);
            const monthEnd = new Date(current.getFullYear(), current.getMonth() + 1, 0);
            
            // Calculate visible portion of this month in timeline
            const visibleStart = monthStart < minDate ? minDate : monthStart;
            const visibleEnd = monthEnd > maxDate ? maxDate : monthEnd;
            
            const startOffset = this.daysBetween(minDate, visibleStart);
            const width = this.daysBetween(visibleStart, visibleEnd);
            
            const leftPercent = (startOffset / totalDays) * 100;
            const widthPercent = (width / totalDays) * 100;
            
            labels.push({
                key: `${current.getFullYear()}-${current.getMonth()}`,
                label: `${this.getMonthName(current.getMonth())} ${current.getFullYear() % 100}`,
                style: `left: ${leftPercent}%; width: ${widthPercent}%;`
            });
            
            current.setMonth(current.getMonth() + 1);
        }
        
        this.monthLabels = labels;
    }
    
    handleScheduleClick(event) {
        const scheduleId = event.currentTarget.dataset.scheduleId;
        const schedule = this.billingSchedules.find(bs => bs.id === scheduleId);
        
        if (schedule) {
            this.selectedSchedule = {
                ...schedule,
                formattedTotalAmount: this.formatCurrency(schedule.totalAmount),
                formattedBilledAmount: this.formatCurrency(schedule.billedAmount),
                formattedPendingAmount: this.formatCurrency(schedule.pendingAmount),
                formattedBillingPeriodAmount: this.formatCurrency(schedule.billingPeriodAmount),
                formattedUnitPrice: this.formatCurrency(schedule.unitPrice),
                formattedNetUnitPrice: this.formatCurrency(schedule.netUnitPrice),
                formattedStartDate: this.formatDate(schedule.startDate),
                formattedEndDate: this.formatDate(schedule.endDate),
                formattedNextBillingDate: this.formatDate(schedule.nextBillingDate),
                progressPercentage: this.calculateProgress(schedule.billedAmount, schedule.totalAmount),
                progressBarStyle: `width: ${this.calculateProgress(schedule.billedAmount, schedule.totalAmount)}`
            };
        }
    }
    
    closeScheduleDetails() {
        this.selectedSchedule = null;
    }
    
    daysBetween(date1, date2) {
        const oneDay = 24 * 60 * 60 * 1000;
        return Math.round(Math.abs((date2 - date1) / oneDay));
    }
    
    getMonthName(monthIndex) {
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        return months[monthIndex];
    }
    
    formatCurrency(amount) {
        if (amount === null || amount === undefined) return '$0.00';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(amount);
    }
    
    formatDate(dateString) {
        if (!dateString) return '--';
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        }).format(date);
    }
    
    calculateProgress(billed, total) {
        if (!total || total === 0) return '0%';
        const percentage = (billed / total) * 100;
        return `${Math.round(percentage)}%`;
    }
}