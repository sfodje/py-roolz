import inspect
from typing import Iterable, List, Type, Union, get_origin, get_args
import types

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

    keys = tuple(condition.keys())

    # Handle logical operators
    if keys == ("all",):
        return all(evaluate_condition(fact, cond) for cond in condition["all"])
    elif keys == ("any",):
        return any(evaluate_condition(fact, cond) for cond in condition["any"])
    elif keys == ("not",):
        return not evaluate_condition(fact, condition["not"])

    # Handle fact-based conditions
    elif "fact" in condition:
        return _evaluate_fact_condition(fact, condition)

    # If we get here, the condition format is invalid
    else:
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
    args = condition.get("args", [])
    params = condition.get("params", {})

    # Handle string-based facts
    if isinstance(fact_dict, str):
        if fact_dict in {"true", "true()"}:
            return True
        if fact_dict in {"false", "false()"}:
            return False
        fact_method_name = fact_dict
    # Handle dictionary-based facts
    elif isinstance(fact_dict, dict):
        if len(fact_dict) != 1:
            raise InvalidConditionError(
                "", "Fact dictionary must contain exactly one key"
            )
        fact_method_name, fact_params = next(iter(fact_dict.items()))
        if isinstance(fact_params, list):
            args = fact_params
            params = {}
        elif isinstance(fact_params, dict):
            params = fact_params
            args = []
        else:
            args = []
            params = {}
    else:
        raise InvalidConditionError("", "'fact' must be a string or a dictionary")

    # Get the fact method and operator
    try:
        fact_method = getattr(fact, fact_method_name)
    except AttributeError:
        raise AttributeError(
            f"Fact method '{fact_method_name}' not found on {type(fact).__name__}"
        )

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

    keys = tuple(condition.keys())
    if keys == ("all",):
        return __validate_all_condition(condition, path, fact)
    elif keys == ("any",):
        return __validate_any_condition(condition, path, fact)
    elif keys == ("not",):
        return __validate_not_condition(condition, path, fact)
    elif "fact" in condition or "operator" in condition:
        return __validate_fact_condition(condition, path, fact)
    else:
        return [InvalidConditionError(path, "Invalid condition format")]


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
    fact_method_name, params, args = _extract_fact_info(
        condition, path, validation_errors
    )

    # Validate fact method exists and parameters
    if fact and fact_method_name:
        if not hasattr(fact, fact_method_name):
            validation_errors.append(
                InvalidConditionError(
                    path,
                    f"Fact method '{fact_method_name}' is not defined in '{fact.__name__}'",
                )
            )
        else:
            # Validate parameters against method signature
            param_errors = _validate_fact_parameters(
                fact, fact_method_name, params, args, path
            )
            validation_errors.extend(param_errors)

    return validation_errors


