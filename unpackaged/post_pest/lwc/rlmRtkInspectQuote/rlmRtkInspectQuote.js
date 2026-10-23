import { LightningElement, api } from 'lwc';
import { FlowAttributeChangeEvent } from 'lightning/flowSupport';

const PLANS = [
    {
        sku: 'RTK-ESSENTIAL',
        name: 'Essential',
        price: 45,
        blurb: 'General pest coverage for smaller homes',
        features: ['Monthly visits', 'Ants, spiders, roaches']
    },
    {
        sku: 'RTK-HOME-PROT',
        name: 'Home Protection',
        price: 59,
        blurb: 'Best for most single-family homes',
        features: ['Monthly visits', 'Broader pest list', 'Re-service guarantee']
    },
    {
        sku: 'RTK-HOME-PROT-PLUS',
        name: 'Home Protection Plus',
        price: 79,
        blurb: 'Premium coverage with priority response',
        features: ['Bi-weekly option', 'Extended pests', 'Priority booking']
    }
];

const PROPERTIES = [
    { value: 'SingleFamily', label: 'Single family', icon: 'utility:home', hint: 'Detached house' },
    { value: 'Townhome', label: 'Townhome', icon: 'utility:rows', hint: 'Shared walls' },
    { value: 'Condo', label: 'Condo', icon: 'utility:company', hint: 'Multi-unit' }
];

const SQFT_BUCKETS = [
    { value: 'Under2000', label: 'Under 2,000', min: 800, max: 1999 },
    { value: '2000to3500', label: '2,000 – 3,500', min: 2000, max: 3500 },
    { value: 'Over3500', label: 'Over 3,500', min: 3501, max: 6000 }
];

const SEVERITIES = [
    { value: 'Light', label: 'Light', tone: 'light', hint: 'A few sightings' },
    { value: 'Moderate', label: 'Moderate', tone: 'moderate', hint: 'Active trails' },
    { value: 'Heavy', label: 'Heavy', tone: 'heavy', hint: 'Widespread' }
];

export default class RlmRtkInspectQuote extends LightningElement {
    @api accountName;
    @api postalCode;

    _planSku = 'RTK-HOME-PROT';
    _propertyType = 'SingleFamily';
    _squareFootage = 'Under2000';
    _severity = 'Moderate';
    _includeMosquito = true;
    _includeTermite = false;
    _rec;
    _overrideNote = '';
    sqftSlider = 1600;

    @api
    get recommendationJson() {
        return this._rec ? JSON.stringify(this._rec) : undefined;
    }
    set recommendationJson(v) {
        try {
            this._rec = v ? JSON.parse(v) : undefined;
        } catch (e) {
            this._rec = undefined;
        }
    }

    @api
    get overrideReason() {
        return this.composeOverride();
    }
    set overrideReason(v) {
        this._overrideNote = v || '';
    }

    @api
    get planSku() {
        return this._planSku;
    }
    set planSku(v) {
        if (v) this._planSku = v;
    }

    @api
    get propertyType() {
        return this._propertyType;
    }
    set propertyType(v) {
        if (v) this._propertyType = v;
    }

    @api
    get squareFootage() {
        return this._squareFootage;
    }
    set squareFootage(v) {
        if (v) {
            this._squareFootage = v;
            const bucket = SQFT_BUCKETS.find((b) => b.value === v);
            if (bucket) {
                this.sqftSlider = Math.round((bucket.min + Math.min(bucket.max, bucket.min + 800)) / 2);
            }
        }
    }

    @api
    get severity() {
        return this._severity;
    }
    set severity(v) {
        if (v) this._severity = v;
    }

    @api
    get includeMosquito() {
        return this._includeMosquito;
    }
    set includeMosquito(v) {
        if (v !== undefined && v !== null) this._includeMosquito = !!v;
    }

    @api
    get includeTermite() {
        return this._includeTermite;
    }
    set includeTermite(v) {
        if (v !== undefined && v !== null) this._includeTermite = !!v;
    }

    connectedCallback() {
        this.publishAll();
    }

    // ---------- recommendation from the inspection walk ----------
    get hasInspection() {
        return !!(this._rec && this._rec.planSku);
    }

    get recommendedSku() {
        return this.hasInspection ? this._rec.planSku : 'RTK-HOME-PROT';
    }

    reasonsFor(sku) {
        if (!this.hasInspection || !this._rec.reasons) return [];
        const r = this._rec.reasons.find((x) => x.sku === sku);
        return r && r.because ? r.because.map((text, i) => ({ key: `${sku}-${i}`, text })) : [];
    }

    get mosquitoReasons() {
        return this.reasonsFor('RTK-MOSQUITO');
    }

    get termiteReasons() {
        return this.reasonsFor('RTK-TERMITE');
    }

    get hasMosquitoReasons() {
        return this.mosquitoReasons.length > 0;
    }

    get hasTermiteReasons() {
        return this.termiteReasons.length > 0;
    }

    get planSubtitle() {
        return this.hasInspection
            ? 'Pre-selected from your inspection findings. You can still change it.'
            : 'Tap a card — Home Protection is the usual pick for Bloomingdale.';
    }

    get severityFromInspection() {
        return this.hasInspection ? this._rec.severity : null;
    }

