import { LightningElement, api, wire } from 'lwc';
import { refreshApex } from '@salesforce/apex';
import { NavigationMixin } from 'lightning/navigation';
import getBillingScheduleGroupData from '@salesforce/apex/RLM_BSGTimelineController.getBillingScheduleGroupData';
import getConsolidatedTimeline from '@salesforce/apex/RLM_BSGTimelineController.getConsolidatedTimeline';

export default class RlmBsgOverview extends NavigationMixin(LightningElement) {
    @api recordId;

    bsgData;
    rawSegments = [];
    chartGroups = [];
    consolidatedSegments = [];
    ganttSchedules = [];
    monthLabels = [];
    chartPlotClass = 'chart-plot-area';
    chartInnerStyle = '';
    isCrowdedChart = false;
    selectedSchedule;
    isLoading = true;
    error;
    activeView = 'period';
    milestoneChartItems = [];
    _isMilestoneBilling = false;
    _wiredBSG;
    _wiredTimeline;

    @wire(getBillingScheduleGroupData, { recordId: '$recordId' })
    wiredBSGData(result) {
        this._wiredBSG = result;
        if (result.data) {
            this.bsgData = result.data;
            this.error = undefined;
            if (this.rawSegments.length > 0) {
                this._buildAll();
            }
        } else if (result.error) {
            this.error = result.error.body?.message || 'An error occurred loading the BSG data';
            this.bsgData = undefined;
            this.isLoading = false;
        }
    }

    @wire(getConsolidatedTimeline, { recordId: '$recordId' })
    wiredConsolidatedData(result) {
        this._wiredTimeline = result;
        if (result.data) {
            this.rawSegments = result.data;
            this.error = undefined;
            this._buildAll();
        } else if (result.error) {
            this.error = result.error.body?.message || 'An error occurred loading the consolidated data';
            this.consolidatedSegments = [];
            this.chartGroups = [];
            this.isLoading = false;
        }
    }

    // ─── Getters ─────────────────────────────────────────────────────────────

    get hasData() {
        return !this.isLoading && this.bsgData != null;
    }

    get segmentCount() {
        return this.consolidatedSegments ? this.consolidatedSegments.length : 0;
    }

    get bsCount() {
        return this.bsgData?.billingSchedules?.length || 0;
    }

    get scheduleCount() {
        return this.ganttSchedules ? this.ganttSchedules.length : 0;
    }

    get hasScheduleData() {
        return !this.isLoading && this.ganttSchedules && this.ganttSchedules.length > 0;
    }

    get hasSegments() {
        return this.chartGroups && this.chartGroups.length > 0;
    }

    get periodTableRows() {
        if (!this.chartGroups) return [];

        return this.chartGroups.map(g => {
            const activeBS = g.activeBS || g.formattedActiveBS || [];
            const netQty = activeBS.reduce((sum, bs) => sum + (bs.quantity || 0), 0);
            const scheduleLinks = activeBS.map(bs => ({
                id: bs.id || bs.scheduleNumber,
                label: bs.scheduleNumber
            }));

            let status, statusClass;
            if (g.isSuspended) {
                status = 'Suspended';
                statusClass = 'status-suspended';
            } else if (g.isAfterEnd) {
                status = 'Past End Date';
                statusClass = 'status-cancelled';
            } else if (g.billedAmount > 0 && g.pendingAmount === 0) {
                status = 'Billed';
                statusClass = 'status-billed';
            } else if (g.billedAmount > 0 && g.pendingAmount > 0) {
                status = 'Partial';
                statusClass = 'status-partial';
            } else {
                status = 'Pending';
                statusClass = 'status-pending';
            }

            let rowClass = 'slds-hint-parent';
            if (g.isSuspended) rowClass += ' suspended-table-row';
            if (g.isAfterEnd) rowClass += ' past-end-row';

            return {
                key: g.key,
                label: g.label,
                netQty: String(netQty),
                formattedBilling: g.isSuspended ? '$0.00'
                    : g.isProrated ? `${g.formattedNet || this.formatCurrency(g.netAmount)} (prorated)`
                    : (g.formattedNet || this.formatCurrency(g.netAmount)),
                formattedCredits: '--',
                scheduleLinks,
                status,
                statusClass,
                rowClass
            };
        });
    }

    get selectedScheduleTitle() {
        return this.selectedSchedule ?
            `${this.selectedSchedule.scheduleNumber} - ${this.selectedSchedule.status} - ${this.selectedSchedule.category}` : '';
    }

    get isMilestoneBilling() { return this._isMilestoneBilling; }
    get periodViewLabel() { return 'Billings by Period'; }
    get isTimelineView() { return this.activeView === 'timeline'; }
    get isPeriodView()   { return this.activeView === 'period'; }
    get timelineButtonVariant() { return this.activeView === 'timeline' ? 'brand' : 'neutral'; }
    get periodButtonVariant()   { return this.activeView === 'period'   ? 'brand' : 'neutral'; }

    showTimelineView() { this.activeView = 'timeline'; }
    showPeriodView()   { this.activeView = 'period'; }

    handleRefresh() {
        this.isLoading = true;
        this.selectedSchedule = undefined;
        Promise.all([
            refreshApex(this._wiredBSG),
            refreshApex(this._wiredTimeline)
        ]).catch(() => { this.isLoading = false; });
    }

