<h1>
  <img src="logo.png" alt="Roolz" height="48" style="vertical-align: middle; margin-right: 0.5rem" />
  Py-Roolz
</h1>

Roolz is a Python rule engine that evaluates JSON-defined conditions against a **fact object** and executes actions on an **actor object** when conditions are met. Rules are plain Python dicts — no DSL, no special config files.

## Installation

```bash
pip install roolz
```

## Core Concepts

A **rule** is a dict with two keys:

| Key | Type | Description |
|---|---|---|
| `condition` | bool / str / dict | The condition to evaluate against the fact object |
| `actions` | list of dicts | Actions to execute on the actor object when the condition is `True` |

```python
rule = {
    "condition": {"fact": "is_premium", "operator": "is_true"},
    "actions": [{"action": "send_welcome_email"}]
}
```

The **fact object** is any Python object whose methods are called to retrieve values for condition evaluation. The **actor object** is any Python object whose methods are called when a rule fires.

---

## Usage

### Validating Rules

`validate_rules` checks that all condition and action references are valid without executing anything. Pass the fact and actor instances (or their classes) to enable method-signature checking.

```python
from roolz import validate_rules

class User:
    def is_premium(self) -> bool:
        return True

class Mailer:
    def send_welcome_email(self):
        print("Welcome!")

rule = {
    "condition": {"fact": "is_premium", "operator": "is_true"},
    "actions": [{"action": "send_welcome_email"}]
}

errors = validate_rules(rule, User(), Mailer())
if errors:
    for e in errors:
        print(e)
```

### Executing Rules

`execute_rules` validates and then evaluates the condition. If it is `True`, the actions are executed in order.

```python
from roolz import execute_rules

execute_rules(rule, User(), Mailer())
# → "Welcome!" (printed if is_premium returns True)
```

---

## Condition Types

### Boolean

The simplest conditions — a literal `True`/`False` or its string equivalent.

```python
{"condition": True}
{"condition": False}
{"condition": "true"}   # also accepted: "true()", "false", "false()"
```

### Fact-Based

Calls a method on the fact object and compares the return value using an operator.

```python
# Simple — no arguments
{"fact": "is_premium", "operator": "is_true"}

# With keyword params (flat form — params key at top level)
{"fact": "parcel_weight", "operator": "less_than", "value": 50, "params": {"unit": "lb"}}

# With keyword params (dict form — params embedded in the fact key)
{"fact": {"parcel_weight": {"unit": "lb"}}, "operator": "less_than", "value": 50}

# With positional args (dict form)
{"fact": {"get_location": ["US", "CA"]}, "operator": "equal_to", "value": "US"}
```

Both the flat `params` form and the dict-fact form are equivalent. Use whichever reads more clearly.

### Logical Operators

Combine conditions with `all` (AND), `any` (OR), or `not` (negation). These can be nested to any depth.

```python
# All conditions must be true
{"all": [
    {"fact": "is_premium", "operator": "is_true"},
    {"fact": "get_age", "operator": "greater_than", "value": 18}
]}

# At least one condition must be true
{"any": [
    {"fact": "is_premium", "operator": "is_true"},
    {"fact": "get_age", "operator": "greater_than", "value": 65}
]}

# Negate a condition
{"not": {"fact": "is_suspended", "operator": "is_true"}}
```

---

## Actions

An action is a dict with an `action` key (the method name on the actor) and optional `params` (keyword args) or `args` (positional args).

```python
# No arguments
{"action": "send_welcome_email"}

# Keyword arguments
{"action": "send_notification", "params": {"message": "Hello!", "priority": "high"}}

# Positional arguments
{"action": "log_event", "args": ["login", "success"]}
```

---

## Examples

### Example 1: Simple Rule

```python
from roolz import execute_rules

class Order:
    def is_first_order(self) -> bool:
        return True

class OrderProcessor:
    def apply_discount(self, percentage: int):
        print(f"Applied {percentage}% discount")

rule = {
    "condition": {"fact": "is_first_order", "operator": "is_true"},
    "actions": [{"action": "apply_discount", "params": {"percentage": 10}}]
}

execute_rules(rule, Order(), OrderProcessor())
# → "Applied 10% discount"
```

### Example 2: Fact with Parameters

