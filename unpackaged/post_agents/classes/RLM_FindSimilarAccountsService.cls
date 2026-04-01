public with sharing class RLM_FindSimilarAccountsService {

    public class Request {
        @InvocableVariable(required=true label='Account ID')
        public String accountId;

        @InvocableVariable(required=false label='Match Criteria')
        public String matchCriteria;
    }

    public class Response {
        @InvocableVariable
        public Boolean success;

        @InvocableVariable
        public String message;

        @InvocableVariable
        public String similarAccountIds;
    }

    @InvocableMethod(label='Find Similar Accounts' description='Finds accounts similar to the given account based on user-chosen criteria: Industry only, Type only, either Industry or Type (default), or both Industry and Type.')
    public static List<Response> findSimilar(List<Request> requests) {
        List<Response> responses = new List<Response>();

        for (Request req : requests) {
            Response resp = new Response();

            try {
                // Parse match criteria - default to "either" (OR) if not specified
                String criteria = String.isNotBlank(req.matchCriteria) ? req.matchCriteria.toLowerCase().trim() : 'either';
                Boolean useIndustry = criteria.contains('industry') || criteria == 'both' || criteria == 'either' || criteria == 'all' || criteria == 'or';
                Boolean useType = criteria.contains('type') || criteria == 'both' || criteria == 'either' || criteria == 'all' || criteria == 'or';
                Boolean useOr = criteria == 'either' || criteria == 'or' || criteria == 'any';

                // If neither was explicitly matched, default to both with OR
                if (!useIndustry && !useType) {
                    useIndustry = true;
                    useType = true;
                    useOr = true;
                }

                List<Account> targetAccounts = [
                    SELECT Id, Name, Industry, Type
                    FROM Account
                    WHERE Id = :req.accountId
                    LIMIT 1
                ];

                if (targetAccounts.isEmpty()) {
                    resp.success = false;
                    resp.message = 'Account not found with ID: ' + req.accountId;
                } else {
                    Account target = targetAccounts[0];

                    // Check that the requested criteria fields have values
                    Boolean industryBlank = String.isBlank(target.Industry);
                    Boolean typeBlank = String.isBlank(target.Type);

                    if (useIndustry && industryBlank && useType && typeBlank) {
                        resp.success = true;
                        resp.message = 'Account "' + target.Name + '" has no Industry or Type set. Cannot find similar accounts without at least one matching criterion.';
                    } else if (useIndustry && industryBlank && !useType) {
                        resp.success = true;
                        resp.message = 'Account "' + target.Name + '" has no Industry set. Cannot match by Industry. Try matching by Type instead.';
                    } else if (useType && typeBlank && !useIndustry) {
                        resp.success = true;
                        resp.message = 'Account "' + target.Name + '" has no Type set. Cannot match by Type. Try matching by Industry instead.';
                    } else {
                        String query = 'SELECT Id, Name, Industry, Type FROM Account WHERE Id != \'' + String.escapeSingleQuotes(target.Id) + '\'';

                        List<String> conditions = new List<String>();
                        List<String> criteriaUsed = new List<String>();

                        if (useIndustry && String.isNotBlank(target.Industry)) {
                            conditions.add('Industry = \'' + String.escapeSingleQuotes(target.Industry) + '\'');
                            criteriaUsed.add('Industry (' + target.Industry + ')');
                        }
                        if (useType && String.isNotBlank(target.Type)) {
                            conditions.add('Type = \'' + String.escapeSingleQuotes(target.Type) + '\'');
                            criteriaUsed.add('Type (' + target.Type + ')');
                        }

                        if (!conditions.isEmpty()) {
                            String joinOperator = useOr ? ' OR ' : ' AND ';
                            query += ' AND (' + String.join(conditions, joinOperator) + ')';
                        }
                        query += ' ORDER BY Name LIMIT 50';

                        List<Account> similarAccounts = Database.query(query);
                        String criteriaJoin = useOr ? ' or ' : ' and ';
                        String criteriaLabel = String.join(criteriaUsed, criteriaJoin);

                        // If AND logic found no results and we have both criteria, retry with OR logic
                        if (similarAccounts.isEmpty() && !useOr && conditions.size() > 1) {
                            String orQuery = 'SELECT Id, Name, Industry, Type FROM Account WHERE Id != \'' + String.escapeSingleQuotes(target.Id) + '\'';
                            orQuery += ' AND (' + String.join(conditions, ' OR ') + ')';
                            orQuery += ' ORDER BY Name LIMIT 50';
                            similarAccounts = Database.query(orQuery);

                            if (!similarAccounts.isEmpty()) {
                                criteriaLabel = String.join(criteriaUsed, ' or ');
                                criteriaJoin = ' or ';
                            }
                        }

                        if (similarAccounts.isEmpty()) {
                            resp.success = true;
                            resp.message = 'No similar accounts found matching ' + criteriaLabel + ' for "' + target.Name + '".';
                        } else {
                            List<String> ids = new List<String>();
                            List<String> names = new List<String>();
                            for (Account a : similarAccounts) {
                                ids.add(a.Id);
                                names.add(a.Name);
                            }
                            resp.similarAccountIds = String.join(ids, ',');
                            resp.success = true;
                            resp.message = 'Found ' + similarAccounts.size() + ' accounts matching ' + criteriaLabel + ' for ' + target.Name + ': ' + String.join(names, ', ') + '. Now analyzing product gaps across these peers.';
                        }
                    }
                }
            } catch (Exception e) {
                resp.success = false;
                resp.message = 'Error finding similar accounts: ' + e.getMessage();
            }

            responses.add(resp);
        }

        return responses;
    }
}
