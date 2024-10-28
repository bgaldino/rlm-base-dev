import { LightningElement, api } from 'lwc';

export default class GenericRecordPicker extends LightningElement {

    @api objectName;
    @api objectLabel;
    @api displayinfoparam;
    @api matchinginfoparam;
    @api filterparam;
    @api pickerLabel;
    @api pickerLabelVariant;
    @api placeholder;

    _currentSelectedRecordId;

    @api
    get currentSelectedRecordId() {
        return this._currentSelectedRecordId;
    }

    set currentSelectedRecordId(value) {
        this._currentSelectedRecordId = value;
    }

    handleRecordSelect(event) {
        this._currentSelectedRecordId = event.detail.recordId;
    }
}