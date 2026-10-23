import { LightningElement, api } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';
import { FlowAttributeChangeEvent } from 'lightning/flowSupport';
import getState from '@salesforce/apex/RLM_RTK_Inspection.getState';
import saveFinding from '@salesforce/apex/RLM_RTK_Inspection.saveFinding';
import deleteFinding from '@salesforce/apex/RLM_RTK_Inspection.deleteFinding';

const ZONES = [
    { value: 'Exterior Perimeter', icon: 'utility:home', hint: 'Foundation, siding, eaves' },
    { value: 'Garage', icon: 'utility:open_folder', hint: 'Door seals, corners, storage' },
    { value: 'Kitchen', icon: 'utility:food_and_drink', hint: 'Under sink, appliances' },
    { value: 'Bathrooms', icon: 'utility:water', hint: 'Plumbing, moisture' },
    { value: 'Living Areas', icon: 'utility:people', hint: 'Baseboards, windows' },
    { value: 'Basement / Crawlspace', icon: 'utility:layers', hint: 'Sill plate, joists' },
    { value: 'Attic', icon: 'utility:up', hint: 'Insulation, vents' },
    { value: 'Yard', icon: 'utility:world', hint: 'Standing water, wood piles' }
];
const PESTS = ['Ants', 'Spiders', 'Cockroaches', 'Rodents', 'Termites', 'Mosquitoes', 'Wasps / Bees', 'Other'];
const EVIDENCE = [
    'Live Activity',
    'Droppings',
    'Damage',
    'Nest',
    'Entry Point',
    'Standing Water',
    'Wood-to-Soil Contact',
    'Moisture'
];
const SEVERITIES = ['Light', 'Moderate', 'Heavy'];
const PHOTO_FORMATS = ['.jpg', '.jpeg', '.png', '.heic', '.heif', '.webp'];

const emptyDraft = (zone) => ({
    id: null,
    zone,
    pest: null,
    evidence: null,
    severity: 'Light',
    customerNote: '',
    internalNote: ''
});

export default class RlmRtkInspectionWalk extends NavigationMixin(LightningElement) {
    @api inspectionId;
    @api accountName;
    @api serviceAddress;

    @api planSku;
    @api severity;
    @api includeMosquito;
    @api includeTermite;
    @api recommendationJson;
    @api findingCount;

    findings = [];
    recommendation;
    clearZones = new Set();
    activeZone;
    draft;
    saving = false;
    loading = true;
    error;

    photoFormats = PHOTO_FORMATS;

    connectedCallback() {
        this.load();
    }

    async load() {
        try {
            this.apply(await getState({ inspectionId: this.inspectionId }));
        } catch (e) {
            this.error = this.message(e);
        } finally {
            this.loading = false;
        }
    }

    apply(state) {
        this.findings = state.findings || [];
        this.recommendation = state.recommendation;
        this.error = undefined;
        const rec = this.recommendation || {};
        this.emit('planSku', rec.planSku);
        this.emit('severity', rec.severity);
        this.emit('includeMosquito', rec.includeMosquito === true);
        this.emit('includeTermite', rec.includeTermite === true);
        this.emit('recommendationJson', JSON.stringify(rec));
        this.emit('findingCount', this.findings.length);
    }

    emit(name, value) {
        this.dispatchEvent(new FlowAttributeChangeEvent(name, value));
    }

    message(e) {
        return (e && e.body && e.body.message) || (e && e.message) || 'Something went wrong';
    }

    // ---------- zones ----------
    get zones() {
        return ZONES.map((z) => {
            const count = this.findings.filter((f) => f.zone === z.value).length;
            const clear = this.clearZones.has(z.value);
            let status = 'Not checked';
            let tone = 'todo';
            if (count) {
                status = `${count} finding${count === 1 ? '' : 's'}`;
                tone = 'found';
            } else if (clear) {
                status = 'Clear';
                tone = 'clear';
            }
            const active = z.value === this.activeZone;
            return {
                ...z,
                status,
                cardClass: `zone-card ${tone}${active ? ' active' : ''}`,
                ariaPressed: active ? 'true' : 'false'
            };
        });
    }

    get checkedCount() {
        return ZONES.filter(
            (z) => this.clearZones.has(z.value) || this.findings.some((f) => f.zone === z.value)
        ).length;
    }

    get zoneTotal() {
        return ZONES.length;
    }

    get progressStyle() {
        return `width: ${Math.round((this.checkedCount / ZONES.length) * 100)}%`;
    }

    get hasActiveZone() {
        return !!this.activeZone;
    }

    get activeZoneHint() {
        const z = ZONES.find((x) => x.value === this.activeZone);
        return z ? z.hint : '';
    }

    get activeFindings() {
        return this.findings
            .filter((f) => f.zone === this.activeZone)
            .map((f) => ({
                ...f,
                title: [f.pest, f.evidence].filter(Boolean).join(' · ') || 'Observation',
                sevClass: `sev-pill ${(f.severity || 'Light').toLowerCase()}`,
                hasPhotos: f.photos && f.photos.length > 0,
                photoCount: f.photos ? f.photos.length : 0,
                photos: (f.photos || []).map((p) => ({
                    ...p,
                    url: `/sfc/servlet.shepherd/version/renditionDownload?rendition=THUMB240BY180&versionId=${p.versionId}`
                }))
            }));
    }