def _validate_fact_parameters(
    fact: Type, fact_method_name: str, params: dict, args: list, path: str
) -> List[InvalidConditionError]:
    """
    Validate that the provided parameters match the fact method signature.

    Args:
        fact: The fact class type
        fact_method_name: Name of the fact method
        params: Dictionary of keyword parameters
        args: List of positional arguments
        path: Current validation path for error reporting

    Returns:
        List of validation errors
    """
    validation_errors = []

    try:
        # Get the method from the class
        method = getattr(fact, fact_method_name)
        class_name = fact.__name__

        # Skip validation for special cases
        if fact_method_name in ["is_true", "is_false"]:
            return validation_errors

        # Get method signature
        sig = inspect.signature(method)
        parameters = sig.parameters

        # Remove 'self' parameter for instance methods
        if parameters and list(parameters.keys())[0] == "self":
            parameters = {k: v for k, v in parameters.items() if k != "self"}

        # Check if method accepts any parameters
        if not parameters:
            if params or args:
                received = list(params.keys()) + [
                    f"positional arg {i+1}" for i in range(len(args))
                ]
                validation_errors.append(
                    InvalidConditionError(
                        path,
                        f"Method '{fact_method_name}' of class '{class_name}' does not accept any parameters, but received: {received}.",
                    )
                )
            return validation_errors

        # Check if method accepts arbitrary positional/keyword arguments
        has_args = any(
            param.kind == inspect.Parameter.VAR_POSITIONAL
            for param in parameters.values()
        )
        has_kwargs = any(
            param.kind == inspect.Parameter.VAR_KEYWORD for param in parameters.values()
        )

        # Validate positional arguments
        if args:
            # Pre-compute parameter lists for efficiency
            required_pos_params = [
                param.name
                for param in parameters.values()
                if param.default == inspect.Parameter.empty
                and param.kind
                in [
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                ]
            ]
            non_var_pos_params = [
                param.name
                for param in parameters.values()
                if param.kind
                in [
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                ]
            ]
            keyword_params = [
                p
                for p in parameters.keys()
                if parameters[p].kind
                in [
                    inspect.Parameter.KEYWORD_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                ]
            ]
            
            if not has_args and len(args) > len(non_var_pos_params):
                validation_errors.append(
                    InvalidConditionError(
                        path,
                        f"Too many positional arguments for method '{fact_method_name}' of class '{class_name}': expected at most {len(non_var_pos_params)}, got {len(args)}. Allowed positional parameters: {non_var_pos_params}.",
                    )
                )
            elif len(args) < len(required_pos_params):
                validation_errors.append(
                    InvalidConditionError(
                        path,
                        f"Missing required positional arguments for method '{fact_method_name}' of class '{class_name}': expected at least {len(required_pos_params)}, got {len(args)}. Required positional parameters: {required_pos_params}.",
                    )
                )
            else:
                # Validate positional argument values
                param_names = list(parameters.keys())
                for i, (arg_value, param_name) in enumerate(zip(args, param_names)):
                    param = parameters[param_name]
                    value_errors = _validate_parameter_value(
                        param,
                        arg_value,
                        param_name,
                        fact_method_name,
                        class_name,
                        f"{path}[{i}]",
                    )
                    validation_errors.extend(value_errors)

        # Validate keyword arguments
        if params:
            for param_name, param_value in params.items():
                if param_name not in parameters and not has_kwargs:
                    validation_errors.append(
                        InvalidConditionError(
                            path,
                            f"Unknown parameter '{param_name}' for method '{fact_method_name}' of class '{class_name}'. Allowed parameters: {keyword_params}.",
                        )
                    )
                elif param_name in parameters:
                    param = parameters[param_name]
                    if param.kind == inspect.Parameter.POSITIONAL_ONLY:
                        validation_errors.append(
                            InvalidConditionError(
                                path,
                                f"Parameter '{param_name}' in method '{fact_method_name}' of class '{class_name}' is positional-only and cannot be passed as a keyword argument.",
                            )
                        )
                    else:
                        # Validate parameter value
                        value_errors = _validate_parameter_value(
                            param,
                            param_value,
                            param_name,
                            fact_method_name,
                            class_name,
                            path,
                        )
                        validation_errors.extend(value_errors)

        # Check for missing required keyword parameters
        required_params = [
            p for p in parameters.keys() 
            if parameters[p].default == inspect.Parameter.empty
        ]
        for param_name, param in parameters.items():
            if (
                param.default == inspect.Parameter.empty
                and param.kind
                in [
                    inspect.Parameter.KEYWORD_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                ]
                and param_name not in params
                and param_name
                not in [
                    p.name
                    for p in sig.parameters.values()
                    if p.kind == inspect.Parameter.VAR_POSITIONAL
                ]
            ):
                validation_errors.append(
                    InvalidConditionError(
                        path,
                        f"Missing required parameter '{param_name}' for method '{fact_method_name}' of class '{class_name}'. Required parameters: {required_params}.",
                    )
                )

    except (AttributeError, ValueError) as e:
        validation_errors.append(
            InvalidConditionError(
                path,
                f"Error validating parameters for method '{fact_method_name}' of class '{fact.__name__}': {str(e)}",
            )
        )

    return validation_errors


