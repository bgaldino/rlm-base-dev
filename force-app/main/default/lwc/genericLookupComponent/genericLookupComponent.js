import { LightningElement, api, track, wire } from 'lwc';
import { gql, graphql } from 'lightning/uiGraphQLApi';
import { FlowAttributeChangeEvent } from 'lightning/flowSupport';

const DELAY = 300;

export default class GenericLookupComponent extends LightningElement {

    @api helpText; // Text to show on hover the field.
    @api required = false; // Mark field as required.
    @api selectedIconName = "standard:all"; // Field icon from SLDS.
    @api objectLabel; // Object name.
    @api objectApiName; // Standard or Custom object api name.
    @api fieldLabel; // Field name.
    @api fieldApiName = 'Name'; // Api field name.
    @api placeholder; // Placeholder value.
    @api queryNeedleType = 'String!'; // Data type for the needle.
    @api queryNeedle = ''; // The needle, search value from parent component.
    @api additionalConditions = '';
    @api additionalFieldsInResponse = '';
    @api queryFields = ``; // Fields to query.
    @api queryWhere = ``; // Query where conditions.
    @api showAddNewButton = false; // Show the "+ New record" button
    @api queryLimit = 10; // Limit the graphql query
    @api variant = 'standard';
    @api disabled = false;
    @api runningTest = false;
    @api secondDisplayText;
    @api fieldsSet;

    @api selectedRecordName;
    @api selectedRecordId;
    preventClosingOfSerachPanel = false;
    searchTerm;
    gqlQuery;
    error;
    isModalOpen = false;
    clearList = false;

    @wire(graphql, {
        query: '$gqlQuery',
        variables: '$variables'
    })
    records;

    @api get variables() {
        return {
            queryNeedle: this.searchTerm === '' ? ' ' : `%${this.searchTerm}%`
        };
    }

    get isValueSelected() {
        return this.selectedRecordId;
    }

    get list() {
        if (this.records.data && this.records.data.uiapi && this.records.data.uiapi.query && this.records.data.uiapi.query[this.objectApiName] && this.records.data.uiapi.query[this.objectApiName].edges) {
            let edges = this.records.data.uiapi.query[this.objectApiName].edges;
            let edgesUpdated;
            if (this.secondDisplayText)
                edgesUpdated = edges.map(edg => { return { ...edg, "displayValue": edg.node[this.fieldApiName].value, "secondDisplayValue": this.secondDisplayValue(edg.node[this.secondDisplayField].value) } });
            else
                edgesUpdated = edges.map(edg => { return { ...edg, "displayValue": edg.node[this.fieldApiName].value } });
            return edgesUpdated;
        }
        return [];
    }

    set list(value) {
        this.records = value;
    }

    @api secondDisplayField;

    extractSecondDisplayField(displayText) {
        let firstIndex = displayText.indexOf("::");
        let lastIndex = displayText.lastIndexOf("::");
        let fieldname = displayText.substring(firstIndex + 2, lastIndex);
        return fieldname;
    }

    secondDisplayValue(replaceValue) {
        let displayText = "";
        let placeholder = `::${this.secondDisplayField}::`;
        if (this.secondDisplayText) {
            displayText = this.secondDisplayText;
            displayText = displayText.replace(placeholder, replaceValue);
        }
        return displayText;
    }

    @api queryResult;

    get dynamicQueryBuild() {
        this.queryResult = `
        query genericSearch($queryNeedle: ${this.queryNeedleType}) {
            uiapi {
                query {
                    ${this.objectApiName}(
                        first: ${this.queryLimit}
                        where: { ${this.queryWhere} ${this.additionalConditions} }
                        orderBy: { ${this.fieldApiName}: { order: ASC } }
                    ) {
                        edges {
                            node {
                                ${this.queryFields}
                            }
                        }
                    }
                }
            }
        }`;
        return this.queryResult;
    }

    @wire(graphql, {
        query: "$selectedRecordQuery",
        variables: "$selectedRecordQueryData",
    })
    selectedRecord({ error, data }) {
        if (error) {
            //some code
        } else if (data) {
            if (this.selectedRecordId && !this.selectedRecordName) {
                const nodeItem = data.uiapi.query[this.objectApiName].edges[0].node;
                this.selectedRecordName = nodeItem[this.fieldApiName].value;
                // bubble event selected event
                const selectedRecord = {
                    id: nodeItem.Id,
                    //name: nodeItem.Name.value,
                    name: nodeItem[this.fieldApiName].value,
                    field: this.fieldApiName,
                    record: nodeItem
                };

                // Creates the event
                const selectedEvent = new CustomEvent('lookupselected', {
                    detail: selectedRecord,
                    bubbles: true,
                    composed: true
                });

                //dispatching the custom event
                this.dispatchEvent(selectedEvent);
            }
        }
    }
    get selectedRecordQuery() {
        if (!this.selectedRecordId || this.selectedRecordName) {
            return undefined;
        }
        return gql`
        query getSelectedRecord($selectedRecordId: ID!) {
            uiapi {
                query {
                    ${this.objectApiName}(
                        first: 1
                        where: { Id: { eq: $selectedRecordId } }
                    ) {
                        edges {
                            node {
                                ${this.queryFields}
                            }
                        }
                    }
                }
            }
        }`;
    }
    get selectedRecordQueryData() {
        return {
            selectedRecordId: this.selectedRecordId,
        };
    }

