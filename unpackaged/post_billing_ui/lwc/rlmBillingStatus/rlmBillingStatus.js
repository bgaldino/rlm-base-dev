import { LightningElement, api, track, wire } from 'lwc';
import { gql, graphql } from 'lightning/graphql';

export default class RlmBillingStatus extends LightningElement {
    @api recordId;
    @track statusData = null;
    @track isLoading = true;

    @wire(graphql, {
        query: '$queryBillingAccount',
        variables: '$variables'
    })
    wiredResult({ data, errors }) {
        if (!this.recordId) {
            this.isLoading = false;
            return;
        }
        if (errors && errors.length) {
            this.statusData = { isSuspended: false, isActive: true };
            this.isLoading = false;
            return;
        }
        if (data) {
            this.processData(data);
            this.isLoading = false;
        }
    }

    get variables() {
        return this.recordId ? { accountId: this.recordId } : undefined;
    }

    queryBillingAccount = gql`
        query BillingAccountForAccount($accountId: ID!) {
            uiapi {
                query {
                    BillingAccount(
                        where: {
                            AccountId: { eq: $accountId }
                            IsDefaultBillingProfile: { eq: true }
                        }
                        first: 1
                    ) {
                        edges {
                            node {
                                Id
                                BillingSuspensionDate { value }
                                BillingResumptionDate { value }
                            }
                        }
                    }
                }
            }
        }
    `;

    processData(data) {
        const node = data?.uiapi?.query?.BillingAccount?.edges?.[0]?.node;
        if (!node) {
            this.statusData = { isSuspended: false, isActive: true };
            return;
        }

        const suspensionDate = node?.BillingSuspensionDate?.value;
        const resumptionDate = node?.BillingResumptionDate?.value;
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const resumptionDateValue = resumptionDate ? new Date(resumptionDate) : null;
        if (resumptionDateValue) resumptionDateValue.setHours(0, 0, 0, 0);
        const isSuspended = !!suspensionDate && (!resumptionDateValue || resumptionDateValue >= today);

        this.statusData = {
            isSuspended,
            isActive: !isSuspended,
            formattedSuspensionDate: suspensionDate
                ? new Date(suspensionDate).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
                : '',
            formattedResumptionDate: resumptionDate
                ? new Date(resumptionDate).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
                : ''
        };
    }

    get showSuspended() {
        return !this.isLoading && this.statusData?.isSuspended;
    }
}