def _validate_parameter_value(
    param: inspect.Parameter,
    value: object,
    param_name: str,
    method_name: str,
    class_name: str,
    path: str,
) -> List[InvalidConditionError]:
    """
    Validate a parameter value against its type annotation and constraints.

    Args:
        param: The parameter object from inspect.signature
        value: The value to validate
        param_name: Name of the parameter
        method_name: Name of the method
        class_name: Name of the class
        path: Current validation path for error reporting

    Returns:
        List of validation errors
    """
    validation_errors = []

    # Skip validation if parameter accepts any type (Any annotation or no annotation)
    if param.annotation == inspect.Parameter.empty:
        return validation_errors

    try:
        # Basic type validation
        if param.annotation != inspect.Parameter.empty:
            annotation = param.annotation
            origin = get_origin(annotation)
            args = get_args(annotation)
            # Handle Union types (including Optional and PEP 604)
            if (origin is Union or origin is types.UnionType) and args:
                union_errors = []
                for union_type in args:
                    # Special case: NoneType
                    if union_type is type(None):
                        if value is None:
                            break
                        else:
                            continue
                    # Try normal validation for this type
                    try:
                        # Handle common types
                        if union_type is str:
                            if isinstance(value, str):
                                break
                        elif union_type is int:
                            if isinstance(value, int):
                                break
                        elif union_type is float:
                            if isinstance(value, (int, float)):
                                break
                        elif union_type is bool:
                            if isinstance(value, bool):
                                break
                        elif union_type is list:
                            if isinstance(value, list):
                                break
                        elif union_type is dict:
                            if isinstance(value, dict):
                                break
                        else:
                            if isinstance(value, union_type):
                                break
                            try:
                                union_type(value)
                                break
                            except Exception as e:
                                union_errors.append(e)
                    except Exception as e:
                        union_errors.append(e)
                else:
                    # If we never broke, value is not valid for any type in the union
                    validation_errors.append(
                        InvalidConditionError(
                            path,
                            f"Parameter '{param_name}' in method '{method_name}' of class '{class_name}' expects one of [{', '.join(repr(_get_type_name(t)) for t in args)}], but got {type(value).__name__}."
                        )
                    )
            else:
                # Handle common type annotations
                if annotation is str:
                    if not isinstance(value, str):
                        validation_errors.append(
                            InvalidConditionError(
                                path,
                                f"Parameter '{param_name}' in method '{method_name}' of class '{class_name}' expects a string, but got {type(value).__name__}."
                            )
                        )
                elif annotation is int:
                    if not isinstance(value, int):
                        validation_errors.append(
                            InvalidConditionError(
                                path,
                                f"Parameter '{param_name}' in method '{method_name}' of class '{class_name}' expects an integer, but got {type(value).__name__}."
                            )
                        )
                elif annotation is float:
                    if not isinstance(value, (int, float)):
                        validation_errors.append(
                            InvalidConditionError(
                                path,
                                f"Parameter '{param_name}' in method '{method_name}' of class '{class_name}' expects a number, but got {type(value).__name__}."
                            )
                        )
                elif annotation is bool:
                    if not isinstance(value, bool):
                        validation_errors.append(
                            InvalidConditionError(
                                path,
                                f"Parameter '{param_name}' in method '{method_name}' of class '{class_name}' expects a boolean, but got {type(value).__name__}."
                            )
                        )
                elif annotation is list:
                    if not isinstance(value, list):
                        validation_errors.append(
                            InvalidConditionError(
                                path,
                                f"Parameter '{param_name}' in method '{method_name}' of class '{class_name}' expects a list, but got {type(value).__name__}."
                            )
                        )
                elif annotation is dict:
                    if not isinstance(value, dict):
                        validation_errors.append(
                            InvalidConditionError(
                                path,
                                f"Parameter '{param_name}' in method '{method_name}' of class '{class_name}' expects a dictionary, but got {type(value).__name__}."
                            )
                        )
                else:
                    # For other types, try to check if the value is an instance
                    try:
                        if not isinstance(value, annotation):
                            # Try to instantiate the class from the value
                            try:
                                annotation(value)
                            except (TypeError, ValueError, Exception):
                                validation_errors.append(
                                    InvalidConditionError(
                                        path,
                                        f"Parameter '{param_name}' in method '{method_name}' of class '{class_name}' expects {annotation.__name__} or a value that can be converted to {annotation.__name__}, but got {type(value).__name__}."
                                    )
                                )
                    except TypeError:
                        # If isinstance fails (e.g., for special typing types), skip type validation
                        pass
        # Basic value validation for common types
        if isinstance(value, str) and value.strip() == "":
            validation_errors.append(
                InvalidConditionError(
                    path,
                    f"Parameter '{param_name}' in method '{method_name}' of class '{class_name}' cannot be an empty string."
                )
            )
        elif isinstance(value, (list, dict)) and len(value) == 0:
            validation_errors.append(
                InvalidConditionError(
                    path,
                    f"Parameter '{param_name}' in method '{method_name}' of class '{class_name}' cannot be an empty {type(value).__name__}."
                )
            )
    except Exception as e:
        # If validation fails for any reason, add a generic error
        validation_errors.append(
            InvalidConditionError(
                path,
                f"Error validating parameter '{param_name}' in method '{method_name}' of class '{class_name}': {str(e)}"
            )
        )
    return validation_errors


def _get_type_name(t):
    try:
        return t.__name__
    except AttributeError:
        # For NoneType and others
        if t is type(None):
            return 'NoneType'
        return str(t)


def _extract_fact_info(
    condition: dict, path: str, validation_errors: List[InvalidConditionError]
) -> tuple[str | None, dict, list]:
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
        if len(fact_dict) != 1:
            validation_errors.append(
                InvalidConditionError(
                    path, "Fact dictionary must contain exactly one key"
                )
            )
            return None, {}, []

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