    @api set fieldSelectedId(value) {
        this.selectedRecordId = value;
        this.clearList = true;
    }

    get fieldSelectedId() {
        return this.selectedRecordId;
    }

    @api set fieldSelectedName(value) {
        this.selectedRecordName = value;
        this.clearList = true;
    }

    get fieldSelectedName() {
        return this.selectedRecordName;
    }

    connectedCallback() {
        try {
            this.fieldsSet = new Set();
            this.fieldsSet.add("Id");
            this.searchTerm = this.queryNeedle;
            if (this.queryWhere === '') {
                this.queryWhere = `${this.fieldApiName} : { like: $queryNeedle }`;
            }

            if (this.queryFields === '') {
                this.queryFields = `
            Id
            ${this.fieldApiName} {
                value
            }`;
                this.fieldsSet.add(this.fieldApiName);
            }

            if (this.secondDisplayText) {
                this.secondDisplayField = this.extractSecondDisplayField(this.secondDisplayText);
                this.queryFields = this.queryFields + `
            ${this.secondDisplayField} {
                value
            }`;
                this.fieldsSet.add(this.secondDisplayField);
            }

            if (this.additionalFieldsInResponse) {
                let fieldsList = this.additionalFieldsInResponse.split(',');

                if (fieldsList.length > 0) {
                    for (let i = 0; i < fieldsList.length; i++) {
                        this.queryFields = this.queryFields + `
                    ${fieldsList[i]} {
                        value
                    }`;
                        this.fieldsSet.add(fieldsList[i]);
                    }
                }
            }
            this.gqlQuery = gql`${this.dynamicQueryBuild}`;
        } catch (error) {
            console.log('error: ' + error);
        }
    }

    renderedCallback() {
        if (this.clearList) {
            this.clearList = false;
            this.list = [];
        }
    }

    handlefocus(event) {
        this.handleKeyChange(event);
    }

    handleKeyChange(event) {
        // Debouncing this method: Do not update the reactive property as long as this function is
        // being called within a delay of DELAY. This is to avoid a very large number of Apex method calls.
        window.clearTimeout(this.delayTimeout);
        const searchTerm = !event.target.value ? '%' : event.target.value;
        // eslint-disable-next-line @lwc/lwc/no-async-operation
        this.delayTimeout = setTimeout(() => {
            this.searchTerm = searchTerm;
        }, DELAY);
    }

    //handler for clicking outside the selection panel
    handleBlur() {
        this.searchTerm = '';
        this.list = [];
    }

    @api selectedRecordOutput;


    //handler for selection of records from lookup result list
    handleSelect(event) {
        try {
            const position = event.currentTarget.dataset.position;
            const nodeItem = this.list[position].node;
            const selectedRecord = {
                id: nodeItem.Id,
                name: nodeItem[this.fieldApiName].value,
                field: this.fieldApiName,
                record: nodeItem
            };
            this.selectedRecordId = selectedRecord.id;
            this.selectedRecordName = selectedRecord.name;

            this.selectedRecordOutput = {};
            this.selectedRecordOutput.Id = nodeItem.Id;
            for (const item of this.fieldsSet) {
                if (item === "Id") continue;
                this.selectedRecordOutput[item] = nodeItem[item].value;
            }
            this.list = [];

            // Creates the event
            const selectedEvent = new CustomEvent('lookupselected', {
                detail: selectedRecord,
                bubbles: true,
                composed: true
            });

            //dispatching the custom event
            this.dispatchEvent(selectedEvent);
            if (!this.runningTest) {
                this.dispatchEvent(new FlowAttributeChangeEvent('selectedRecordId', this.selectedRecordId));
                this.dispatchEvent(new FlowAttributeChangeEvent('selectedRecordOutput', this.selectedRecordOutput));
            }
        } catch (error) {
            console.error(error);
        }
    }

    //handler for deselection of the selected item
    handleCommit(e) {
        if (this.disabled) {
            e.preventDefault();
        }
        else {
            this.selectedRecordId = '';
            this.selectedRecordName = '';
            this.selectedRecordOutput = {};
            this.list = [];

            // Creates the event
            const clearedEvent = new CustomEvent('lookupcleared', {
                bubbles: true,
                composed: true,
                detail: {}
            });

            //dispatching the custom event
            this.dispatchEvent(clearedEvent);
            if (!this.runningTest) {
                this.dispatchEvent(new FlowAttributeChangeEvent('selectedRecordId', this.selectedRecordId));
                this.dispatchEvent(new FlowAttributeChangeEvent('selectedRecordOutput', this.selectedRecordOutput));
            }
        }
    }

    //open modal window
    openModal() {
        this.isModalOpen = true;
        this.list = [];
    }

    //close modal window
    closeModal() {
        this.isModalOpen = false;
    }

    //submit form details
    submitDetails() {
        // TODO: pending
    }
}