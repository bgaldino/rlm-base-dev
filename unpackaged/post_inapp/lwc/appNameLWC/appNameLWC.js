import { LightningElement,track, wire } from 'lwc';
import { CurrentPageReference } from 'lightning/navigation';
export default class AppNameLWC extends LightningElement {

    @track appData={};
    @track dataLoaded
   
    @wire(CurrentPageReference) 
    getStateParameters(currentPageReference) {
        if (currentPageReference) {
           this.appNameValue = currentPageReference.state?.c__appName;
           //console.log('inside connectedCallback for AppNameLWC for application == ' + this.appNameValue);

           for(var i=0;i<this.data.length;i++){
            if(this.data[i].Name===this.appNameValue)
                {
                    this.appData.Name = this.appNameValue;
                    this.appData.Type = this.data[i].details.Type;
                    this.dataLoaded = true
                    //console.log(JSON.stringify(this.appData));
                }

           }
        }
     }


    data=[
        {
            "Id":"1",
            "Name":"Contact Center Console",
            "details":{
                "Type":"Business Applicaton",
            } 
        },
        {
            "Id":"2",
            "Name":"Self Serve Portal",
            "details":{
                "Type":"Business Applicaton",
            } 
        },
        {
            "Id":"3",
            "Name":"Short Cycle Work",
            "details":{
                "Type":"Business Applicaton",
            } 
        },
        {
            "Id":"4",
            "Name":"Contractor Portal",
            "details":{
                "Type":"Business Applicaton",
            } 
        },
        {
            "Id":"5",
            "Name":"Program Management Console",
            "details":{
                "Type":"Business Applicaton",
            } 
        }
    ];
   


}