from roolz.errors import InvalidRuleError
from roolz._rules import validate_rules, execute_rules


class MockFact:
    def true_method(self):
        return True

    def false_method(self):
        return False


class MockActor:
    def valid_action(self):
        pass

    def action_with_args(self, *args):
        pass

    def action_with_params(self, **params):
        pass


def test_validate_rules_valid():
    rules = {"condition": True, "actions": [{"action": "valid_action"}]}
    fact = MockFact()
    actor = MockActor()
    assert validate_rules(rules, fact, actor) is None


def test_validate_rules_invalid_condition():
    rules = {"condition": "invalid", "actions": [{"action": "valid_action"}]}
    fact = MockFact()
    actor = MockActor()
    assert isinstance(validate_rules(rules, fact, actor), InvalidRuleError)


def test_validate_rules_invalid_action():
    rules = {"condition": True, "actions": [{"action": "missing_action"}]}
    fact = MockFact()
    actor = MockActor()
    assert isinstance(validate_rules(rules, fact, actor), InvalidRuleError)


def test_execute_rules_valid():
    rules = {"condition": True, "actions": [{"action": "valid_action"}]}
    fact = MockFact()
    actor = MockActor()
    execute_rules(rules, fact, actor)


def test_execute_rules_condition_not_met():
    rules = {"condition": False, "actions": [{"action": "valid_action"}]}
    fact = MockFact()
    actor = MockActor()
    execute_rules(rules, fact, actor)


def test_execute_rules_actions_executed():
    rules = {"condition": True, "actions": [{"action": "valid_action"}]}
    fact = MockFact()
    actor = MockActor()
    execute_rules(rules, fact, actor)
