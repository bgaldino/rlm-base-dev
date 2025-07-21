/* This class is required for the Forms Fast Q Tool. It was updated June 2021 */

public class New_Wto_Ext {
                        public List<String> rt_ids {get;set;}
                        public List<RecordType> rts {get;set;}
                        public String sObjectName {get;set;}
                        public String selectedRecordId {get;set;}
                      private ApexPages.StandardController ctrl;

                        public New_Wto_Ext(ApexPages.StandardController controller) {
                         ctrl = controller;
                           sObjectName = controller.getRecord().getSObjectType().getDescribe().getName();
                        }

                        public List<SelectOption> getRecordTypes() {
                            List<SelectOption> options = new List<SelectOption>();

                            rts = [SELECT Id, Name From RecordType WHERE SobjectType =: sObjectName ];

                            for (RecordType r : rts) {
                                options.add(new SelectOption(r.Id,r.Name));
                            }

                            return options;
                        }

                        public List<SelectOption> getDefaultCaseOrigin() {
                            List<SelectOption> dc_options = new List<SelectOption>();
                            Schema.DescribeFieldResult fieldResult = Case.Origin.getDescribe();
                            List<Schema.PicklistEntry> ple = fieldResult.getPicklistValues();

                            for(Schema.PicklistEntry f : ple) {
                                dc_options.add(new SelectOption(f.getLabel(), f.getValue()));
                            }

                            return dc_options;

                        }

                        public void save() {

                                if (ctrl.getRecord().getsObjectType() == Case.sObjectType) {
                                    try {
                                        //Fetching the assignment rules on case
                                        AssignmentRule AR = new AssignmentRule();
                                        AR = [select id from AssignmentRule where SobjectType = 'Case' and Active = true limit 1];
                                        System.Debug('CASE AR: ' + AR);

                                        Database.DMLOptions dmlOpts = new Database.DMLOptions();
                                        dmlOpts.assignmentRuleHeader.assignmentRuleId= AR.id;

                                        Case newCase = new Case();
                                        newCase = (Case)ctrl.getRecord();
                                        //Setting the DMLOption on Case instance
                                        //newCase.RecordTypeId = selectedRecordId;
                                        newCase.setOptions(dmlOpts);
                                        upsert newCase;
                                        ApexPages.Message myMsg = new ApexPages.Message(ApexPages.Severity.CONFIRM , 'Thank you for your submission');
                                        ApexPages.addMessage(myMsg);
                                    } catch (Exception e) {
                                        ApexPages.Message myMsg = new ApexPages.Message(ApexPages.Severity.ERROR , e.getMessage());
                                        ApexPages.addMessage(myMsg);
                                    }
                                } else if (ctrl.getRecord().getsObjectType() == Lead.sObjectType) {
                                    try {
                                        //Fetching the assignment rules on case
                                        AssignmentRule AR = new AssignmentRule();
                                        AR = [select id from AssignmentRule where SobjectType = 'Lead' and Active = true limit 1];
                                        System.Debug('LEAD AR: ' + AR);

                                        Database.DMLOptions dmlOpts = new Database.DMLOptions();
                                        dmlOpts.assignmentRuleHeader.assignmentRuleId= AR.id;

                                        Lead newLead = new Lead();
                                        newLead = (Lead)ctrl.getRecord();
                                        //Setting the DMLOption on Case instance
                                        newLead.setOptions(dmlOpts);
                                        upsert newLead;
                                        ApexPages.Message myMsg = new ApexPages.Message(ApexPages.Severity.CONFIRM , 'Thank you for your submission');
                                        ApexPages.addMessage(myMsg);
                                    } catch (Exception e) {
                                        System.Debug('Error: ' + e.getMessage());
                                        ApexPages.Message myMsg = new ApexPages.Message(ApexPages.Severity.ERROR , e.getMessage());
                                        ApexPages.addMessage(myMsg);
                                    }

                                } else {
                                    try {
                                        ctrl.save();
                                        ApexPages.Message myMsg = new ApexPages.Message(ApexPages.Severity.CONFIRM , 'Thank you for your submission');
                                        ApexPages.addMessage(myMsg);
                                    } catch (Exception e) {
                                      System.Debug('Error: ' + e.getMessage() + e.getCause().getMessage() + e.getTypeName());
                                        ApexPages.Message myMsg = new ApexPages.Message(ApexPages.Severity.ERROR , e.getMessage() + e.getCause().getMessage() + e.getTypeName());
                                        ApexPages.addMessage(myMsg);
                                    }

                                }


                       }
                    }