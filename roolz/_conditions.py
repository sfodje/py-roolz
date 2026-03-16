from typing import Iterable

from roolz._operators import get_operator
from roolz.errors import InvalidConditionError, UndefinedOperatorError


def evaluate_condition(fact: object, condition: dict | str | bool) -> bool:
    if isinstance(condition, bool):
        return condition

    if v := isinstance(condition, str) and condition.lower():
        if v in ["true", "true()"]:
            return True

        if v in ["false", "false()"]:
            return False

        raise InvalidConditionError("", "Invalid condition")

    if not isinstance(condition, dict):
        raise InvalidConditionError("", "Condition must be a boolean or a dictionary")

    keys = list(condition.keys())
    if keys == ["all"]:
        for cond in condition["all"]:
            if not evaluate_condition(fact, cond):
                return False
        return True
    elif keys == ["any"]:
        for cond in condition["any"]:
            if evaluate_condition(fact, cond):
                return True
        return False
    elif keys == ["not"]:
        return not evaluate_condition(fact, condition["not"])
    else:
        fact_method = getattr(fact, condition["fact"])
        operator = get_operator(condition["operator"])
        args = condition.get("args", [])
        params = condition.get("params", {})
        return operator(fact_method(*args, **params), condition.get("value"))


def validate_condition(
    condition: dict | str | bool, fact: object = None
) -> list[InvalidConditionError]:
    return __validate_condition(condition, "condition", fact)


def __validate_condition(
    condition: dict | str | bool, path: str, fact: object = None
) -> list[InvalidConditionError]:
    if isinstance(condition, bool):
        return []

    if isinstance(condition, str) and condition.lower() in [
        "true",
        "true()",
        "false",
        "false()",
    ]:
        return []

    if not isinstance(condition, dict):
        return [
            InvalidConditionError(path, "Condition must be a boolean or a dictionary")
        ]

    keys = list(condition.keys())
    if keys == ["all"]:
        return __validate_all_condition(condition, path, fact)
    elif keys == ["any"]:
        return __validate_any_condition(condition, path, fact)
    elif keys == ["not"]:
        return __validate_not_condition(condition, path, fact)
    else:
        return __validate_fact_condition(condition, path, fact)


def __validate_all_condition(
    condition: dict, path: str, fact: object = None
) -> list[InvalidConditionError]:
    operands = condition["all"]
    new_path = f"{path}.all"
    if not isinstance(operands, Iterable) or not operands:
        return [
            InvalidConditionError(
                new_path, "'all' must be a list with at least one element"
            )
        ]

    validation_errors = list()
    for i, operand in enumerate(operands):
        new_path = f"{path}.all[{i}]"
        if errors := __validate_condition(operand, new_path, fact):
            validation_errors.extend(errors)
    return validation_errors


def __validate_any_condition(
    condition: dict, path: str, fact: object = None
) -> list[InvalidConditionError]:
    operands = condition["any"]
    new_path = f"{path}.any"
    if not isinstance(operands, Iterable) or not operands:
        return [
            InvalidConditionError(
                new_path, "'any' must be a list with at least one element"
            )
        ]

    validation_errors = list()
    for i, operand in enumerate(operands):
        new_path = f"{path}.any[{i}]"
        if errors := __validate_condition(operand, new_path, fact):
            validation_errors.extend(errors)
    return validation_errors


def __validate_not_condition(
    condition: dict, path: str, fact: object = None
) -> list[InvalidConditionError]:
    operand = condition["not"]
    new_path = f"{path}.not"
    return __validate_condition(operand, new_path, fact)


def __validate_fact_condition(
    condition: dict, path: str, fact: object
) -> list[InvalidConditionError]:
    validation_errors = list()
    if not fact:
        validation_errors.append(
            InvalidConditionError(path, "Fact is required for this condition")
        )

    invalid_keys = set(condition.keys()) - {
        "fact",
        "args",
        "params",
        "operator",
        "value",
    }
    if invalid_keys:
        validation_errors.append(
            InvalidConditionError(path, f"Invalid keys: {', '.join(invalid_keys)}")
        )

    if not condition.get("operator"):
        validation_errors.append(InvalidConditionError(path, "'operator' is required"))
    else:
        try:
            get_operator(condition["operator"])
        except UndefinedOperatorError as e:
            validation_errors.append(InvalidConditionError(path, str(e)))

    args = condition.get("args")
    if args and not isinstance(args, list):
        validation_errors.append(InvalidConditionError(path, "'args' must be a list"))

    params = condition.get("params")
    if params and not isinstance(params, dict):
        validation_errors.append(
            InvalidConditionError(path, "'params' must be a dictionary")
        )

    fact_method_name = condition.get("fact")
    if not fact_method_name:
        validation_errors.append(
            InvalidConditionError(path, "Fact method name is required")
        )

    if fact and fact_method_name and not hasattr(fact, fact_method_name):
        validation_errors.append(
            InvalidConditionError(
                path,
                f"Fact method '{fact_method_name}' is not defined in '{fact.__class__.__name__}'",
            )
        )

    return validation_errors
