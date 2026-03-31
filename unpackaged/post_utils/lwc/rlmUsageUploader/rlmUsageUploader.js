/**
 * rlmUsageUploader.js
 *
 * Lightning Web Component for uploading usage data on Revenue Cloud Assets.
 * Supports two modes:
 *  - Single Entry: form-based upload of one TransactionJournal record
 *  - CSV Upload: parse CSV, preview in table, validate, then bulk-create
 *
 * Placed on Asset record pages.
 */
import { LightningElement, api, wire } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import getAssetsForAccount from '@salesforce/apex/RLM_UsageUploaderController.getAssetsForAccount';
import getUsageResourcesForAsset from '@salesforce/apex/RLM_UsageUploaderController.getUsageResourcesForAsset';
import uploadUsage from '@salesforce/apex/RLM_UsageUploaderController.uploadUsage';
import validateUsageEntries from '@salesforce/apex/RLM_UsageUploaderController.validateUsageEntries';
import bulkUploadUsage from '@salesforce/apex/RLM_UsageUploaderController.bulkUploadUsage';

const CSV_COLUMNS = [
    { label: 'Row', fieldName: 'rowNum', type: 'number', initialWidth: 60 },
    { label: 'Usage Resource', fieldName: 'usageResourceName', type: 'text' },
    { label: 'Quantity', fieldName: 'quantity', type: 'number' },
    { label: 'Transaction Date', fieldName: 'transactionDate', type: 'date' },
    {
        label: 'Status',
        fieldName: 'statusIcon',
        type: 'text',
        initialWidth: 120,
        cellAttributes: {
            class: { fieldName: '_cssClass' }
        }
    }
];

const STATUS_ICONS = {
    PENDING: '⏳ Pending',
    VALID: '✅ Valid',
    ERROR: '❌'
};

const COLUMN_PATTERNS = {
    RESOURCE: ['usage resource', 'resource', 'usageresourcename'],
    QUANTITY: ['quantity', 'qty', 'amount'],
    DATE: ['date', 'transactiondate']
};

export default class RlmUsageUploader extends LightningElement {
    @api recordId;

    // Context detection (Account vs Asset)
    contextObject;
    accountAssets = [];
    assetOptions = [];
    selectedAssetId;
    assetsLoaded = false;
    _wiredAssets;

    // Mode toggle
    activeTab = 'single';

    // Usage resources loaded from Apex
    usageResources = [];
    resourceOptions = [];
    resourcesLoaded = false;
    resourceError;

    // Single entry form fields
    selectedResourceId;
    selectedUomId;
    singleQuantity;
    singleDate;
    isSingleUploading = false;

    // CSV upload state
    csvData = [];
    csvColumns = CSV_COLUMNS;
    csvFileName;
    csvValidated = false;
    csvHasErrors = false;
    isCsvUploading = false;
    validationResults = [];
    isDragOver = false;

    // ─── Lifecycle ──────────────────────────────────────────────────────

    connectedCallback() {
        // Detect context by object key prefix (Account: 001, Asset: 02i)
        if (this.recordId) {
            const prefix = this.recordId.substring(0, 3);
            this.contextObject = prefix === '001' ? 'Account' : 'Asset';
        }
    }

    // ─── Wire Adapters ──────────────────────────────────────────────────

    // Wire Assets when on Account
    @wire(getAssetsForAccount, { accountId: '$effectiveAccountId' })
    wiredAssets(result) {
        this._wiredAssets = result;
        const { data, error } = result;
        if (data) {
            this.accountAssets = data;
            this.assetOptions = data.map(a => ({
                label: `${a.assetName} (${a.productName})`,
                value: a.assetId
            }));
            this.assetsLoaded = true;
        } else if (error) {
            this.showToast('Error', 'Failed to load assets: ' + this.reduceErrors(error), 'error');
            this.assetsLoaded = true;
        }
    }

    // Wire usage resources for the effective Asset
    _wiredResources;

    @wire(getUsageResourcesForAsset, { assetId: '$effectiveAssetId' })
    wiredResources(result) {
        this._wiredResources = result;
        const { data, error } = result;
        if (data) {
            this.usageResources = data;
            this.resourceOptions = data.map(r => ({
                label: r.resourceName,
                value: r.resourceId
            }));
            this.resourcesLoaded = true;
            this.resourceError = undefined;

            // Set defaults: first resource, its default UoM, quantity 1, today's date
            if (data.length > 0 && !this.selectedResourceId) {
                this.selectedResourceId = data[0].resourceId;
                this.selectedUomId = data[0].unitOfMeasureId;
                this.singleQuantity = 1;
                this.singleDate = this._todayISO();
            }
        } else if (error) {
            this.resourceError = this.reduceErrors(error);
            this.usageResources = [];
            this.resourceOptions = [];
            this.resourcesLoaded = true;
        }
    }

