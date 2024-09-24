String libraryApiName = 'DocgenDocumentTemplateLibrary';

try {
    List<ContentWorkspace> libraries = [SELECT Id FROM ContentWorkspace WHERE DeveloperName = :libraryApiName LIMIT 1];

    if(libraries.isEmpty()) {
        ContentWorkspace library = new ContentWorkspace();
        library.Name = 'Docgen Document Template Library';
        library.DeveloperName = 'DocgenDocumentTemplateLibrary';
        insert library;
        System.debug(libraryApiName + ' Docgen Document Template Library has been created');
    } else {
        System.debug(libraryApiName + ' Docgen Document Template Library already exists');
    }
} catch (Exception e) {
    System.debug('createDocgenTemplateLibrary error: ' + e.getMessage());
}