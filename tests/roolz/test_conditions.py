import pytest

from roolz import evaluate_condition, validate_condition
from roolz.errors import InvalidConditionError


class LengthUnit:
    """A simple class that can be instantiated from a string."""

    def __init__(self, value):
        if isinstance(value, str):
            # Parse string like "10cm" or "5in"
            if value.endswith("cm"):
                self.value = float(value[:-2])
                self.unit = "cm"
            elif value.endswith("in"):
                self.value = float(value[:-2])
                self.unit = "in"
            else:
                raise ValueError(f"Cannot parse length unit from: {value}")
        else:
            self.value = float(value)
            self.unit = "cm"  # default unit

    def __str__(self):
        return f"{self.value}{self.unit}"


class MockFact:
    def some_fact_method(self):
        pass

    def true_method(self):
        return True

    def false_method(self):
        return False

    def value_method(self, *args, **kwargs):
        return kwargs.get("value", None)

    def required_param_method(self, required_param):
        return required_param

    def optional_param_method(self, optional_param=None):
        return optional_param

    def mixed_params_method(self, required_param, optional_param=None):
        return required_param, optional_param

    def positional_only_method(self, param, /):
        return param

    def keyword_only_method(self, *, param):
        return param

    # New methods for testing value validation
    def string_param_method(self, text: str):
        return text

    def int_param_method(self, number: int):
        return number

    def float_param_method(self, value: float):
        return value

    def bool_param_method(self, flag: bool):
        return flag

    def list_param_method(self, items: list):
        return items

    def dict_param_method(self, data: dict):
        return data

    def count_param_method(self, count: int):
        return count

    def size_param_method(self, size: int):
        return size

    def length_unit_method(self, length: LengthUnit):
        return length


def test_validate_condition_boolean():
    assert validate_condition(True) == []
    assert validate_condition(False) == []


def test_validate_condition_string():
    assert validate_condition("true") == []
    assert validate_condition("true()") == []
    assert validate_condition("false") == []
    assert validate_condition("false()") == []
    assert validate_condition("invalid") == [
        InvalidConditionError(
            "*", "Condition must be a boolean or a dictionary", input_value="invalid"
        )
    ]


def test_validate_condition_invalid_type():
    assert validate_condition(123) == [  # type: ignore
        InvalidConditionError(
            "*", "Condition must be a boolean or a dictionary", input_value=123
        )
    ]


def test_validate_all_condition_empty_list():
    condition = {"all": []}
    assert validate_condition(condition) == [
        InvalidConditionError("*.all", "'all' must be a list with at least one element")
    ]


def test_validate_all_condition_valid():
    condition = {"all": [True]}
    assert validate_condition(condition) == []

    condition = {"all": [True, False]}
    assert validate_condition(condition) == []

    condition = {"all": [False, "false()", True]}
    assert validate_condition(condition) == []


def test_validate_all_condition_invalid():
    condition = {"all": [False, "false()", 123]}
    assert validate_condition(condition) == [
        InvalidConditionError("*.all[2]", "Condition must be a boolean or a dictionary")
    ]

    condition = {"all": [True, {"any": [False, True, {"fact": "some_fact_method"}]}]}
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*.all[1].any[2]",
            "'operator' is required",
        )
    ]

    condition = {"all": [True, {"any": [False, True, {"fact": "some_fact_method"}]}]}
    assert validate_condition(condition) == [
        InvalidConditionError("*.all[1].any[2]", "Fact is required for this condition"),
        InvalidConditionError(
            "*.all[1].any[2]",
            "'operator' is required",
        ),
    ]


def test_validate_any_condition_empty_list():
    condition = {"any": []}
    assert validate_condition(condition) == [
        InvalidConditionError("*.any", "'any' must be a list with at least one element")
    ]


def test_validate_any_condition_valid():
    condition = {"any": [True]}
    assert validate_condition(condition) == []

    condition = {"any": [True, False]}
    assert validate_condition(condition) == []

    condition = {"any": [False, "false()", True]}
    assert validate_condition(condition) == []