    get hasBsgEndDate() {
        return !!this.bsgData?.endDate;
    }

    get chartSuspensionOverlayStyle() {
        if (!this.hasSuspension || !this.chartGroups || this.chartGroups.length === 0) return '';
        const groups = this.chartGroups;
        const suspStart = new Date(this.bsgData.suspensionDate);
        const suspEnd = this.bsgData.resumptionDate ? new Date(this.bsgData.resumptionDate) : null;

        if (this._isMilestoneBilling) {
            // Position based on bar indices relative to milestone sortDates
            const count = groups.length;
            if (count === 0) return '';
            let firstIdx = -1, lastIdx = -1;
            for (let i = 0; i < count; i++) {
                const d = groups[i].sortDate;
                if (!d || isNaN(d.getTime())) continue;
                const inSusp = suspEnd ? (d >= suspStart && d <= suspEnd) : (d >= suspStart);
                if (inSusp) {
                    if (firstIdx === -1) firstIdx = i;
                    lastIdx = i;
                }
            }
            if (firstIdx === -1) {
                // No milestones fall in suspension — show zone between nearest bars
                const leftPct = 0;
                let rightIdx = groups.findIndex(g => g.sortDate && g.sortDate > suspStart);
                if (rightIdx === -1) rightIdx = count;
                const left = ((rightIdx - 0.5) / count) * 100;
                const width = (1 / count) * 100;
                return `left: ${Math.max(0, left - width / 2)}%; width: ${Math.max(width, 5)}%;`;
            }
            const leftPct = (firstIdx / count) * 100;
            const widthPct = ((lastIdx - firstIdx + 1) / count) * 100;
            return `left: ${leftPct}%; width: ${Math.max(widthPct, 3)}%;`;
        }

        const termUnit = this._getTermUnit();
        const firstDate = new Date(groups[0].key);
        const lastDate = new Date(groups[groups.length - 1].key);
        const lastPeriodEnd = this._periodEnd(lastDate, termUnit);

        const totalSpan = lastPeriodEnd.getTime() - firstDate.getTime();
        if (totalSpan <= 0) return '';

        const effectiveEnd = suspEnd || lastPeriodEnd;
        const clampedStart = suspStart < firstDate ? firstDate : suspStart;
        const clampedEnd = effectiveEnd > lastPeriodEnd ? lastPeriodEnd : effectiveEnd;

        const leftPct = ((clampedStart.getTime() - firstDate.getTime()) / totalSpan) * 100;
        const widthPct = ((clampedEnd.getTime() - clampedStart.getTime()) / totalSpan) * 100;

        if (widthPct <= 0) return '';
        return `left: ${leftPct}%; width: ${widthPct}%;`;
    }

    get bsgEndDateLabel() {
        if (!this.bsgData?.endDate) return '';
        return 'End: ' + this.formatDate(this.bsgData.endDate);
    }

    get bsgEndDateChartStyle() {
        if (this._isMilestoneBilling) return '';
        if (!this.bsgData?.endDate || !this.chartGroups || this.chartGroups.length === 0) return '';
        const endDate = new Date(this.bsgData.endDate);
        const groups = this.chartGroups;
        const termUnit = this._getTermUnit();

        const firstDate = new Date(groups[0].key);
        const lastDate = new Date(groups[groups.length - 1].key);
        const lastPeriodEnd = this._periodEnd(lastDate, termUnit);

        if (endDate > lastPeriodEnd) return '';

        const totalSpan = lastPeriodEnd.getTime() - firstDate.getTime();
        if (totalSpan <= 0) return '';

        const endOffset = endDate.getTime() - firstDate.getTime();
        const pct = Math.min(100, Math.max(0, (endOffset / totalSpan) * 100));
        return `left: ${pct}%;`;
    }

    get bsgEndDateGanttStyle() {
        if (!this.bsgData?.endDate || !this.bsgData?.billingSchedules) return '';
        const schedules = this.bsgData.billingSchedules;
        let minDate = null;
        let maxDate = null;
        schedules.forEach(bs => {
            const s = new Date(bs.startDate);
            const e = new Date(bs.endDate);
            if (!minDate || s < minDate) minDate = s;
            if (!maxDate || e > maxDate) maxDate = e;
        });
        if (!minDate || !maxDate) return '';

        const totalDays = this.daysBetween(minDate, maxDate);
        if (totalDays === 0) return '';

        const endDate = new Date(this.bsgData.endDate);
        if (endDate > maxDate) return '';

        const leftPct = (this.daysBetween(minDate, endDate) / totalDays) * 100;
        const leftFrac = leftPct / 100;
        return `left: calc(200px + (100% - 200px) * ${leftFrac});`;
    }

    get hasSuspension() {
        return !!this.bsgData?.suspensionDate;
    }

