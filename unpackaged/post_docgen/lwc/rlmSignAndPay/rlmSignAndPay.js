import { LightningElement, api } from 'lwc';
import { FlowAttributeChangeEvent, FlowNavigationFinishEvent } from 'lightning/flowSupport';
import { NavigationMixin } from 'lightning/navigation';
import loadContext from '@salesforce/apex/RLM_SignAndPay.loadContext';
import accept from '@salesforce/apex/RLM_SignAndPay.accept';

/** Same Create Order screen flow the Quote highlight "Create Order" button runs. */
const CREATE_ORDERS_FLOW = 'RLM_CreateOrdersFromQuote';

export default class RlmSignAndPay extends NavigationMixin(LightningElement) {
    @api quoteId;
    @api contentDocumentId;
    @api documentTitle;

    _accepted = false;
    _signerName = '';
    _cardLast4 = '';
    _message = '';

    accountName;
    quoteNumber;
    grandTotal;
    currencyIsoCode = 'USD';
    proposalTitle;
    proposalDocId;
    loading = true;
    submitting = false;
    error;
    alreadySigned = false;
    signedBy;
    signedAt;
    onFileLast4;
    onFileBrand;
    /** 'onfile' = choose saved card, 'entry' = card + signature form, 'done' = accepted */
    mode = 'entry';

    cardName = '';
    cardNumber = '';
    cardExp = '';
    cardCvc = '';
    cardBrand = 'Visa';
    drawing = false;

    @api
    get accepted() {
        return this._accepted;
    }
    set accepted(v) {
        this._accepted = !!v;
    }

    @api
    get signerName() {
        return this._signerName;
    }
    set signerName(v) {
        if (v) this._signerName = v;
    }

    @api
    get cardLast4() {
        return this._cardLast4;
    }
    set cardLast4(v) {
        if (v) this._cardLast4 = v;
    }

    @api
    get message() {
        return this._message;
    }
    set message(v) {
        if (v) this._message = v;
    }

    connectedCallback() {
        this.refresh();
    }

    renderedCallback() {
        this.sizeCanvas();
    }

