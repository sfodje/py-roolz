import inspect
import re
from datetime import datetime
from datetime import timezone as tz
from functools import lru_cache, wraps
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
CmpType = int | float | str | Comparable
RawType = int | float | str | bool | Iterable | Comparable | None


# Registry to store operator functions - using __slots__ for memory efficiency
class OperatorRegistry:
    __slots__ = ("_operators", "_annotations")

    def __init__(self):
        self._operators: dict[str, Operator] = {}
        self._annotations: dict[str, List[type]] = {}

    def get(self, name: str) -> Operator | None:
        """Fast lookup with direct dict access."""
        return self._operators.get(name)

    def set(self, name: str, operator: Operator, annotations: List[type]) -> None:
        """Set operator with annotations."""
        self._operators[name] = operator
        self._annotations[name] = annotations

    def has(self, name: str) -> bool:
        """Check if operator exists."""
        return name in self._operators

    def keys(self) -> List[str]:
        """Get all operator names."""
        return list(self._operators.keys())

    def get_annotations(self, name: str) -> List[type] | None:
        """Get annotations for an operator."""
        return self._annotations.get(name)


# Global registry instance
__operator_registry = OperatorRegistry()

# Cache for compiled regex patterns - using LRU cache for memory management
@lru_cache(maxsize=128)
def _get_compiled_regex(pattern: str) -> re.Pattern:
    """Get compiled regex pattern from cache."""
    return re.compile(pattern)


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
        annotations = __operator_registry.get_annotations(name)
        if not annotations:
            return func(left_operand, right_operand)

        for i, (operand, annotation) in enumerate(
            zip((left_operand, right_operand), annotations)
        ):
            if annotation is Any or Any in get_args(annotation):
                annotation = RawType

            if annotation is not inspect.Parameter.empty and not isinstance(
                operand, annotation
            ):
                raise TypeError(
                    f"Operand {i + 1} of operator '{name}' must be of type {annotation}."
                )
        return func(left_operand, right_operand)

    return wrapper


@lru_cache(maxsize=128)
def get_operator(name: str) -> Operator:
    """
    Retrieve an operator function by name with caching.

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
    if __operator_registry.has(name):
        raise ValueError(f"The '{name}' operator has already been registered.")

    signature = inspect.signature(operator_func)
    annotations = [p.annotation for p in signature.parameters.values()]
    __operator_registry.set(name, __validate_operands(operator_func), annotations)


# Built-in operators with optimizations
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
def is_true(
    left_operand: bool | str | int | float, right_operand: Any | None = None
) -> bool:
    """Check if the left operand is True."""
    if isinstance(left_operand, str):
        return left_operand.lower() == "true"
    if isinstance(left_operand, bool):
        return left_operand
    if isinstance(left_operand, (int, float)):
        return left_operand == 1
    return False


@operator()
def is_false(
    left_operand: bool | str | int | float, right_operand: Any | None = None
) -> bool:
    """Check if the left operand is False."""
    return not is_true(left_operand, None)


@operator()
def matches_regex(left_operand: str, right_operand: str) -> bool:
    """Check if the left operand matches the regex pattern."""
    pattern = _get_compiled_regex(right_operand)
    return pattern.fullmatch(left_operand) is not None


@operator()
def date_between(left_operand: str | datetime, right_operand: List | tuple) -> bool:
    """Check if the date is between two dates."""
    if len(right_operand) != 2:
        raise ValueError("The 'date_between' operator requires a tuple of two dates.")

    # Optimize datetime parsing
    if isinstance(left_operand, datetime):
        left_date = left_operand
    else:
        left_date = datetime.fromisoformat(left_operand)

    if isinstance(right_operand[0], datetime):
        from_date = right_operand[0]
    else:
        from_date = datetime.fromisoformat(right_operand[0])

    if isinstance(right_operand[1], datetime):
        to_date = right_operand[1]
    else:
        to_date = datetime.fromisoformat(right_operand[1])

    # Convert to UTC once
    left_utc = left_date.astimezone(tz.utc)
    from_utc = from_date.astimezone(tz.utc)
    to_utc = to_date.astimezone(tz.utc)

    return from_utc <= left_utc <= to_utc


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
    # Optimize for sets
    if isinstance(left_operand, set):
        return all(item in left_operand for item in right_operand)
    # Convert to set for faster lookups
    left_set = set(left_operand)
    return all(item in left_set for item in right_operand)


@operator()
def contains_any(left_operand: Iterable, right_operand: Iterable) -> bool:
    """Check if collection contains any element."""
    # Optimize for sets
    if isinstance(left_operand, set):
        return any(item in left_operand for item in right_operand)
    # Convert to set for faster lookups
    left_set = set(left_operand)
    return any(item in left_set for item in right_operand)


def list_operators() -> List[str]:
    """
    List all registered operators.

    Returns:
        List of registered operator names
    """
    return __operator_registry.keys()
