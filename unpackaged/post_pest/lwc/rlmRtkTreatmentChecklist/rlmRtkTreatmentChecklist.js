import { LightningElement, api } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';
import getWorkOrderFindings from '@salesforce/apex/RLM_RTK_Inspection.getWorkOrderFindings';
import saveTreatment from '@salesforce/apex/RLM_RTK_Inspection.saveTreatment';
import tagAfterPhotos from '@salesforce/apex/RLM_RTK_Inspection.tagAfterPhotos';

const THUMB = '/sfc/servlet.shepherd/version/renditionDownload?rendition=THUMB240BY180&versionId=';
const PHOTO_FORMATS = ['.jpg', '.jpeg', '.png', '.heic', '.heif', '.webp'];
const STATUSES = [
    { value: 'Treated', label: 'Treated', tone: 'done' },
    { value: 'Needs Follow-up', label: 'Needs follow-up', tone: 'follow' }
];

export default class RlmRtkTreatmentChecklist extends NavigationMixin(LightningElement) {
    @api recordId;
    @api workOrderId;

    state;
    loaded = false;
    error;
    savingId;
    notes = {};
    photoFormats = PHOTO_FORMATS;

    connectedCallback() {
        this.load();
    }

    get targetId() {
        return this.workOrderId || this.recordId;
    }

    async load() {
        try {
            this.apply(await getWorkOrderFindings({ workOrderId: this.targetId }));
        } catch (e) {
            this.error = this.message(e);
        } finally {
            this.loaded = true;
        }
    }

    apply(state) {
        this.state = state;
        this.error = undefined;
    }

    message(e) {
        return (e && e.body && e.body.message) || (e && e.message) || 'Something went wrong';
    }

    get hasInspection() {
        return !!(this.state && this.state.findings && this.state.findings.length);
    }

    get showEmpty() {
        return this.loaded && !this.hasInspection && !this.error;
    }

    get total() {
        return this.state.findings.length;
    }

    get treated() {
        return this.state.treatedCount || 0;
    }

    get progressStyle() {
        return `width: ${this.total ? Math.round((this.treated / this.total) * 100) : 0}%`;
    }

    get allDone() {
        return this.total > 0 && this.treated === this.total;
    }

    get findings() {
        return this.state.findings.map((f) => {
            const status = f.treatmentStatus || 'Open';
            const thumbs = (list) => (list || []).map((p) => ({ ...p, url: THUMB + p.versionId }));
            return {
                ...f,
                observation: [f.pest, f.evidence].filter(Boolean).join(' – ') || 'Observation',
                sevClass: `sev-pill ${(f.severity || 'Light').toLowerCase()}`,
                cardClass: `finding ${status === 'Treated' ? 'done' : status === 'Needs Follow-up' ? 'follow' : ''}`,
                statusLabel: status,
                beforePhotos: thumbs(f.photos),
                afterThumbs: thumbs(f.afterPhotos),
                noBefore: !(f.photos && f.photos.length > 0),
                busy: this.savingId === f.id,
                noteValue: this.notes[f.id] !== undefined ? this.notes[f.id] : f.treatmentNote || '',
                statuses: STATUSES.map((s) => ({
                    ...s,
                    cls: `status-btn ${s.tone}${status === s.value ? ' selected' : ''}`,
                    ariaPressed: status === s.value ? 'true' : 'false'
                }))
            };
        });
    }

    handleNote(event) {
        this.notes = { ...this.notes, [event.target.dataset.id]: event.target.value };
    }

    async setStatus(event) {
        const { id, value } = event.currentTarget.dataset;
        const f = this.state.findings.find((x) => x.id === id);
        const current = f.treatmentStatus || 'Open';
        const next = current === value ? 'Open' : value;
        const note = this.notes[id] !== undefined ? this.notes[id] : f.treatmentNote;
        this.savingId = id;
        try {
            this.apply(await saveTreatment({ workOrderId: this.targetId, findingId: id, status: next, note }));
            const rest = { ...this.notes };
            delete rest[id];
            this.notes = rest;
        } catch (e) {
            this.error = this.message(e);
        } finally {
            this.savingId = undefined;
        }
    }

    async saveNote(event) {
        const id = event.currentTarget.dataset.id;
        const f = this.state.findings.find((x) => x.id === id);
        this.savingId = id;
        try {
            this.apply(
                await saveTreatment({
                    workOrderId: this.targetId,
                    findingId: id,
                    status: f.treatmentStatus,
                    note: this.notes[id]
                })
            );
            const rest = { ...this.notes };
            delete rest[id];
            this.notes = rest;
        } catch (e) {
            this.error = this.message(e);
        } finally {
            this.savingId = undefined;
        }
    }

    async handleAfterUpload(event) {
        const findingId = event.target.dataset.id;
        const documentIds = (event.detail.files || []).map((file) => file.documentId);
        try {
            this.apply(await tagAfterPhotos({ workOrderId: this.targetId, findingId, documentIds }));
        } catch (e) {
            this.error = this.message(e);
        }
    }

    previewPhoto(event) {
        this[NavigationMixin.Navigate]({
            type: 'standard__namedPage',
            attributes: { pageName: 'filePreview' },
            state: { selectedRecordId: event.currentTarget.dataset.doc }
        });
    }
}
