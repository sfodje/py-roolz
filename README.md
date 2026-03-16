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
from roolz._rules import validate_rules

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
from roolz._rules import execute_rules

rules = {
    "condition": True,
    "actions": [{"action": "valid_action"}]
}

fact = MockFact()
actor = MockActor()
execute_rules(rules, fact, actor)
```

## Examples

### Example 1: Simple Condition and Action

```python
from roolz._rules import validate_rules, execute_rules

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
from roolz._rules import validate_rules, execute_rules

class MockFact:
    def value_method(self, *args, **kwargs):
        return kwargs.get("value", None)

class MockActor:
    def valid_action(self):
        print("Action executed")

rules = {
    "condition": {"fact": "value_method", "operator": "equal_to", "params": {"value": 42}, "value": 42},
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
