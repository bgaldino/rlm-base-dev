import { LightningElement } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import getEnabled from '@salesforce/apex/RLM_HomeServices_SettingsCtrl.getEnabled';
import setEnabled from '@salesforce/apex/RLM_HomeServices_SettingsCtrl.setEnabled';

export default class RlmHomeServicesSettingsToggle extends LightningElement {
    isEnabled = false;
    isLoading = true;

    connectedCallback() {
        this.loadSetting();
    }

    async loadSetting() {
        try {
            this.isEnabled = await getEnabled();
        } catch (error) {
            this.showToast('Error', 'Could not load Home Services setting.', 'error');
        } finally {
            this.isLoading = false;
        }
    }

    async handleToggle(event) {
        const newValue = event.target.checked;
        this.isLoading = true;
        try {
            await setEnabled({ enabled: newValue });
            this.isEnabled = newValue;
            const state = newValue ? 'enabled' : 'disabled';
            this.showToast('Success', `Home Services automation ${state}.`, 'success');
        } catch (error) {
            this.isEnabled = !newValue;
            this.showToast('Error', 'Could not update setting. Check permissions.', 'error');
        } finally {
            this.isLoading = false;
        }
    }

    showToast(title, message, variant) {
        this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
    }
}
