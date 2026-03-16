from typing import Iterable, List, Type, Union

from roolz._operators import get_operator
from roolz.errors import InvalidConditionError, UndefinedOperatorError


def evaluate_condition(fact: object, condition: Union[dict, str, bool]) -> bool:
    """
    Evaluate a condition against a fact object.
    
    Args:
        fact: The object to evaluate the condition against
        condition: The condition to evaluate (boolean, string, or dict)
        
    Returns:
        bool: True if condition is met, False otherwise
        
    Raises:
        InvalidConditionError: If the condition format is invalid
        AttributeError: If the fact method doesn't exist
    """
    if isinstance(condition, bool):
        return condition

    if isinstance(condition, str):
        condition_lower = condition.lower()
        if condition_lower in ["true", "true()"]:
            return True
        if condition_lower in ["false", "false()"]:
            return False
        raise InvalidConditionError("", "Invalid condition")

    if not isinstance(condition, dict):
        raise InvalidConditionError("", "Condition must be a boolean or a dictionary")

    keys = list(condition.keys())
    
    # Handle logical operators
    if keys == ["all"]:
        return all(evaluate_condition(fact, cond) for cond in condition["all"])
    elif keys == ["any"]:
        return any(evaluate_condition(fact, cond) for cond in condition["any"])
    elif keys == ["not"]:
        return not evaluate_condition(fact, condition["not"])
    
    # Handle fact-based conditions
    elif "fact" in condition:
        return _evaluate_fact_condition(fact, condition)
    
    # If we get here, the condition format is invalid
    raise InvalidConditionError("", "Invalid condition format")


def _evaluate_fact_condition(fact: object, condition: dict) -> bool:
    """
    Evaluate a fact-based condition.
    
    Args:
        fact: The fact object
        condition: The condition dictionary containing fact, operator, and value
        
    Returns:
        bool: Result of the fact condition evaluation
    """
    fact_dict = condition["fact"]
    
    # Handle string-based facts
    if isinstance(fact_dict, str):
        if fact_dict in ["true", "true()"]:
            return True
        if fact_dict in ["false", "false()"]:
            return False
        
        fact_method_name = fact_dict
        params = {}
        args = []
    
    # Handle dictionary-based facts
    elif isinstance(fact_dict, dict):
        fact_method_name, params = next(iter(fact_dict.items()))
        if isinstance(params, list):
            args = params
            params = {}
        else:
            args = []
    
    else:
        raise InvalidConditionError("", "'fact' must be a string or a dictionary")
    
    # Get the fact method and operator
    try:
        fact_method = getattr(fact, fact_method_name)
    except AttributeError:
        raise AttributeError(f"Fact method '{fact_method_name}' not found on {type(fact).__name__}")
    
    operator = get_operator(condition["operator"])
    
    # Evaluate the fact method
    if not callable(fact_method):
        fact_value = fact_method
    else:
        fact_value = fact_method(*args, **params)
    
    return operator(fact_value, condition.get("value"))


def validate_condition(
    condition: Union[dict, str, bool], fact: Type | None = None
) -> List[InvalidConditionError]:
    """
    Validate a condition against a fact type.
    
    Args:
        condition: The condition to validate
        fact: The fact type to validate against (optional)
        
    Returns:
        List of validation errors, empty if condition is valid
    """
    return __validate_condition(condition, "*", fact)