    get activeZoneHasFindings() {
        return this.activeFindings.length > 0;
    }

    get activeZoneClear() {
        return this.clearZones.has(this.activeZone);
    }

    get canMarkClear() {
        return !this.activeZoneHasFindings && !this.activeZoneClear;
    }

    selectZone(event) {
        const zone = event.currentTarget.dataset.zone;
        this.activeZone = this.activeZone === zone ? null : zone;
        this.draft = null;
    }

    markClear() {
        const next = new Set(this.clearZones);
        next.add(this.activeZone);
        this.clearZones = next;
        this.activeZone = null;
    }

    // ---------- finding editor ----------
    get editing() {
        return !!this.draft;
    }

    get pestChips() {
        return this.chips(PESTS, this.draft && this.draft.pest, 'pest');
    }

    get evidenceChips() {
        return this.chips(EVIDENCE, this.draft && this.draft.evidence, 'evidence');
    }

    get severityChips() {
        return SEVERITIES.map((s) => {
            const on = this.draft && this.draft.severity === s;
            return {
                value: s,
                cls: `sev-chip ${s.toLowerCase()}${on ? ' selected' : ''}`,
                ariaPressed: on ? 'true' : 'false'
            };
        });
    }

    chips(values, selected, field) {
        return values.map((v) => ({
            value: v,
            field,
            cls: v === selected ? 'chip selected' : 'chip',
            ariaPressed: v === selected ? 'true' : 'false'
        }));
    }

    get saveDisabled() {
        return this.saving || !this.draft || (!this.draft.pest && !this.draft.evidence);
    }

    get editorTitle() {
        return this.draft && this.draft.id ? 'Edit finding' : 'New finding';
    }

    startFinding() {
        this.draft = emptyDraft(this.activeZone);
    }

    editFinding(event) {
        const f = this.findings.find((x) => x.id === event.currentTarget.dataset.id);
        if (f) {
            this.draft = {
                id: f.id,
                zone: f.zone,
                pest: f.pest,
                evidence: f.evidence,
                severity: f.severity || 'Light',
                customerNote: f.customerNote || '',
                internalNote: f.internalNote || ''
            };
        }
    }

    cancelFinding() {
        this.draft = null;
    }

    pickChip(event) {
        const { field, value } = event.currentTarget.dataset;
        const current = this.draft[field];
        this.draft = { ...this.draft, [field]: current === value ? null : value };
    }

    pickSeverity(event) {
        this.draft = { ...this.draft, severity: event.currentTarget.dataset.value };
    }

    handleNote(event) {
        this.draft = { ...this.draft, [event.target.dataset.field]: event.target.value };
    }

    async submitFinding() {
        this.saving = true;
        try {
            this.apply(await saveFinding({ inspectionId: this.inspectionId, finding: this.draft }));
            this.draft = null;
            const next = new Set(this.clearZones);
            next.delete(this.activeZone);
            this.clearZones = next;
        } catch (e) {
            this.error = this.message(e);
        } finally {
            this.saving = false;
        }
    }

    async removeFinding(event) {
        this.saving = true;
        try {
            this.apply(
                await deleteFinding({ inspectionId: this.inspectionId, findingId: event.currentTarget.dataset.id })
            );
        } catch (e) {
            this.error = this.message(e);
        } finally {
            this.saving = false;
        }
    }

    async handleUploadFinished() {
        this.apply(await getState({ inspectionId: this.inspectionId }));
    }

    previewPhoto(event) {
        this[NavigationMixin.Navigate]({
            type: 'standard__namedPage',
            attributes: { pageName: 'filePreview' },
            state: { selectedRecordId: event.currentTarget.dataset.doc }
        });
    }

    // ---------- recommendation ----------
    get hasRecommendation() {
        return !!(this.recommendation && this.recommendation.reasons);
    }

    get reasons() {
        return ((this.recommendation && this.recommendation.reasons) || []).map((r) => ({
            ...r,
            key: r.sku,
            because: (r.because || []).map((text, i) => ({ key: `${r.sku}-${i}`, text }))
        }));
    }

    get overallSeverity() {
        return (this.recommendation && this.recommendation.severity) || 'Light';
    }

    get overallSevClass() {
        return `sev-pill ${this.overallSeverity.toLowerCase()}`;
    }

    get photoTotal() {
        return this.findings.reduce((n, f) => n + (f.photos ? f.photos.length : 0), 0);
    }

    get findingTotal() {
        return this.findings.length;
    }

    @api
    validate() {
        if (this.editing) {
            return { isValid: false, errorMessage: 'Save or cancel the open finding before continuing.' };
        }
        if (this.checkedCount === 0) {
            return {
                isValid: false,
                errorMessage: 'Check at least one zone: add a finding or mark it clear.'
            };
        }
        return { isValid: true };
    }
}
