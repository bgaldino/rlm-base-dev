public with sharing class ContactDAO {
    public Contact getContactIdByEmail (String email, Id accountId) {
        List<Contact> contacts = [
            SELECT Id, FirstName, LastName, Email, Phone 
            FROM Contact 
            WHERE 
            	Email = :email 
            	and AccountId = :accountId
            with SECURITY_ENFORCED 
            LIMIT 1
        ];
        if (contacts.isEmpty()) {
            return null;
        }
        return contacts[0];
    }
}