def test_validate_any_condition_invalid():
    condition = {"any": [False, "false()", 123]}
    assert validate_condition(condition) == [
        InvalidConditionError("*.any[2]", "Condition must be a boolean or a dictionary")
    ]

    condition = {"any": [True, {"all": [False, True, {"fact": "some_fact_method"}]}]}
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*.any[1].all[2]",
            "'operator' is required",
        )
    ]

    condition = {"any": [True, {"all": [False, True, {"fact": "some_fact_method"}]}]}
    assert validate_condition(condition) == [
        InvalidConditionError("*.any[1].all[2]", "Fact is required for this condition"),
        InvalidConditionError(
            "*.any[1].all[2]",
            "'operator' is required",
        ),
    ]


def test_validate_not_condition_valid():
    condition = {"not": True}
    assert validate_condition(condition) == []


def test_validate_fact_condition_missing_fact():
    condition = {"fact": "some_fact_method"}
    assert validate_condition(condition) == [
        InvalidConditionError("*", "Fact is required for this condition"),
        InvalidConditionError(
            "*",
            "'operator' is required",
        ),
    ]


def test_validate_fact_condition_invalid_keys():
    condition = {"fact": "some_fact_method", "invalid_key": "value"}
    assert validate_condition(condition) == [
        InvalidConditionError("*", "Fact is required for this condition"),
        InvalidConditionError("*", "Invalid keys: invalid_key"),
        InvalidConditionError(
            "*",
            "'operator' is required",
        ),
    ]


def test_validate_fact_condition_invalid_args():
    condition = {"fact": {"some_fact_method": {"args": "invalid"}}}
    assert validate_condition(condition) == [
        InvalidConditionError("*", "Fact is required for this condition"),
        InvalidConditionError(
            "*",
            "'operator' is required",
        ),
    ]


def test_validate_fact_condition_invalid_params():
    condition = {"fact": {"some_fact_method": {"params": "invalid"}}}
    assert validate_condition(condition) == [
        InvalidConditionError("*", "Fact is required for this condition"),
        InvalidConditionError(
            "*",
            "'operator' is required",
        ),
    ]


def test_validate_fact_condition_missing_method():
    condition = {"fact": "invalid_fact_method", "operator": "is_none"}
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*",
            "Fact method 'invalid_fact_method' is not defined in 'MockFact'",
        )
    ]
    condition = {"fact": "invalid_fact_method", "operator": "is_none"}
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*",
            "Fact method 'invalid_fact_method' is not defined in 'MockFact'",
        )
    ]

    condition = {"operator": "is_none"}
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError("*", "Fact method name is required")
    ]


def test_validate_fact_condition_invalid_operator():
    condition = {"fact": "some_fact_method", "operator": "invalid_operator"}
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError("*", "Operator 'invalid_operator' is not defined."),
    ]


def test_validate_fact_condition_dict_with_multiple_keys():
    """Test that fact dictionary with multiple keys is invalid."""
    condition = {
        "fact": {"method1": {"param1": "value1"}, "method2": {"param2": "value2"}},
        "operator": "is_true",
    }
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError("*", "Fact dictionary must contain exactly one key")
    ]


def test_validate_fact_condition_dict_with_empty_dict():
    """Test that fact dictionary with empty dict is invalid."""
    condition = {"fact": {}, "operator": "is_true"}
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError("*", "Fact dictionary must contain exactly one key")
    ]


def test_validate_fact_condition_dict_with_single_key():
    """Test that fact dictionary with single key is valid."""
    condition = {
        "fact": {"value_method": {"value": 42}},
        "operator": "equal_to",
        "value": 42,
    }
    assert validate_condition(condition, MockFact) == []


