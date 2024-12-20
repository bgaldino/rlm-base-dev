public with sharing class QuoteBaseConstants {
    public QuoteBaseConstants() {}

    public static final String EMPTY_STRING = '';
    public static final String ORG62_URL = 'https://org62.lightning.force.com';

    // Approval Related
    public static final String DRAFT_STATUS = 'Draft';
    public static final String PENDING_STATUS = 'Pending';
    public static final String APPROVED_STATUS = 'Approved';
    public static final String REJECTED_STATUS = 'Rejected';
    public static final String RECALLED_STATUS = 'Recalled';
    public static final String REQUESTED_STATUS = 'Requested';
    public static final String ASSIGNED_STATUS = 'Assigned';
    public static final String REVOKED_STATUS = 'Revoked';
    public static final String QUOTE_STATUS_IN_REVIEW = 'In Review';
    public static final Set<String> APPROVAL_PREVIEW_STATUSES = new Set<String>{null, DRAFT_STATUS, RECALLED_STATUS};

    // Approver Constants
    public static final String BACKUP_GROUP_PREFIX = 'Backup Group - ';
    public static final String BACKUP_GROUP_OWNER_PREFIX = 'Backup Group Owner - ';

    // the order with which one status should take precedence over other status values if there are multiple approval recors for the same approval level
    public static final List<String> APPROVAL_STATUS_PRIORITY = new List<String>{'FAILURE', 'REJECTED', 'PENDING', 'APPROVED'};

    // Approval Chains
    public static final String APPROVAL_CHAIN_QUOTE_TERM = 'Quote Term';

    //External ID prefix
    public static final String ORG_PREFIX = 'orgsf-';

    // The Custom Metadata record label of Report for Approval Request Email
    public static final String APPROVAL_REQUEST_EMAIL_REPORT_LABEL = 'Approvals By Quote Report Id';

    public static final List<String> APP_CONFIG_MDT_CATEGORIES = new List<String>{'Profiles'};
    public static final List<String> APP_CONFIG_MDT_FUNCTIONAL_AREAS = new List<String>{'Consumption Rate Table Edit'};
    public static final String APP_CONFIG_ERROR_EMAIL_LOG = 'ErrorEmailLog';

    //Quoteline constants
    public static final String NOT_APPLICABLE = 'Not Applicable';
    public static final String DEFAULTVALUE_NO = 'No';
    public static final String DEFAULTVALUE_YES = 'Yes';
    
    public static final Set<String> DEFAULT_LANGUAGES = new Set<String>{'English'};
}