```python
from roolz import execute_rules

class Parcel:
    def weight(self, unit: str = "lb") -> float:
        return 12.5 if unit == "lb" else 5.67

class ShippingService:
    def approve(self):
        print("Parcel approved for shipping")

rule = {
    "condition": {
        "fact": "weight",
        "operator": "less_than_or_equal_to",
        "value": 50,
        "params": {"unit": "lb"}
    },
    "actions": [{"action": "approve"}]
}

execute_rules(rule, Parcel(), ShippingService())
# → "Parcel approved for shipping"
```

### Example 3: Nested Logical Conditions

```python
from roolz import execute_rules

class User:
    def is_premium(self) -> bool:
        return True

    def get_age(self) -> int:
        return 25

    def get_country(self) -> str:
        return "US"

class NotificationService:
    def send_email(self, message: str):
        print(f"Email: {message}")

    def send_sms(self, message: str):
        print(f"SMS: {message}")

rule = {
    "condition": {
        "all": [
            {"fact": "is_premium", "operator": "is_true"},
            {
                "any": [
                    {"fact": "get_age", "operator": "greater_than", "value": 18},
                    {"fact": "get_country", "operator": "equal_to", "value": "US"}
                ]
            }
        ]
    },
    "actions": [
        {"action": "send_email", "params": {"message": "Welcome, premium user!"}},
        {"action": "send_sms",   "params": {"message": "Premium features activated"}}
    ]
}

execute_rules(rule, User(), NotificationService())
```

### Example 4: Validation Before Execution

```python
from roolz import validate_rules, execute_rules

rule = {
    "condition": {"fact": "get_total", "operator": "greater_than", "value": 100},
    "actions": [{"action": "apply_discount", "params": {"percentage": 15}}]
}

errors = validate_rules(rule, Order(), OrderProcessor())
if errors:
    for e in errors:
        print("Validation error:", e)
else:
    execute_rules(rule, Order(), OrderProcessor())
```

---

## Available Operators

### Boolean / None
| Operator | Description |
|---|---|
| `is_true` | Fact value is `True` |
| `is_false` | Fact value is `False` |
| `is_none` | Fact value is `None` |
| `is_not_none` | Fact value is not `None` |
| `is_empty` | Fact value is falsy or empty |
| `is_not_empty` | Fact value is truthy and non-empty |

### Comparison
| Operator | Description |
|---|---|
| `equal_to` | `fact == value` |
| `not_equal_to` | `fact != value` |
| `less_than` | `fact < value` |
| `less_than_or_equal_to` | `fact <= value` |
| `greater_than` | `fact > value` |
| `greater_than_or_equal_to` | `fact >= value` |

### String
| Operator | Description |
|---|---|
| `starts_with` | String starts with the given prefix |
| `ends_with` | String ends with the given suffix |
| `contains` | String or collection contains the given element |
| `does_not_contain` | String or collection does not contain the element |
| `matches_regex` | String matches the given regex pattern |
| `case_fold_equal_to` | Case-insensitive equality (`"Hello" == "hello"`) |

### Collection
| Operator | Description |
|---|---|
| `one_of` | Fact value is in the given list |
| `contains_all` | Collection contains all elements in the given list |
| `contains_any` | Collection contains at least one element in the given list |

### Date
| Operator | Description |
|---|---|
| `date_between` | Date falls within `[start, end]` (ISO 8601 strings) |

---

## Custom Operators

Register your own operators with the `@operator` decorator:

```python
from roolz import operator

@operator("is_even")
def is_even(fact_value, _value):
    return isinstance(fact_value, int) and fact_value % 2 == 0
```

Once registered, the operator is available by name in any condition:

```python
{"fact": "get_count", "operator": "is_even"}
```

---

## Rule Builder

Roolz includes a visual web UI for building and validating rulesets without writing JSON by hand. It supports:

- Visual condition trees (fact conditions, ALL / ANY / NOT groups, unlimited nesting)
- Fact autocomplete from a definition file or Python source introspection
- Validation that catches typos in fact names and parameter keys
- Export to `ruleset.json` and import back into the editor
- Auto-save to `localStorage` so your work persists across page refreshes

→ **[Rule Builder documentation](rule_builder/README.md)**

---


## Testing

```bash
uv run pytest
```

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Write tests for your changes.
4. Ensure all tests pass.
5. Submit a pull request.

## License

This project is licensed under the MIT License.