def test_validate_fact_condition_dict_with_single_key_no_fact():
    """Test that fact dictionary with single key is valid even without fact object."""
    condition = {
        "fact": {"value_method": {"value": 42}},
        "operator": "equal_to",
        "value": 42,
    }
    assert validate_condition(condition) == [
        InvalidConditionError("*", "Fact is required for this condition")
    ]


def test_validate_fact_condition_parameter_validation():
    """Test parameter validation against fact method signatures."""

    # Test method with no parameters - should reject parameters
    condition = {"fact": {"some_fact_method": {"value": 42}}, "operator": "is_true"}
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*",
            "Method 'some_fact_method' of class 'MockFact' does not accept any parameters, but received: ['value'].",
        )
    ]

    # Test method with required parameter - should require it
    condition = {"fact": "required_param_method", "operator": "is_true"}
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*",
            "Missing required parameter 'required_param' for method 'required_param_method' of class 'MockFact'. Required parameters: ['required_param'].",
        )
    ]

    # Test method with required parameter - should accept it
    condition = {
        "fact": {"required_param_method": {"required_param": 42}},
        "operator": "is_true",
    }
    assert validate_condition(condition, MockFact) == []

    # Test method with optional parameter - should work without it
    condition = {"fact": "optional_param_method", "operator": "is_true"}
    assert validate_condition(condition, MockFact) == []

    # Test method with optional parameter - should accept it
    condition = {
        "fact": {"optional_param_method": {"optional_param": 42}},
        "operator": "is_true",
    }
    assert validate_condition(condition, MockFact) == []

    # Test method with mixed parameters - should require the required one
    condition = {"fact": "mixed_params_method", "operator": "is_true"}
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*",
            "Missing required parameter 'required_param' for method 'mixed_params_method' of class 'MockFact'. Required parameters: ['required_param'].",
        )
    ]

    # Test method with mixed parameters - should work with required parameter
    condition = {
        "fact": {"mixed_params_method": {"required_param": 42}},
        "operator": "is_true",
    }
    assert validate_condition(condition, MockFact) == []

    # Test method with mixed parameters - should work with both parameters
    condition = {
        "fact": {"mixed_params_method": {"required_param": 42, "optional_param": 100}},
        "operator": "is_true",
    }
    assert validate_condition(condition, MockFact) == []

    # Test unknown parameter
    condition = {"fact": {"value_method": {"unknown_param": 42}}, "operator": "is_true"}
    assert validate_condition(condition, MockFact) == []

    # Test positional-only parameter passed as keyword
    condition = {
        "fact": {"positional_only_method": {"param": 42}},
        "operator": "is_true",
    }
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*",
            "Parameter 'param' in method 'positional_only_method' of class 'MockFact' is positional-only and cannot be passed as a keyword argument.",
        )
    ]

    # Test keyword-only parameter - should require it
    condition = {"fact": "keyword_only_method", "operator": "is_true"}
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*",
            "Missing required parameter 'param' for method 'keyword_only_method' of class 'MockFact'. Required parameters: ['param'].",
        )
    ]

    # Test keyword-only parameter - should accept it
    condition = {"fact": {"keyword_only_method": {"param": 42}}, "operator": "is_true"}
    assert validate_condition(condition, MockFact) == []


def test_evaluate_condition_boolean():
    assert evaluate_condition(None, True) is True
    assert evaluate_condition(None, False) is False


def test_evaluate_condition_string():
    assert evaluate_condition(None, "true") is True
    assert evaluate_condition(None, "false") is False
    with pytest.raises(InvalidConditionError):
        evaluate_condition(None, "invalid")


def test_evaluate_invalid_type():
    with pytest.raises(InvalidConditionError):
        evaluate_condition(None, 123)  # type: ignore


def test_evaluate_condition_all():
    condition = {"all": [True, "true"]}
    assert evaluate_condition(None, condition) is True

    condition = {"all": [True, False]}
    assert evaluate_condition(None, condition) is False


