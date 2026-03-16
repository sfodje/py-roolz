from roolz._actions import execute_actions, validate_actions
from roolz._conditions import evaluate_condition, validate_condition
from roolz.errors import InvalidRuleError


def validate_rules(rules: dict, fact: object, actor: object = None) -> InvalidRuleError | None:
    actor = actor or fact
    condition_errors = validate_condition(rules.get("condition", {}), type(fact))
    action_errors = validate_actions(rules.get("actions", []), actor)

    if condition_errors or action_errors:
        return InvalidRuleError(condition_errors, action_errors)
    return None


def execute_rules(rules: dict, fact: object, actor: object = None):
    actor = actor or fact
    if rules.get("condition") and not evaluate_condition(fact, rules["condition"]):
        return

    execute_actions(actor, rules.get("actions", []))
