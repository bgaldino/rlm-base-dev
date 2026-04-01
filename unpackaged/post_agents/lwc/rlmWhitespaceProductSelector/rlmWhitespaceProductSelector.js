import { LightningElement, api } from 'lwc';

export default class RlmWhitespaceProductSelector extends LightningElement {
    @api value; // Receives List<RLM_WhitespaceProduct> from Agentforce

    selectedRows = [];

    columns = [
        { label: 'Product Name', fieldName: 'productName', type: 'text', sortable: true },
        {
            label: 'Adoption Rate',
            fieldName: 'adoptionPercent',
            type: 'percent',
            typeAttributes: { maximumFractionDigits: 0 },
            sortable: true,
            cellAttributes: { alignment: 'center' }
        }
    ];

    get products() {
        if (!this.value || !Array.isArray(this.value)) return [];
        return this.value.map(item => ({
            productId: item.productId,
            productName: item.productName,
            productFamily: item.productFamily || 'General',
            adoptionDisplay: `${item.adoptionCount}/${item.peerCount}`,
            adoptionPercent: (item.adoptionPercent || 0) / 100
        }));
    }

    get selectedIds() {
        return this.selectedRows.map(r => r.productId);
    }

    handleRowSelection(event) {
        this.selectedRows = event.detail.selectedRows;

        // Dispatch valuechange event on every selection change
        // Agent can access selectedProductIds, selectedProductNames, and selectedCount
        // when user types "create quote" or similar in the chat
        const selectedNames = this.selectedRows.map(r => r.productName).join(', ');
        const selectedProductIds = this.selectedRows.map(r => r.productId).join(',');

        this.dispatchEvent(new CustomEvent('valuechange', {
            detail: {
                value: {
                    selectedProductNames: selectedNames,
                    selectedProductIds: selectedProductIds,
                    selectedCount: this.selectedRows.length
                }
            },
            bubbles: true,
            composed: true
        }));
    }
}
