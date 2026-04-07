import { LightningElement, api, wire } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';
import getBillingScheduleGroupData from '@salesforce/apex/RLM_BSGTimelineController.getBillingScheduleGroupData';
import getConsolidatedTimeline from '@salesforce/apex/RLM_BSGTimelineController.getConsolidatedTimeline';

export default class RlmBsgConsolidatedTimeline extends NavigationMixin(LightningElement) {
    @api recordId;

    bsgData;
    rawSegments = [];
    chartGroups = [];
    consolidatedSegments = [];
    isLoading = true;
    error;

    @wire(getBillingScheduleGroupData, { recordId: '$recordId' })
    wiredBSGData({ error, data }) {
        if (data) {
            this.bsgData = data;
            this.error = undefined;
            if (this.rawSegments.length > 0) {
                this._buildAll();
            }
        } else if (error) {
            this.error = error.body?.message || 'An error occurred loading the BSG data';
            this.bsgData = undefined;
            this.isLoading = false;
        }
    }

    @wire(getConsolidatedTimeline, { recordId: '$recordId' })
    wiredConsolidatedData({ error, data }) {
        if (data) {
            this.rawSegments = data;
            this.error = undefined;
            this._buildAll();
        } else if (error) {
            this.error = error.body?.message || 'An error occurred loading the consolidated data';
            this.consolidatedSegments = [];
            this.chartGroups = [];
            this.isLoading = false;
        }
    }

    // ─── Getters ─────────────────────────────────────────────────────────────

    get hasData() {
        return !this.isLoading && this.consolidatedSegments && this.consolidatedSegments.length > 0;
    }

    get segmentCount() {
        return this.consolidatedSegments ? this.consolidatedSegments.length : 0;
    }

    get bsCount() {
        return this.bsgData?.billingSchedules?.length || 0;
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
        if (!this.bsgData || !this.rawSegments || this.rawSegments.length === 0) {
            this.consolidatedSegments = [];
            this.chartGroups = [];
            this.isLoading = false;
            return;
        }
        this.processConsolidatedSegments(this.rawSegments);
        this.buildChartGroups();
        this.isLoading = false;
    }

    // ─── Term unit helpers ────────────────────────────────────────────────────

    _normaliseUnit(raw) {
        const s = (raw || '').toLowerCase().replace(/[-_ ]/g, '');
        if (s === 'month')                  return 'month';
        if (s === 'year' || s === 'annual') return 'year';
        if (s === 'quarterly')              return 'quarterly';
        if (s === 'semiannual')             return 'semiannual';
        if (s === 'onetime')                return 'onetime';
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
        // BSG-level unit wins if explicitly set
        const rawBsg = (this.bsgData?.billingTermUnit || '').trim();
        if (rawBsg) return this._normaliseUnit(rawBsg);
        // Otherwise use finest unit across all BS so nothing gets lost
        return this._getFinestUnit(this.bsgData?.billingSchedules);
    }

    // ─── Period iteration helpers ─────────────────────────────────────────────

