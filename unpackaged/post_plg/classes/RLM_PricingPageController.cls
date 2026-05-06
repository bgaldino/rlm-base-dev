public without sharing class RLM_PricingPageController {

    public RLM_PricingPageController() {}

    private static Boolean isGuestContext() {
        return UserInfo.getUserType() == 'Guest' || Site.getSiteId() != null;
    }

    // ── Register (Create Account) ─────────────────────────────────
    @RemoteAction
    public static Map<String, Object> registerUser(
            String firstName, String lastName, String email,
            String password, String company) {

        Map<String, Object> result = new Map<String, Object>();
        try {
            List<Contact> existing = [
                SELECT Id FROM Contact WHERE Email = :email LIMIT 1
            ];
            if (!existing.isEmpty()) {
                result.put('success', false);
                result.put('message', 'An account with this email already exists. Please log in instead.');
                return result;
            }

            Account acct = findOrCreateAccount(company);

            Contact con = new Contact(
                FirstName      = firstName,
                LastName       = lastName,
                Email          = email,
                AccountId      = acct.Id,
                RLM_Password_Hash__c = hashPassword(password)
            );
            insert con;

            result.put('success', true);
            result.put('message', 'Account created successfully!');
            result.put('contactId', con.Id);
            result.put('accountId', acct.Id);
            result.put('firstName', firstName);
            result.put('lastName', lastName);
            result.put('email', email);
            result.put('company', company);
        } catch (Exception e) {
            result.put('success', false);
            result.put('message', 'Registration error: ' + e.getMessage());
        }
        return result;
    }

    // ── Login ─────────────────────────────────────────────────────
    @RemoteAction
    public static Map<String, Object> loginUser(String email, String password) {
        Map<String, Object> result = new Map<String, Object>();
        try {
            List<Contact> contacts = [
                SELECT Id, FirstName, LastName, Email, AccountId,
                       Account.Name, RLM_Password_Hash__c
                FROM Contact WHERE Email = :email LIMIT 1
            ];

            if (contacts.isEmpty()) {
                result.put('success', false);
                result.put('message', 'No account found with this email. Please create an account first.');
                return result;
            }

            Contact con = contacts[0];
            if (con.RLM_Password_Hash__c == null || con.RLM_Password_Hash__c != hashPassword(password)) {
                result.put('success', false);
                result.put('message', 'Invalid email or password. Please try again.');
                return result;
            }

            result.put('success', true);
            result.put('message', 'Welcome back, ' + con.FirstName + '!');
            result.put('contactId', con.Id);
            result.put('accountId', con.AccountId);
            result.put('firstName', con.FirstName);
            result.put('lastName', con.LastName);
            result.put('email', con.Email);
            result.put('company', con.Account != null ? con.Account.Name : '');
        } catch (Exception e) {
            result.put('success', false);
            result.put('message', 'Login error: ' + e.getMessage());
        }
        return result;
    }

    // ── Free Trial ────────────────────────────────────────────────
    @RemoteAction
    public static Map<String, Object> startFreeTrial(
            String firstName, String lastName, String email,
            String company, String selectedPlan) {

        Map<String, Object> result = new Map<String, Object>();
        try {
            if (isGuestContext()) {
                return startFreeTrialDirect(firstName, lastName, email, company, selectedPlan);
            }

            Map<String, Object> flowInputs = new Map<String, Object>{
                'firstName'    => firstName,
                'lastName'     => lastName,
                'email'        => email,
                'companyName'  => company,
                'selectedPlan' => selectedPlan
            };

            Flow.Interview flow = Flow.Interview.createInterview('RLM_Start_Free_Trial', flowInputs);
            flow.start();

            result.put('success', true);
            result.put('message', 'Your 14-day free trial has been activated!');
            result.put('transactionId', flow.getVariableValue('transactionId'));
        } catch (Exception e) {
            result.put('success', false);
            result.put('message', 'Error starting trial: ' + e.getMessage());
        }
        return result;
    }

    private static Map<String, Object> startFreeTrialDirect(
            String firstName, String lastName, String email,
            String company, String selectedPlan) {

        Map<String, Object> result = new Map<String, Object>();

        Account acct = findOrCreateAccount(company);
        findOrCreateContact(firstName, lastName, email, acct.Id);

        String txnId = null;
        try {
            Map<String, Object> txnRequest = new Map<String, Object>{
                'transactionType' => 'NewSale',
                'accountId'       => acct.Id,
                'pricingFlow'     => 'GET_PRICE',
                'lineItems'       => new List<Map<String, Object>>{
                    new Map<String, Object>{
                        'productName' => selectedPlan,
                        'quantity'    => 1
                    }
                }
            };
            Map<String, Object> txnResult = RLM_RevenueCloudService.placeSalesTransaction(txnRequest);
            txnId = (String) txnResult.get('id');
        } catch (Exception e) {
            System.debug(LoggingLevel.WARN, 'RLM callout skipped in guest context: ' + e.getMessage());
        }

        result.put('success', true);
        result.put('message', 'Your 14-day free trial has been activated! Check your email at ' + email + ' for next steps.');
        result.put('transactionId', txnId);
        result.put('accountId', acct.Id);
        return result;
    }

    // ── Request Quote / Contact Sales ─────────────────────────────
    @RemoteAction
    public static Map<String, Object> requestQuote(
            String firstName, String lastName, String email,
            String company, String phone, String selectedPlan,
            Integer seats, String message) {

        Map<String, Object> result = new Map<String, Object>();
        try {
            if (isGuestContext()) {
                return requestQuoteDirect(firstName, lastName, email, company, phone, selectedPlan, seats, message);
            }

            Map<String, Object> flowInputs = new Map<String, Object>{
                'firstName'    => firstName,
                'lastName'     => lastName,
                'email'        => email,
                'companyName'  => company,
                'phone'        => phone,
                'selectedPlan' => selectedPlan,
                'seats'        => seats != null ? seats : 1,
                'message'      => message
            };

            Flow.Interview flow = Flow.Interview.createInterview('RLM_Request_Quote', flowInputs);
            flow.start();

            result.put('success', true);
            result.put('message',
                'Your quote request has been submitted! A sales representative will contact you within 24 hours.');
            result.put('quoteNumber', flow.getVariableValue('quoteNumber'));
            result.put('opportunityId', flow.getVariableValue('opportunityId'));
        } catch (Exception e) {
            result.put('success', false);
            result.put('message', 'Error requesting quote: ' + e.getMessage());
        }
        return result;
    }

    private static Map<String, Object> requestQuoteDirect(
            String firstName, String lastName, String email,
            String company, String phone, String selectedPlan,
            Integer seats, String message) {

        Map<String, Object> result = new Map<String, Object>();
        Integer qty = seats != null ? seats : 1;

        Account acct = findOrCreateAccount(company);
        if (String.isNotBlank(phone) && acct.Phone == null) {
            acct.Phone = phone;
            update acct;
        }

        Contact con = findOrCreateContact(firstName, lastName, email, acct.Id);
        if (String.isNotBlank(phone) && con.Phone == null) {
            con.Phone = phone;
            update con;
        }

        Opportunity opp = new Opportunity(
            Name        = company + ' - ' + selectedPlan + ' Quote',
            AccountId   = acct.Id,
            StageName   = 'Proposal/Price Quote',
            CloseDate   = Date.today().addDays(30),
            Description = 'Plan: ' + selectedPlan
                + '\nSeats: ' + qty
                + '\n\n' + (String.isNotBlank(message) ? message : '')
        );
        insert opp;

        // ── Create Revenue Cloud Quote + Line Item ──
        String quoteNumber;
        try {
            String planSku = getPlanSku(selectedPlan);
            List<Product2> products = new List<Product2>();
            if (String.isNotBlank(planSku)) {
                products = [
                    SELECT Id, Name FROM Product2
                    WHERE StockKeepingUnit = :planSku AND IsActive = true LIMIT 1
                ];
            }
            if (products.isEmpty()) {
                String productSearch = 'NovaSpark ' + selectedPlan + '%';
                products = [
                    SELECT Id, Name FROM Product2
                    WHERE Name LIKE :productSearch AND IsActive = true LIMIT 1
                ];
            }
            Id stdPbId = [SELECT Id FROM Pricebook2 WHERE IsStandard = true LIMIT 1].Id;

            Quote q = new Quote(
                Name            = company + ' - NovaSpark ' + selectedPlan,
                OpportunityId   = opp.Id,
                ContactId       = con.Id,
                Pricebook2Id    = stdPbId,
                Status          = 'Draft',
                ExpirationDate  = Date.today().addDays(14)
            );
            insert q;

            quoteNumber = [SELECT QuoteNumber FROM Quote WHERE Id = :q.Id].QuoteNumber;

            if (!products.isEmpty()) {
                List<PricebookEntry> pbes = [
                    SELECT Id, UnitPrice FROM PricebookEntry
                    WHERE Product2Id = :products[0].Id AND Pricebook2Id = :stdPbId AND IsActive = true LIMIT 1
                ];
                if (!pbes.isEmpty()) {
                    QuoteLineItem qli = new QuoteLineItem(
                        QuoteId          = q.Id,
                        PricebookEntryId = pbes[0].Id,
                        Product2Id       = products[0].Id,
                        Quantity         = qty,
                        UnitPrice        = pbes[0].UnitPrice,
                        Description      = products[0].Name + ' subscription',
                        ServiceDate      = Date.today()
                    );
                    insert qli;
                }
            }
            result.put('quoteId', q.Id);
            result.put('quoteNumber', quoteNumber);
        } catch (Exception e) {
            System.debug(LoggingLevel.WARN, 'Quote creation failed (non-blocking): ' + e.getMessage());
        }

        // ── Notify sales rep: Task + Custom Notification ──
        try {
            Id ownerId = acct.OwnerId;

            Task followUp = new Task(
                Subject      = 'New Quote Request - ' + company + ' - ' + selectedPlan,
                Description  = 'A prospect has requested a quote from the pricing page.\n'
                    + 'Contact: ' + firstName + ' ' + lastName + ' (' + email + ')\n'
                    + 'Plan: ' + selectedPlan + ', Seats: ' + qty
                    + (quoteNumber != null ? '\nQuote: ' + quoteNumber : ''),
                WhatId       = opp.Id,
                OwnerId      = ownerId,
                Priority     = 'High',
                Status       = 'Not Started',
                ActivityDate = Date.today().addDays(1)
            );
            insert followUp;

            List<CustomNotificationType> notifTypes = [
                SELECT Id FROM CustomNotificationType
                WHERE DeveloperName = 'RLM_Quote_Request_Notification' LIMIT 1
            ];
            if (!notifTypes.isEmpty()) {
                Messaging.CustomNotification notif = new Messaging.CustomNotification();
                notif.setTitle('New Quote Request: ' + company);
                notif.setBody(firstName + ' ' + lastName + ' requested a quote for NovaSpark '
                    + selectedPlan + ' (' + qty + ' seats). '
                    + (quoteNumber != null ? 'Quote ' + quoteNumber + ' created.' : ''));
                notif.setNotificationTypeId(notifTypes[0].Id);
                notif.setTargetId(opp.Id);
                notif.send(new Set<String>{ ownerId });
            }
        } catch (Exception e) {
            System.debug(LoggingLevel.WARN, 'Notification failed (non-blocking): ' + e.getMessage());
        }

        result.put('success', true);
        result.put('message',
            'Your quote request has been submitted! A sales representative will contact you within 24 hours.'
            + (quoteNumber != null ? ' Quote #' + quoteNumber + ' has been created.' : ''));
        result.put('opportunityId', opp.Id);
        return result;
    }

    // ── Step 3: Create Order (Place Sales Transaction) ───────────
    @RemoteAction
    public static Map<String, Object> createOrder(
            String accountId, String planName,
            Integer seats, String billingCycle) {

        Map<String, Object> result = new Map<String, Object>();
        Integer qty = seats != null ? seats : 1;
        String cycle = String.isNotBlank(billingCycle) ? billingCycle : 'annual';

        try {
            Map<String, Object> txnRequest = new Map<String, Object>{
                'transactionType' => 'NewSale',
                'accountId'       => accountId,
                'pricingFlow'     => 'GET_PRICE',
                'lineItems'       => new List<Map<String, Object>>{
                    new Map<String, Object>{
                        'productName'      => 'NovaSpark ' + planName,
                        'quantity'          => qty,
                        'billingFrequency' => cycle
                    }
                }
            };
            Map<String, Object> apiResult = RLM_RevenueCloudService.placeSalesTransaction(txnRequest);
            result.put('success', true);
            result.put('orderId', apiResult.get('id'));
            result.put('orderNumber', apiResult.get('transactionNumber'));
            result.put('message', 'Order created via Revenue Cloud API');
            result.put('source', 'API');
            return result;
        } catch (Exception e) {
            System.debug(LoggingLevel.INFO, 'RLM API unavailable, using direct DML: ' + e.getMessage());
        }

        return createOrderDirect(accountId, planName, qty, cycle);
    }

    private static Map<String, Object> createOrderDirect(
            String accountId, String planName,
            Integer qty, String billingCycle) {

        Map<String, Object> result = new Map<String, Object>();

        String planSku = getPlanSku(planName);
        List<Product2> products = new List<Product2>();
        if (String.isNotBlank(planSku)) {
            products = [
                SELECT Id, Name FROM Product2
                WHERE StockKeepingUnit = :planSku AND IsActive = true LIMIT 1
            ];
        }
        if (products.isEmpty()) {
            String productSearch = 'NovaSpark ' + planName + '%';
            products = [
                SELECT Id, Name FROM Product2
                WHERE Name LIKE :productSearch AND IsActive = true LIMIT 1
            ];
        }
        if (products.isEmpty()) {
            result.put('success', false);
            result.put('message', 'Product "NovaSpark ' + planName + '" not found in catalog.');
            return result;
        }
        Product2 product = products[0];

        Id stdPbId = [SELECT Id FROM Pricebook2 WHERE IsStandard = true LIMIT 1].Id;

        List<PricebookEntry> pbes = [
            SELECT Id, UnitPrice FROM PricebookEntry
            WHERE Product2Id = :product.Id AND Pricebook2Id = :stdPbId AND IsActive = true LIMIT 1
        ];
        if (pbes.isEmpty()) {
            result.put('success', false);
            result.put('message', 'No active price found for ' + product.Name);
            return result;
        }
        PricebookEntry pbe = pbes[0];

        Decimal unitPrice = pbe.UnitPrice;
        if (billingCycle == 'annual') {
            unitPrice = unitPrice * 0.80;
        }

        Account acct = [
            SELECT Id, BillingStreet, BillingCity, BillingState, BillingPostalCode, BillingCountry,
                   ShippingStreet, ShippingCity, ShippingState, ShippingPostalCode, ShippingCountry
            FROM Account WHERE Id = :accountId
        ];
        if (acct.BillingStreet == null) {
            acct.BillingStreet = '100 Main St';
            acct.BillingCity = 'San Francisco';
            acct.BillingState = 'CA';
            acct.BillingPostalCode = '94105';
            acct.BillingCountry = 'US';
            acct.ShippingStreet = acct.BillingStreet;
            acct.ShippingCity = acct.BillingCity;
            acct.ShippingState = acct.BillingState;
            acct.ShippingPostalCode = acct.BillingPostalCode;
            acct.ShippingCountry = acct.BillingCountry;
            update acct;
        }

        List<Contact> cons = [SELECT Id FROM Contact WHERE AccountId = :accountId LIMIT 1];
        Id billToContactId = cons.isEmpty() ? null : cons[0].Id;

        Order ord = new Order(
            AccountId        = accountId,
            Status           = 'Draft',
            EffectiveDate    = Date.today(),
            Pricebook2Id     = stdPbId,
            BillingStreet    = acct.BillingStreet,
            BillingCity      = acct.BillingCity,
            BillingState     = acct.BillingState,
            BillingPostalCode = acct.BillingPostalCode,
            BillingCountry   = acct.BillingCountry,
            ShippingStreet   = acct.ShippingStreet != null ? acct.ShippingStreet : acct.BillingStreet,
            ShippingCity     = acct.ShippingCity != null ? acct.ShippingCity : acct.BillingCity,
            ShippingState    = acct.ShippingState != null ? acct.ShippingState : acct.BillingState,
            ShippingPostalCode = acct.ShippingPostalCode != null ? acct.ShippingPostalCode : acct.BillingPostalCode,
            ShippingCountry  = acct.ShippingCountry != null ? acct.ShippingCountry : acct.BillingCountry,
            BillToContactId  = billToContactId
        );
        insert ord;

        OrderAction oa = new OrderAction(OrderId = ord.Id, Type = 'Add');
        insert oa;

        OrderItem oi = new OrderItem(
            OrderId          = ord.Id,
            PricebookEntryId = pbe.Id,
            Quantity         = qty,
            UnitPrice        = unitPrice,
            ServiceDate      = Date.today(),
            OrderActionId    = oa.Id,
            NetUnitPrice     = unitPrice,
            TotalLineAmount  = unitPrice * qty,
            BillingFrequency2 = (billingCycle == 'annual' ? 'Annual' : 'Monthly')
        );
        insert oi;

        AppUsageAssignment aua = new AppUsageAssignment(
            RecordId     = ord.Id,
            AppUsageType = 'RevenueLifecycleManagement'
        );
        insert aua;

        result.put('success', true);
        result.put('orderId', ord.Id);
        result.put('orderNumber', 'ORD-' + String.valueOf(ord.Id).right(8));
        result.put('productName', product.Name);
        result.put('unitPrice', unitPrice);
        result.put('totalAmount', unitPrice * qty * (billingCycle == 'annual' ? 12 : 1));
        result.put('message', 'Order created successfully');
        result.put('source', 'DML');
        return result;
    }

    // ── Step 5: Activate Order + create Asset + Invoice + Payment ──
    @RemoteAction
    public static Map<String, Object> activateOrderAndCreateAsset(String orderId) {
        Map<String, Object> result = new Map<String, Object>();
        try {
            Order ord = [
                SELECT Id, Status, AccountId, OrderNumber,
                       (SELECT Id, Product2Id, Product2.Name, Quantity, UnitPrice, TotalPrice
                        FROM OrderItems)
                FROM Order WHERE Id = :orderId
            ];

            if (ord.Status == 'Draft') {
                ord.Status = 'Activated';
                update ord;
            }

            String productName = '';
            Decimal totalAmount = 0;
            if (ord.OrderItems != null && !ord.OrderItems.isEmpty()) {
                productName = ord.OrderItems[0].Product2.Name;
                for (OrderItem oi : ord.OrderItems) {
                    totalAmount += (oi.TotalPrice != null ? oi.TotalPrice : oi.UnitPrice * oi.Quantity);
                }
            }

            // Asset creation is handled by the Customized_Order_To_Asset_Flow
            // record-triggered flow when the Order status changes to Activated.
            result.put('assetSource', 'OrderActivationFlow');

            // 2. Schedule async invoice generation (billing schedules need transaction commit first)
            try {
                generateInvoiceAsync(orderId, ord.AccountId);
                result.put('invoiceCreated', true);
                result.put('invoiceMessage', 'Invoice generation queued.');
            } catch (Exception invEx) {
                System.debug(LoggingLevel.WARN, 'Invoice async scheduling failed: ' + invEx.getMessage());
                result.put('invoiceCreated', false);
                result.put('invoiceMessage', 'Invoice will be auto-generated on next billing run.');
            }

            // 3. Create Payment record
            Map<String, Object> paymentResult = createPaymentForOrder(ord.AccountId, totalAmount, ord.OrderNumber);
            result.put('paymentCreated', paymentResult.get('success'));
            if (paymentResult.containsKey('paymentId')) {
                result.put('paymentId', paymentResult.get('paymentId'));
            }
            if (paymentResult.containsKey('paymentNumber')) {
                result.put('paymentNumber', paymentResult.get('paymentNumber'));
            }

            result.put('success', true);
            result.put('orderNumber', ord.OrderNumber);
            result.put('productName', productName);
            result.put('totalAmount', totalAmount);
            result.put('message',
                'Order ' + ord.OrderNumber + ' activated — asset, invoice, and payment processed.');
        } catch (Exception e) {
            result.put('success', false);
            result.put('message', 'Error activating order: ' + e.getMessage());
        }
        return result;
    }

    @future(callout=true)
    public static void generateInvoiceAsync(String orderId, Id accountId) {
        try {
            List<SObject> bsgs = Database.query(
                'SELECT Id FROM BillingScheduleGroup '
                + 'WHERE Id IN (SELECT BillingScheduleGroupId FROM BillingSchedule WHERE ReferenceEntityId = \''
                + String.escapeSingleQuotes(orderId) + '\') LIMIT 1'
            );

            if (!bsgs.isEmpty()) {
                Invocable.Action invAction = Invocable.Action.createStandardAction('createInvoice');
                invAction.setInvocationParameter('billingScheduleGroupId', String.valueOf(bsgs[0].Id));
                invAction.setInvocationParameter('targetDate', String.valueOf(Date.today()));
                List<Invocable.Action.Result> actionResults = invAction.invoke();

                if (actionResults != null && !actionResults.isEmpty() && actionResults[0].isSuccess()) {
                    System.debug('Invoice generated via createInvoice invocable for order: ' + orderId);
                    return;
                } else if (actionResults != null && !actionResults.isEmpty()) {
                    String errMsg = '';
                    for (Invocable.Action.Error err : actionResults[0].getErrors()) {
                        errMsg += err.getMessage() + '; ';
                    }
                    System.debug(LoggingLevel.WARN, 'createInvoice warnings: ' + errMsg);
                }
            }

            // Fallback: try the REST API endpoint
            try {
                Map<String, Object> apiReq = new Map<String, Object>{
                    'accountId' => accountId,
                    'targetDate' => String.valueOf(Date.today()),
                    'referenceEntityId' => orderId
                };
                Map<String, Object> apiRes = RLM_RevenueCloudService.generateInvoice(apiReq);
                if (apiRes != null) {
                    System.debug('Invoice generated via REST API for order: ' + orderId);
                    return;
                }
            } catch (Exception apiEx) {
                System.debug(LoggingLevel.WARN, 'Invoice API: ' + apiEx.getMessage());
            }

            // Fallback: try generateBillingDocument
            try {
                Map<String, Object> docReq = new Map<String, Object>{
                    'accountId' => accountId,
                    'sourceObject' => orderId,
                    'targetDate' => String.valueOf(Date.today())
                };
                RLM_RevenueCloudService.generateBillingDocument(docReq);
                System.debug('Billing document generated for order: ' + orderId);
            } catch (Exception docEx) {
                System.debug(LoggingLevel.WARN, 'Billing doc: ' + docEx.getMessage());
            }
        } catch (Exception e) {
            System.debug(LoggingLevel.ERROR, 'generateInvoiceAsync error: ' + e.getMessage());
        }
    }

    private static Map<String, Object> createPaymentForOrder(Id accountId, Decimal amount, String orderNumber) {
        Map<String, Object> result = new Map<String, Object>();
        try {
            String refNum = 'PAY-' + orderNumber + '-' + String.valueOf(Datetime.now().getTime());
            Payment p = new Payment(
                AccountId      = accountId,
                Amount         = amount,
                Status         = 'Processed',
                Type           = 'Sale',
                ProcessingMode = 'External',
                Date           = Datetime.now(),
                EffectiveDate  = Datetime.now(),
                GatewayRefNumber       = refNum,
                GatewayResultCode      = 'approved',
                GatewayResultCodeDescription = 'Payment processed for order ' + orderNumber
            );
            insert p;

            Payment created = [SELECT Id, PaymentNumber FROM Payment WHERE Id = :p.Id];
            result.put('success', true);
            result.put('paymentId', created.Id);
            result.put('paymentNumber', created.PaymentNumber);
        } catch (Exception e) {
            result.put('success', false);
            result.put('message', 'Payment creation error: ' + e.getMessage());
        }
        return result;
    }

    // ── Real-time Pricing ─────────────────────────────────────────
    @RemoteAction
    public static Map<String, Object> getRealtimePricing(
            String planName, Integer seats, String billingCycle) {
        try {
            Map<String, Object> pricingReq = new Map<String, Object>{
                'pricingFlow' => 'GET_PRICE',
                'lineItems'   => new List<Map<String, Object>>{
                    new Map<String, Object>{
                        'productName'      => planName,
                        'quantity'          => seats,
                        'billingFrequency' => billingCycle
                    }
                }
            };
            return RLM_RevenueCloudService.calculatePricing(pricingReq);
        } catch (Exception e) {
            return new Map<String, Object>{ 'error' => e.getMessage() };
        }
    }

    // ── Kept for backward compatibility ───────────────────────────
    @RemoteAction
    public static Map<String, Object> convertTrialToPaid(
            String accountId, String selectedPlan,
            Integer seats, String billingCycle) {
        return createOrder(accountId, selectedPlan, seats, billingCycle);
    }

    // ── My Dashboard ──────────────────────────────────────────────
    @RemoteAction
    public static Map<String, Object> getMyDashboard(String accountId) {
        Map<String, Object> result = new Map<String, Object>();
        try {
            // Build a map of Product2Id -> most recent OrderItem for billing info
            Map<Id, OrderItem> prodToOrderItem = new Map<Id, OrderItem>();
            for (OrderItem oi : [
                SELECT Id, Product2Id, UnitPrice, BillingFrequency2, Quantity
                FROM OrderItem
                WHERE Order.AccountId = :accountId AND Order.Status = 'Activated'
                ORDER BY CreatedDate DESC
                LIMIT 50
            ]) {
                if (!prodToOrderItem.containsKey(oi.Product2Id)) {
                    prodToOrderItem.put(oi.Product2Id, oi);
                }
            }

            List<Map<String, Object>> assetList = new List<Map<String, Object>>();
            for (Asset a : [
                SELECT Id, Name, Product2Id, Product2.Name, Quantity, Price, Status, PurchaseDate,
                       HasLifecycleManagement, CurrentAmount, TotalLifecycleAmount, CreatedDate
                FROM Asset WHERE AccountId = :accountId
                ORDER BY CreatedDate DESC LIMIT 20
            ]) {
                String billingCycle = null;
                Decimal unitPrice = null;
                OrderItem matchOi = a.Product2Id != null ? prodToOrderItem.get(a.Product2Id) : null;
                if (matchOi != null) {
                    billingCycle = matchOi.BillingFrequency2;
                    unitPrice = matchOi.UnitPrice;
                }
                if (billingCycle == null && unitPrice != null) {
                    Map<String, Decimal> monthlyPrices = new Map<String, Decimal>{
                        'NovaSpark Starter' => 39, 'NovaSpark Pro' => 79, 'NovaSpark Enterprise' => 199
                    };
                    Decimal mp = monthlyPrices.get(a.Name);
                    if (mp != null) {
                        billingCycle = (unitPrice < mp) ? 'Annual' : 'Monthly';
                    }
                }
                assetList.add(new Map<String, Object>{
                    'id'           => a.Id,
                    'name'         => a.Name,
                    'product'      => a.Product2 != null ? a.Product2.Name : a.Name,
                    'quantity'     => a.Quantity,
                    'price'        => a.Price,
                    'unitPrice'    => unitPrice,
                    'billingCycle' => billingCycle,
                    'status'       => a.Status,
                    'purchased'    => a.PurchaseDate,
                    'managed'      => a.HasLifecycleManagement,
                    'created'      => a.CreatedDate
                });
            }

            List<Map<String, Object>> quoteList = new List<Map<String, Object>>();
            for (Quote q : [
                SELECT Id, QuoteNumber, Name, Status, GrandTotal, ExpirationDate, CreatedDate,
                       (SELECT Product2.Name, Quantity, UnitPrice, TotalPrice FROM QuoteLineItems)
                FROM Quote WHERE Opportunity.AccountId = :accountId
                ORDER BY CreatedDate DESC LIMIT 10
            ]) {
                List<Map<String, Object>> lines = new List<Map<String, Object>>();
                if (q.QuoteLineItems != null) {
                    for (QuoteLineItem qli : q.QuoteLineItems) {
                        lines.add(new Map<String, Object>{
                            'product'  => qli.Product2 != null ? qli.Product2.Name : '',
                            'quantity' => qli.Quantity,
                            'price'    => qli.UnitPrice,
                            'total'    => qli.TotalPrice
                        });
                    }
                }
                quoteList.add(new Map<String, Object>{
                    'id'         => q.Id,
                    'number'     => q.QuoteNumber,
                    'name'       => q.Name,
                    'status'     => q.Status,
                    'total'      => q.GrandTotal,
                    'expires'    => q.ExpirationDate,
                    'created'    => q.CreatedDate,
                    'lineItems'  => lines
                });
            }

            List<Map<String, Object>> orderList = new List<Map<String, Object>>();
            for (Order o : [
                SELECT Id, OrderNumber, Status, TotalAmount, EffectiveDate, CreatedDate,
                       (SELECT Product2.Name, Quantity, UnitPrice, TotalPrice FROM OrderItems)
                FROM Order WHERE AccountId = :accountId
                ORDER BY CreatedDate DESC LIMIT 10
            ]) {
                List<Map<String, Object>> lines = new List<Map<String, Object>>();
                if (o.OrderItems != null) {
                    for (OrderItem oi : o.OrderItems) {
                        lines.add(new Map<String, Object>{
                            'product'  => oi.Product2 != null ? oi.Product2.Name : '',
                            'quantity' => oi.Quantity,
                            'price'    => oi.UnitPrice,
                            'total'    => oi.TotalPrice
                        });
                    }
                }
                orderList.add(new Map<String, Object>{
                    'id'        => o.Id,
                    'number'    => o.OrderNumber,
                    'status'    => o.Status,
                    'total'     => o.TotalAmount,
                    'date'      => o.EffectiveDate,
                    'created'   => o.CreatedDate,
                    'lineItems' => lines
                });
            }

            List<Map<String, Object>> paymentList = new List<Map<String, Object>>();
            for (Payment p : [
                SELECT Id, PaymentNumber, Amount, Status, Type, Date, EffectiveDate,
                       GatewayRefNumber, GatewayResultCode, CreatedDate
                FROM Payment WHERE AccountId = :accountId
                ORDER BY CreatedDate DESC LIMIT 10
            ]) {
                paymentList.add(new Map<String, Object>{
                    'id'      => p.Id,
                    'number'  => p.PaymentNumber,
                    'amount'  => p.Amount,
                    'status'  => p.Status,
                    'type'    => p.Type,
                    'date'    => p.Date,
                    'ref'     => p.GatewayRefNumber,
                    'created' => p.CreatedDate
                });
            }

            result.put('success', true);
            result.put('assets', assetList);
            result.put('quotes', quoteList);
            result.put('orders', orderList);
            result.put('payments', paymentList);
        } catch (Exception e) {
            result.put('success', false);
            result.put('message', 'Error loading dashboard: ' + e.getMessage());
        }
        return result;
    }

    // ── Cancel Subscription (for Change Plan) ─────────────────────
    @RemoteAction
    public static Map<String, Object> cancelSubscription(String assetId) {
        Map<String, Object> result = new Map<String, Object>();
        try {
            Invocable.Action cancelAction = Invocable.Action.createStandardAction('cancelAsset');
            cancelAction.setInvocationParameter('assetId', String.valueOf(assetId));
            cancelAction.setInvocationParameter('cancellationDate', String.valueOf(Date.today()));
            cancelAction.setInvocationParameter('cancellationOutputType', 'order');
            List<Invocable.Action.Result> actionResults = cancelAction.invoke();

            if (actionResults != null && !actionResults.isEmpty()) {
                Invocable.Action.Result ar = actionResults[0];
                if (ar.isSuccess()) {
                    result.put('success', true);
                    result.put('message', 'Subscription cancelled via Revenue Cloud.');
                } else {
                    String errMsg = '';
                    for (Invocable.Action.Error err : ar.getErrors()) {
                        errMsg += err.getMessage() + '; ';
                    }
                    Asset ast = [SELECT Id, Status FROM Asset WHERE Id = :assetId];
                    ast.Status = 'Obsolete';
                    update ast;
                    result.put('success', true);
                    result.put('message', 'Subscription cancelled.');
                    result.put('warning', errMsg);
                }
            } else {
                result.put('success', true);
                result.put('message', 'Cancel action completed.');
            }
        } catch (Exception e) {
            try {
                Asset ast = [SELECT Id, Status FROM Asset WHERE Id = :assetId];
                ast.Status = 'Obsolete';
                update ast;
                result.put('success', true);
                result.put('message', 'Subscription cancelled (direct).');
            } catch (Exception e2) {
                result.put('success', false);
                result.put('message', 'Error cancelling subscription: ' + e2.getMessage());
            }
        }
        return result;
    }

    // ── Helpers ────────────────────────────────────────────────────
    private static String getPlanSku(String planName) {
        if (String.isBlank(planName)) {
            return null;
        }
        String normalized = planName.trim().toLowerCase();
        if (normalized == 'starter') {
            return 'NS-STARTER';
        }
        if (normalized == 'pro') {
            return 'NS-PRO';
        }
        if (normalized == 'enterprise') {
            return 'NS-ENTERPRISE';
        }
        return null;
    }

    private static Account findOrCreateAccount(String companyName) {
        List<Account> existing = [SELECT Id, Name, OwnerId, Phone FROM Account WHERE Name = :companyName LIMIT 1];
        if (!existing.isEmpty()) {
            return existing[0];
        }
        Account acct = new Account(Name = companyName);
        insert acct;
        return [SELECT Id, Name, OwnerId, Phone FROM Account WHERE Id = :acct.Id];
    }

    private static Contact findOrCreateContact(String firstName, String lastName, String email, Id accountId) {
        List<Contact> existing = [SELECT Id, FirstName, LastName, Email, Phone FROM Contact WHERE Email = :email LIMIT 1];
        if (!existing.isEmpty()) {
            return existing[0];
        }
        Contact con = new Contact(
            FirstName = firstName,
            LastName  = lastName,
            Email     = email,
            AccountId = accountId
        );
        insert con;
        return con;
    }

    private static String hashPassword(String password) {
        Blob digest = Crypto.generateDigest('SHA-256', Blob.valueOf(password));
        return EncodingUtil.convertToHex(digest);
    }
}