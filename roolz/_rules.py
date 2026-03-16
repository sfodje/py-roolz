from typing import Any, Dict, List, Optional, Union

from roolz._actions import execute_actions, validate_actions
from roolz._conditions import evaluate_condition, validate_condition
from roolz.errors import InvalidRuleError


def validate_rules(rules: Dict[str, Any], fact: Any, actor: Optional[Any] = None) -> Optional[InvalidRuleError]:
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
    condition_errors = validate_condition(rules.get("condition", {}), type(fact))
    action_errors = validate_actions(rules.get("actions", []), actor)

    if condition_errors or action_errors:
        return InvalidRuleError(condition_errors, action_errors)
    return None


def execute_rules(rules: Dict[str, Any], fact: Any, actor: Optional[Any] = None) -> None:
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
