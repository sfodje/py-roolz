import pytest
from roolz import validate_condition, evaluate_condition
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
            "condition", "Condition must be a boolean or a dictionary"
        )
    ]


def test_validate_condition_invalid_type():
    assert validate_condition(123) == [
        InvalidConditionError(
            "condition", "Condition must be a boolean or a dictionary"
        )
    ]


def test_validate_all_condition_empty_list():
    condition = {"all": []}
    assert validate_condition(condition) == [
        InvalidConditionError(
            "condition.all", "'all' must be a list with at least one element"
        )
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
        InvalidConditionError(
            "condition.all[2]", "Condition must be a boolean or a dictionary"
        )
    ]

    condition = {"all": [True, {"any": [False, True, {"fact": "some_fact_method"}]}]}
    assert validate_condition(condition, MockFact()) == [
        InvalidConditionError(
            "condition.all[1].any[2]",
            "'operator' is required",
        )
    ]

    condition = {"all": [True, {"any": [False, True, {"fact": "some_fact_method"}]}]}
    assert validate_condition(condition) == [
        InvalidConditionError(
            "condition.all[1].any[2]", "Fact is required for this condition"
        ),
        InvalidConditionError(
            "condition.all[1].any[2]",
            "'operator' is required",
        ),
    ]


def test_validate_any_condition_empty_list():
    condition = {"any": []}
    assert validate_condition(condition) == [
        InvalidConditionError(
            "condition.any", "'any' must be a list with at least one element"
        )
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
        InvalidConditionError(
            "condition.any[2]", "Condition must be a boolean or a dictionary"
        )
    ]

    condition = {"any": [True, {"all": [False, True, {"fact": "some_fact_method"}]}]}
    assert validate_condition(condition, MockFact()) == [
        InvalidConditionError(
            "condition.any[1].all[2]",
            "'operator' is required",
        )
    ]

    condition = {"any": [True, {"all": [False, True, {"fact": "some_fact_method"}]}]}
    assert validate_condition(condition) == [
        InvalidConditionError(
            "condition.any[1].all[2]", "Fact is required for this condition"
        ),
        InvalidConditionError(
            "condition.any[1].all[2]",
            "'operator' is required",
        ),
    ]


def test_validate_not_condition_valid():
    condition = {"not": True}
    assert validate_condition(condition) == []


def test_validate_fact_condition_missing_fact():
    condition = {"fact": "some_fact_method"}
    assert validate_condition(condition) == [
        InvalidConditionError("condition", "Fact is required for this condition"),
        InvalidConditionError(
            "condition",
            "'operator' is required",
        ),
    ]


def test_validate_fact_condition_invalid_keys():
    condition = {"fact": "some_fact_method", "invalid_key": "value"}
    assert validate_condition(condition) == [
        InvalidConditionError("condition", "Fact is required for this condition"),
        InvalidConditionError("condition", "Invalid keys: invalid_key"),
        InvalidConditionError(
            "condition",
            "'operator' is required",
        ),
    ]


def test_validate_fact_condition_invalid_args():
    condition = {"fact": "some_fact_method", "args": "invalid"}
    assert validate_condition(condition) == [
        InvalidConditionError("condition", "Fact is required for this condition"),
        InvalidConditionError(
            "condition",
            "'operator' is required",
        ),
        InvalidConditionError("condition", "'args' must be a list"),
    ]


def test_validate_fact_condition_invalid_params():
    condition = {"fact": "some_fact_method", "params": "invalid"}
    assert validate_condition(condition) == [
        InvalidConditionError("condition", "Fact is required for this condition"),
        InvalidConditionError(
            "condition",
            "'operator' is required",
        ),
        InvalidConditionError("condition", "'params' must be a dictionary"),
    ]


def test_validate_fact_condition_missing_method():
    condition = {"fact": "invalid_fact_method", "operator": "is_none"}
    assert validate_condition(condition, MockFact()) == [
        InvalidConditionError(
            "condition",
            "Fact method 'invalid_fact_method' is not defined in 'MockFact'",
        )
    ]
    condition = {"fact": "invalid_fact_method", "operator": "is_none"}
    assert validate_condition(condition, MockFact()) == [
        InvalidConditionError(
            "condition",
            "Fact method 'invalid_fact_method' is not defined in 'MockFact'",
        )
    ]

    condition = {"operator": "is_none"}
    assert validate_condition(condition, MockFact()) == [
        InvalidConditionError("condition", "Fact method name is required")
    ]


def test_validate_fact_condition_invalid_operator():
    condition = {"fact": "some_fact_method", "operator": "invalid_operator"}
    assert validate_condition(condition, MockFact()) == [
        InvalidConditionError(
            "condition", "Operator 'invalid_operator' is not defined."
        ),
    ]


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
        evaluate_condition(None, 123)


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
        "fact": "value_method",
        "operator": "equal_to",
        "params": {"value": 42},
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
