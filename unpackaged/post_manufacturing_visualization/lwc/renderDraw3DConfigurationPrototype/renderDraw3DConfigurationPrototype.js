import { api, LightningElement, track, wire } from 'lwc';
import { subscribe, MessageContext, unsubscribe, publish } from "lightning/messageService";
import { loadStyle, loadScript } from "lightning/platformResourceLoader";
import revenuecloudRenderDrawStyling from "@salesforce/resourceUrl/revenuecloudRenderDrawStyling";
import NotificationMessageChannel from '@salesforce/messageChannel/lightning__productConfigurator_notification';
// import REVENUE_TRANSACTIONNOTIFICATION_CHANNEL from '@salesforce/messageChannel/revenue_transactionNotification';
import getAttributeForId from "@salesforce/apex/UTIL_ConfigHelper.getAttributeForId";
import getChildProductForRelatedComponentId from "@salesforce/apex/UTIL_ConfigHelper.getChildProductForRelatedComponentId"
import getPicklistValuesForPicklistId from "@salesforce/apex/UTIL_ConfigHelper.getPicklistValuesForPicklistId";
export default class RenderDraw3DConfigurationPrototype extends LightningElement {
    vfOrigin;
    @track _configuratorContext = null;
    @track _optionGroups = [];
    @api get optionGroups() {
        return this._optionGroups;
    }
    set optionGroups(value) {
        this._optionGroups = value;
    }
    @track debug = false;

    @api
    get configuratorContext() {
        return this._configuratorContext;
    }
    set configuratorContext(value) {
        if (value) {
            this.existingConfigurationContext = this._configuratorContext
            this._configuratorContext = value;
            debugger;
            // this.parseChanges();
        }
    }
    @track _salesTransactionItems = [];
    @api
    get salesTransactionItems() {
        return this._salesTransactionItems;
    }
    set salesTransactionItems(value) {
        debugger;
        this._salesTransactionItems = value;
    }

    @track existingConfigurationContext = null;
    @track attributePicklists = [];

