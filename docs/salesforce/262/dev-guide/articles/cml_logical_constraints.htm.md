---
page_id: cml_logical_constraints.htm
title: Logical Constraints
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_logical_constraints.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Constraint Modeling Language
parent_page: cml_constraints.htm
fetched_at: 2026-06-09
---

# Logical Constraints

A logical constraint defines a statement that must hold true logically. The constraint
can be any logical expression by using a logical operator.

For example, the statement `c0 ? c1 : c2` means that if
`c0` is true, then `c1` needs to be true, otherwise `c2` needs to be
true.

## Constraint Syntax Patterns

Here are the details of the constraint
syntax patterns.

- `constraint(logic expression);`: The simplest form,
  enforcing a logic statement.
- `constraint(logic expression, string literal | string
  variable);`: Includes an optional failure explanation that is displayed if the
  constraint is violated.
- `constraint(logic expression, string literal | string
  variable, arg, …, arg);`: Includes a failure explanation with additional
  arguments to be interpolated into the string of the failure explanation.

If a constraint is violated, it takes an optional string variable or string literal as
the failure explanation. The failure explanation could be in a string format with additional
arguments. CML supports two string formats. One is the standard string format and another is
a string with {} placeholder, to be replaced with the actual argument value.

## Key Components of the Constraint Syntax

Here are the details of the key components of the constraint syntax.

| Component | Description | Code Sample |
| --- | --- | --- |
| Logic Expression | This can be a basic mathematical expression (using operators like +, -, \* , /) or a relational expression (using ==, !=, >, <, and so on). It can also include logical operators such as AND (&&), OR (||), NOT (!), the implication operator (->), or the bi-directional operator (< - >). | Basic ``` constraint(generator.sum(quantity) > 20); ``` |
| Failure Explanation | This optional string literal or variable provides a human-readable reason for the violation. CML supports two formatting styles for these strings:   - Java string format (for example, using `%`d   or `%s`). - Placeholder format using `{}` | With Explanation ``` constraint(x + y <= 100, "Total must not exceed 100"); ``` |
| Arguments (arg) | Arguments are used to replace the placeholders in the failure explanation string with actual values at runtime. | With Explanation and Arguments ``` constraint(requiredKW <= 2500, "The required capacity of {} kW exceeds the maximum supported limit of 2500 kW.",requiredKW); ``` |

See the complete example in [Constraints using Format Specifiers (%s, %d) and
Dates](./cml_core_concept_examples.htm.md "These examples illustrate core Constraint Modeling Language (CML) concepts including type, relationships, constraints, and so on.").

## Constraint Example

In this example, the first constraint specifies that, if the `DutyRating` value isn't `Prime Power (PRP)`,
then the quantity of `Warranty_PRP (Warranties subtype)`
must be 0. Similarly in the second constraint, if `DutyRating` value isn't `Data Center Continuous
(DCC)` then the quantity of `Warranty_DCC` must
be 0. Lastly, in the third constraint, if `DutyRating`
value isn't `Emergency Standby Power (ESP)`, then the
quantity of `Warranty_ESP` must be 0.

```
type Warranty;
type Warranty_PRP : Warranty;
type Warranty_DCC : Warranty;
type Warranty_ESP : Warranty;
type GeneratorSet  {
string DutyRating = ["Prime Power (PRP)", "Continuous Power (COP)", "Data Center Continuous (DCC)", "Emergency Standby Power (ESP)"];
relation Warranties : Warranty[3];
constraint(DutyRating != "Prime Power (PRP)" -> Warranties[Warranty_PRP] == 0);
constraint(DutyRating != "Data Center Continuous (DCC)" -> Warranties[Warranty_DCC] == 0);
constraint(DutyRating != "Emergency Standby Power (ESP)" -> Warranties[Warranty_ESP] == 0);
}
```

## Example: Constraints Using String and Logical Operators

This example demonstrates how a GeneratorSet uses string functions to extract a numeric
voltage value, and then uses logical operators (`->`,
`&&`,
`||`) to enforce safety and certification
requirements.

## Explanation of Operators Used in the Example

Here are the details of the operators used in the example.

| Operator/Function | Category | Usage in Example |
| --- | --- | --- |
| `strtoint()` | String Function | Converts the extracted voltage string to the integer `Voltage3`. |
| `regexpreplace()` | String Function | Replaces the full Voltage string with only the second matched group (the high voltage number) using the defined `VOLTAGE_REGEX`. |
| `strcontain()` | String Function | Checks if the `DutyRating` string contains the substring "Power". |
| `->` | Logical Implication | Defines a conditional rule: If the condition on the left is true, the condition on the right must be true. |
| `&&` | Logical AND | Requires both conditions (high requiredKW AND duty rating contains "Power") to be true. |
| `||` | Logical OR | Requires `standardsAndCompliance` to be "`Listing-UL 2200`" or "`Certification-CSA`". |
| `!=` | Comparison/Relational | Used to check if the string value is "Not Equal" to a specific string literal. |

```
// --- Constants (Required for String Manipulation) ---
define VOLTAGE_REGEX "^(+)/(+)$"

