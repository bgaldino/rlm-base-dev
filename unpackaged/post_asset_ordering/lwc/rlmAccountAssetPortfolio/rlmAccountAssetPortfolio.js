import { LightningElement, api, wire, track } from 'lwc';
import { loadScript } from 'lightning/platformResourceLoader';
import ChartJs from '@salesforce/resourceUrl/ChartJs';
import getAccountAssetTimeline from '@salesforce/apex/RLM_AccountAssetPortfolioService.getAccountAssetTimeline';

const PALETTE = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
    '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'
];

function padTwo(n) {
    return String(n).padStart(2, '0');
}

export default class RlmAccountAssetPortfolio extends LightningElement {
    @api recordId;

    @track assets = [];
    @track points = [];
    @track selectedMetric = 'MRR'; // 'MRR' | 'QTY'
    @track assetFilter = '';

    chart;
    chartJsInitialized = false;
    wiredError;

    // ---- Metric options ----
    get metricOptions() {
        return [
            { label: 'Monthly Recurring Revenue (MRR)', value: 'MRR' },
            { label: 'Quantity', value: 'QTY' }
        ];
    }

    // ---- KPI getters ----

    get _latestPoints() {
        const latest = {};
        this.points.forEach(p => {
            if (!p.assetId || !p.startDate) return;
            if (!latest[p.assetId] || p.startDate > latest[p.assetId].startDate) {
                latest[p.assetId] = p;
            }
        });
        return latest;
    }