    get suspensionOverlayStyle() {
        if (!this.bsgData?.suspensionDate || !this.ganttSchedules || this.ganttSchedules.length === 0) return '';

        const schedules = this.bsgData.billingSchedules;
        let minDate = null;
        let maxDate = null;
        schedules.forEach(bs => {
            const s = bs.startDate ? new Date(bs.startDate) : null;
            const e = bs.endDate ? new Date(bs.endDate) : null;
            if (s && (!minDate || s < minDate)) minDate = s;
            if (e && (!maxDate || e > maxDate)) maxDate = e;
        });

        // For milestone BSGs with no end date, use resumption date or a reasonable range
        if (minDate && !maxDate) {
            const suspEnd = this.bsgData.resumptionDate ? new Date(this.bsgData.resumptionDate) : null;
            const lastMilestone = this._isMilestoneBilling && this.milestoneChartItems?.length > 0
                ? this.milestoneChartItems.reduce((latest, m) => {
                    if (!m.completionDate) return latest;
                    const d = new Date(m.completionDate);
                    return (!latest || d > latest) ? d : latest;
                }, null)
                : null;
            maxDate = suspEnd || lastMilestone || new Date(minDate.getTime() + 365 * 86400000);
        }
        if (!minDate || !maxDate) return '';

        const totalDays = this.daysBetween(minDate, maxDate);
        if (totalDays === 0) return '';

        const suspStart = new Date(this.bsgData.suspensionDate);
        const suspEnd = this.bsgData.resumptionDate ? new Date(this.bsgData.resumptionDate) : maxDate;

        const leftPct = (this.daysBetween(minDate, suspStart) / totalDays) * 100;
        const widthPct = (this.daysBetween(suspStart, suspEnd) / totalDays) * 100;

        const leftFrac = leftPct / 100;
        const widthFrac = widthPct / 100;
        return `left: calc(200px + (100% - 200px) * ${leftFrac}); width: calc((100% - 200px) * ${widthFrac});`;
    }

    get formattedTotalBilled() {
        return this.formatCurrency(this.bsgData?.totalBilledAmount || 0);
    }

    get formattedTotalPending() {
        return this.formatCurrency(this.bsgData?.totalPendingAmount || 0);
    }

    get netQuantity() {
        if (!this.bsgData?.billingSchedules) return 0;
        return this.bsgData.billingSchedules.reduce((sum, bs) => sum + (bs.quantity || 0), 0);
    }

    get billingCompletionPercentage() {
        const billed = this.bsgData?.totalBilledAmount || 0;
        const pending = this.bsgData?.totalPendingAmount || 0;
        const total = billed + pending;
        if (total === 0) return '0.0%';
        return `${((billed / total) * 100).toFixed(1)}%`;
    }

    get billingCompletionSubtext() {
        const total = (this.bsgData?.totalBilledAmount || 0) + (this.bsgData?.totalPendingAmount || 0);
        return `${this.formattedTotalBilled} of ${this.formatCurrency(total)}`;
    }

    get billedBarStyle() {
        const billed = this.bsgData?.totalBilledAmount || 0;
        const pending = this.bsgData?.totalPendingAmount || 0;
        const total = billed + pending;
        if (total === 0) return 'width: 0%';
        return `width: ${(billed / total) * 100}%`;
    }

    get pendingBarStyle() {
        const billed = this.bsgData?.totalBilledAmount || 0;
        const pending = this.bsgData?.totalPendingAmount || 0;
        const total = billed + pending;
        if (total === 0) return 'width: 0%; left: 0%';
        const billedPct = (billed / total) * 100;
        const pendingPct = (pending / total) * 100;
        return `width: ${pendingPct}%; left: ${billedPct}%`;
    }

    get yAxisLabels() {
        if (!this.chartGroups || this.chartGroups.length === 0) return [];
        let maxValue = 0;
        this.chartGroups.forEach(g => {
            if ((g.netAmount || 0) > maxValue) maxValue = g.netAmount;
        });
        if (maxValue === 0) return ['$0.00', '$0.00', '$0.00', '$0.00', '$0.00'];
        const labels = [];
        for (let i = 4; i >= 0; i--) {
            labels.push(this.formatCurrency((maxValue / 4) * i));
        }
        return labels;
    }

    // ─── Core build ──────────────────────────────────────────────────────────

    _buildAll() {
        if (!this.bsgData) {
            this.consolidatedSegments = [];
            this.chartGroups = [];
            this.ganttSchedules = [];
            this.isLoading = false;
            return;
        }

        // Check if this is a milestone-billed BSG
        const schedules = this.bsgData?.billingSchedules || [];
        this._isMilestoneBilling = schedules.length > 0 &&
            schedules.some(bs => (bs.billingTermUnit || '').toLowerCase().includes('milestone'));

        if (this._isMilestoneBilling) {
            this.milestoneChartItems = this.bsgData.milestoneItems || [];
            this._buildMilestoneChartGroups();
            this.processGanttSchedules();
            this.isLoading = false;
            return;
        }

        if (this.rawSegments && this.rawSegments.length > 0) {
            this.processConsolidatedSegments(this.rawSegments);
            this.buildChartGroups();
        }
        this.processGanttSchedules();
        this.isLoading = false;
    }

