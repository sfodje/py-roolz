from datetime import datetime, timezone as tz
import inspect
import re
from functools import wraps
from inspect import Parameter
from typing import Any, Callable, Iterable, get_args

from roolz.errors import UndefinedOperatorError

# Type alias for an operator function that takes two operands (left and right) and returns a boolean
Operator = Callable[[Any, Any | None], bool]
CmpType = int | float | str
RawType = int | float | str | bool | Iterable | None

# Registry to store operator functions
__operator_registry: dict[str, Operator] = {}

# Registry to store parameter type annotations for operator functions
__operator_annotations: dict[str, list[type]] = {}


def __validate_operands(func: Operator):
    """
    Decorator to validate the types of operands passed to an operator function.

    Args:
        func (Operator): The operator function to be validated.

    Returns:
        Operator: A wrapped operator function with operand type validation.
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

            if annotation is not Parameter.empty and not isinstance(
                operand, annotation
            ):
                raise TypeError(
                    f"Operand {i + 1} of operator '{name}' must be of type {annotation}."
                )
        return func(left_operand, right_operand)

    return wrapper


def get_operator(name: str) -> Operator:
    """
    Retrieve an operator function by name.

    Args:
        name (str): The name of the operator.

    Returns:
        Operator: The operator function.

    Raises:
        UndefinedOperatorError: If the operator is not found in the registry.
    """
    operator = __operator_registry.get(name)
    if operator is None:
        raise UndefinedOperatorError(name)
    return operator


def register_operator(name: str, operator_func: Callable[[Any, Any | None], bool]):
    """
    Register a new operator function.

    Args:
        name (str): The name of the operator.
        operator_func (Callable[[Any, Any | None], bool]): The operator function to be registered.

    Raises:
        ValueError: If the operator has already been registered.
    """
    if name in __operator_registry:
        raise ValueError(f"The '{name}' operator has already been registered.")

    signature = inspect.signature(operator_func)
    __operator_annotations[name] = [p.annotation for p in signature.parameters.values()]
    __operator_registry[name] = __validate_operands(operator_func)


def __register(cls):
    """
    Class decorator to register built-in operators.

    Args:
        cls (type): The class containing built-in operators.

    Returns:
        type: The class itself.
    """
    if hasattr(cls, "register_builtins"):
        cls.register_builtins()
    return cls


@__register
class _Operators:
    """
    A class containing built-in operator functions.
    """

    @staticmethod
    def is_none(left_operand: Any | None, _) -> bool:
        """
        Check if the left operand is None.

        Args:
            left_operand (Any | None): The operand to check.
            _ (Any): Unused.

        Returns:
            bool: True if the operand is None, False otherwise.
        """
        return left_operand is None

    @staticmethod
    def is_not_none(left_operand: Any | None, _) -> bool:
        """
        Check if the left operand is not None.

        Args:
            left_operand (Any | None): The operand to check.
            _ (Any): Unused.

        Returns:
            bool: True if the operand is not None, False otherwise.
        """
        return left_operand is not None

    @staticmethod
    def is_empty(left_operand: Any | None, _) -> bool:
        """
        Check if the left operand is empty.

        Args:
            left_operand (Any | None): The operand to check.
            _ (Any): Unused.

        Returns:
            bool: True if the operand is empty, False otherwise.
        """
        return not left_operand

    @staticmethod
    def is_not_empty(left_operand: Any | None, _) -> bool:
        """
        Check if the left operand is not empty.

        Args:
            left_operand (Any | None): The operand to check.
            _ (Any): Unused.

        Returns:
            bool: True if the operand is not empty, False otherwise.
        """
        return bool(left_operand)

    @staticmethod
    def is_true(left_operand: bool | str | int | float, _) -> bool:
        """
        Check if the left operand is True.

        Args:
            left_operand (bool | None): The operand to check.
            _ (Any): Unused.

        Returns:
            bool: True if the operand is True, False otherwise.
        """
        if isinstance(left_operand, str):
            return left_operand.lower() == "true"

        if isinstance(left_operand, bool):
            return left_operand

        if isinstance(left_operand, int | float):
            return left_operand == 1

        return False

    @staticmethod
    def is_false(left_operand: bool | str | int, _) -> bool:
        """
        Check if the left operand is False.

        Args:
            left_operand (bool | None): The operand to check.
            _ (Any): Unused.

        Returns:
            bool: True if the operand is False, False otherwise.
        """
        return not _Operators.is_true(left_operand, None)

    @staticmethod
    def matches_regex(left_operand: str, right_operand: str) -> bool:
        """
        Check if the left operand matches the regex pattern provided by the right operand.

        Args:
            left_operand (str): The string to be matched.
            right_operand (str): The regex pattern.

        Returns:
            bool: True if the string matches the pattern, False otherwise.
        """
        return re.fullmatch(right_operand, left_operand) is not None

    @staticmethod
    def date_between(
        left_operand: str | datetime, right_operand: str | datetime
    ) -> bool:
        """
        Check if the current date is between the left and right operand dates.

        Args:
            left_operand (str | datetime): The start date.
            right_operand (str | datetime): The end date.

        Returns:
            bool: True if the current date is between the start and end dates, False otherwise.
        """
        left_date = (
            left_operand
            if isinstance(left_operand, datetime)
            else datetime.fromisoformat(left_operand)
        )
        right_date = (
            right_operand
            if isinstance(right_operand, datetime)
            else datetime.fromisoformat(right_operand)
        )
        now = datetime.now(tz=tz.utc)
        return left_date.astimezone(tz.utc) <= now <= right_date.astimezone(tz.utc)

    @staticmethod
    def one_of(left_operand: Any, right_operand: Iterable) -> bool:
        """
        Check if the left operand is one of the elements in the right operand.

        Args:
            left_operand (Any): The element to check.
            right_operand (Iterable): The collection to check against.

        Returns:
            bool: True if the element is in the collection, False otherwise.
        """
        return left_operand in right_operand

    @staticmethod
    def less_than(left_operand: CmpType, right_operand: CmpType) -> bool:
        """
        Check if the left operand is less than the right operand.

        Args:
            left_operand (CmpType): The left operand.
            right_operand (CmpType): The right operand.

        Returns:
            bool: True if the left operand is less than the right operand, False otherwise.
        """
        return left_operand < right_operand

    @staticmethod
    def greater_than(left_operand: CmpType, right_operand: CmpType) -> bool:
        """
        Check if the left operand is greater than the right operand.

        Args:
            left_operand (CmpType): The left operand.
            right_operand (CmpType): The right operand.

        Returns:
            bool: True if the left operand is greater than the right operand, False otherwise.
        """
        return left_operand > right_operand

    @staticmethod
    def equal_to(left_operand: Any, right_operand: Any) -> bool:
        """
        Check if the left operand is equal to the right operand.

        Args:
            left_operand (Any): The left operand.
            right_operand (Any): The right operand.

        Returns:
            bool: True if the left operand is equal to the right operand, False otherwise.
        """
        return left_operand == right_operand

    @staticmethod
    def not_equal_to(left_operand: Any, right_operand: Any) -> bool:
        """
        Check if the left operand is not equal to the right operand.

        Args:
            left_operand (Any): The left operand.
            right_operand (Any): The right operand.

        Returns:
            bool: True if the left operand is not equal to the right operand, False otherwise.
        """
        return left_operand != right_operand

    @staticmethod
    def greater_than_or_equal_to(left_operand: CmpType, right_operand: CmpType) -> bool:
        """
        Check if the left operand is greater than or equal to the right operand.

        Args:
            left_operand (CmpType): The left operand.
            right_operand (CmpType): The right operand.

        Returns:
            bool: True if the left operand is greater than or equal to the right operand, False otherwise.
        """
        return left_operand >= right_operand

    @staticmethod
    def less_than_or_equal_to(left_operand: CmpType, right_operand: CmpType) -> bool:
        """
        Check if the left operand is less than or equal to the right operand.

        Args:
            left_operand (CmpType): The left operand.
            right_operand (CmpType): The right operand.

        Returns:
            bool: True if the left operand is less than or equal to the right operand, False otherwise.
        """
        return left_operand <= right_operand

    @staticmethod
    def starts_with(left_operand: str, right_operand: str) -> bool:
        """
        Check if the left operand starts with the right operand.

        Args:
            left_operand (str): The string to check.
            right_operand (str): The prefix to check for.

        Returns:
            bool: True if the string starts with the prefix, False otherwise.
        """
        return left_operand.startswith(right_operand)

    @staticmethod
    def ends_with(left_operand: str, right_operand: str) -> bool:
        """
        Check if the left operand ends with the right operand.

        Args:
            left_operand (str): The string to check.
            right_operand (str): The suffix to check for.

        Returns:
            bool: True if the string ends with the suffix, False otherwise.
        """
        return left_operand.endswith(right_operand)

    @staticmethod
    def contains(left_operand: Iterable, right_operand: Any) -> bool:
        """
        Check if the left operand contains the right operand.

        Args:
            left_operand (Iterable): The collection to check.
            right_operand (Any): The element to check for.

        Returns:
            bool: True if the collection contains the element, False otherwise.
        """
        return right_operand in left_operand

    @staticmethod
    def does_not_contain(left_operand: Iterable, right_operand: Any) -> bool:
        """
        Check if the left operand does not contain the right operand.

        Args:
            left_operand (Iterable): The collection to check.
            right_operand (Any): The element to check for.

        Returns:
            bool: True if the collection does not contain the element, False otherwise.
        """
        return right_operand not in left_operand

    @staticmethod
    def contains_all(left_operand: Iterable, right_operand: Iterable) -> bool:
        """
        Check if the left operand contains all elements of the right operand.

        Args:
            left_operand (Iterable): The collection to check.
            right_operand (Iterable): The elements to check for.

        Returns:
            bool: True if the collection contains all elements, False otherwise.
        """
        return all(item in left_operand for item in right_operand)

    @staticmethod
    def contains_any(left_operand: Iterable, right_operand: Iterable) -> bool:
        """
        Check if the left operand contains any element of the right operand.

        Args:
            left_operand (Iterable): The collection to check.
            right_operand (Iterable): The elements to check for.

        Returns:
            bool: True if the collection contains any element, False otherwise.
        """
        return any(item in set(left_operand) for item in right_operand)

    @classmethod
    def register_builtins(cls):
        """
        Register all built-in operator functions in the class.
        """
        for name, method in cls.__dict__.items():
            if callable(method):
                register_operator(name, method)
