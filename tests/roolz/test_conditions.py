import pytest

from roolz import evaluate_condition, validate_condition
from roolz.errors import InvalidConditionError


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


def test_validate_condition_boolean():
    assert validate_condition(True) == []
    assert validate_condition(False) == []


def test_validate_condition_string():
    assert validate_condition("true") == []
    assert validate_condition("true()") == []
    assert validate_condition("false") == []
    assert validate_condition("false()") == []
    assert validate_condition("invalid") == [
        InvalidConditionError("*", "Condition must be a boolean or a dictionary")
    ]


def test_validate_condition_invalid_type():
    assert validate_condition(123) == [  # type: ignore
        InvalidConditionError("*", "Condition must be a boolean or a dictionary")
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
