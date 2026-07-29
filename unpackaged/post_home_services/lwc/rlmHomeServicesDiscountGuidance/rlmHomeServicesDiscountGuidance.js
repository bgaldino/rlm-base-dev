import { LightningElement } from 'lwc';
import discountGuidanceUrl from '@salesforce/resourceUrl/RLM_HomeServices_DiscountGuidance';

export default class Rlm_discountGuidance extends LightningElement {
    guidance = null;
    error = null;

    connectedCallback() {
        fetch(discountGuidanceUrl)
            .then((res) => res.json())
            .then((data) => {
                this.guidance = data;
            })
            .catch(() => {
                this.error = 'Failed to load guidance.';
            });
    }

    get hasGuidance() {
        return this.guidance != null;
    }

    get hasError() {
        return this.error != null;
    }

    get isLoading() {
        return !this.hasGuidance && !this.hasError;
    }

    get title() {
        return this.guidance?.title ?? 'Discount Guidance';
    }

    get steps() {
        const steps = this.guidance?.steps ?? [];
        return steps.map((step, idx) => ({
            ...step,
            key: `step-${idx}`
        }));
    }
}