    // ─── Computed Properties ───────────────────────────────────────────

    get isAccountContext() {
        return this.contextObject === 'Account';
    }

    get showAssetPicker() {
        return this.isAccountContext;
    }

    get shouldShowMainContent() {
        return this.isAccountContext ? !!this.selectedAssetId : true;
    }

    get effectiveAssetId() {
        return this.isAccountContext ? this.selectedAssetId : this.recordId;
    }

    get effectiveAccountId() {
        return this.isAccountContext ? this.recordId : undefined;
    }

    get hasAssetOptions() {
        return this.assetOptions.length > 0;
    }

    get noAssetsMessage() {
        return this.isAccountContext && this.assetsLoaded && !this.hasAssetOptions;
    }

    get hasCsvData() {
        return this.csvData.length > 0;
    }

    get csvRowCount() {
        return this.csvData.length;
    }

    get csvValidCount() {
        return this.validationResults.filter(r => r.isValid).length;
    }

    get csvErrorCount() {
        return this.validationResults.filter(r => !r.isValid).length;
    }

    get canConfirmUpload() {
        return this.csvValidated && this.csvValidCount > 0 && !this.isCsvUploading;
    }

    get csvConfirmDisabled() {
        return !this.canConfirmUpload;
    }

    get singleUploadButtonLabel() {
        return this.isSingleUploading ? 'Uploading...' : 'Upload Usage';
    }

    get csvUploadButtonLabel() {
        return this.isCsvUploading ? 'Uploading...' : 'Confirm Upload';
    }

    get isSingleSubmitDisabled() {
        return this.isSingleUploading || !this.selectedResourceId || !this.singleQuantity || !this.singleDate;
    }

    get uomOptions() {
        if (!this.selectedResourceId) return [];
        const resource = this.usageResources.find(r => r.resourceId === this.selectedResourceId);
        if (!resource || !resource.availableUoms) return [];
        return resource.availableUoms.map(u => ({
            label: `${u.uomName} (${u.uomCode})`,
            value: u.uomId
        }));
    }

    get hasUomOptions() {
        return this.uomOptions.length > 0;
    }

    get isLoading() {
        // On Account context without Asset selected: check if Assets are loading
        if (this.isAccountContext && !this.selectedAssetId) {
            return !this.assetsLoaded;
        }
        // On Account with Asset selected OR on Asset context: check if Resources are loading
        return !this.resourcesLoaded;
    }

    get hasResources() {
        return this.usageResources.length > 0;
    }

    get dropzoneClass() {
        let cls = 'slds-file-selector__dropzone';
        if (this.isDragOver) {
            cls += ' slds-has-drag-over';
        }
        return cls;
    }

    // ─── Tab Handling ──────────────────────────────────────────────────

    handleTabChange(event) {
        this.activeTab = event.detail.value;
    }

    // ─── Asset Selection (Account Context) ─────────────────────────────

    handleAssetChange(event) {
        this.selectedAssetId = event.detail.value;
        // Reset form when Asset changes
        this.selectedResourceId = undefined;
        this.selectedUomId = undefined;
        this.singleQuantity = undefined;
        this.singleDate = this._todayISO();
        this.csvData = [];
        this.csvValidated = false;
    }

    // ─── Single Entry Handlers ─────────────────────────────────────────

    handleResourceChange(event) {
        this.selectedResourceId = event.detail.value;
        // Default UoM to the resource's default UoM
        const resource = this.usageResources.find(r => r.resourceId === this.selectedResourceId);
        this.selectedUomId = resource ? resource.unitOfMeasureId : undefined;
    }

    handleUomChange(event) {
        this.selectedUomId = event.detail.value;
    }

    handleQuantityChange(event) {
        this.singleQuantity = event.detail.value;
    }

    handleDateChange(event) {
        this.singleDate = event.detail.value;
    }