def test_evaluate_condition_any():
    condition = {"any": [False, "true"]}
    assert evaluate_condition(None, condition) is True

    condition = {"any": [False, False]}
    assert evaluate_condition(None, condition) is False


def test_evaluate_condition_not():
    condition = {"not": True}
    assert evaluate_condition(None, condition) is False

    condition = {"not": False}
    assert evaluate_condition(None, condition) is True


def test_evaluate_condition_fact_method():
    fact = MockFact()
    condition = {"fact": "true_method", "operator": "is_true"}
    assert evaluate_condition(fact, condition) is True

    condition = {"fact": "false_method", "operator": "is_true"}
    assert evaluate_condition(fact, condition) is False


def test_evaluate_condition_fact_method_with_args():
    fact = MockFact()
    condition = {
        "fact": {"value_method": {"value": 42}},
        "operator": "equal_to",
        "value": 42,
    }
    assert evaluate_condition(fact, condition) is True

    condition = {
        "fact": "value_method",
        "operator": "equal_to",
        "params": {"value": 42},
        "value": 43,
    }
    assert evaluate_condition(fact, condition) is False


def test_evaluate_condition_fact_dict_with_multiple_keys():
    """Test that evaluate_condition raises error when fact dict has multiple keys."""
    fact = MockFact()
    condition = {
        "fact": {"method1": {"param1": "value1"}, "method2": {"param2": "value2"}},
        "operator": "is_true",
    }
    with pytest.raises(
        InvalidConditionError, match="Fact dictionary must contain exactly one key"
    ):
        evaluate_condition(fact, condition)


def test_evaluate_condition_fact_dict_with_empty_dict():
    """Test that evaluate_condition raises error when fact dict is empty."""
    fact = MockFact()
    condition = {"fact": {}, "operator": "is_true"}
    with pytest.raises(
        InvalidConditionError, match="Fact dictionary must contain exactly one key"
    ):
        evaluate_condition(fact, condition)


def test_validate_parameter_value_type_validation():
    """Test that parameter values are validated against their type annotations."""

    # Test string parameter validation
    condition = {"fact": {"string_param_method": {"text": 123}}, "operator": "is_true"}
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*",
            "Parameter 'text' in method 'string_param_method' of class 'MockFact' expects a string, but got int.",
        )
    ]

    # Test int parameter validation
    condition = {
        "fact": {"int_param_method": {"number": "not_a_number"}},
        "operator": "is_true",
    }
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*",
            "Parameter 'number' in method 'int_param_method' of class 'MockFact' expects an integer, but got str.",
        )
    ]

    # Test float parameter validation
    condition = {
        "fact": {"float_param_method": {"value": "not_a_float"}},
        "operator": "is_true",
    }
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*",
            "Parameter 'value' in method 'float_param_method' of class 'MockFact' expects a number, but got str.",
        )
    ]

    # Test bool parameter validation
    condition = {
        "fact": {"bool_param_method": {"flag": "not_a_bool"}},
        "operator": "is_true",
    }
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*",
            "Parameter 'flag' in method 'bool_param_method' of class 'MockFact' expects a boolean, but got str.",
        )
    ]

    # Test list parameter validation
    condition = {
        "fact": {"list_param_method": {"items": "not_a_list"}},
        "operator": "is_true",
    }
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*",
            "Parameter 'items' in method 'list_param_method' of class 'MockFact' expects a list, but got str.",
        )
    ]

    # Test dict parameter validation
    condition = {
        "fact": {"dict_param_method": {"data": "not_a_dict"}},
        "operator": "is_true",
    }
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*",
            "Parameter 'data' in method 'dict_param_method' of class 'MockFact' expects a dictionary, but got str.",
        )
    ]


