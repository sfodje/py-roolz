import inspect
import re
from datetime import datetime
from datetime import timezone as tz
from functools import wraps
from inspect import Parameter
from typing import Any, Callable, Iterable, List, Protocol, get_args, runtime_checkable

from roolz.errors import UndefinedOperatorError


@runtime_checkable
class Comparable(Protocol):
    """Protocol for objects that support comparison operations."""
    def __eq__(self, other: object) -> bool: ...
    def __lt__(self, other: object) -> bool: ...
    def __gt__(self, other: object) -> bool: ...
    def __le__(self, other: object) -> bool: ...
    def __ge__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...


# Type aliases
Operator = Callable[[Any, Any | None], bool]
BinaryOperator = Callable[[Any, Any], bool]
CmpType = int | float | str | Comparable
RawType = int | float | str | bool | Iterable | Comparable | None

# Registry to store operator functions
__operator_registry: dict[str, Operator] = {}

# Registry to store parameter type annotations for operator functions
__operator_annotations: dict[str, List[type]] = {}


def operator(name: str | None = None):
    """
    Decorator to register a custom operator function.
    
    Args:
        name (str): The name of the operator to register
        
    Example:
        @operator("is_even")
        def is_even(left_operand: int, right_operand: Any | None = None) -> bool:
            return left_operand % 2 == 0
    """
    def decorator(func: Callable) -> Callable:
        operator_name = name or func.__name__
        register_operator(operator_name, func)
        return func
    return decorator


def __validate_operands(func: Operator) -> Operator:
    """
    Decorator to validate operand types for operator functions.
    
    Args:
        func: The operator function to validate
        
    Returns:
        Wrapped function with type validation
    """
    name = func.__name__

    @wraps(func)
    def wrapper(left_operand: Any, right_operand: Any | None = None) -> bool:
        if name not in __operator_annotations:
            return func(left_operand, right_operand)

        annotations = __operator_annotations[name]
        for i, (operand, annotation) in enumerate(
            zip((left_operand, right_operand), annotations)
        ):
            if annotation is Any or Any in get_args(annotation):
                annotation = RawType

            if annotation is not Parameter.empty and not isinstance(operand, annotation):
                raise TypeError(
                    f"Operand {i + 1} of operator '{name}' must be of type {annotation}."
                )
        return func(left_operand, right_operand)

    return wrapper


def get_operator(name: str) -> Operator:
    """
    Retrieve an operator function by name.

    Args:
        name: The name of the operator

    Returns:
        The operator function

    Raises:
        UndefinedOperatorError: If the operator is not found
    """
    operator = __operator_registry.get(name)
    if operator is None:
        raise UndefinedOperatorError(name)
    return operator


def register_operator(name: str, operator_func: Callable) -> None:
    """
    Register a new operator function.

    Args:
        name: The name of the operator
        operator_func: The operator function to register

    Raises:
        ValueError: If the operator is already registered
    """
    if name in __operator_registry:
        raise ValueError(f"The '{name}' operator has already been registered.")

    signature = inspect.signature(operator_func)
    __operator_annotations[name] = [p.annotation for p in signature.parameters.values()]
    __operator_registry[name] = __validate_operands(operator_func)


# Built-in operators
@operator()
def is_none(left_operand: Any | None, right_operand: Any | None = None) -> bool:
    """Check if the left operand is None."""
    return left_operand is None


@operator()
def is_not_none(left_operand: Any | None, right_operand: Any | None = None) -> bool:
    """Check if the left operand is not None."""
    return left_operand is not None


@operator()
def is_empty(left_operand: Any | None, right_operand: Any | None = None) -> bool:
    """Check if the left operand is empty."""
    return not left_operand


@operator()
def is_not_empty(left_operand: Any | None, right_operand: Any | None = None) -> bool:
    """Check if the left operand is not empty."""
    return bool(left_operand)


