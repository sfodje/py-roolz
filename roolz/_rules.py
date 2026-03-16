import json
from functools import lru_cache
from typing import Any, Dict, Optional

from roolz._actions import execute_actions, validate_actions
from roolz._conditions import evaluate_condition, validate_condition
from roolz.errors import InvalidRuleError


def _canonicalize_rules(rules: Dict[str, Any]) -> str:
    """Create a canonical string representation of rules for caching."""
    # Sort keys and use JSON for consistent serialization
    return json.dumps(rules, sort_keys=True, separators=(",", ":"))


@lru_cache(maxsize=128)
def _create_rule_cache_key(
    rules_repr: str, fact_type_name: str, actor_type_name: str
) -> str:
    """Create a cache key for rule validation."""
    return f"{rules_repr}:{fact_type_name}:{actor_type_name}"


# Cache for rule validation results - using LRU cache for memory management
@lru_cache(maxsize=128)
def _cached_validate_rules(
    rules_repr: str, fact_type_name: str, actor_type_name: str
) -> Optional[InvalidRuleError]:
    """
    Cached rule validation helper.

    Args:
        rules_repr: Canonical string representation of rules
        fact_type_name: Name of the fact type
        actor_type_name: Name of the actor type

    Returns:
        InvalidRuleError if validation fails, None if valid
    """
    # Parse rules back to dict for validation
    try:
        json.loads(rules_repr)  # Validate JSON format
    except json.JSONDecodeError:
        # Return a generic error for invalid JSON
        return InvalidRuleError([], [])

    # This is a placeholder - in practice, we'd need the actual objects
    # For now, return None to indicate valid
    return None


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
        return InvalidRuleError([], [])

    actor = actor or fact

    # Create canonical representation for caching
    rules_repr = _canonicalize_rules(rules)
    fact_type_name = type(fact).__name__
    actor_type_name = type(actor).__name__

    # Try to get from cache first
    cached_result = _cached_validate_rules(rules_repr, fact_type_name, actor_type_name)
    if cached_result is not None:
        return cached_result

    # Perform actual validation
    condition_errors = validate_condition(rules.get("condition", {}), type(fact))
    action_errors = validate_actions(rules.get("actions", []), actor)

    result = None
    if condition_errors or action_errors:
        result = InvalidRuleError(condition_errors, action_errors)

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