    get totalCurrentMrrFormatted() {
        let total = 0;
        Object.values(this._latestPoints).forEach(p => {
            if (p.mrr != null) total += Number(p.mrr) || 0;
        });
        return 'USD ' + total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    get totalCurrentQuantityFormatted() {
        let total = 0;
        Object.values(this._latestPoints).forEach(p => {
            if (p.quantity != null) total += Number(p.quantity) || 0;
        });
        return total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    get activeAssetCount() {
        return new Set(this.points.map(p => p.assetId).filter(Boolean)).size;
    }

    get hasData() {
        return this.assets.length > 0 && this.points.length > 0;
    }

    get hasNoData() {
        return !this.hasData;
    }

    // ---- Wire Apex ----
    @wire(getAccountAssetTimeline, { accountId: '$recordId' })
    wiredPortfolio({ error, data }) {
        if (error) {
            console.error('[Portfolio] Apex ERROR', JSON.stringify(error));
            this.wiredError = error;
            this.assets = [];
            this.points = [];
            this.refreshChart();
        } else if (data) {
            this.wiredError = undefined;
            this.assets = data.assets || [];
            this.points = data.points || [];
            this.refreshChart();
        }
    }

    // ---- Lifecycle: load Chart.js once ----
    renderedCallback() {
        if (this.chartJsInitialized) return;
        const canvas = this.template.querySelector('canvas.chart-canvas');
        if (!canvas) return;

        loadScript(this, ChartJs)
            .then(() => {
                this.chartJsInitialized = true;
                this.refreshChart();
            })
            .catch(err => console.error('[Portfolio] Chart.js load error', err));
    }

    // ---- UI handlers ----
    handleMetricChange(event) {
        this.selectedMetric = event.detail.value;
        this.refreshChart();
    }

    handleFilterChange(event) {
        this.assetFilter = (event.detail.value || '').trim();
        this.refreshChart();
    }

    // ---- Chart refresh — always destroys and recreates for clean config ----
    refreshChart() {
        if (!this.chartJsInitialized) return;

        const canvas = this.template.querySelector('canvas.chart-canvas');
        if (!canvas) return;

        if (this.chart) {
            this.chart.destroy();
            this.chart = undefined;
        }

        if (!this.hasData) return;

        const { displayLabels, isoKeys, datasets } = this.buildChartData();
        if (!displayLabels.length || !datasets.length) return;

        const metric = this.selectedMetric;

        // Determine today's label index using local year-month (avoids UTC offset issues)
        const now = new Date();
        const todayYYYYMM = `${now.getFullYear()}-${padTwo(now.getMonth() + 1)}`;
        const todayIdx = isoKeys.findIndex(k => k.slice(0, 7) === todayYYYYMM);

        // Inline Today-line plugin — no external dependency required
        const todayLinePlugin = {
            id: 'todayLine',
            afterDraw(chartInstance) {
                if (todayIdx < 0) return;
                const xScale = chartInstance.scales && chartInstance.scales.x;
                if (!xScale) return;
                const x = xScale.getPixelForValue(todayIdx);
                const { top, bottom } = chartInstance.chartArea;
                const ctx2 = chartInstance.ctx;

                ctx2.save();
                ctx2.beginPath();
                ctx2.moveTo(x, top);
                ctx2.lineTo(x, bottom);
                ctx2.strokeStyle = '#0070d2';
                ctx2.lineWidth = 2;
                ctx2.setLineDash([6, 4]);
                ctx2.stroke();
                ctx2.restore();

                ctx2.save();
                ctx2.fillStyle = '#fff';
                ctx2.font = 'bold 11px sans-serif';
                ctx2.textAlign = 'center';
                const labelW = 42;
                const labelH = 16;
                ctx2.fillRect(x - labelW / 2, top - labelH - 2, labelW, labelH);
                ctx2.fillStyle = '#0070d2';
                ctx2.fillRect(x - labelW / 2, top - labelH - 2, labelW, labelH);
                ctx2.fillStyle = '#fff';
                ctx2.fillText('Today', x, top - 6);
                ctx2.restore();
            }
        };

        this.chart = new window.Chart(canvas.getContext('2d'), {
            type: 'line',
            data: { labels: displayLabels, datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { position: 'top' },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                if (context.parsed.y == null) return null;
                                const lbl = context.dataset.label || '';
                                const val = context.parsed.y;
                                return metric === 'MRR'
                                    ? `${lbl}: $${this.formatNumber(val, 2)}`
                                    : `${lbl}: ${this.formatNumber(val, 2)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Date' },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 0,
                            autoSkip: true,
                            maxTicksLimit: 13
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: metric === 'MRR' ? 'MRR (USD / month)' : 'Quantity'
                        },
                        ticks: {
                            callback: (value) => {
                                if (metric === 'MRR') {
                                    if (value >= 1000000) return '$' + (value / 1000000).toFixed(1) + 'M';
                                    if (value >= 1000) return '$' + (value / 1000).toFixed(0) + 'K';
                                    return '$' + value;
                                }
                                if (value >= 1000) return (value / 1000).toFixed(1) + 'K';
                                return value;
                            }
                        }
                    }
                },
                elements: {
                    line: { tension: 0, stepped: true },
                    point: { radius: 3, hoverRadius: 5 }
                }
            },
            plugins: [todayLinePlugin]
        });
    }

    // ---- Build chart data ----
    buildChartData() {
        const metric = this.selectedMetric;
        const MONTH_HORIZON = 12;

        // Find the earliest month across all state periods (pure string comparison, no Date parsing)
        let minYYYYMM = null;
        this.points.forEach(p => {
            if (!p.startDate) return;
            const ym = p.startDate.slice(0, 7); // "YYYY-MM"
            if (!minYYYYMM || ym < minYYYYMM) minYYYYMM = ym;
        });

        if (!minYYYYMM) return { displayLabels: [], isoKeys: [], datasets: [] };

        // Build monthly label arrays using local date constructor (avoids UTC-offset issues)
        const [startYear, startMonth] = minYYYYMM.split('-').map(Number);
        const cursor = new Date(startYear, startMonth - 1, 1);
        const endLimit = new Date(startYear, startMonth - 1 + MONTH_HORIZON, 1);

        const displayLabels = [];
        const isoKeys = [];

        while (cursor <= endLimit) {
            isoKeys.push(`${cursor.getFullYear()}-${padTwo(cursor.getMonth() + 1)}-01`);
            displayLabels.push(cursor.toLocaleString('en-US', { month: 'short', year: 'numeric' }));
            cursor.setMonth(cursor.getMonth() + 1);
        }

        // Index points by asset → month bucket (normalize startDate to "YYYY-MM-01")
        const byAsset = {};
        this.points.forEach(p => {
            if (!p.assetId || !p.startDate) return;
            if (!byAsset[p.assetId]) byAsset[p.assetId] = {};
            const key = p.startDate.slice(0, 7) + '-01';
            // Last write wins when multiple points fall in same month bucket
            if (!byAsset[p.assetId][key] || p.startDate > byAsset[p.assetId][key].startDate) {
                byAsset[p.assetId][key] = p;
            }
        });

        // Apply asset name filter
        const filter = (this.assetFilter || '').toLowerCase();
        const filteredAssets = this.assets.filter(a => {
            if (!filter) return true;
            return (a.productName || a.name || '').toLowerCase().includes(filter);
        });

        const datasets = [];

        filteredAssets.forEach((asset, idx) => {
            let lastValue = null;
            const assetPoints = byAsset[asset.id] || {};
            const sortedKeys = Object.keys(assetPoints).sort();
            let keyIdx = 0;

            const data = isoKeys.map(isoKey => {
                while (keyIdx < sortedKeys.length && sortedKeys[keyIdx] <= isoKey) {
                    const pt = assetPoints[sortedKeys[keyIdx]];
                    if (pt) {
                        if (metric === 'MRR' && pt.mrr != null) {
                            const v = Number(pt.mrr);
                            if (!Number.isNaN(v)) lastValue = v;
                        }
                        if (metric === 'QTY' && pt.quantity != null) {
                            const v = Number(pt.quantity);
                            if (!Number.isNaN(v)) lastValue = v;
                        }
                    }
                    keyIdx++;
                }
                return lastValue;
            });

            if (!data.some(v => v != null)) return;

            const color = PALETTE[idx % PALETTE.length];

            datasets.push({
                label: asset.productName || asset.name || 'Asset',
                data,
                borderColor: color,
                backgroundColor: color,
                stepped: true,
                spanGaps: true,
                fill: false,
                borderWidth: 2,
                pointRadius: 3,
                pointHoverRadius: 5
            });
        });

        return { displayLabels, isoKeys, datasets };
    }

    // ---- Helpers ----
    formatNumber(value, decimals) {
        const v = Number(value);
        if (Number.isNaN(v)) return '';
        return v.toLocaleString('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    }
}