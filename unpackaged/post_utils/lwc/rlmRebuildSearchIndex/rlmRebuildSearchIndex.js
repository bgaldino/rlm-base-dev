import { LightningElement } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import deployIndex from '@salesforce/apex/RLM_RebuildSearchIndex.deployIndex';

export default class RlmRebuildSearchIndex extends LightningElement {
    isDeploying = false;

    get buttonLabel() {
        return this.isDeploying ? 'Building...' : 'Build Catalog Index';
    }

    get isButtonDisabled() {
        return this.isDeploying;
    }

    async handleBuildIndex() {
        if (this.isDeploying) return;
        this.isDeploying = true;

        try {
            const result = await deployIndex();

            if (result.isSuccess) {
                this.showToast(
                    'Index Build Started',
                    'PCM catalog index deployment initiated. Allow up to 15 minutes for completion.',
                    'success'
                );
            } else {
                this.showToast('Index Build Failed', result.message, 'error');
            }
        } catch (error) {
            this.showToast('Error', error.body?.message || error.message, 'error');
        } finally {
            this.isDeploying = false;
        }
    }

    showToast(title, message, variant) {
        this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
    }
}
