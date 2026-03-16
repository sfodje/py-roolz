from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from roolz._actions import execute_actions, validate_actions
from roolz._conditions import evaluate_condition, validate_condition
from roolz.errors import InvalidRuleError

# Cache for rule validation results
__rule_validation_cache: dict[str, Optional[InvalidRuleError]] = {}


@lru_cache(maxsize=128)
def _create_rule_cache_key(
    rules_repr: str, fact_type_name: str, actor_type_name: str
) -> str:
    """Create a cache key for rule validation."""
    return f"{rules_repr}:{fact_type_name}:{actor_type_name}"


def validate_rules(
    rules: Dict[str, Any], fact: Any, actor: Optional[Any] = None
) -> Optional[InvalidRuleError]:
    """
    Validate a rule configuration.

    Args:
        rules: Rule configuration dictionary with 'condition' and 'actions' keys
        fact: The fact object to validate against
        actor: The actor object (defaults to fact if not provided)

    Returns:
        InvalidRuleError if validation fails, None if valid
    """
    if not isinstance(rules, dict):
        return InvalidRuleError("Rules must be a dictionary", None)

    actor = actor or fact

    # Create cache key
    rules_repr = str(sorted(rules.items()))
    fact_type_name = type(fact).__name__
    actor_type_name = type(actor).__name__
    cache_key = _create_rule_cache_key(rules_repr, fact_type_name, actor_type_name)

    # Check cache first
    if cache_key in __rule_validation_cache:
        return __rule_validation_cache[cache_key]

    condition_errors = validate_condition(rules.get("condition", {}), type(fact))
    action_errors = validate_actions(rules.get("actions", []), actor)

    result = None
    if condition_errors or action_errors:
        result = InvalidRuleError(condition_errors, action_errors)

    # Cache the result
    __rule_validation_cache[cache_key] = result
    return result


def execute_rules(
    rules: Dict[str, Any], fact: Any, actor: Optional[Any] = None
) -> None:
    """
    Execute rules based on condition evaluation.

    Args:
        rules: Rule configuration dictionary with 'condition' and 'actions' keys
        fact: The fact object to evaluate conditions against
        actor: The actor object to execute actions on (defaults to fact if not provided)
    """
    if not isinstance(rules, dict):
        raise ValueError("Rules must be a dictionary")

    actor = actor or fact
    condition = rules.get("condition")

    # Execute actions if no condition or condition is met
    if condition is None or evaluate_condition(fact, condition):
        execute_actions(actor, rules.get("actions", []))
