import { LightningElement, track } from 'lwc';

export default class Tags extends LightningElement {

    @track appData
    @track dataLoaded
    connectedCallback() {
        //console.log('inside connectedCallback');
        this.appData=[
            {
                "Id":"1",
                "Name":"Platform"
            },
            {
                "Id":"2",
                "Name":"Data Cloud"
            },
            {
                "Id":"3",
                "Name":"Sales Cloud"
            },
            {
                "Id":"4",
                "Name":"Service Cloud"
            },
            {
                "Id":"5",
                "Name":"Salesforce Field Service"
            }
        ];
        // //console.log('ending connectedCallback  ' + JSON.stringify(this.appData));
        this.dataLoaded = true
      }
}