def __validate_condition(
    condition: Union[dict, str, bool], path: str, fact: Type | None = None
) -> List[InvalidConditionError]:
    """
    Internal validation function for conditions.
    
    Args:
        condition: The condition to validate
        path: Current validation path for error reporting
        fact: The fact type to validate against
        
    Returns:
        List of validation errors
    """
    if isinstance(condition, bool):
        return []

    if isinstance(condition, str) and condition.lower() in [
        "true", "true()", "false", "false()"
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
    elif "fact" in condition or "operator" in condition:
        return __validate_fact_condition(condition, path, fact)
    else:
        return [
            InvalidConditionError(path, "Invalid condition format")
        ]


def __validate_all_condition(
    condition: dict, path: str, fact: Type | None = None
) -> List[InvalidConditionError]:
    """Validate an 'all' condition."""
    operands = condition["all"]
    new_path = f"{path}.all"
    
    if not isinstance(operands, Iterable) or not operands:
        return [
            InvalidConditionError(
                new_path, "'all' must be a list with at least one element"
            )
        ]

    validation_errors = []
    for i, operand in enumerate(operands):
        new_path = f"{path}.all[{i}]"
        if errors := __validate_condition(operand, new_path, fact):
            validation_errors.extend(errors)
    return validation_errors


def __validate_any_condition(
    condition: dict, path: str, fact: Type | None = None
) -> List[InvalidConditionError]:
    """Validate an 'any' condition."""
    operands = condition["any"]
    new_path = f"{path}.any"
    
    if not isinstance(operands, Iterable) or not operands:
        return [
            InvalidConditionError(
                new_path, "'any' must be a list with at least one element"
            )
        ]

    validation_errors = []
    for i, operand in enumerate(operands):
        new_path = f"{path}.any[{i}]"
        if errors := __validate_condition(operand, new_path, fact):
            validation_errors.extend(errors)
    return validation_errors


def __validate_not_condition(
    condition: dict, path: str, fact: Type | None = None
) -> List[InvalidConditionError]:
    """Validate a 'not' condition."""
    operand = condition["not"]
    new_path = f"{path}.not"
    return __validate_condition(operand, new_path, fact)


def __validate_fact_condition(
    condition: dict, path: str, fact: Type | None
) -> List[InvalidConditionError]:
    """Validate a fact-based condition."""
    validation_errors = []
    
    # Check if fact is required
    if not fact:
        validation_errors.append(
            InvalidConditionError(path, "Fact is required for this condition")
        )

    # Validate keys
    invalid_keys = set(condition.keys()) - {"fact", "operator", "value"}
    if invalid_keys:
        validation_errors.append(
            InvalidConditionError(path, f"Invalid keys: {', '.join(invalid_keys)}")
        )

    # Validate operator
    if not condition.get("operator"):
        validation_errors.append(InvalidConditionError(path, "'operator' is required"))
    else:
        try:
            get_operator(condition["operator"])
        except UndefinedOperatorError as e:
            validation_errors.append(InvalidConditionError(path, str(e)))

    # Validate fact
    fact_method_name, params, args = _extract_fact_info(condition, path, validation_errors)
    
    # Validate fact method exists
    if fact and fact_method_name and not hasattr(fact, fact_method_name):
        validation_errors.append(
            InvalidConditionError(
                path,
                f"Fact method '{fact_method_name}' is not defined in '{fact.__name__}'",
            )
        )

    return validation_errors


def _extract_fact_info(condition: dict, path: str, validation_errors: List[InvalidConditionError]) -> tuple[str | None, dict, list]:
    """
    Extract fact method name, params, and args from condition.
    
    Args:
        condition: The condition dictionary
        path: Current validation path
        validation_errors: List to append validation errors to
        
    Returns:
        Tuple of (fact_method_name, params, args)
    """
    fact_dict = condition.get("fact")
    
    if fact_dict is None:
        validation_errors.append(
            InvalidConditionError(path, "Fact method name is required")
        )
        return None, {}, []
    
    if isinstance(fact_dict, str):
        if fact_dict in ["true", "true()"]:
            return "is_true", {}, []
        elif fact_dict in ["false", "false()"]:
            return "is_false", {}, []
        else:
            return fact_dict, {}, []
    
    elif isinstance(fact_dict, dict):
        fact_method_name, params = next(iter(fact_dict.items()))
        if isinstance(params, list):
            return fact_method_name, {}, params
        else:
            return fact_method_name, params or {}, []
    
    else:
        validation_errors.append(
            InvalidConditionError(path, "'fact' must be a string or a dictionary")
        )
        return None, {}, []