    _buildMilestoneChartGroups() {
        const items = this.milestoneChartItems;
        if (!items || items.length === 0) {
            this.chartGroups = [];
            return;
        }

        const withDates = items.filter(i => i.completionDate);
        const noDates = items.filter(i => !i.completionDate);

        withDates.sort((a, b) => new Date(a.completionDate) - new Date(b.completionDate));

        const allItems = [...withDates, ...noDates];

        const bs = this.bsgData?.billingSchedules?.[0];
        const bsLink = bs ? { id: bs.id, scheduleNumber: bs.scheduleNumber } : null;
        const bsQuantity = bs?.quantity != null ? bs.quantity : 1;

        const buckets = allItems.map((item, idx) => {
            const amt = item.amount || 0;
            const isInvoiced = item.status === 'Invoiced';

            let label;
            if (item.completionDate) {
                const d = new Date(item.completionDate);
                label = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: '2-digit' }).format(d);
            } else {
                label = 'Event';
            }

            return {
                key: item.id || String(idx),
                label,
                sortDate: item.completionDate ? new Date(item.completionDate) : new Date('2099-12-31'),
                netAmount: amt,
                billedAmount: isInvoiced ? amt : 0,
                pendingAmount: isInvoiced ? 0 : amt,
                isZero: amt <= 0,
                isSuspended: false,
                isProrated: false,
                isAfterEnd: false,
                activeBS: bsLink ? [{
                    ...bsLink,
                    quantity: bsQuantity,
                    amount: amt
                }] : [],
                _isMilestone: true,
                _milestoneName: item.name,
                _milestoneStatus: item.status,
                _milestoneType: item.milestoneType
            };
        });

        this._finaliseChartGroups(buckets);
    }

    // ─── Term unit helpers ────────────────────────────────────────────────────

    _normaliseUnit(raw) {
        const s = (raw || '').toLowerCase().replace(/[-_ ]/g, '');
        if (s === 'month' || s === 'monthly')               return 'month';
        if (s === 'year' || s === 'annual' || s === 'yearly') return 'year';
        if (s === 'quarter' || s === 'quarterly')            return 'quarterly';
        if (s === 'semiannual' || s === 'semiannually')      return 'semiannual';
        if (s === 'onetime')                                 return 'onetime';
        return 'month';
    }

    // Finest unit wins so no BS gets collapsed into a too-coarse bucket
    // Priority: month(5) > quarterly(4) > semiannual(3) > year(2) > onetime(1)
    _getFinestUnit(schedules) {
        const priority = { month: 5, quarterly: 4, semiannual: 3, year: 2, onetime: 1 };
        let best = 'month';
        let bestP = 0;
        (schedules || []).forEach(bs => {
            const u = this._normaliseUnit(bs.billingTermUnit);
            const p = priority[u] || 0;
            if (p > bestP) { bestP = p; best = u; }
        });
        return best;
    }

    _getTermUnit() {
        // Always use the finest (most granular) billing frequency across all
        // billing schedules so the X-axis captures every billing event.
        return this._getFinestUnit(this.bsgData?.billingSchedules);
    }

    // ─── Period iteration helpers ─────────────────────────────────────────────

    // Advance a date by one bucket period
    _advancePeriod(date, termUnit) {
        return this._advancePeriodByN(date, termUnit, 1);
    }

    // Advance a date by N units of the given term
    _advancePeriodByN(date, termUnit, n) {
        const d = new Date(date);
        const count = n || 1;
        switch (termUnit) {
            case 'year':      d.setFullYear(d.getFullYear() + count); break;
            case 'semiannual':d.setMonth(d.getMonth() + 6 * count);   break;
            case 'quarterly': d.setMonth(d.getMonth() + 3 * count);   break;
            case 'onetime':   d.setFullYear(d.getFullYear() + 100);   break;
            case 'month':
            default:          d.setMonth(d.getMonth() + count);       break;
        }
        return d;
    }

    // Last day of the bucket that starts at periodStart
    _periodEnd(periodStart, termUnit) {
        const next = this._advancePeriod(periodStart, termUnit);
        const end = new Date(next);
        end.setDate(end.getDate() - 1);
        return end;
    }

    _bucketLabel(date, termUnit) {
        const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        const yr = String(date.getFullYear()).slice(-2);
        switch (termUnit) {
            case 'year':      return String(date.getFullYear());
            case 'semiannual': {
                const startMo = date.getMonth() < 6 ? 0 : 6;
                return `${months[startMo]}-${months[startMo + 5]} '${yr}`;
            }
            case 'quarterly': {
                const qStart = Math.floor(date.getMonth() / 3) * 3;
                return `${months[qStart]}-${months[qStart + 2]} '${yr}`;
            }
            case 'onetime':   return 'One-Time';
            case 'month':
            default:          return `${months[date.getMonth()]} '${yr}`;
        }
    }

    // Snap a date back to the start of its bucket
    _snapToPeriodStart(date, termUnit) {
        const d = new Date(date);
        switch (termUnit) {
            case 'year':
                return new Date(d.getFullYear(), 0, 1);
            case 'semiannual':
                return new Date(d.getFullYear(), d.getMonth() < 6 ? 0 : 6, 1);
            case 'quarterly':
                return new Date(d.getFullYear(), Math.floor(d.getMonth() / 3) * 3, 1);
            case 'onetime':
                return new Date(d.getFullYear(), d.getMonth(), d.getDate());
            case 'month':
            default:
                return new Date(d.getFullYear(), d.getMonth(), 1);
        }
    }

    // ─── Main chart build: calendar-period bucketing ──────────────────────────

    buildChartGroups() {
        const schedules = this.bsgData?.billingSchedules;
        if (!schedules || schedules.length === 0) {
            this.chartGroups = [];
            return;
        }

        const termUnit = this._getTermUnit();

        // Find overall date range across all BSs
        let minDate = null;
        let maxDate = null;
        schedules.forEach(bs => {
            if (!bs.startDate || !bs.endDate) return;
            const s = new Date(bs.startDate);
            const e = new Date(bs.endDate);
            if (!minDate || s < minDate) minDate = s;
            if (!maxDate || e > maxDate) maxDate = e;
        });

        if (!minDate || !maxDate) { this.chartGroups = []; return; }

        // Handle One-Time: single bucket
        if (termUnit === 'onetime') {
            this._buildOneTimeBucket(schedules);
            return;
        }

        // ── Step 1: build ordered list of all calendar period start dates ──
        const periodStarts = [];
        let cursor = this._snapToPeriodStart(minDate, termUnit);
        while (cursor <= maxDate) {
            periodStarts.push(new Date(cursor));
            cursor = this._advancePeriod(cursor, termUnit);
        }

        // ── Step 2: pre-compute chronological billed periods per BS ────────
        // Each BS bills at its OWN frequency (billingTermUnit). We compute
        // which X-axis buckets each BS actually bills in, and place the full
        // billingPeriodAmount only in those buckets. A quarterly BS in a
        // monthly X-axis will show a bar every 3rd month.
        const bsContributions = schedules.map(bs => {
            const bsStart     = new Date(bs.startDate);
            const bsEnd       = new Date(bs.endDate);
            const periodAmt   = Math.abs(bs.billingPeriodAmount != null ? bs.billingPeriodAmount : 0);
            const isCredit    = (bs.billingPeriodAmount || 0) < 0;
            const billedAmt   = Math.abs(bs.billedAmount  != null ? bs.billedAmount  : 0);
            const bsUnit      = this._normaliseUnit(bs.billingTermUnit);
            const bsTerm      = bs.billingTerm != null && bs.billingTerm > 0 ? bs.billingTerm : 1;

            // Build the set of X-axis bucket keys where this BS actually bills.
            // Use billingTerm to determine how many units to advance per period.
            // e.g. billingTerm=3, billingTermUnit='Month' → advance 3 months each step
            const billingBucketKeys = new Set();
            if (bsUnit === 'onetime') {
                const snap = this._snapToPeriodStart(bsStart, termUnit);
                billingBucketKeys.add(snap.toISOString().slice(0, 10));
            } else {
                let bsCursor = new Date(bsStart);
                while (bsCursor <= bsEnd) {
                    const snap = this._snapToPeriodStart(bsCursor, termUnit);
                    billingBucketKeys.add(snap.toISOString().slice(0, 10));
                    bsCursor = this._advancePeriodByN(bsCursor, bsUnit, bsTerm);
                }
            }

            let billedRemaining = billedAmt;
            const map = new Map();

            periodStarts.forEach(ps => {
                const pe = this._periodEnd(ps, termUnit);
                if (ps > bsEnd || pe < bsStart) return;

                const key = ps.toISOString().slice(0, 10);

                if (!billingBucketKeys.has(key)) return;

                if (periodAmt === 0) {
                    map.set(key, { billedAmt: 0, pendingAmt: 0, isCredit });
                    return;
                }

                const thisBilled  = Math.min(billedRemaining, periodAmt);
                const thisPending = periodAmt - thisBilled;
                billedRemaining   = Math.max(0, billedRemaining - periodAmt);

                map.set(key, {
                    billedAmt:  Math.round(thisBilled  * 100) / 100,
                    pendingAmt: Math.round(thisPending * 100) / 100,
                    isCredit
                });
            });

            return map;
        });

        // ── Step 3: sum contributions per calendar period, handle suspension ──
        const suspStart = this.bsgData?.suspensionDate ? new Date(this.bsgData.suspensionDate) : null;
        const suspEnd   = this.bsgData?.resumptionDate ? new Date(this.bsgData.resumptionDate) : null;

        let suspendedBilled  = 0;
        let suspendedPending = 0;
        let resumptionBucketKey = null;

        // If there's a resumption date, find which bucket it falls in
        if (suspEnd) {
            const snap = this._snapToPeriodStart(suspEnd, termUnit);
            resumptionBucketKey = snap.toISOString().slice(0, 10);
        }

        const bsgEndDate = this.bsgData?.endDate ? new Date(this.bsgData.endDate) : null;

        const rawBuckets = periodStarts.map(ps => {
            const key = ps.toISOString().slice(0, 10);
            const pe  = this._periodEnd(ps, termUnit);

            // Check if this period is fully within the suspension window
            const isSuspended = suspStart && (
                suspEnd
                    ? (ps >= suspStart && pe <= suspEnd)
                    : (ps >= suspStart)
            );

            // Check if BSG ends within this period (prorated)
            const isProrated = bsgEndDate && bsgEndDate >= ps && bsgEndDate < pe;
            let prorationFactor = 1;
            if (isProrated) {
                const fullDays = this.daysBetween(ps, pe) + 1;
                const activeDays = this.daysBetween(ps, bsgEndDate) + 1;
                prorationFactor = activeDays / fullDays;
            }

            // Check if period is entirely after BSG end date
            const isAfterEnd = bsgEndDate && ps > bsgEndDate;

            let netBilled  = 0;
            let netPending = 0;
            const activeBS = [];

            if (!isAfterEnd) {
                bsContributions.forEach((map, idx) => {
                    const contrib = map.get(key);
                    if (!contrib) return;
                    const bs = schedules[idx];
                    let bAmt = contrib.billedAmt;
                    let pAmt = contrib.pendingAmt;

                    if (isProrated) {
                        bAmt = Math.round(bAmt * prorationFactor * 100) / 100;
                        pAmt = Math.round(pAmt * prorationFactor * 100) / 100;
                    }

                    if (contrib.isCredit) {
                        netBilled  -= bAmt;
                        netPending -= pAmt;
                    } else {
                        netBilled  += bAmt;
                        netPending += pAmt;
                    }
                    const amt = contrib.isCredit ? -(bAmt + pAmt) : (bAmt + pAmt);
                    activeBS.push({
                        scheduleNumber: bs.scheduleNumber || bs.id,
                        quantity: isProrated ? Math.round((bs.quantity || 0) * prorationFactor * 100) / 100 : (bs.quantity != null ? bs.quantity : 0),
                        amount: Math.round(amt * 100) / 100
                    });
                });
            }

            netBilled  = Math.round(netBilled  * 100) / 100;
            netPending = Math.round(netPending * 100) / 100;

            if (isSuspended) {
                suspendedPending += Math.max(0, Math.round((netBilled + netPending) * 100) / 100);
                return {
                    key,
                    label:         this._bucketLabel(ps, termUnit),
                    sortDate:      ps,
                    netAmount:     0,
                    billedAmount:  0,
                    pendingAmount: 0,
                    isZero:        false,
                    isSuspended:   true,
                    isProrated:    false,
                    isAfterEnd:    false,
                    activeBS:      []
                };
            }

            const netAmount = Math.round((netBilled + netPending) * 100) / 100;
            return {
                key,
                label:     this._bucketLabel(ps, termUnit),
                sortDate:  ps,
                netAmount: Math.max(0, netAmount),
                billedAmount:  Math.max(0, netBilled),
                pendingAmount: Math.max(0, netPending),
                isZero:        netAmount <= 0 && !isAfterEnd,
                isSuspended:   false,
                isProrated,
                isAfterEnd,
                activeBS
            };
        });

        // Add accumulated suspended billings to the resumption bucket
        if (suspendedPending > 0) {
            const targetKey = resumptionBucketKey;
            const targetBucket = targetKey
                ? rawBuckets.find(b => b.key === targetKey)
                : rawBuckets.find(b => !b.isSuspended && b.sortDate > suspStart);

            if (targetBucket) {
                targetBucket.pendingAmount = Math.round((targetBucket.pendingAmount + suspendedPending) * 100) / 100;
                targetBucket.netAmount = Math.round((targetBucket.billedAmount + targetBucket.pendingAmount) * 100) / 100;
                targetBucket.isZero = targetBucket.netAmount <= 0;
            }
        }

        this._finaliseChartGroups(rawBuckets);
    }

    _buildOneTimeBucket(schedules) {
        let billedAmount  = 0;
        let pendingAmount = 0;

        schedules.forEach(bs => {
            const billed  = bs.billedAmount  != null ? bs.billedAmount  : 0;
            const pending = bs.pendingAmount != null ? bs.pendingAmount : 0;
            billedAmount  += billed;
            pendingAmount += pending;
        });

        this._finaliseChartGroups([{
            key:           'onetime',
            label:         'One-Time',
            sortDate:      new Date(),
            netAmount:     Math.round((billedAmount + pendingAmount) * 100) / 100,
            billedAmount:  Math.round(billedAmount  * 100) / 100,
            pendingAmount: Math.round(pendingAmount * 100) / 100,
            isZero:        (billedAmount + pendingAmount) === 0
        }]);
    }

    _finaliseChartGroups(buckets) {
        const CHART_HEIGHT_PX = 200;
        const ZERO_MARKER_PX  = 4;

        let maxValue = 0;
        buckets.forEach(b => { if (b.netAmount > maxValue) maxValue = b.netAmount; });

        const count = buckets.length;
        const isCrowded = count > 12;
        const BAR_WIDTH_PX = count <= 3  ? 80 :
                             count <= 6  ? 70 :
                             count <= 12 ? 56 :
                             44;
        const BAR_GAP_PX = 16;
        this.isCrowdedChart = isCrowded;
        this.chartPlotClass = isCrowded ? 'chart-plot-area crowded' : 'chart-plot-area';
        this.chartInnerStyle = isCrowded
            ? `min-width: ${count * (BAR_WIDTH_PX + BAR_GAP_PX) + BAR_GAP_PX}px;`
            : '';

        this.chartGroups = buckets.map(b => {
            const isZero = b.isZero;
            const isSuspended = b.isSuspended === true;

            let totalBarPx, tooltip;

            if (isSuspended) {
                totalBarPx = CHART_HEIGHT_PX;
                tooltip = `${b.label}: Billing Suspended`;
            } else if (isZero) {
                totalBarPx = ZERO_MARKER_PX;
                tooltip = `${b.label}: $0.00 net (cancelled/amended)`;
            } else {
                totalBarPx = maxValue > 0 ? Math.max(ZERO_MARKER_PX, Math.round((b.netAmount / maxValue) * CHART_HEIGHT_PX)) : ZERO_MARKER_PX;
                tooltip = `${b.label}: ${this.formatCurrency(b.netAmount)} — Billed: ${this.formatCurrency(b.billedAmount)}, Pending: ${this.formatCurrency(b.pendingAmount)}`;
            }

            const gross      = b.billedAmount + b.pendingAmount;
            const billedPct  = gross > 0 ? Math.min(100, (b.billedAmount  / gross) * 100) : 0;
            const pendingPct = 100 - billedPct;

            const formattedActiveBS = (b.activeBS || []).map(bs => ({
                ...bs,
                formattedAmount: this.formatCurrency(bs.amount)
            }));
            const hasActiveBS = formattedActiveBS.length > 0;

            return {
                ...b,
                totalBarPx,
                billedPct,
                pendingPct,
                isZero:      isZero && !isSuspended,
                isSuspended,
                barGroupStyle:   `width: ${BAR_WIDTH_PX}px; height: ${CHART_HEIGHT_PX}px; display: flex; align-items: flex-end;`,
                xAxisLabelStyle: `width: ${BAR_WIDTH_PX}px; text-align: center;`,
                billingBarStyle: `height: ${totalBarPx}px; width: ${BAR_WIDTH_PX}px;`,
                billedSegStyle:  `height: ${billedPct}%; background: #2e844a; width: 100%;`,
                pendingSegStyle: `height: ${pendingPct}%; background: #5eb3f6; width: 100%;`,
                suspendedBarStyle: `height: ${CHART_HEIGHT_PX}px; width: ${BAR_WIDTH_PX}px; background: repeating-linear-gradient(45deg, #fe9339, #fe9339 4px, #ffb75d 4px, #ffb75d 8px); border-radius: 4px 4px 0 0; opacity: 0.7;`,
                zeroBarStyle:    `height: ${ZERO_MARKER_PX}px; width: ${BAR_WIDTH_PX}px; background: #dddbda; border-radius: 2px 2px 0 0;`,
                formattedNet:     this.formatCurrency(b.netAmount),
                formattedBilled:  this.formatCurrency(b.billedAmount),
                formattedPending: this.formatCurrency(b.pendingAmount),
                tooltip,
                formattedActiveBS,
                hasActiveBS
            };
        });
    }

    processConsolidatedSegments(segments) {
        if (!segments || segments.length === 0) {
            this.consolidatedSegments = [];
            return;
        }

        this.consolidatedSegments = segments.map((seg) => {
            const scheduleLinks = (seg.activeScheduleIds || []).map((id, idx) => ({
                id,
                label: seg.activeScheduleNumbers[idx] || id
            }));

            let statusClass = 'status-active';
            if (seg.status === 'Cancelled')              statusClass = 'status-cancelled';
            else if (seg.status === 'Completely Billed') statusClass = 'status-billed';

            let rowClass = 'slds-hint-parent';
            if (seg.status === 'Cancelled') rowClass += ' cancelled-row';

            // Explicitly convert numeric fields to strings so LWC renders 0 correctly
            const netQty         = seg.netQuantity  != null ? String(seg.netQuantity)  : '0';
            const periodicAmt    = seg.periodicBilling != null ? seg.periodicBilling : 0;
            const creditsAmt     = seg.credits         != null ? seg.credits         : 0;

            return {
                ...seg,
                netQuantityDisplay:       netQty,
                formattedStartDate:       this.formatDate(seg.startDate),
                formattedEndDate:         this.formatDate(seg.endDate),
                formattedPeriodicBilling: this.formatCurrency(periodicAmt),
                formattedCredits:         creditsAmt < 0 ? this.formatCurrency(creditsAmt) : '--',
                scheduleLinks,
                statusClass,
                rowClass
            };
        });
    }

    // ─── Gantt Timeline ─────────────────────────────────────────────────────────

    processGanttSchedules() {
        if (!this.bsgData || !this.bsgData.billingSchedules) {
            this.ganttSchedules = [];
            return;
        }

        const schedules = this.bsgData.billingSchedules;

        let minDate = null;
        let maxDate = null;

        schedules.forEach(bs => {
            const start = new Date(bs.startDate);
            const end = new Date(bs.endDate);
            if (!minDate || start < minDate) minDate = start;
            if (!maxDate || end > maxDate) maxDate = end;
        });

        if (!minDate || !maxDate) {
            this.ganttSchedules = [];
            return;
        }

        this.generateMonthLabels(minDate, maxDate);

        const totalDays = this.daysBetween(minDate, maxDate);

        this.ganttSchedules = schedules.map(bs => {
            const startDate = new Date(bs.startDate);
            const endDate = new Date(bs.endDate);

            const startOffset = this.daysBetween(minDate, startDate);
            const duration = this.daysBetween(startDate, endDate);

            const leftPercent = totalDays > 0 ? (startOffset / totalDays) * 100 : 0;
            const widthPercent = totalDays > 0 ? (duration / totalDays) * 100 : 100;

            let statusClass = 'active';
            if (bs.category === 'Cancellation' || bs.status === 'Cancelled') {
                statusClass = 'cancelled';
            } else if (bs.status === 'Completely Billed') {
                statusClass = 'billed';
            } else if (bs.status === 'Planned') {
                statusClass = 'planned';
            }

            let categoryClass = 'category-original';
            if (bs.category === 'Amendment') {
                categoryClass = 'category-amendment';
            } else if (bs.category === 'Cancellation') {
                categoryClass = 'category-cancellation';
            }

            const rawAmount = (bs.billingPeriodAmount != null) ? bs.billingPeriodAmount : bs.totalAmount;
            const displayAmount = this.formatCurrency(rawAmount);

            const termUnit = (bs.billingTermUnit || '').toLowerCase().replace(/[-_ ]/g, '');
            let frequencyLabel = '';
            if (termUnit === 'onetime') {
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

            return {
                ...bs,
                barStyle: `left: ${leftPercent}%; width: ${widthPercent}%;`,
                barClass: `timeline-bar ${statusClass}`,
                categoryClass,
                displayAmount: displayAmount + frequencyLabel
            };
        });
    }

    generateMonthLabels(minDate, maxDate) {
        const labels = [];
        let current = new Date(minDate.getFullYear(), minDate.getMonth(), 1);
        const end = new Date(maxDate.getFullYear(), maxDate.getMonth(), 1);

        const totalDays = this.daysBetween(minDate, maxDate);
        if (totalDays === 0) { this.monthLabels = []; return; }

        while (current <= end) {
            const monthStart = new Date(current);
            const monthEnd = new Date(current.getFullYear(), current.getMonth() + 1, 0);

            const visibleStart = monthStart < minDate ? minDate : monthStart;
            const visibleEnd = monthEnd > maxDate ? maxDate : monthEnd;

            const startOffset = this.daysBetween(minDate, visibleStart);
            const width = this.daysBetween(visibleStart, visibleEnd);

            const leftPercent = (startOffset / totalDays) * 100;
            const widthPercent = (width / totalDays) * 100;

            const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

            labels.push({
                key: `${current.getFullYear()}-${current.getMonth()}`,
                label: `${months[current.getMonth()]} ${String(current.getFullYear()).slice(-2)}`,
                style: `left: ${leftPercent}%; width: ${widthPercent}%;`
            });

            current.setMonth(current.getMonth() + 1);
        }

        this.monthLabels = labels;
    }

    handleScheduleClick(event) {
        event.stopPropagation();
        const scheduleId = event.currentTarget.dataset.scheduleId;
        const schedule = this.ganttSchedules.find(bs => bs.id === scheduleId);

        if (schedule) {
            const statusBadgeMap = {
                'ReadyForInvoicing': 'badge-info',
                'Active':           'badge-active',
                'CompletelyBilled': 'badge-billed',
                'Cancelled':        'badge-cancelled',
                'Planned':          'badge-planned'
            };
            const statusBadgeClass = statusBadgeMap[schedule.status] || 'badge-default';
            const displayStatus = this._humanizeLabel(schedule.status);
            const displayCategory = this._humanizeLabel(schedule.category);

            this.selectedSchedule = {
                ...schedule,
                displayStatus,
                displayCategory,
                formattedTotalAmount: this.formatCurrency(schedule.totalAmount),
                formattedBilledAmount: this.formatCurrency(schedule.billedAmount),
                formattedPendingAmount: this.formatCurrency(schedule.pendingAmount),
                formattedBillingPeriodAmount: this.formatCurrency(schedule.billingPeriodAmount),
                formattedUnitPrice: this.formatCurrency(schedule.unitPrice),
                formattedNetUnitPrice: this.formatCurrency(schedule.netUnitPrice),
                formattedStartDate: this.formatDate(schedule.startDate),
                formattedEndDate: this.formatDate(schedule.endDate),
                formattedNextBillingDate: this.formatDate(schedule.nextBillingDate),
                progressPercentage: this.calculateProgress(schedule.billedAmount, schedule.pendingAmount),
                progressBarStyle: `width: ${this.calculateProgress(schedule.billedAmount, schedule.pendingAmount)}`,
                categoryBadgeClass: 'badge-category',
                statusBadgeClass
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

    calculateProgress(billed, pending) {
        const b = billed || 0;
        const p = pending || 0;
        const total = b + p;
        if (total === 0) return '0%';
        return `${Math.round((b / total) * 100)}%`;
    }

    // ─── Navigation & utilities ───────────────────────────────────────────────

    navigateToSchedule(event) {
        const scheduleId = event.currentTarget.dataset.scheduleId;
        this[NavigationMixin.Navigate]({
            type: 'standard__recordPage',
            attributes: { recordId: scheduleId, objectApiName: 'BillingSchedule', actionName: 'view' }
        });
    }

    handleScheduleLinkClick(event) {
        event.preventDefault();
        event.stopPropagation();
        const scheduleId = event.currentTarget.dataset.scheduleId;
        this[NavigationMixin.Navigate]({
            type: 'standard__recordPage',
            attributes: { recordId: scheduleId, objectApiName: 'BillingSchedule', actionName: 'view' }
        });
    }

    formatCurrency(amount) {
        if (amount === null || amount === undefined) return '$0.00';
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2 }).format(amount);
    }

    formatDate(dateString) {
        if (!dateString) return '--';
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(date);
    }

    _humanizeLabel(value) {
        if (!value) return '';
        return value.replace(/([a-z])([A-Z])/g, '$1 $2')
                     .replace(/([A-Z]+)([A-Z][a-z])/g, '$1 $2');
    }
}