    get changes() {
        if (!this.hasInspection) return [];
        const rec = this._rec;
        const out = [];
        const name = (sku) => (PLANS.find((p) => p.sku === sku) || { name: sku }).name;
        if (this._planSku !== rec.planSku) out.push(`Plan ${name(rec.planSku)} → ${name(this._planSku)}`);
        if (rec.severity && this._severity !== rec.severity) out.push(`Severity ${rec.severity} → ${this._severity}`);
        if (this._includeMosquito !== (rec.includeMosquito === true)) {
            out.push(this._includeMosquito ? 'Mosquito added' : 'Mosquito removed');
        }
        if (this._includeTermite !== (rec.includeTermite === true)) {
            out.push(this._includeTermite ? 'Termite added' : 'Termite removed');
        }
        return out;
    }

    get isOverridden() {
        return this.changes.length > 0;
    }

    get changeSummary() {
        return this.changes.join(' · ');
    }

    get overrideNote() {
        return this._overrideNote;
    }

    composeOverride() {
        if (!this.isOverridden) return null;
        return `${this.changeSummary}. Reason: ${this._overrideNote || ''}`.trim();
    }

    handleOverride(event) {
        this._overrideNote = event.target.value;
        this.emit('overrideReason', this.composeOverride());
    }

    get plans() {
        const recSku = this.recommendedSku;
        return PLANS.map((p) => ({
            ...p,
            recommended: p.sku === recSku,
            because: this.reasonsFor(p.sku),
            hasBecause: p.sku === recSku && this.reasonsFor(p.sku).length > 0,
            selected: p.sku === this._planSku,
            cardClass: p.sku === this._planSku ? 'plan-card selected' : 'plan-card',
            priceLabel: `$${p.price}`,
            ariaPressed: p.sku === this._planSku ? 'true' : 'false'
        }));
    }

    get properties() {
        return PROPERTIES.map((p) => ({
            ...p,
            selected: p.value === this._propertyType,
            tileClass: p.value === this._propertyType ? 'prop-tile selected' : 'prop-tile',
            ariaPressed: p.value === this._propertyType ? 'true' : 'false'
        }));
    }

    get severities() {
        return SEVERITIES.map((s) => ({
            ...s,
            selected: s.value === this._severity,
            chipClass:
                s.value === this._severity
                    ? `sev-chip ${s.tone} selected`
                    : `sev-chip ${s.tone}`,
            ariaPressed: s.value === this._severity ? 'true' : 'false'
        }));
    }

    get sqftBucketLabel() {
        const bucket = SQFT_BUCKETS.find((b) => b.value === this._squareFootage);
        return bucket ? bucket.label : '';
    }

    get sqftDisplay() {
        return `${this.sqftSlider.toLocaleString()} sq ft`;
    }

    get mosquitoCardClass() {
        return this._includeMosquito ? 'addon-card on' : 'addon-card';
    }

    get termiteCardClass() {
        return this._includeTermite ? 'addon-card on' : 'addon-card';
    }

    get selectedPlanName() {
        const plan = PLANS.find((p) => p.sku === this._planSku);
        return plan ? plan.name : '';
    }

    get summaryBits() {
        const bits = [this.selectedPlanName, this._propertyType, this.sqftBucketLabel, this._severity];
        if (this._includeMosquito) bits.push('Mosquito');
        if (this._includeTermite) bits.push('Termite');
        return bits.filter(Boolean).join(' · ');
    }

    get hasZip() {
        return !!this.postalCode;
    }

    selectPlan(event) {
        this._planSku = event.currentTarget.dataset.sku;
        this.emit('planSku', this._planSku);
    }

    selectProperty(event) {
        this._propertyType = event.currentTarget.dataset.value;
        this.emit('propertyType', this._propertyType);
    }

    selectSeverity(event) {
        this._severity = event.currentTarget.dataset.value;
        this.emit('severity', this._severity);
    }

    handleSqft(event) {
        this.sqftSlider = Number(event.target.value);
        let bucket = SQFT_BUCKETS[0];
        for (const b of SQFT_BUCKETS) {
            if (this.sqftSlider >= b.min) bucket = b;
        }
        if (bucket.value !== this._squareFootage) {
            this._squareFootage = bucket.value;
            this.emit('squareFootage', this._squareFootage);
        }
    }

    toggleMosquito() {
        this._includeMosquito = !this._includeMosquito;
        this.emit('includeMosquito', this._includeMosquito);
    }

    toggleTermite() {
        this._includeTermite = !this._includeTermite;
        this.emit('includeTermite', this._includeTermite);
    }

    emit(name, value) {
        this.dispatchEvent(new FlowAttributeChangeEvent(name, value));
        if (name !== 'overrideReason') {
            this.dispatchEvent(new FlowAttributeChangeEvent('overrideReason', this.composeOverride()));
        }
    }

    publishAll() {
        this.emit('planSku', this._planSku);
        this.emit('propertyType', this._propertyType);
        this.emit('squareFootage', this._squareFootage);
        this.emit('severity', this._severity);
        this.emit('includeMosquito', this._includeMosquito);
        this.emit('includeTermite', this._includeTermite);
    }

    @api
    validate() {
        if (!this._planSku || !this._propertyType || !this._squareFootage || !this._severity) {
            return {
                isValid: false,
                errorMessage: 'Complete each section before creating the quote.'
            };
        }
        if (this.isOverridden && !(this._overrideNote || '').trim()) {
            return {
                isValid: false,
                errorMessage: 'You changed the inspection recommendation. Add a reason before creating the quote.'
            };
        }
        return { isValid: true };
    }
}