    async handleSingleUpload() {
        if (this.isSingleSubmitDisabled) return;

        this.isSingleUploading = true;
        try {
            const journalId = await uploadUsage({
                assetId: this.effectiveAssetId,
                usageResourceId: this.selectedResourceId,
                quantity: parseFloat(this.singleQuantity),
                transactionDate: this.singleDate,
                unitOfMeasureId: this.selectedUomId || null
            });

            this.dispatchEvent(new ShowToastEvent({
                title: 'Success',
                message: 'Usage record created: {0}',
                variant: 'success',
                messageData: [
                    {
                        url: `/lightning/r/TransactionJournal/${journalId}/view`,
                        label: 'View Transaction Journal'
                    }
                ]
            }));
            this.resetSingleForm();
        } catch (error) {
            this.showToast('Error', this.reduceErrors(error), 'error');
        } finally {
            this.isSingleUploading = false;
        }
    }

    resetSingleForm() {
        // Restore defaults: first resource, its default UoM, quantity 1, today
        if (this.usageResources.length > 0) {
            this.selectedResourceId = this.usageResources[0].resourceId;
            this.selectedUomId = this.usageResources[0].unitOfMeasureId;
        } else {
            this.selectedResourceId = undefined;
            this.selectedUomId = undefined;
        }
        this.singleQuantity = 1;
        this.singleDate = this._todayISO();
    }

    // ─── CSV Upload Handlers ───────────────────────────────────────────

    // ─── Sample CSV Download ──────────────────────────────────────────

    handleDownloadSampleCsv() {
        const today = this._todayISO();
        const header = 'Usage Resource,Quantity,Transaction Date';
        const rows = this.usageResources.map(r => {
            // Escape resource name in case it contains commas
            const name = r.resourceName.includes(',')
                ? `"${r.resourceName}"`
                : r.resourceName;
            return `${name},1,${today}`;
        });

        const csvContent = [header, ...rows].join('\n');

        // Use navigation-compatible download: create a data URI and open via a hidden <a>
        // LWC shadow DOM blocks document.body access, so use an encoded data URI instead
        const encodedUri = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', 'usage_upload_template.csv');
        link.click();
    }

    handleDropzoneClick() {
        const fileInput = this.template.querySelector('[data-id="csv-file-input"]');
        if (fileInput) {
            fileInput.click();
        }
    }

