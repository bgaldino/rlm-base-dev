import { LightningElement, api } from 'lwc';

const PREVIEW_HEIGHT = '100%';
const STYLE_ID = 'rlm-doc-preview-height-fix';

// Module-level reference count — tracks how many instances are currently
// mounted. The style tag is injected on the first mount and removed only
// when the last instance disconnects, preventing one instance from tearing
// down the shared style while sibling instances are still visible.
let _instanceCount = 0;

export default class RlmDocPreview extends LightningElement {
    @api fileId;
    @api contentDocumentId;

    connectedCallback() {
        _instanceCount += 1;
        // LWS security prevents shadowRoot access across namespaces from LWC JS.
        // community_content-file-previewer (the inner renderer) uses LWC synthetic
        // shadow, so global CSS rules DO reach its internal elements. Inject once,
        // guarded by id, so repeated flow renders don't duplicate the style tag.
        // eslint-disable-next-line @lwc/lwc/no-document-query
        if (!document.getElementById(STYLE_ID)) {
            // eslint-disable-next-line @lwc/lwc/no-document-query
            const style = document.createElement('style');
            style.id = STYLE_ID;
            style.textContent =
                `community_content-file-previewer .bodyContainer { height: ${PREVIEW_HEIGHT} !important; }`;
            // eslint-disable-next-line @lwc/lwc/no-document-query
            document.head.appendChild(style);
        }
    }

    disconnectedCallback() {
        _instanceCount -= 1;
        // Only remove the shared style when the last instance leaves the DOM,
        // so it does not persist and affect file previewers on other pages in
        // the same SPA session.
        if (_instanceCount <= 0) {
            _instanceCount = 0;
            // eslint-disable-next-line @lwc/lwc/no-document-query
            const style = document.getElementById(STYLE_ID);
            if (style) {
                style.remove();
            }
        }
    }
}
