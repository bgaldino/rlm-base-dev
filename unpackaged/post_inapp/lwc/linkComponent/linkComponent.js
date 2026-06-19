import { LightningElement, api } from 'lwc';

export default class LinkComponent extends LightningElement {
    @api linkUrl;
    @api linkText;
}