    // Advance a date by one bucket period
    _advancePeriod(date, termUnit) {
        const d = new Date(date);
        switch (termUnit) {
            case 'year':      d.setFullYear(d.getFullYear() + 1); break;
            case 'semiannual':d.setMonth(d.getMonth() + 6);       break;
            case 'quarterly': d.setMonth(d.getMonth() + 3);       break;
            case 'onetime':   d.setFullYear(d.getFullYear() + 100); break; // effectively infinite
            case 'month':
            default:          d.setMonth(d.getMonth() + 1);       break;
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
            case 'semiannual':return `H${date.getMonth() < 6 ? 1 : 2} '${yr}`;
            case 'quarterly': return `Q${Math.floor(date.getMonth() / 3) + 1} '${yr}`;
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
        // For each BS: billedAmount / billingPeriodAmount = number of periods billed
        // Walk its periods in order, filling billed "credit" chronologically.
        // Returns a Map: periodStartISO → { billedAmt, pendingAmt } for this BS
        const bsContributions = schedules.map(bs => {
            const bsStart     = new Date(bs.startDate);
            const bsEnd       = new Date(bs.endDate);
            const periodAmt   = Math.abs(bs.billingPeriodAmount != null ? bs.billingPeriodAmount : 0);
            const isCredit    = (bs.billingPeriodAmount || 0) < 0;
            const billedAmt   = Math.abs(bs.billedAmount  != null ? bs.billedAmount  : 0);

            // How many full periods are billed, and is there a partial remainder?
            let billedRemaining = billedAmt; // amount left to "assign" as billed
            const map = new Map();

            // Only iterate periods that overlap this BS
            periodStarts.forEach(ps => {
                const pe = this._periodEnd(ps, termUnit);
                if (ps > bsEnd || pe < bsStart) return; // BS not active in this period

                if (periodAmt === 0) {
                    map.set(ps.toISOString().slice(0, 10), { billedAmt: 0, pendingAmt: 0, isCredit });
                    return;
                }

                // How much of this period is billed?
                const thisBilled  = Math.min(billedRemaining, periodAmt);
                const thisPending = periodAmt - thisBilled;
                billedRemaining   = Math.max(0, billedRemaining - periodAmt);

                map.set(ps.toISOString().slice(0, 10), {
                    billedAmt:  Math.round(thisBilled  * 100) / 100,
                    pendingAmt: Math.round(thisPending * 100) / 100,
                    isCredit
                });
            });

            return map;
        });

        // ── Step 3: sum contributions per calendar period ──────────────────
        const buckets = periodStarts.map(ps => {
            const key = ps.toISOString().slice(0, 10);

            let netBilled  = 0;
            let netPending = 0;

            bsContributions.forEach(map => {
                const contrib = map.get(key);
                if (!contrib) return;
                if (contrib.isCredit) {
                    // Credits reduce billed first, then pending
                    netBilled  -= contrib.billedAmt;
                    netPending -= contrib.pendingAmt;
                } else {
                    netBilled  += contrib.billedAmt;
                    netPending += contrib.pendingAmt;
                }
            });

            netBilled  = Math.round(netBilled  * 100) / 100;
            netPending = Math.round(netPending * 100) / 100;
            const netAmount = Math.round((netBilled + netPending) * 100) / 100;

            return {
                key,
                label:     this._bucketLabel(ps, termUnit),
                sortDate:  ps,
                netAmount: Math.max(0, netAmount), // clamp — negative net means fully cancelled
                billedAmount:  Math.max(0, netBilled),
                pendingAmount: Math.max(0, netPending),
                isZero:   netAmount <= 0
            };
        });

        this._finaliseChartGroups(buckets);
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
        // Bar width scales with count but flexbox justify-content handles spacing,
        // so no explicit margins needed — bars spread evenly across the full width
        const BAR_WIDTH_PX = count <= 3  ? 80 :
                             count <= 6  ? 70 :
                             count <= 12 ? 56 :
                             Math.max(20, Math.floor(700 / count));

        this.chartGroups = buckets.map(b => {
            const isZero = b.isZero;

            const totalBarPx = isZero
                ? ZERO_MARKER_PX
                : (maxValue > 0 ? Math.max(ZERO_MARKER_PX, Math.round((b.netAmount / maxValue) * CHART_HEIGHT_PX)) : ZERO_MARKER_PX);

            // Billed/pending split within the bar — direct amounts, no ratio hacks
            const gross      = b.billedAmount + b.pendingAmount;
            const billedPct  = gross > 0 ? Math.min(100, (b.billedAmount  / gross) * 100) : 0;
            const pendingPct = 100 - billedPct;

            const tooltip = isZero
                ? `${b.label}: $0.00 net (cancelled/amended)`
                : `${b.label}: ${this.formatCurrency(b.netAmount)} — Billed: ${this.formatCurrency(b.billedAmount)}, Pending: ${this.formatCurrency(b.pendingAmount)}`;

            return {
                ...b,
                totalBarPx,
                billedPct,
                pendingPct,
                isZero,
                // No margin — flexbox justify-content:space-evenly handles even spacing
                barGroupStyle:   `width: ${BAR_WIDTH_PX}px; height: ${CHART_HEIGHT_PX}px; display: flex; align-items: flex-end;`,
                xAxisLabelStyle: `width: ${BAR_WIDTH_PX}px; text-align: center;`,
                billingBarStyle: `height: ${totalBarPx}px; width: ${BAR_WIDTH_PX}px;`,
                billedSegStyle:  `height: ${billedPct}%; background: #2e844a; width: 100%;`,
                pendingSegStyle: `height: ${pendingPct}%; background: #5eb3f6; width: 100%;`,
                zeroBarStyle:    `height: ${ZERO_MARKER_PX}px; width: ${BAR_WIDTH_PX}px; background: #dddbda; border-radius: 2px 2px 0 0;`,
                formattedNet:     this.formatCurrency(b.netAmount),
                formattedBilled:  this.formatCurrency(b.billedAmount),
                formattedPending: this.formatCurrency(b.pendingAmount),
                tooltip
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

    // ─── Navigation & utilities ───────────────────────────────────────────────

    navigateToSchedule(event) {
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
}