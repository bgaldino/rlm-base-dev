import { createElement } from 'lwc';
import GenericLookupComponent from 'c/genericLookupComponent';
import { graphql } from 'lightning/uiGraphQLApi';
import { FlowAttributeChangeEventName } from 'lightning/flowSupport';

const GQL_ONE_RESULT = require("./data/gql_one_result.json");
const GQL_THREE_RESULTS = require("./data/gql_three_results.json");
const GQL_ONE_RESULT_TENANT = require("./data/gql_one_result_tenant.json");

const resolvePromises = async () => Promise.resolve;

const createComponentUnderTest = async () => {

    const el = createElement('c-generic-lookup-component', {
        is: GenericLookupComponent
    });

    el.helpText = 'Jest Test Contact';
    el.objectLabel = 'Contact';
    el.objectApiName = 'Contact';
    el.fieldLabel = 'Contact';
    el.fieldApiName = 'Name';
    el.secondDisplayText = '::Department::';
    el.additionalFieldsInResponse = 'Email';
    el.placeholder = 'Jest Test Contact Placeholder';

    return el;
};

const createComponentUnderTestForTenant = async () => {

    const el = createElement('c-generic-lookup-component', {
        is: GenericLookupComponent
    });

    el.helpText = 'Jest Test Tenant';
    el.objectLabel = 'Tenant';
    el.objectApiName = 'Tenant__c';
    el.fieldLabel = 'Tenant';
    el.fieldApiName = 'OptionalName__c';
    el.secondDisplayText = 'Status - ::Quoting_Status__c::';
    el.placeholder = 'Jest Test Tenant Placeholder';

    return el;
};

const DEFAULT_GQL_FIELDS = `
            Id
            Name {
                value
            }
            Department {
                value
            }
                    Email {
                        value
                    }`;

const DEFAULT_GQL_WHERE = `Name : { like: $queryNeedle }`;