    handleDropzoneKeydown(event) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            this.handleDropzoneClick();
        }
    }

    handleDragOver(event) {
        event.preventDefault();
        this.isDragOver = true;
    }

    handleDragLeave() {
        this.isDragOver = false;
    }

    handleDrop(event) {
        event.preventDefault();
        this.isDragOver = false;

        const files = event.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (file.name.toLowerCase().endsWith('.csv')) {
                this.processFile(file);
            } else {
                this.showToast('Error', 'Please drop a CSV file.', 'error');
            }
        }
    }

    handleFileChange(event) {
        const file = event.target.files[0];
        if (!file) return;
        this.processFile(file);
    }

    processFile(file) {
        this.csvFileName = file.name;
        this.csvValidated = false;
        this.csvHasErrors = false;
        this.validationResults = [];

        const reader = new FileReader();
        reader.onload = () => {
            this.parseCSV(reader.result);
        };
        reader.readAsText(file);
    }

    parseCSV(csvText) {
        const lines = csvText.split(/\r?\n/).filter(line => line.trim().length > 0);
        if (lines.length < 2) {
            this.showToast('Error', 'CSV file must have a header row and at least one data row.', 'error');
            this.csvData = [];
            return;
        }

        const headers = this.parseCSVLine(lines[0]).map(h => h.trim().toLowerCase());

        const matchColumn = (patterns) => headers.findIndex(h =>
            patterns.some(p => h.includes(p) || h === p)
        );

        const resourceIdx = matchColumn(COLUMN_PATTERNS.RESOURCE);
        const qtyIdx = matchColumn(COLUMN_PATTERNS.QUANTITY);
        const dateIdx = matchColumn(COLUMN_PATTERNS.DATE);

        if (resourceIdx === -1 || qtyIdx === -1 || dateIdx === -1) {
            this.showToast('Error',
                'CSV must contain columns: Usage Resource (or Resource), Quantity (or Qty), and Date (or Transaction Date).',
                'error'
            );
            this.csvData = [];
            return;
        }

        const parsed = [];
        const resourceIdByName = {};
        for (const r of this.usageResources) {
            if (r.resourceName) {
                resourceIdByName[r.resourceName.toLowerCase()] = r.resourceId;
            }
        }
        for (let i = 1; i < lines.length; i++) {
            const values = this.parseCSVLine(lines[i]);
            if (values.length === 0) continue;

            const rawDate = this.normalizeCsvCell(values[dateIdx]);
            const normalizedDate = this.normalizeDate(rawDate);
            const resourceName = this.normalizeCsvCell(values[resourceIdx]);
            const rawQuantity = this.normalizeCsvCell(values[qtyIdx]);
            const parsedQuantity = this.parseQuantity(rawQuantity);

            parsed.push({
                id: `row-${i}`,
                rowNum: i,
                usageResourceName: resourceName,
                usageResourceId: resourceName ? (resourceIdByName[resourceName.toLowerCase()] || null) : null,
                quantity: Number.isFinite(parsedQuantity) ? parsedQuantity : 0,
                rawQuantity: rawQuantity,
                transactionDate: normalizedDate,
                rawDate: rawDate,
                statusIcon: STATUS_ICONS.PENDING
            });
        }

        this.csvData = parsed;

        if (parsed.length > 0) {
            this.validateCsvData();
        }
    }

    parseCSVLine(line) {
        const result = [];
        let current = '';
        let inQuotes = false;

        for (let i = 0; i < line.length; i++) {
            const char = line[i];
            if (inQuotes) {
                if (char === '"' && i + 1 < line.length && line[i + 1] === '"') {
                    current += '"';
                    i++;
                } else if (char === '"') {
                    inQuotes = false;
                } else {
                    current += char;
                }
            } else {
                if (char === '"') {
                    inQuotes = true;
                } else if (char === ',') {
                    result.push(current);
                    current = '';
                } else {
                    current += char;
                }
            }
        }
        result.push(current);
        return result;
    }

    async validateCsvData() {
        try {
            const entries = this.csvData.map(row => ({
                usageResourceId: row.usageResourceId || null,
                usageResourceName: this.normalizeCsvCell(row.usageResourceName) || null,
                quantity: Number.isFinite(row.quantity) ? row.quantity : this.parseQuantity(row.rawQuantity),
                transactionDate: row.transactionDate || this.normalizeDate(this.normalizeCsvCell(row.rawDate)) || null
            }));

            const results = await validateUsageEntries({
                assetId: this.effectiveAssetId,
                entries: entries
            });

            this.validationResults = results;

            // Update CSV data with validation results
            this.csvData = this.csvData.map((row, idx) => {
                const vr = results[idx];
                return {
                    ...row,
                    statusIcon: vr.isValid ? STATUS_ICONS.VALID : STATUS_ICONS.ERROR + ' ' + vr.errorMessage,
                    _cssClass: vr.isValid ? '' : 'slds-text-color_error'
                };
            });

            this.csvValidated = true;
            this.csvHasErrors = results.some(r => !r.isValid);

        } catch (error) {
            this.showToast('Error', 'Validation failed: ' + this.reduceErrors(error), 'error');
        }
    }

    async handleCsvUpload() {
        if (!this.canConfirmUpload) return;

        this.isCsvUploading = true;
        try {
            const entries = this.csvData.map(row => ({
                usageResourceId: row.usageResourceId || null,
                usageResourceName: this.normalizeCsvCell(row.usageResourceName) || null,
                quantity: Number.isFinite(row.quantity) ? row.quantity : this.parseQuantity(row.rawQuantity),
                transactionDate: row.transactionDate || this.normalizeDate(this.normalizeCsvCell(row.rawDate)) || null
            }));

            const result = await bulkUploadUsage({
                assetId: this.effectiveAssetId,
                entries: entries
            });

            if (result.successCount > 0) {
                this.showToast('Success',
                    `${result.successCount} usage record(s) created successfully.` +
                    (result.errorCount > 0 ? ` ${result.errorCount} row(s) had errors.` : ''),
                    result.errorCount > 0 ? 'warning' : 'success'
                );
            }

            if (result.errors && result.errors.length > 0) {
                console.error('Bulk upload errors:', result.errors);
            }

            this.handleCsvCancel();
        } catch (error) {
            this.showToast('Error', 'Bulk upload failed: ' + this.reduceErrors(error), 'error');
        } finally {
            this.isCsvUploading = false;
        }
    }

    handleCsvCancel() {
        this.csvData = [];
        this.csvFileName = undefined;
        this.csvValidated = false;
        this.csvHasErrors = false;
        this.validationResults = [];

        // Reset the file input
        const fileInput = this.template.querySelector('[data-id="csv-file-input"]');
        if (fileInput) {
            fileInput.value = '';
        }
    }

    // ─── Date Normalization ──────────────────────────────────────────

    /**
     * Converts various date formats to ISO YYYY-MM-DD for Apex @AuraEnabled Date deserialization.
     * Supported formats:
     *   YYYY-MM-DD, YYYY/MM/DD        (ISO)
     *   MM/DD/YYYY, MM-DD-YYYY        (US)
     *   DD/MM/YYYY, DD-MM-YYYY        (EU — used when day > 12)
     *   Month DD, YYYY  /  DD Month YYYY  /  Mon DD YYYY  (named months)
     *   M/D/YYYY, M/D/YY              (short variants)
     * Returns empty string if parsing fails.
     */
    normalizeDate(raw) {
        if (!raw) return '';
        // Normalize common Unicode dash variants and NBSP from spreadsheet exports.
        const s = this.normalizeCsvCell(raw);

        // Already ISO: YYYY-MM-DD or YYYY/MM/DD
        const isoMatch = s.match(/^(\d{4})[/-](\d{1,2})[/-](\d{1,2})$/);
        if (isoMatch) {
            return this._buildDate(isoMatch[1], isoMatch[2], isoMatch[3]);
        }

        // Named-month formats: "March 30, 2026", "Mar 30 2026", "30 March 2026", "30-Mar-2026"
        const namedMatch = s.match(
            /^(\d{1,2})[/\s-]*([A-Za-z]+)[,\s-]+(\d{4})$|^([A-Za-z]+)[.\s-]+(\d{1,2})[,\s-]+(\d{4})$/
        );
        if (namedMatch) {
            let day, monthStr, year;
            if (namedMatch[1]) {
                // DD Month YYYY or DD-Mon-YYYY
                day = namedMatch[1];
                monthStr = namedMatch[2];
                year = namedMatch[3];
            } else {
                // Month DD, YYYY or Mon DD YYYY
                monthStr = namedMatch[4];
                day = namedMatch[5];
                year = namedMatch[6];
            }
            const month = this._monthNameToNumber(monthStr);
            if (month) {
                return this._buildDate(year, month, day);
            }
        }

        // Numeric with separators: MM/DD/YYYY, DD/MM/YYYY, MM-DD-YYYY, DD-MM-YYYY, M/D/YY
        const numMatch = s.match(/^(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})$/);
        if (numMatch) {
            let [, part1, part2, yearPart] = numMatch;
            // Expand 2-digit year
            if (yearPart.length === 2) {
                const yy = parseInt(yearPart, 10);
                yearPart = (yy >= 50 ? '19' : '20') + yearPart;
            }
            const p1 = parseInt(part1, 10);
            const p2 = parseInt(part2, 10);

            // If first part > 12, it must be a day (EU format DD/MM/YYYY)
            if (p1 > 12 && p2 <= 12) {
                return this._buildDate(yearPart, part2, part1);
            }
            // Default to US format MM/DD/YYYY
            return this._buildDate(yearPart, part1, part2);
        }

        return '';
    }

    normalizeCsvCell(value) {
        if (value == null) return '';
        return String(value)
            .replace(/\uFEFF/g, '')              // UTF-8 BOM
            .replace(/\u00A0/g, ' ')             // non-breaking space
            .replace(/[\u2012\u2013\u2014\u2015]/g, '-') // en/em/horizontal dashes
            .trim();
    }

    parseQuantity(value) {
        const normalized = this.normalizeCsvCell(value).replace(/,/g, '');
        if (!normalized) return null;
        const parsed = parseFloat(normalized);
        return Number.isFinite(parsed) ? parsed : null;
    }

    _monthNameToNumber(name) {
        const months = {
            jan: 1, january: 1, feb: 2, february: 2, mar: 3, march: 3,
            apr: 4, april: 4, may: 5, jun: 6, june: 6,
            jul: 7, july: 7, aug: 8, august: 8, sep: 9, september: 9,
            oct: 10, october: 10, nov: 11, november: 11, dec: 12, december: 12
        };
        return months[name.toLowerCase()] || null;
    }

    _buildDate(year, month, day) {
        const y = String(year).padStart(4, '0');
        const m = String(parseInt(month, 10)).padStart(2, '0');
        const d = String(parseInt(day, 10)).padStart(2, '0');

        // Basic range check
        const mi = parseInt(m, 10);
        const di = parseInt(d, 10);
        if (mi < 1 || mi > 12 || di < 1 || di > 31) return '';

        return `${y}-${m}-${d}`;
    }

    // ─── Utility ───────────────────────────────────────────────────────

    _todayISO() {
        const d = new Date();
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${y}-${m}-${day}`;
    }

    showToast(title, message, variant) {
        this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
    }

    reduceErrors(error) {
        if (typeof error === 'string') return error;
        if (error?.body?.message) return error.body.message;
        if (error?.message) return error.message;
        if (Array.isArray(error?.body)) {
            return error.body.map(e => e.message).join(', ');
        }
        return 'Unknown error';
    }
}