    async connectedCallback() {
        // await loadStyle(this, revenuecloudRenderDrawStyling);

        this.susbscribeToChannels();

        // Get the Visualforce origin
        this.vfOrigin = `${window.location.protocol}//${window.location.hostname}`;

        // Add message listener for iframe communication
        window.addEventListener('message', this.handleMessage.bind(this));
    }
    @track isExpanded = false;
    @track activeSectionName = "visualization-section"
    get componentClass() {
        return this.isExpanded ? "render-draw-3d-config open" : "render-draw-3d-config closed"
    }
    get visualizationSectionClass() {
        return this.isExpanded ? "visualization-section open" : "visualization-section closed"
    }
    handleAccordionSectionToggle(event) {
        this.isExpanded = !this.isExpanded
    }
    @wire(MessageContext)
    messageContext;
    recordFieldCompletionActivationChannel = null;
    revenueTransactionNotificationActivationChannel = null;
    susbscribeToChannels() {
        if (!this.recordFieldCompletionActivationChannel) {
            this.recordFieldCompletionActivationChannel = subscribe(this.messageContext, NotificationMessageChannel, (message) =>
                this.handleRecordFieldCompletionInteractionMessage(message)
            );
        }
        // if (!this.revenueTransactionNotificationActivationChannel) {
        //     this.revenueTransactionNotificationActivationChannel = subscribe(this.messageContext, REVENUE_TRANSACTIONNOTIFICATION_CHANNEL, (message) =>
        //         this.handleRevenueTransactionNotificationActivationChannelMessage(message)
        //     );
        // }
    }
    unsubscribeToChannels() {
        unsubscribe(this.recordSelectedSubscription);
        this.recordSelectedSubscription = null;
    }
    unsubscribeFromMessageChannels() {
        // RecordSelected
        unsubscribe(this.recordSelectedSubscription);
        this.recordSelectedSubscription = null;
        //Others
    }
    disconnectedCallback() {
        window.removeEventListener('message', this.handleMessage.bind(this));
    }
    async updateVisualLogicForAttribute(attributeId, value, keyvalues) {
        // if (this.renderer) {
        let attribute = await getAttributeForId({ Id: attributeId });
        if (attribute.DataType == "Picklist") {
            let picklistValues = await getPicklistValuesForPicklistId({ Id: attribute.PicklistId });
            let val = picklistValues.find(pv => pv.Id == value);
            if (val) {
                this.template.querySelector("RDraw-canvas3-d").raiseInteractionEvent(attribute.Name, "change", attribute.Name, val.DisplayValue, keyvalues);
            }

        }
        else {
            let val = null;
            if (attribute) {
                if (attribute.DataType == "Number")
                    val = parseFloat(value);
            }
            if (val == null)
                val = value;
            this.raiseInteractionEvent(attribute.Name, val, keyvalues)
            //this is a direct attribute, with text input
        }
        // }
    }
    async updateVisualLogicForProductRelatedComponent(productRelatedComponentId, value, keyvalues) {
        // if (this.renderer) {
        debugger;
        let relatedChildComponentProduct = await getChildProductForRelatedComponentId({ Id: productRelatedComponentId });
        if (relatedChildComponentProduct) {
            if (!keyvalues) {
                keyvalues = [];
            } else {
                keyvalues = JSON.parse(JSON.stringify(keyvalues));
            }
            keyvalues.push({ key: "Id", value: relatedChildComponentProduct.Id });
            keyvalues.push({ key: "ProductCode", value: relatedChildComponentProduct.ProductCode });
            this.raiseInteractionEvent(relatedChildComponentProduct.ProductCode, value, keyvalues);
            // this.template.querySelector("RDraw-canvas3-d").raiseInteractionEvent(relatedChildComponentProduct.Name, "change", relatedChildComponentProduct.Name, value, keyvalues);
        }
        // }
    }
    raiseInteractionEvent(productCode, value, keyvalues) {
        if (productCode.includes('FESBA_S1ENC')) {
            this.handleToggleMeshByName('NAUO13_primitive0', value);
            this.setCameraPositionAndAim(this.targetList.initial.position, this.targetList.initial.target);

        }
        else if (productCode.includes('FESBA_B225-2') && value == true) {
            this.setCameraPositionAndAim(this.targetList.tempSensor.position, this.targetList.tempSensor.target);
            this.sendMessageToFrame('loadTempSensorModel')
        }
        else if (productCode.includes('FESBA_B225-2') && value == false) {
            this.sendMessageToFrame('hideTempSensorModel')
            this.setCameraPositionAndAim(this.targetList.initial.position, this.targetList.initial.target);
        } else if (productCode.includes("max dB level")) {
            if (value < 90) {
                this.handleToggleMeshByName('NAUO13_primitive0', true);
                this.setCameraPositionAndAim(this.targetList.initial.position, this.targetList.initial.target);
            } else {
                this.handleToggleMeshByName('NAUO13_primitive0', false);
                this.setCameraPositionAndAim(this.targetList.initial.position, this.targetList.initial.target);
            }

        }


    }
    handleMessage(event) {
        // Verify the message origin
        // if (event.origin !== this.vfOrigin) return;
        const message = event.data;
        switch (message.name) {
            case 'sceneInitialized':
                this.handleSceneInitialized();
                break;
            case 'initialModelLoaded':
                this.setCameraPositionAndAim(this.targetList.initial.position, this.targetList.initial.target);
                this.handleToggleMeshByName('NAUO13_primitive0', false);
                break;
            case 'getCameraPositionandTarget':
                console.log('got camera Position & aim:');
                console.log(message.payload);
                break;
            // Add other message handlers as needed
        }
    }
    async handleRecordFieldCompletionInteractionMessage(message) {
        try {
            let mess = JSON.parse(JSON.stringify(message));
            console.log('receivedFieldCompletionInteractionMessage: ' + mess.action);
            if (mess.action == "valueChanged") {
                for (let i = 0; i < message.data.length; i++) {
                    let data = message.data[i];
                    if (data.field == "AttributeField") {
                        await this.updateVisualLogicForAttribute(data.attributeId, data.value, data.key);
                    } else if (data.field == "isSelected") {
                        if (data.productRelatedComponentId)
                            await this.updateVisualLogicForProductRelatedComponent(data.productRelatedComponentId, data.value, data.key)
                    }
                }
            }
        } catch (error) {
            console.error("An error occurred while handling the canvas interaction message:", error);
        }
    }
    handleRevenueTransactionNotificationActivationChannelMessage(message) {
        try {
            debugger;
        } catch (error) {
            console.error("An error occurred while handling the canvas interaction message:", error);
        }
    }
    handleSceneInitialized() {
        // Scene is ready, you can now send commands
        this.loadInitialModel();


    }
    loadInitialModel() {
        let url = "https://files.renderdraw.us/public/demoassets/generator.glb";
        let position = { x: 0, y: 1, z: 0 };
        this.loadModel(url, position);
    }
    loadModel(url, position) {
        let parameter = {
            url: url,
            position: position
        }
        this.sendMessageToFrame('loadModel', parameter);
    }

    addCube() {
        this.sendMessageToFrame('addCube');
    }
    sendMessageToFrame(messagetype, parameter) {
        const iframe = this.template.querySelector('iframe');
        iframe.contentWindow.postMessage({
            type: messagetype,
            parameter: { ...parameter }
        }, '*');
    }
    getCameraPosition() {
        this.sendMessageToFrame('getCameraPositionAndAim');
    }
    setCameraPositionAndAim(position, aim) {
        let parameter = { position: position, target: aim };
        this.sendMessageToFrame('setCameraPositionAndAim', parameter);
    }

    @track tempSensorLoaded = false;

    handleTriggerTempSensor() {
        if (!this.tempSensorLoaded) {
            this.setCameraPositionAndAim(this.targetList.tempSensor.position, this.targetList.tempSensor.target);
            this.sendMessageToFrame('loadTempSensorModel')
        } else {
            this.sendMessageToFrame('hideTempSensorModel')
            this.setCameraPositionAndAim(this.targetList.initial.position, this.targetList.initial.target);
        }
        this.tempSensorLoaded = !this.tempSensorLoaded;
    }
    targetList = {
        initial: {
            position: { x: -1.355, y: 2.131, z: -1.443, alpha: -139.806, beta: 48.686 },
            target: { x: 0.096, y: 0.461, z: -0.217 }
        },
        tempSensor: {
            position: { x: -1.233, y: 0.697, z: -0.238, alpha: -179.233, beta: 84.849 },
            target: { x: 0.106, y: 0.577, z: -0.22 }
        }
    }
    handleToggleMeshByName(name, isEnabled) {
        let parameter = {
            name: name,
            enabled: isEnabled
        };
        this.sendMessageToFrame('toggleMeshByName', parameter)
    }
    handleToggleDebugMode() {
        this.sendMessageToFrame('enableSceneDebugger');
    }
}