describe('c-generic-lookup-component', () => {

    afterEach(() => {
        // The jsdom instance is shared across test cases in a single file so reset the DOM
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    async function flushPromises() {
        return Promise.resolve();
    }

    it('should validate default values', async () => {

        const component = await createComponentUnderTest();
        const id = '003O8000003DoBpIAK';
        const name = 'Carlos Hernandez';
        component.fieldSelectedId = id;

        document.body.appendChild(component);

        await resolvePromises();
        
        graphql.emit(GQL_THREE_RESULTS);

        await flushPromises();


        expect(component.fieldSelectedId).toBe(id);
        expect(component.fieldSelectedName).toBe(name);
        component.fieldSelectedName = 'moo';
        expect(component.fieldSelectedName).toBe('moo');

        expect(component.selectedIconName).toBe('standard:all');
        expect(component.queryNeedleType).toBe('String!');
        expect(component.required).toBe(false);
        expect(component.queryFields).toBe(DEFAULT_GQL_FIELDS);
        expect(component.queryWhere).toBe(DEFAULT_GQL_WHERE);
    });

    it('should have three items in the lookup list', async () => {
        const component = await createComponentUnderTest();

        document.body.appendChild(component);

        await resolvePromises();
        
        await graphql.emit(GQL_THREE_RESULTS);

        await flushPromises();

        const listOfLookupResults = component.shadowRoot.querySelectorAll('.lwc-lookup-item');

        expect(listOfLookupResults.length).toBe(3);
    });

    
    it('should have zero items in the lookup list', async () => {
        
        const component = await createComponentUnderTest();

        component.queryNeedle = '';

        document.body.appendChild(component);

        await resolvePromises();
        
        await graphql.emit();

        await flushPromises();

        const listOfLookupResults = component.shadowRoot.querySelectorAll('.lwc-lookup-item');

       expect(listOfLookupResults.length).toBe(0);
    });

    it('should fire onchange event within lightning input', async () => {
        
        const SEARCH_TERM = 'Carlos Hernandez';

        const component = await createComponentUnderTest();

        const handleKeyChange = jest.fn();

        document.body.appendChild(component);

        await resolvePromises();
        
        await graphql.emit(GQL_THREE_RESULTS);

        await flushPromises();

        const inputElement = component.shadowRoot.querySelector('lightning-input');

        inputElement.addEventListener('change', handleKeyChange);
        inputElement.value = SEARCH_TERM;
        inputElement.dispatchEvent(new CustomEvent('change', { 
            detail: { target: { value: SEARCH_TERM } },
            bubbles: true,
            composed: true 
        }));

        expect(handleKeyChange).toHaveBeenCalled();
    });


    it('should fire onfocus event within lightning input for a different field than Name', async () => {
        
        const SEARCH_TERM = '';

        const component = await createComponentUnderTestForTenant();

        const handleFocus = jest.fn();

        document.body.appendChild(component);

        await resolvePromises();
        
        await graphql.emit(GQL_ONE_RESULT_TENANT);

        await flushPromises();

        const inputElement = component.shadowRoot.querySelector('lightning-input');

        inputElement.addEventListener('focus', handleFocus);
        inputElement.value = SEARCH_TERM;
        inputElement.dispatchEvent(new CustomEvent('focus', { 
            detail: { target: { value: SEARCH_TERM } },
            bubbles: true,
            composed: true 
        }));

        expect(handleFocus).toHaveBeenCalled();
    });


    it('should fire click event on li elements', async () => {
        
        const SEARCH_TERM = 'Carlos Hernandez';

        const component = await createComponentUnderTest();
        component.runningTest = false;

        let cmpInstance = document.body.appendChild(component);

        const handleKeyChange = jest.fn();
        const handleSelect = jest.fn();
        const handleCommit = jest.fn();
        const mockEventHandler = jest.fn();
        

        await resolvePromises();
        
        await graphql.emit(GQL_ONE_RESULT);

        await flushPromises();

        const inputElement = cmpInstance.shadowRoot.querySelector('lightning-input');

        inputElement.addEventListener('change', handleKeyChange);
        inputElement.addEventListener(FlowAttributeChangeEventName, mockEventHandler);
        
        inputElement.value = SEARCH_TERM;
        inputElement.dispatchEvent(new CustomEvent('change', { 
            detail: { target: { value: SEARCH_TERM } },
            bubbles: true,
            composed: true 
        }));

        let listOfLookupResults = cmpInstance.shadowRoot.querySelectorAll('.lwc-lookup-item');

        expect(listOfLookupResults.length).toBe(1);
        
        const divClickeableElement = listOfLookupResults[0].firstChild;
        divClickeableElement.addEventListener('click', handleSelect);
        divClickeableElement.dispatchEvent(new CustomEvent('click', { 
            detail: { currentTarget: { dataset: { position: 0 } } },
            bubbles: true 
        }));

        return Promise.resolve().then(() => {
            cmpInstance = document.body.querySelector('c-generic-lookup-component');

            expect(handleKeyChange).toHaveBeenCalled();
            expect(handleSelect).toHaveBeenCalled();

            const valueSelectedElement = cmpInstance.shadowRoot.querySelector('.slds-pill_container');
            expect(valueSelectedElement).toBeTruthy();

            const selectedRecordNameElement = cmpInstance.shadowRoot.querySelector('.sf-c-pill');
            expect(selectedRecordNameElement).toBeTruthy();
            expect(selectedRecordNameElement.label).toBe("Carlos Hernandez");        
    
            selectedRecordNameElement.addEventListener('remove', handleCommit);
            selectedRecordNameElement.dispatchEvent(new CustomEvent('remove', {
                bubbles: true,
                composed: true 
            }));

            expect(handleCommit).toHaveBeenCalled();

            listOfLookupResults = cmpInstance.shadowRoot.querySelectorAll('.lwc-lookup-item');

            expect(listOfLookupResults.length).toBe(0);
        });
    });

    it('should handle blur event on parent div of ul', async () => {

        const component = await createComponentUnderTest();

        document.body.appendChild(component);

        const handleBlur = jest.fn();

        await resolvePromises();
        
        await graphql.emit(GQL_THREE_RESULTS);

        await flushPromises();

        const listbox = component.shadowRoot.querySelector('.slds-dropdown.slds-dropdown_length-with-icon-7.slds-dropdown_fluid');

        listbox.addEventListener('blur', handleBlur);
        listbox.dispatchEvent(new CustomEvent('blur', { 
            bubbles: true,
            composed: true 
        }));

        expect(handleBlur).toHaveBeenCalled();
    });


    it('should dispatch lookupselected event', async () => {

        const TEST_RECORD_ID = 'xxxxx';
        const TEST_NAME = 'Test';
        const TEST_FIELD_API_NAME = 'Test_Field';
        
        const component = await createComponentUnderTest();

        const cmpInstance = document.body.appendChild(component);

        const handleLookupSelected = jest.fn((e) => {
            expect(e.detail.id).toBe(TEST_RECORD_ID);
            expect(e.detail.name).toBe(TEST_NAME);
            expect(e.detail.field).toBe(TEST_FIELD_API_NAME);
            expect(e.detail.record.data).toBe(true);
        });

        await resolvePromises();
        
        await graphql.emit(GQL_THREE_RESULTS);

        await flushPromises();

        const eventPayload = {
            id: TEST_RECORD_ID,
            name: TEST_NAME,
            field: TEST_FIELD_API_NAME,
            record: { 
                data: true
             }
        };
    
        cmpInstance.addEventListener('lookupselected', handleLookupSelected);
        const event = new CustomEvent('lookupselected', { detail: eventPayload,bubbles: true,composed: true });
        cmpInstance.dispatchEvent(event);
    
        expect(handleLookupSelected).toHaveBeenCalled();
    });

    it('should show new record button', async () => {
        const component = await createComponentUnderTest();

        component.showAddNewButton = true;

        document.body.appendChild(component);

        await resolvePromises();
        
        await graphql.emit(GQL_THREE_RESULTS);

        await flushPromises();

        const listOfLookupResults = component.shadowRoot.querySelectorAll('.slds-listbox__item');

        expect(listOfLookupResults.length).toBe(5);
    });

    it('should hide new record button', async () => {
        const component = await createComponentUnderTest();

        document.body.appendChild(component);

        await resolvePromises();
        
        await graphql.emit(GQL_THREE_RESULTS);

        await flushPromises();

        const listOfLookupResults = component.shadowRoot.querySelectorAll('.slds-listbox__item');

        expect(listOfLookupResults.length).toBe(4);
    });

    it('should show up modal', async () => {
        const component = await createComponentUnderTest();

        component.showAddNewButton = true;
        component.isModalOpen = false;

        let cmpInstance = document.body.appendChild(component);

        const openModal = jest.fn();

        await resolvePromises();
        
        await graphql.emit(GQL_THREE_RESULTS);

        await flushPromises();

        const newRecordFeature = cmpInstance.shadowRoot.querySelector('.lwc-new-record');

        expect(newRecordFeature).toBeTruthy();

        const clickeableElement = newRecordFeature.querySelector('.slds-media');

        let modal = cmpInstance.shadowRoot.querySelector('.slds-modal');

        expect(modal).toBeNull();
        expect(cmpInstance.isModalOpen).toBe(false);
    
        clickeableElement.addEventListener('click', openModal);
        clickeableElement.dispatchEvent(new CustomEvent('click', { 
            bubbles: true 
        }));

        return Promise.resolve().then(() => {
            cmpInstance = document.body.querySelector('c-generic-lookup-component');
            modal = cmpInstance.shadowRoot.querySelector('.slds-modal');

            expect(openModal).toHaveBeenCalled();
            expect(modal).toBeTruthy();
        });
    });

    it('should handle click event on new record button', async () => {
        const component = await createComponentUnderTest();

        component.showAddNewButton = true;

        document.body.appendChild(component);

        await resolvePromises();

        await graphql.emit(GQL_THREE_RESULTS);

        await flushPromises();

        const newRecordButton = component.shadowRoot.querySelector('.sf-c-add-new');

        const handleClick = jest.fn();
        newRecordButton.addEventListener('click', handleClick);
        newRecordButton.dispatchEvent(new CustomEvent('click'));

        expect(handleClick).toHaveBeenCalled();
    });

    it('should handle click event on cancel button', async () => {
        const component = await createComponentUnderTest();

        component.showAddNewButton = true;
        component.isModalOpen = false;

        let cmpInstance = document.body.appendChild(component);

        const openModal = jest.fn();

        await resolvePromises();
        
        await graphql.emit(GQL_THREE_RESULTS);

        await flushPromises();

        const newRecordFeature = cmpInstance.shadowRoot.querySelector('.lwc-new-record');

        expect(newRecordFeature).toBeTruthy();

        const clickeableElement = newRecordFeature.querySelector('.slds-media');

        const modal = cmpInstance.shadowRoot.querySelector('.slds-modal');

        expect(modal).toBeNull();
        expect(cmpInstance.isModalOpen).toBe(false);
    
        clickeableElement.addEventListener('click', openModal);
        clickeableElement.dispatchEvent(new CustomEvent('click', { 
            bubbles: true 
        }));

        return Promise.resolve().then(() => {
            cmpInstance = document.body.querySelector('c-generic-lookup-component');
            
            const cancelButton = cmpInstance.shadowRoot.querySelector('.slds-modal__close');

            const handleClick = jest.fn();
            cancelButton.addEventListener('click', handleClick);
            cancelButton.dispatchEvent(new CustomEvent('click', { 
                bubbles: true 
            }));

            expect(handleClick).toHaveBeenCalled();
        });
    });
});