from roolz.errors import InvalidRuleError
from roolz._conditions import validate_condition, evaluate_condition
from roolz._actions import validate_actions, execute_actions


def validate_rules(rules: dict, fact: object, actor: object = None) -> InvalidRuleError:
    actor = actor or fact
    condition_errors = validate_condition(rules.get("condition"), fact)
    action_errors = validate_actions(rules.get("actions", []), actor)

    if condition_errors or action_errors:
        return InvalidRuleError(condition_errors, action_errors)


def execute_rules(rules: dict, fact: object, actor: object = None):
    actor = actor or fact
    if rules.get("condition") and not evaluate_condition(fact, rules["condition"]):
        return

    execute_actions(actor, rules.get("actions", []))