def test_validate_parameter_value_constraints():
    """Test that parameter values are validated against common constraints."""

    # Test empty string validation
    condition = {"fact": {"string_param_method": {"text": ""}}, "operator": "is_true"}
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*",
            "Parameter 'text' in method 'string_param_method' of class 'MockFact' cannot be an empty string.",
        )
    ]

    # Test empty list validation
    condition = {"fact": {"list_param_method": {"items": []}}, "operator": "is_true"}
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*",
            "Parameter 'items' in method 'list_param_method' of class 'MockFact' cannot be an empty list.",
        )
    ]

    # Test empty dict validation
    condition = {"fact": {"dict_param_method": {"data": {}}}, "operator": "is_true"}
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*",
            "Parameter 'data' in method 'dict_param_method' of class 'MockFact' cannot be an empty dict.",
        )
    ]

    # Test negative count validation (should now pass)
    condition = {"fact": {"count_param_method": {"count": -1}}, "operator": "is_true"}
    assert validate_condition(condition, MockFact) == []

    # Test negative size validation (should now pass)
    condition = {"fact": {"size_param_method": {"size": -5}}, "operator": "is_true"}
    assert validate_condition(condition, MockFact) == []


def test_validate_parameter_value_valid_cases():
    """Test that valid parameter values pass validation."""

    # Test valid string
    condition = {
        "fact": {"string_param_method": {"text": "valid_text"}},
        "operator": "is_true",
    }
    assert validate_condition(condition, MockFact) == []

    # Test valid int
    condition = {"fact": {"int_param_method": {"number": 42}}, "operator": "is_true"}
    assert validate_condition(condition, MockFact) == []

    # Test valid float
    condition = {"fact": {"float_param_method": {"value": 3.14}}, "operator": "is_true"}
    assert validate_condition(condition, MockFact) == []

    # Test valid bool
    condition = {"fact": {"bool_param_method": {"flag": True}}, "operator": "is_true"}
    assert validate_condition(condition, MockFact) == []

    # Test valid list
    condition = {
        "fact": {"list_param_method": {"items": [1, 2, 3]}},
        "operator": "is_true",
    }
    assert validate_condition(condition, MockFact) == []

    # Test valid dict
    condition = {
        "fact": {"dict_param_method": {"data": {"key": "value"}}},
        "operator": "is_true",
    }
    assert validate_condition(condition, MockFact) == []

    # Test valid positive count
    condition = {"fact": {"count_param_method": {"count": 5}}, "operator": "is_true"}
    assert validate_condition(condition, MockFact) == []

    # Test valid positive size
    condition = {"fact": {"size_param_method": {"size": 10}}, "operator": "is_true"}
    assert validate_condition(condition, MockFact) == []


def test_validate_parameter_value_no_annotation():
    """Test that parameters without type annotations don't trigger validation errors."""

    # Test unannotated parameter with any value
    condition = {
        "fact": {"value_method": {"value": "any_value"}},
        "operator": "is_true",
    }
    assert validate_condition(condition, MockFact) == []

    condition = {"fact": {"value_method": {"value": 123}}, "operator": "is_true"}
    assert validate_condition(condition, MockFact) == []

    condition = {"fact": {"value_method": {"value": [1, 2, 3]}}, "operator": "is_true"}
    assert validate_condition(condition, MockFact) == []


def test_validate_parameter_value_instantiable_class():
    """Test that classes that can be instantiated from values are considered valid."""

    # Test LengthUnit can be instantiated from string
    condition = {
        "fact": {"length_unit_method": {"length": "10cm"}},
        "operator": "is_true",
    }
    assert validate_condition(condition, MockFact) == []

    # Test LengthUnit can be instantiated from number
    condition = {
        "fact": {"length_unit_method": {"length": 5.5}},
        "operator": "is_true",
    }
    assert validate_condition(condition, MockFact) == []

    # Test LengthUnit with invalid string should fail
    condition = {
        "fact": {"length_unit_method": {"length": "invalid"}},
        "operator": "is_true",
    }
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*",
            "Parameter 'length' in method 'length_unit_method' of class 'MockFact' expects LengthUnit or a value that can be converted to LengthUnit, but got str.",
        )
    ]

    # Test LengthUnit with wrong type should fail
    condition = {
        "fact": {"length_unit_method": {"length": [1, 2, 3]}},
        "operator": "is_true",
    }
    assert validate_condition(condition, MockFact) == [
        InvalidConditionError(
            "*",
            "Parameter 'length' in method 'length_unit_method' of class 'MockFact' expects LengthUnit or a value that can be converted to LengthUnit, but got list.",
        )
    ]