@operator()
def is_true(left_operand: bool | str | int | float, right_operand: Any | None = None) -> bool:
    """Check if the left operand is True."""
    if isinstance(left_operand, str):
        return left_operand.lower() == "true"
    if isinstance(left_operand, bool):
        return left_operand
    if isinstance(left_operand, (int, float)):
        return left_operand == 1
    return False


@operator()
def is_false(left_operand: bool | str | int | float, right_operand: Any | None = None) -> bool:
    """Check if the left operand is False."""
    return not is_true(left_operand, None)


@operator()
def matches_regex(left_operand: str, right_operand: str) -> bool:
    """Check if the left operand matches the regex pattern."""
    return re.fullmatch(right_operand, left_operand) is not None


@operator()
def date_between(left_operand: str | datetime, right_operand: List | tuple) -> bool:
    """Check if the date is between two dates."""
    if len(right_operand) != 2:
        raise ValueError("The 'date_between' operator requires a tuple of two dates.")

    left_date = (
        left_operand
        if isinstance(left_operand, datetime)
        else datetime.fromisoformat(left_operand)
    )
    from_date = (
        right_operand[0]
        if isinstance(right_operand[0], datetime)
        else datetime.fromisoformat(right_operand[0])
    )
    to_date = (
        right_operand[1]
        if isinstance(right_operand[1], datetime)
        else datetime.fromisoformat(right_operand[1])
    )
    return (
        from_date.astimezone(tz.utc)
        <= left_date.astimezone(tz.utc)
        <= to_date.astimezone(tz.utc)
    )


@operator()
def one_of(left_operand: Any, right_operand: Iterable) -> bool:
    """Check if the left operand is in the right operand collection."""
    return left_operand in right_operand


@operator()
def less_than(left_operand: CmpType, right_operand: CmpType) -> bool:
    """Check if left operand is less than right operand."""
    return left_operand < right_operand  # type: ignore


@operator()
def greater_than(left_operand: CmpType, right_operand: CmpType) -> bool:
    """Check if left operand is greater than right operand."""
    return left_operand > right_operand  # type: ignore


@operator()
def equal_to(left_operand: Any, right_operand: Any) -> bool:
    """Check if operands are equal."""
    return left_operand == right_operand


@operator()
def case_fold_equal_to(left_operand: str, right_operand: str) -> bool:
    """Check if strings are equal ignoring case."""
    return left_operand.casefold() == right_operand.casefold()


@operator()
def not_equal_to(left_operand: Any, right_operand: Any) -> bool:
    """Check if operands are not equal."""
    return left_operand != right_operand


@operator()
def greater_than_or_equal_to(left_operand: CmpType, right_operand: CmpType) -> bool:
    """Check if left operand is greater than or equal to right operand."""
    return left_operand >= right_operand  # type: ignore


@operator()
def less_than_or_equal_to(left_operand: CmpType, right_operand: CmpType) -> bool:
    """Check if left operand is less than or equal to right operand."""
    return left_operand <= right_operand  # type: ignore


@operator()
def starts_with(left_operand: str, right_operand: str) -> bool:
    """Check if string starts with prefix."""
    return left_operand.startswith(right_operand)


@operator()
def ends_with(left_operand: str, right_operand: str) -> bool:
    """Check if string ends with suffix."""
    return left_operand.endswith(right_operand)


@operator()
def contains(left_operand: Iterable, right_operand: Any) -> bool:
    """Check if collection contains element."""
    return right_operand in left_operand


@operator()
def does_not_contain(left_operand: Iterable, right_operand: Any) -> bool:
    """Check if collection does not contain element."""
    return right_operand not in left_operand


@operator()
def contains_all(left_operand: Iterable, right_operand: Iterable) -> bool:
    """Check if collection contains all elements."""
    return all(item in left_operand for item in right_operand)


@operator()
def contains_any(left_operand: Iterable, right_operand: Iterable) -> bool:
    """Check if collection contains any element."""
    return any(item in set(left_operand) for item in right_operand)


def list_operators() -> List[str]:
    """
    List all registered operators.
    
    Returns:
        List of registered operator names
    """
    return list(__operator_registry.keys())