    get totalLabel() {
        if (this.grandTotal == null) return '';
        try {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: this.currencyIsoCode || 'USD'
            }).format(this.grandTotal);
        } catch (e) {
            return `${this.currencyIsoCode} ${this.grandTotal}`;
        }
    }

    get hasProposal() {
        return !!this.proposalDocId;
    }

    get shellClass() {
        return this._accepted ? 'shell done' : 'shell';
    }

    get submitDisabled() {
        return this.submitting || this.isDone || !this.hasProposal;
    }

    get isOnFile() {
        return this.mode === 'onfile';
    }

    get isEntry() {
        return this.mode === 'entry';
    }

    get isDone() {
        return this.mode === 'done';
    }

    get hasCardOnFile() {
        return !!this.onFileLast4;
    }

    get onFileMasked() {
        return `•••• •••• •••• ${this.onFileLast4}`;
    }

    get onFileSignedLabel() {
        if (!this.signedAt) return this.signedBy ? `Signed by ${this.signedBy}` : '';
        const when = new Date(this.signedAt).toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit'
        });
        return `Signed by ${this.signedBy} · ${when}`;
    }

    get entryTitle() {
        return this.hasCardOnFile ? 'Add another payment method' : 'Card on file';
    }

    get entrySubtitle() {
        return this.hasCardOnFile
            ? `Replaces ${this.onFileBrand || 'card'} •••• ${this.onFileLast4} as the card on this quote. Mock entry only.`
            : 'Mock entry only — nothing is charged or tokenized.';
    }

    async refresh() {
        this.loading = true;
        this.error = undefined;
        try {
            const ctx = await loadContext({
                quoteId: this.quoteId,
                contentDocumentId: this.contentDocumentId || null
            });
            this.accountName = ctx.accountName;
            this.quoteNumber = ctx.quoteNumber;
            this.grandTotal = ctx.grandTotal;
            this.currencyIsoCode = ctx.currencyIsoCode || 'USD';
            this.alreadySigned = ctx.alreadySigned;
            this.signedBy = ctx.signedBy;
            this.signedAt = ctx.signedAt;
            this.onFileLast4 = ctx.cardLast4;
            this.onFileBrand = ctx.cardBrand;
            if (ctx.proposal) {
                this.proposalDocId = ctx.proposal.contentDocumentId;
                this.proposalTitle = this.documentTitle || ctx.proposal.title;
            } else {
                this.proposalDocId = this.contentDocumentId || null;
                this.proposalTitle = this.documentTitle || null;
            }
            if (!this._signerName && this.accountName) {
                this._signerName = this.accountName;
                this.cardName = this.accountName;
            }
            this.mode = this.alreadySigned && this.onFileLast4 ? 'onfile' : 'entry';
        } catch (e) {
            this.error = e?.body?.message || e?.message || 'Unable to load quote context.';
        } finally {
            this.loading = false;
        }
    }

    handleSigner(event) {
        this._signerName = event.target.value;
        this.cardName = this._signerName;
        this.emit('signerName', this._signerName);
    }

    handleCardName(event) {
        this.cardName = event.target.value;
    }

    handleCardNumber(event) {
        const digits = (event.target.value || '').replace(/\D/g, '').slice(0, 16);
        this.cardNumber = digits.replace(/(\d{4})(?=\d)/g, '$1 ').trim();
        this._cardLast4 = digits.slice(-4);
        this.cardBrand = digits.startsWith('4')
            ? 'Visa'
            : digits.startsWith('5')
              ? 'Mastercard'
              : digits.startsWith('3')
                ? 'Amex'
                : 'Card';
        this.emit('cardLast4', this._cardLast4);
    }

    handleExp(event) {
        let v = (event.target.value || '').replace(/[^\d]/g, '').slice(0, 4);
        if (v.length > 2) v = `${v.slice(0, 2)}/${v.slice(2)}`;
        this.cardExp = v;
    }

    handleCvc(event) {
        this.cardCvc = (event.target.value || '').replace(/\D/g, '').slice(0, 4);
    }

    sizeCanvas() {
        const canvas = this.template.querySelector('canvas.sig');
        if (!canvas) return;
        const parent = canvas.parentElement;
        const width = Math.max(280, parent.clientWidth - 2);
        if (canvas.width !== width) {
            canvas.width = width;
            canvas.height = 140;
            this.clearSignature();
        }
    }

    pointerPos(event) {
        const canvas = this.template.querySelector('canvas.sig');
        const rect = canvas.getBoundingClientRect();
        const src = event.touches ? event.touches[0] : event;
        return {
            x: ((src.clientX - rect.left) / rect.width) * canvas.width,
            y: ((src.clientY - rect.top) / rect.height) * canvas.height
        };
    }

    startDraw(event) {
        event.preventDefault();
        this.drawing = true;
        const canvas = this.template.querySelector('canvas.sig');
        const ctx = canvas.getContext('2d');
        const p = this.pointerPos(event);
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
    }

    draw(event) {
        if (!this.drawing) return;
        event.preventDefault();
        const canvas = this.template.querySelector('canvas.sig');
        const ctx = canvas.getContext('2d');
        const p = this.pointerPos(event);
        ctx.lineWidth = 2.2;
        ctx.lineCap = 'round';
        ctx.strokeStyle = '#14241a';
        ctx.lineTo(p.x, p.y);
        ctx.stroke();
    }

    endDraw() {
        this.drawing = false;
    }

    handleClearSignature() {
        this.clearSignature();
    }

    clearSignature() {
        const canvas = this.template.querySelector('canvas.sig');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#f7fbf8';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.strokeStyle = '#d7e2db';
        ctx.beginPath();
        ctx.moveTo(24, canvas.height - 28);
        ctx.lineTo(canvas.width - 24, canvas.height - 28);
        ctx.stroke();
    }

    autofillDemo() {
        this._signerName = this.accountName || 'Michael Reyes';
        this.cardName = this._signerName;
        this.cardNumber = '4242 4242 4242 4242';
        this._cardLast4 = '4242';
        this.cardBrand = 'Visa';
        this.cardExp = '12/28';
        this.cardCvc = '123';
        this.emit('signerName', this._signerName);
        this.emit('cardLast4', this._cardLast4);
        // stylized signature scribble
        const canvas = this.template.querySelector('canvas.sig');
        if (!canvas) return;
        this.clearSignature();
        const ctx = canvas.getContext('2d');
        ctx.strokeStyle = '#14241a';
        ctx.lineWidth = 2.4;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(40, 90);
        ctx.bezierCurveTo(80, 40, 140, 120, 200, 70);
        ctx.bezierCurveTo(240, 40, 280, 100, 340, 65);
        ctx.stroke();
        ctx.font = '16px "Segoe Script", "Brush Script MT", cursive';
        ctx.fillStyle = '#14241a';
        ctx.fillText(this._signerName, 40, 50);
    }

    openDocument() {
        if (!this.proposalDocId) return;
        this[NavigationMixin.Navigate]({
            type: 'standard__namedPage',
            attributes: { pageName: 'filePreview' },
            state: { selectedRecordId: this.proposalDocId }
        });
    }

    emit(name, value) {
        this.dispatchEvent(new FlowAttributeChangeEvent(name, value));
    }

    emitOutputs() {
        this.emit('accepted', this._accepted);
        this.emit('signerName', this._signerName);
        this.emit('cardLast4', this._cardLast4);
        this.emit('message', this._message);
    }

    @api
    validate() {
        // Allow Finish without signing so Create Proposal can exit after preview.
        return { isValid: true };
    }

    async handleAccept() {
        this.error = undefined;
        const digits = (this.cardNumber || '').replace(/\D/g, '');
        if (!this._signerName || digits.length < 12 || !this.cardExp || !this.cardCvc) {
            this.error = 'Enter signer name and a complete demo card (use Autofill demo if needed).';
            return;
        }
        if (!this.proposalDocId) {
            this.error = 'No proposal document on this quote. Run Create Proposal first.';
            return;
        }
        this.submitting = true;
        try {
            const res = await accept({
                quoteId: this.quoteId,
                contentDocumentId: this.proposalDocId,
                signerName: this._signerName,
                cardLast4: digits.slice(-4),
                cardBrand: this.cardBrand
            });
            if (!res.success) {
                this.error = res.message;
                return;
            }
            this._cardLast4 = digits.slice(-4);
            this.onFileLast4 = this._cardLast4;
            this.onFileBrand = this.cardBrand;
            this.signedBy = this._signerName;
            this.signedAt = new Date().toISOString();
            this.completeAndOrder(`${res.message} Opening Create Order…`);
        } catch (e) {
            this.error = e?.body?.message || e?.message || 'Unable to record acceptance.';
        } finally {
            this.submitting = false;
        }
    }

    handleUseCardOnFile() {
        this._signerName = this.signedBy || this._signerName;
        this._cardLast4 = this.onFileLast4;
        this.completeAndOrder(
            `Using ${this.onFileBrand || 'card'} •••• ${this.onFileLast4} on file. Opening Create Order…`
        );
    }

    handleAddAnother() {
        this.error = undefined;
        this.cardNumber = '';
        this.cardExp = '';
        this.cardCvc = '';
        this.cardBrand = 'Visa';
        this.cardName = this.signedBy || this._signerName || this.accountName || '';
        this._signerName = this.cardName;
        this.mode = 'entry';
    }

    handleBackToOnFile() {
        this.error = undefined;
        this.mode = 'onfile';
    }

    completeAndOrder(message) {
        this._accepted = true;
        this._message = message;
        this.mode = 'done';
        this.emitOutputs();
        // Close this flow screen, then open the same Create Order UI as the Quote button.
        // eslint-disable-next-line @lwc/lwc/no-async-operation
        setTimeout(() => {
            this.dispatchEvent(new FlowNavigationFinishEvent());
            this.openCreateOrder();
        }, 350);
    }

    openCreateOrder() {
        if (!this.quoteId) return;
        const url = `/flow/${CREATE_ORDERS_FLOW}?quoteId=${encodeURIComponent(this.quoteId)}`;
        this[NavigationMixin.Navigate]({
            type: 'standard__webPage',
            attributes: { url }
        });
    }

    handleCreateOrderClick() {
        this.openCreateOrder();
    }
}