def test_validate_parameter_value_union_and_optional():
    """Test that Union and Optional types are validated correctly."""
    from typing import Optional, Union

    class UnionFact:
        def union_method(self, value: Union[int, str]):
            return value

        def optional_method(self, value: Optional[int]):
            return value

    # Union[int, str]: int is valid
    condition = {"fact": {"union_method": {"value": 42}}, "operator": "is_true"}
    assert validate_condition(condition, UnionFact) == []
    # Union[int, str]: str is valid
    condition = {"fact": {"union_method": {"value": "foo"}}, "operator": "is_true"}
    assert validate_condition(condition, UnionFact) == []
    # Union[int, str]: float is not valid
    condition = {"fact": {"union_method": {"value": 3.14}}, "operator": "is_true"}
    assert validate_condition(condition, UnionFact) == [
        InvalidConditionError(
            "*",
            "Parameter 'value' in method 'union_method' of class 'UnionFact' expects one of ['int', 'str'], but got float.",
        )
    ]
    # Optional[int]: int is valid
    condition = {"fact": {"optional_method": {"value": 7}}, "operator": "is_true"}
    assert validate_condition(condition, UnionFact) == []
    # Optional[int]: None is valid
    condition = {"fact": {"optional_method": {"value": None}}, "operator": "is_true"}
    assert validate_condition(condition, UnionFact) == []
    # Optional[int]: str is not valid
    condition = {"fact": {"optional_method": {"value": "bad"}}, "operator": "is_true"}
    assert validate_condition(condition, UnionFact) == [
        InvalidConditionError(
            "*",
            "Parameter 'value' in method 'optional_method' of class 'UnionFact' expects one of ['int', 'NoneType'], but got str.",
        )
    ]


def test_validate_parameter_value_pep604_union():
    """Test that PEP 604 union types (e.g., int | str) are validated correctly."""

    class PEP604Fact:
        def union_method(self, value: int | str):
            return value

        def optional_method(self, value: int | None):
            return value

    # int | str: int is valid
    condition = {"fact": {"union_method": {"value": 42}}, "operator": "is_true"}
    assert validate_condition(condition, PEP604Fact) == []
    # int | str: str is valid
    condition = {"fact": {"union_method": {"value": "foo"}}, "operator": "is_true"}
    assert validate_condition(condition, PEP604Fact) == []
    # int | str: float is not valid
    condition = {"fact": {"union_method": {"value": 3.14}}, "operator": "is_true"}
    assert validate_condition(condition, PEP604Fact) == [
        InvalidConditionError(
            "*",
            "Parameter 'value' in method 'union_method' of class 'PEP604Fact' expects one of ['int', 'str'], but got float.",
        )
    ]
    # int | None: int is valid
    condition = {"fact": {"optional_method": {"value": 7}}, "operator": "is_true"}
    assert validate_condition(condition, PEP604Fact) == []
    # int | None: None is valid
    condition = {"fact": {"optional_method": {"value": None}}, "operator": "is_true"}
    assert validate_condition(condition, PEP604Fact) == []
    # int | None: str is not valid
    condition = {"fact": {"optional_method": {"value": "bad"}}, "operator": "is_true"}
    assert validate_condition(condition, PEP604Fact) == [
        InvalidConditionError(
            "*",
            "Parameter 'value' in method 'optional_method' of class 'PEP604Fact' expects one of ['int', 'NoneType'], but got str.",
        )
    ]
