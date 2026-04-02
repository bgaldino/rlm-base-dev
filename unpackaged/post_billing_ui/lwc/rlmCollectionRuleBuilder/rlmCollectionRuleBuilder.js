import { LightningElement } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

export default class RlmCollectionRuleBuilder extends LightningElement {
    conditionIdCounter = 0;

    rule = {
        ruleName: '',
        priority: 1,
        isActive: true,
        conditions: [],
        actions: {
            assignToQueue: '',
            collectionTimeline: ''
        }
    };

    get fieldOptions() {
        return [
            { label: 'Days Past Due', value: 'DaysPastDue' },
            { label: 'Invoice Amount', value: 'InvoiceAmount' },
            { label: 'Customer Risk Tier', value: 'CustomerRiskTier' }
        ];
    }

    get operatorOptions() {
        return [
            { label: 'Equals', value: 'Equals' },
            { label: 'Greater Than', value: 'GreaterThan' },
            { label: 'Less Than', value: 'LessThan' }
        ];
    }

    get queueOptions() {
        return [
            { label: 'Early Stage Collections', value: 'EarlyStageCollections' },
            { label: 'Mid Stage Collections', value: 'MidStageCollections' },
            { label: 'Late Stage Collections', value: 'LateStageCollections' },
            { label: 'Legal Review Queue', value: 'LegalReviewQueue' },
            { label: 'High Value Accounts', value: 'HighValueAccounts' }
        ];
    }

    get timelineOptions() {
        return [
            { label: '30-Day Standard', value: '30DayStandard' },
            { label: '60-Day Extended', value: '60DayExtended' },
            { label: '90-Day Aggressive', value: '90DayAggressive' },
            { label: '120-Day Legal Escalation', value: '120DayLegalEscalation' },
            { label: 'Custom Enterprise Timeline', value: 'CustomEnterprise' }
        ];
    }

    get hasConditions() {
        return this.rule.conditions.length > 0;
    }

    get noConditions() {
        return this.rule.conditions.length === 0;
    }

    get conditionsWithMeta() {
        return this.rule.conditions.map((cond, index) => ({
            ...cond,
            showLogic: index > 0,
            andClass: 'logic-btn' + (cond.logicOperator === 'AND' ? ' logic-btn-active' : ''),
            orClass: 'logic-btn' + (cond.logicOperator === 'OR' ? ' logic-btn-active' : '')
        }));
    }

    // --- Header Handlers ---

    handleRuleNameChange(event) {
        this.rule = { ...this.rule, ruleName: event.detail.value };
    }

    handlePriorityChange(event) {
        this.rule = { ...this.rule, priority: parseInt(event.detail.value, 10) || 1 };
    }

    handleActiveToggle(event) {
        this.rule = { ...this.rule, isActive: event.target.checked };
    }

    // --- Condition Handlers ---

    handleAddCondition() {
        this.conditionIdCounter++;
        const newCondition = {
            id: `cond-${this.conditionIdCounter}`,
            field: '',
            operator: '',
            value: '',
            logicOperator: 'AND'
        };
        this.rule = {
            ...this.rule,
            conditions: [...this.rule.conditions, newCondition]
        };
    }

    handleRemoveCondition(event) {
        const condId = event.currentTarget.dataset.id;
        this.rule = {
            ...this.rule,
            conditions: this.rule.conditions.filter(c => c.id !== condId)
        };
    }

    handleConditionChange(event) {
        const condId = event.currentTarget.dataset.id;
        const fieldName = event.currentTarget.dataset.field;
        const value = event.detail.value;

        this.rule = {
            ...this.rule,
            conditions: this.rule.conditions.map(c =>
                c.id === condId ? { ...c, [fieldName]: value } : c
            )
        };
    }

    handleLogicChange(event) {
        const condId = event.currentTarget.dataset.id;
        const value = event.currentTarget.dataset.value;

        this.rule = {
            ...this.rule,
            conditions: this.rule.conditions.map(c =>
                c.id === condId ? { ...c, logicOperator: value } : c
            )
        };
    }

    // --- Action Handlers ---

    handleQueueChange(event) {
        this.rule = {
            ...this.rule,
            actions: { ...this.rule.actions, assignToQueue: event.detail.value }
        };
    }

    handleTimelineChange(event) {
        this.rule = {
            ...this.rule,
            actions: { ...this.rule.actions, collectionTimeline: event.detail.value }
        };
    }

    // --- Footer Handlers ---

    handleSave() {
        const validationError = this._validate();
        if (validationError) {
            this._showToast('Validation Error', validationError, 'error');
            return;
        }

        const output = {
            ruleName: this.rule.ruleName,
            priority: this.rule.priority,
            isActive: this.rule.isActive,
            conditions: this.rule.conditions.map(({ field, operator, value, logicOperator }) => ({
                field,
                operator,
                value,
                logicOperator
            })),
            actions: { ...this.rule.actions }
        };

        console.log('Collection Rule Saved:', JSON.stringify(output, null, 2));
        this._showToast('Success', `Rule "${this.rule.ruleName}" saved successfully.`, 'success');
    }

    handleCancel() {
        this.rule = {
            ruleName: '',
            priority: 1,
            isActive: true,
            conditions: [],
            actions: {
                assignToQueue: '',
                collectionTimeline: ''
            }
        };
        this.conditionIdCounter = 0;
        this._showToast('Info', 'Form has been reset.', 'info');
    }

    // --- Private Helpers ---

    _validate() {
        if (!this.rule.ruleName || !this.rule.ruleName.trim()) {
            return 'Rule Name is required.';
        }
        if (this.rule.conditions.length === 0) {
            return 'At least one condition is required.';
        }
        const incomplete = this.rule.conditions.find(c => !c.field || !c.operator || !c.value);
        if (incomplete) {
            return 'All condition rows must have Field, Operator, and Value filled in.';
        }
        if (!this.rule.actions.assignToQueue) {
            return 'Please select an Assign To Queue.';
        }
        if (!this.rule.actions.collectionTimeline) {
            return 'Please select a Collection Timeline.';
        }
        return null;
    }

    _showToast(title, message, variant) {
        this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
    }
}