// --- Base Type and Configuration Attributes ---
type Warranty;
type Warranty_ESP : Warranty;

type GeneratorSet {
    // String input attribute for user selection
    string Voltage = ["277/480", "2400/4160", "7976/13800"];

    // String input attribute for operational mode
    string DutyRating = ["Prime Power (PRP)", "Continuous Power (COP)", "Emergency Standby Power (ESP)"];

    // String input attribute for compliance
    string standardsAndCompliance = ["Certification-CSA", "Listing-UL 2200"];
    // Required KW (Int attribute)
    int requiredKW = [101..10000];
// warranties for generator set
relation Warranties : Warranty[3];

    // 1. STRING OPERATORS/FUNCTIONS: Deriving Numeric Data
    // We use strtoint() combined with regexpreplace() to extract the second number (the high voltage)
    // from the Voltage string (e.g., extracting 480 from "277/480").
    int Voltage3 = strtoint(regexpreplace(Voltage, VOLTAGE_REGEX, "$2"), 0);
  // Prime Power or Continuous Power using strcontain
    boolean NonstandbyPower = !strcontain(DutyRating, "ESP");

    // 2. LOGICAL OPERATOR (Implication ->): Certification Validation
    // Constraint: If the standard is UL 2200 (precondition), THEN Voltage3 must be <= 600 (postcondition).
    constraint(
        standardsAndCompliance == "Listing-UL 2200" -> Voltage3 <= 600,
        "The UL 2200 standard covers stationary engine generator assemblies rated at 600 volts or less."
    );

    // 3. LOGICAL OPERATORS (AND &&, OR ||) and STRING FUNCTION (strcontain)
    // Constraint: If the required power is high AND the unit is used for Prime Power OR Continuous Power,
    // THEN a specific standard must be selected.
    constraint(
        (requiredKW >= 5000 && NonstandbyPower) 
        ->
        (standardsAndCompliance == "Listing-UL 2200" || standardsAndCompliance == "Certification-CSA"),  "High power and continuous use requires a major compliance standard.");

    // 4. LOGICAL OPERATOR (Implication ->) and String Comparison (!=)
    // Constraint: If the Duty Rating is NOT Emergency Standby Power, THEN a specific warranty (Warranties[Warranty_ESP]) must be excluded/zero.
    constraint(
        DutyRating != "Emergency Standby Power (ESP)" -> Warranties[Warranty_ESP] == 0,
        "The DutyRating when not equal to Emergency Standby Power, implies that the Warranty must be 0."
    );
}
```

## How User Input Order Affects Constraint Engine Behavior

The constraint engine is architecturally designed to never override or modify a
user-selected value when evaluating constraints, except in the specific case of an `exclude` rule. If a constraint violation occurs due to user
input, the engine generates an error message rather than attempting to fix the value
itself.

## Example: Constraint Evaluation Based on Input Order (Generator Set)

The order in which a user configures attributes for a product (such as a `GeneratorSet`) determines whether the constraint engine
performs an automatic update or enforces a validation error.

Consider a constraint within the `GeneratorSet` type
that links the operational requirement (`DutyRating`) to
the required certification (`standardsAndCompliance`).

```
type GeneratorSet {
// Attribute 1 (Precondition): User selects operational mode
string DutyRating = ["Prime Power (PRP)", "Continuous Power (COP)"];
// Attribute 2 (Dependent): Certification standard
string standardsAndCompliance = ["Certification-CSA", "Listing-UL 2200"];
// Constraint: If the unit is configured for Prime Power, it must have UL 2200 Listing.
constraint(
DutyRating == "Prime Power (PRP)" -> standardsAndCompliance == "Listing-UL 2200",
"Prime Power Duty Rating requires UL 2200 Listing"
);
}
```

The outcomes depend on the user's input sequence.

| Scenario | User Input Sequence | Constraint Engine Result |
| --- | --- | --- |
| Scenario 1: Successful Update (Precondition first) | The user first sets `DutyRating` to "`Prime Power (PRP)`". | The constraint engine recognizes the precondition is met and updates the dependent attribute, setting `standardsAndCompliance` to "`Listing-UL 2200`". The constraint is validated. |
| Scenario 2: Constraint Violation (Conflicting Value first) | The user first sets `standardsAndCompliance` to "`Certification-CSA`", and then sets `DutyRating` to "`Prime Power (PRP)`". | The existing user-selected value ("`Certification-CSA`") violates the constraint. The constraint engine will not override the user's prior selection to change it to "`Listing-UL 2200`". Instead, the engine displays an error. |

To resolve the error in Scenario 2, the user must manually adjust one of their
selections: either change the `DutyRating` (precondition)
or manually update the `standardsAndCompliance`
(dependent value) to "`Listing-UL 2200`".

## Left-Hand Side and Right-Hand Side Behavior in Constraint Resolution

Operator precedence and constraint engine resolution process determines whether the
left-hand side (LHS) or right-hand side (RHS) of a constraint changes or is constrained
to maintain logical validity. Variable origin, which means whether variables are
user-selected, calculated, or restricted by system limitations, can also affect the
outcome for the LHS or RHS in an expression.

These examples show how different user inputs lead to different outcomes for the LHS and
RHS in the same expression.

## Example 1. Implication Operator (->): Directional Enforcement

```
type Order {
int quantity = [1..1000];
boolean requiresApproval;
constraint bulkOrderApproval (
quantity >= 100 -> requiresApproval == true
);
}
```

The implication constraint `A -> B` (if A, then
B) is the primary method for defining a mandatory outcome. The engine evaluates the LHS (A)
first. If the `quantity` is 150 (LHS TRUE), then the
engine forces `requiresApproval` (RHS) to be `TRUE`.

| Scenario | Outcome |
| --- | --- |
| Scenario A: LHS is True, RHS Changes | The user sets a quantity greater than or equal to 100 on the LHS, which makes the condition true. The engine sets or changes the value of requiresApproval, the RHS, to true. |
| Scenario B: RHS is False, LHS is Constrained to be False | The user manually sets requiresApproval, the RHS variable, to false. Since the implication true -> false is forbidden, the LHS condition must be false to satisfy the constraint. The engine constrains quantity on the LHS to be less than 100 to make the LHS false. |

## Example 2. Bi-conditional (<->): Symmetrical Equivalence

```
type BulkOrderSystem {
int quantity = [1..1000];
boolean requiresApproval;
boolean isBulkOrder;

constraint bulkOrderStatus (
isBulkOrder <-> (quantity >= 100 && requiresApproval),
"Bulk order status requires 100+ quantity AND management approval."
);
}
```

The bi-conditional constraint A `<->` B (A if
and only if B) requires that the LHS and RHS must share the same Boolean truth value. Either
side can act as the driver, forcing the other side to change. In the example above:

- A is the boolean variable `isBulkOrder`.
- B is the complex condition `(quantity >= 100
  && requiresApproval)`.

| Scenario | Outcome |
| --- | --- |
| Scenario A: LHS Drives RHS | If the user manually sets the attribute isBulkOrder to true (making the LHS true), the engine immediately forces the RHS (quantity >= 100 && requiresApproval) to also be true, ensuring that both quantity is at least 100 and requiresApproval is set to true. |
| Scenario B: RHS Drives LHS | If the user selects a configuration where the quantity is high (for example, 500) and then sets requiresApproval to false (making the RHS condition false), the engine immediately forces the LHS attribute isBulkOrder to false to maintain equivalence. |

## Exception: The exclude Rule

The only scenario where the constraint engine intentionally overrides user input is when
processing the `exclude` rule. If a user selects a
component or sets an attribute value that violates an `exclude` rule, the engine will automatically override that user input to satisfy
the exclusion constraint. In all other constraint types (like implication constraints shown
previously), the engine relies on the user to fix the error. For more information, see [Exclude
Rule](./cml_exclude_rule.htm.md "The exclude rule is used to automatically remove a specific type in a relationship if a certain condition is met.").
