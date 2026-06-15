---
page_id: apex_class_commercetax_TaxApiException.htm
title: TaxApiException Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_TaxApiException.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# TaxApiException Class

Contains details about any exceptions during the tax calculation
process. Extends the `ApexBaseException`
class.

## Namespace

[CommerceTax](./apex_namespace_commercetax.htm.md "Manage the communication between Salesforce and an external tax engine.")

- **[TaxApiException Constructors](./apex_class_commercetax_TaxApiException.htm.md#apex_commercetax_TaxApiException_constructors)**  
  Learn more about the available constructors with the `TaxApiException` class.

## TaxApiException Constructors

Learn more about the available constructors with the `TaxApiException` class.

The `TaxApiException` class includes these
constructors.

- **[TaxApiException(var1, var2)](./apex_class_commercetax_TaxApiException.htm.md#apex_commercetax_TaxApiException_ctor)**  
  Initializes the `TaxApiException` class using an `Exception` and a string to provide more details about the exception. This constructor is intended for test usage and throws an exception if used outside of the Apex test context.
- **[TaxApiException(var1)](./apex_class_commercetax_TaxApiException.htm.md#apex_commercetax_TaxApiException_ctor_2)**  
  Initializes the `TaxApiException` class using an `Exception`. This constructor is intended for test usage and throws an exception if used outside of the Apex test context.
- **[TaxApiException()](./apex_class_commercetax_TaxApiException.htm.md#apex_commercetax_TaxApiException_ctor_3)**  
  Initializes the `TaxApiException` class without any initialized parameters. This constructor is intended for test usage and throws an exception if used outside of the Apex test context.

### TaxApiException(var1, var2)

Initializes the `TaxApiException`
class using an `Exception` and a string to provide more
details about the exception. This constructor is intended for test usage and throws an
exception if used outside of the Apex test context.

#### Signature

`global
TaxApiException(String var1, Exception
var2)`

#### Parameters

var1
:   Type: String
:   Text that provides more information about the returned exception.

var2
:   Type: [Exception](https://developer.salesforce.com/docs/atlas.en-us.262.0.apexref.meta/apexref/apex_classes_exception_methods.htm)
:   An exception denotes an error that disrupts the normal flow of code execution. You can
    use Apex built-in exceptions or create custom exceptions. All exceptions have common
    methods.

### TaxApiException(var1)

Initializes the `TaxApiException`
class using an `Exception`. This constructor is intended for
test usage and throws an exception if used outside of the Apex test context.

#### Signature

`global
TaxApiException(Exception
var1)`

#### Parameters

var1
:   Type: [Exception](https://developer.salesforce.com/docs/atlas.en-us.262.0.apexref.meta/apexref/apex_classes_exception_methods.htm)
:   An exception denotes an error that disrupts the normal flow of code execution. You can
    use Apex built-in exceptions or create custom exceptions. All exceptions have common
    methods.

### TaxApiException()

Initializes the `TaxApiException`
class without any initialized parameters. This constructor is intended for test usage and
throws an exception if used outside of the Apex test context.

#### Signature

`global
TaxApiException()`
