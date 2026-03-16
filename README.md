# Py-Roolz

Roolz is a Python library for evaluating and executing rules based on conditions and actions. It is designed to be flexible and easy to integrate into various applications.

## Installation

You can install Roolz using pip:

```bash
pip install roolz
```

## Usage

### Validating Rules

To validate rules, use the `validate_rules` function. This function checks the conditions and actions defined in the
rules and returns any validation errors.

```python
from roolz import validate_rules

rules = {
    "condition": True,
    "actions": [{"action": "valid_action"}]
}

fact = MockFact()
actor = MockActor()
errors = validate_rules(rules, fact, actor)
if errors:
    print("Validation errors:", errors)
```

### Executing Rules

To execute rules, use the `execute_rules` function. This function evaluates the conditions and executes the actions if
the conditions are met.

```python
from roolz import execute_rules

rules = {
    "condition": True,
    "actions": [{"action": "valid_action"}]
}

fact = MockFact()
actor = MockActor()
execute_rules(rules, fact, actor)
```

## Condition Types

Roolz supports several types of conditions:

### Boolean Conditions
```python
# Simple boolean values
{"condition": True}
{"condition": False}

# String-based boolean values
{"condition": "true"}
{"condition": "true()"}
{"condition": "false"}
{"condition": "false()"}
```

### Logical Operators
```python
# ALL - all conditions must be true
{"condition": {"all": [True, {"fact": "method1", "operator": "is_true"}, {"fact": "method2", "operator": "equal_to", "value": 42}]}}

# ANY - at least one condition must be true
{"condition": {"any": [False, {"fact": "method1", "operator": "is_true"}, {"fact": "method2", "operator": "equal_to", "value": 42}]}}

# NOT - negate a condition
{"condition": {"not": {"fact": "method1", "operator": "is_true"}}}
```

### Fact-Based Conditions
```python
# Simple fact method call
{"condition": {"fact": "method_name", "operator": "is_true"}}

# Fact method with parameters (using fact dictionary)
{"condition": {"fact": {"method_name": {"param1": "value1", "param2": "value2"}}, "operator": "equal_to", "value": "expected_value"}}

# Fact method with positional arguments (using fact dictionary)
{"condition": {"fact": {"method_name": ["arg1", "arg2"]}, "operator": "equal_to", "value": "expected_value"}}
```

## Examples

### Example 1: Simple Condition and Action

```python
from roolz import validate_rules, execute_rules

class MockFact:
    def true_method(self):
        return True

class MockActor:
    def valid_action(self):
        print("Action executed")

rules = {
    "condition": {"fact": "true_method", "operator": "is_true"},
    "actions": [{"action": "valid_action"}]
}

fact = MockFact()
actor = MockActor()

# Validate rules
errors = validate_rules(rules, fact, actor)
if errors:
    print("Validation errors:", errors)
else:
    # Execute rules
    execute_rules(rules, fact, actor)
```

### Example 2: Condition with Parameters

```python
from roolz import validate_rules, execute_rules

class MockFact:
    def value_method(self, *args, **kwargs):
        return kwargs.get("value", None)

class MockActor:
    def valid_action(self):
        print("Action executed")

# Using fact dictionary for parameters
rules = {
    "condition": {
        "fact": {"value_method": {"value": 42}},
        "operator": "equal_to",
        "value": 42
    },
    "actions": [{"action": "valid_action"}]
}

fact = MockFact()
actor = MockActor()

# Validate rules
errors = validate_rules(rules, fact, actor)
if errors:
    print("Validation errors:", errors)
else:
    # Execute rules
    execute_rules(rules, fact, actor)
```

### Example 3: Complex Logical Conditions

```python
from roolz import validate_rules, execute_rules

class User:
    def is_premium(self):
        return True
    
    def get_age(self):
        return 25
    
    def get_location(self, country):
        return country

class NotificationService:
    def send_email(self, message):
        print(f"Email sent: {message}")
    
    def send_sms(self, message):
        print(f"SMS sent: {message}")

# Complex rule with logical operators
rules = {
    "condition": {
        "all": [
            {"fact": "is_premium", "operator": "is_true"},
            {
                "any": [
                    {"fact": {"get_age": {}}, "operator": "greater_than", "value": 18},
                    {"fact": {"get_location": {"country": "US"}}, "operator": "equal_to", "value": "US"}
                ]
            }
        ]
    },
    "actions": [
        {"action": "send_email", "params": {"message": "Welcome premium user!"}},
        {"action": "send_sms", "params": {"message": "Premium features activated"}}
    ]
}

user = User()
service = NotificationService()

# Execute rules
execute_rules(rules, user, service)
```

### Example 4: Action with Parameters

```python
from roolz import validate_rules, execute_rules

class OrderProcessor:
    def apply_discount(self, percentage):
        print(f"Applied {percentage}% discount")
    
    def send_notification(self, message, priority="normal"):
        print(f"Notification ({priority}): {message}")

class Order:
    def get_total(self):
        return 100
    
    def is_first_order(self):
        return True

rules = {
    "condition": {
        "all": [
            {"fact": "is_first_order", "operator": "is_true"},
            {"fact": {"get_total": {}}, "operator": "greater_than", "value": 50}
        ]
    },
    "actions": [
        {"action": "apply_discount", "params": {"percentage": 10}},
        {"action": "send_notification", "params": {"message": "First order discount applied!", "priority": "high"}}
    ]
}

order = Order()
processor = OrderProcessor()

execute_rules(rules, order, processor)
```

## Available Operators

Roolz provides a comprehensive set of operators for condition evaluation:

### Basic Operators
- `is_none` - Check if value is None
- `is_not_none` - Check if value is not None
- `is_empty` - Check if value is empty/falsy
- `is_not_empty` - Check if value is not empty/truthy
- `is_true` - Check if value is True
- `is_false` - Check if value is False

### Comparison Operators
- `equal_to` - Check if values are equal
- `not_equal_to` - Check if values are not equal
- `less_than` - Check if left value is less than right value
- `greater_than` - Check if left value is greater than right value
- `less_than_or_equal_to` - Check if left value is less than or equal to right value
- `greater_than_or_equal_to` - Check if left value is greater than or equal to right value

### String Operators
- `starts_with` - Check if string starts with prefix
- `ends_with` - Check if string ends with suffix
- `contains` - Check if string contains substring
- `matches_regex` - Check if string matches regex pattern
- `case_fold_equal_to` - Case-insensitive string comparison

### Collection Operators
- `contains` - Check if collection contains element
- `does_not_contain` - Check if collection does not contain element
- `contains_all` - Check if collection contains all elements
- `contains_any` - Check if collection contains any element
- `one_of` - Check if value is in collection

### Date Operators
- `date_between` - Check if date is between two dates

## Testing

To run the tests, use pytest:

```bash
pytest
```

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Write tests for your changes.
4. Ensure all tests pass.
5. Submit a pull request.

## License

This project is licensed under the MIT License.
