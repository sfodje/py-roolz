import pytest
from roolz.errors import InvalidActionError
from roolz._actions import execute_actions, validate_actions


class MockActor:
    def valid_action(self):
        pass

    def action_with_args(self, *args):
        pass

    def action_with_params(self, **params):
        pass


def test_evaluate_actions_valid():
    actor = MockActor()
    actions = [{"action": "valid_action"}]
    execute_actions(actor, actions)


def test_evaluate_actions_with_args():
    actor = MockActor()
    actions = [{"action": "action_with_args", "args": [1, 2, 3]}]
    execute_actions(actor, actions)


def test_evaluate_actions_with_params():
    actor = MockActor()
    actions = [{"action": "action_with_params", "params": {"key": "value"}}]
    execute_actions(actor, actions)


def test_evaluate_actions_missing_actor():
    actions = [{"action": "valid_action"}]
    with pytest.raises(AttributeError):
        execute_actions(None, actions)


def test_evaluate_actions_missing_action_method():
    actor = MockActor()
    actions = [{"action": "missing_action"}]
    with pytest.raises(AttributeError):
        execute_actions(actor, actions)


def test_validate_actions_valid():
    actions = [{"action": "valid_action"}]
    actor = MockActor()
    assert validate_actions(actions, actor) == []


def test_validate_actions_missing_actor():
    actions = [{"action": "valid_action"}]
    assert validate_actions(actions, None) == [
        InvalidActionError("actions", "Actor is required")
    ]


def test_validate_actions_invalid_keys():
    actions = [{"action": "valid_action", "invalid_key": "value"}]
    actor = MockActor()
    assert validate_actions(actions, actor) == [
        InvalidActionError("actions[0]", "Invalid keys: invalid_key")
    ]


def test_validate_actions_missing_action_method():
    actions = [{"action": "missing_action"}]
    actor = MockActor()
    assert validate_actions(actions, actor) == [
        InvalidActionError(
            "actions[0]", "Action method 'missing_action' is not defined in 'MockActor'"
        )
    ]

    actions = [{"action": None, "args": "not_a_list"}]
    actor = MockActor()
    assert validate_actions(actions, actor) == [
        InvalidActionError("actions[0]", "'action' is required"),
        InvalidActionError("actions[0]", "'args' must be a list"),
    ]


def test_validate_actions_invalid_args():
    actions = [{"action": "valid_action", "args": "not_a_list"}]
    actor = MockActor()
    assert validate_actions(actions, actor) == [
        InvalidActionError("actions[0]", "'args' must be a list")
    ]


def test_validate_actions_invalid_params():
    actions = [{"action": "valid_action", "params": "not_a_dict"}]
    actor = MockActor()
    assert validate_actions(actions, actor) == [
        InvalidActionError("actions[0]", "'params' must be a dictionary")
    ]
