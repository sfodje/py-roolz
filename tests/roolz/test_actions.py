from typing import Any, List

import pytest

from roolz._actions import execute_actions, validate_actions


class MockActor:
    """Mock actor class for testing action execution."""

    def __init__(self):
        self.executed_actions = []
        self.call_count = 0

    def valid_action(self):
        """Simple action without parameters."""
        self.executed_actions.append("valid_action")
        self.call_count += 1

    def action_with_args(self, *args):
        """Action that accepts positional arguments."""
        self.executed_actions.append(("action_with_args", args))
        self.call_count += 1

    def action_with_params(self, **params):
        """Action that accepts keyword arguments."""
        self.executed_actions.append(("action_with_params", params))
        self.call_count += 1

    def action_with_both(self, *args, **params):
        """Action that accepts both positional and keyword arguments."""
        self.executed_actions.append(("action_with_both", args, params))
        self.call_count += 1

    def action_returns_value(self, value: Any = None):
        """Action that returns a value."""
        self.call_count += 1
        return value

    def action_raises_exception(self):
        """Action that raises an exception."""
        self.call_count += 1
        raise ValueError("Test exception")


class TestExecuteActions:
    """Test cases for action execution."""

    def test_execute_single_action(self):
        """Test executing a single action."""
        actor = MockActor()
        actions = [{"action": "valid_action"}]

        execute_actions(actor, actions)

        assert actor.call_count == 1
        assert actor.executed_actions == ["valid_action"]

    def test_execute_multiple_actions(self):
        """Test executing multiple actions in sequence."""
        actor = MockActor()
        actions = [
            {"action": "valid_action"},
            {"action": "action_with_args", "args": [1, 2, 3]},
            {"action": "action_with_params", "params": {"key": "value"}},
        ]

        execute_actions(actor, actions)

        assert actor.call_count == 3
        assert len(actor.executed_actions) == 3
        assert actor.executed_actions[0] == "valid_action"
        assert actor.executed_actions[1] == ("action_with_args", (1, 2, 3))
        assert actor.executed_actions[2] == ("action_with_params", {"key": "value"})

    def test_execute_action_with_args(self):
        """Test executing action with positional arguments."""
        actor = MockActor()
        actions = [{"action": "action_with_args", "args": [1, 2, 3]}]

        execute_actions(actor, actions)

        assert actor.call_count == 1
        assert actor.executed_actions[0] == ("action_with_args", (1, 2, 3))

    def test_execute_action_with_params(self):
        """Test executing action with keyword arguments."""
        actor = MockActor()
        actions = [
            {"action": "action_with_params", "params": {"key": "value", "num": 42}}
        ]

        execute_actions(actor, actions)

        assert actor.call_count == 1
        assert actor.executed_actions[0] == (
            "action_with_params",
            {"key": "value", "num": 42},
        )

    def test_execute_action_with_both_args_and_params(self):
        """Test executing action with both positional and keyword arguments."""
        actor = MockActor()
        actions = [
            {"action": "action_with_both", "args": [1, 2], "params": {"key": "value"}}
        ]

        execute_actions(actor, actions)

        assert actor.call_count == 1
        assert actor.executed_actions[0] == (
            "action_with_both",
            (1, 2),
            {"key": "value"},
        )

    def test_execute_action_with_empty_args(self):
        """Test executing action with empty args list."""
        actor = MockActor()
        actions = [{"action": "action_with_args", "args": []}]

        execute_actions(actor, actions)

        assert actor.call_count == 1
        assert actor.executed_actions[0] == ("action_with_args", ())

    def test_execute_action_with_empty_params(self):
        """Test executing action with empty params dict."""
        actor = MockActor()
        actions = [{"action": "action_with_params", "params": {}}]

        execute_actions(actor, actions)

        assert actor.call_count == 1
        assert actor.executed_actions[0] == ("action_with_params", {})

    def test_execute_action_without_args_or_params(self):
        """Test executing action without specifying args or params."""
        actor = MockActor()
        actions = [{"action": "valid_action"}]  # No args or params keys

        execute_actions(actor, actions)

        assert actor.call_count == 1
        assert actor.executed_actions[0] == "valid_action"

    def test_execute_action_returns_value(self):
        """Test that action return values are handled properly."""
        actor = MockActor()
        actions = [{"action": "action_returns_value", "params": {"value": "test"}}]

        # Should not raise an exception
        execute_actions(actor, actions)

        assert actor.call_count == 1

    def test_execute_action_raises_exception(self):
        """Test that exceptions from actions are propagated."""
        actor = MockActor()
        actions = [{"action": "action_raises_exception"}]

        with pytest.raises(ValueError, match="Test exception"):
            execute_actions(actor, actions)

        assert actor.call_count == 1

    def test_execute_empty_actions_list(self):
        """Test executing an empty list of actions."""
        actor = MockActor()
        actions = []

        execute_actions(actor, actions)

        assert actor.call_count == 0
        assert actor.executed_actions == []

    def test_execute_actions_missing_actor(self):
        """Test that AttributeError is raised when actor is None."""
        actions = [{"action": "valid_action"}]

        with pytest.raises(
            AttributeError, match="Action method 'valid_action' not found"
        ):
            execute_actions(None, actions)

    def test_execute_actions_missing_action_method(self):
        """Test that AttributeError is raised when action method doesn't exist."""
        actor = MockActor()
        actions = [{"action": "missing_action"}]

        with pytest.raises(
            AttributeError, match="Action method 'missing_action' not found"
        ):
            execute_actions(actor, actions)


class TestValidateActions:
    """Test cases for action validation."""

    def test_validate_valid_actions(self):
        """Test validation of valid actions."""
        actions = [{"action": "valid_action"}]
        actor = MockActor()

        errors = validate_actions(actions, actor)

        assert errors == []

    def test_validate_multiple_valid_actions(self):
        """Test validation of multiple valid actions."""
        actions = [
            {"action": "valid_action"},
            {"action": "action_with_args", "args": [1, 2]},
            {"action": "action_with_params", "params": {"key": "value"}},
        ]
        actor = MockActor()

        errors = validate_actions(actions, actor)

        assert errors == []

    def test_validate_actions_missing_actor(self):
        """Test validation when actor is None."""
        actions = [{"action": "valid_action"}]

        errors = validate_actions(actions, None)

        assert len(errors) == 1
        assert errors[0].path == "actions"
        assert errors[0].message == "Actor is required"

    def test_validate_actions_invalid_keys(self):
        """Test validation of actions with invalid keys."""
        actions = [{"action": "valid_action", "invalid_key": "value"}]
        actor = MockActor()

        errors = validate_actions(actions, actor)

        assert len(errors) == 1
        assert errors[0].path == "actions[0]"
        assert errors[0].message == "Invalid keys: invalid_key"

    def test_validate_actions_multiple_invalid_keys(self):
        """Test validation of actions with multiple invalid keys."""
        actions = [
            {"action": "valid_action", "invalid1": "value1", "invalid2": "value2"}
        ]
        actor = MockActor()

        errors = validate_actions(actions, actor)

        assert len(errors) == 1
        assert "invalid1" in errors[0].message
        assert "invalid2" in errors[0].message

    def test_validate_actions_missing_action_method(self):
        """Test validation when action method doesn't exist on actor."""
        actions = [{"action": "missing_action"}]
        actor = MockActor()

        errors = validate_actions(actions, actor)

        assert len(errors) == 1
        assert errors[0].path == "actions[0]"
        assert (
            errors[0].message
            == "Action method 'missing_action' is not defined in 'MockActor'"
        )

    def test_validate_actions_missing_action_key(self):
        """Test validation when action key is missing."""
        actions = [{"args": [1, 2], "params": {"key": "value"}}]
        actor = MockActor()

        errors = validate_actions(actions, actor)

        assert len(errors) == 1
        assert errors[0].path == "actions[0]"
        assert errors[0].message == "'action' is required"

    def test_validate_actions_empty_action_key(self):
        """Test validation when action key is empty."""
        actions = [{"action": ""}]
        actor = MockActor()

        errors = validate_actions(actions, actor)

        assert len(errors) == 1
        assert errors[0].path == "actions[0]"
        assert errors[0].message == "'action' is required"

    def test_validate_actions_none_action_key(self):
        """Test validation when action key is None."""
        actions = [{"action": None}]
        actor = MockActor()

        errors = validate_actions(actions, actor)

        assert len(errors) == 1
        assert errors[0].path == "actions[0]"
        assert errors[0].message == "'action' is required"

    def test_validate_actions_invalid_args_type(self):
        """Test validation when args is not a list."""
        actions = [{"action": "valid_action", "args": "not_a_list"}]
        actor = MockActor()

        errors = validate_actions(actions, actor)

        assert len(errors) == 1
        assert errors[0].path == "actions[0]"
        assert errors[0].message == "'args' must be a list"

    def test_validate_actions_invalid_params_type(self):
        """Test validation when params is not a dict."""
        actions = [{"action": "valid_action", "params": "not_a_dict"}]
        actor = MockActor()

        errors = validate_actions(actions, actor)

        assert len(errors) == 1
        assert errors[0].path == "actions[0]"
        assert errors[0].message == "'params' must be a dictionary"

    def test_validate_actions_empty_args_list(self):
        """Test validation of action with empty args list."""
        actions = [{"action": "action_with_args", "args": []}]
        actor = MockActor()

        errors = validate_actions(actions, actor)

        assert errors == []

    def test_validate_actions_empty_params_dict(self):
        """Test validation of action with empty params dict."""
        actions = [{"action": "action_with_params", "params": {}}]
        actor = MockActor()

        errors = validate_actions(actions, actor)

        assert errors == []

    def test_validate_actions_none_args(self):
        """Test validation when args is None."""
        actions = [{"action": "valid_action", "args": None}]
        actor = MockActor()

        errors = validate_actions(actions, actor)

        assert errors == []

    def test_validate_actions_none_params(self):
        """Test validation when params is None."""
        actions = [{"action": "valid_action", "params": None}]
        actor = MockActor()

        errors = validate_actions(actions, actor)

        assert errors == []

    def test_validate_actions_not_dict(self):
        """Test validation when action is not a dictionary."""
        actions: List[Any] = ["not_a_dict"]
        actor = MockActor()

        errors = validate_actions(actions, actor)

        assert len(errors) == 1
        assert errors[0].path == "actions[0]"
        assert errors[0].message == "Action must be a dictionary"

    def test_validate_actions_multiple_errors(self):
        """Test validation with multiple errors in a single action."""
        actions = [{"action": None, "args": "not_a_list", "params": "not_a_dict"}]
        actor = MockActor()

        errors = validate_actions(actions, actor)

        assert len(errors) == 3
        error_messages = [error.message for error in errors]
        assert "'action' is required" in error_messages
        assert "'args' must be a list" in error_messages
        assert "'params' must be a dictionary" in error_messages

    def test_validate_actions_multiple_actions_with_errors(self):
        """Test validation with errors in multiple actions."""
        actions = [
            {"action": "valid_action"},  # Valid
            {"action": "missing_action"},  # Invalid - missing method
            {"action": "valid_action", "invalid_key": "value"},  # Invalid - bad key
            {"action": "action_with_args", "args": "not_a_list"},  # Invalid - bad args
        ]
        actor = MockActor()

        errors = validate_actions(actions, actor)

        assert len(errors) == 3  # Action 0 is valid, others have errors
        error_paths = [error.path for error in errors]
        assert "actions[1]" in error_paths
        assert "actions[2]" in error_paths
        assert "actions[3]" in error_paths

    def test_validate_empty_actions_list(self):
        """Test validation of empty actions list."""
        actions = []
        actor = MockActor()

        errors = validate_actions(actions, actor)

        assert errors == []

    def test_validate_actions_with_complex_data_types(self):
        """Test validation of actions with complex data types in args and params."""
        actions = [
            {
                "action": "action_with_args",
                "args": [1, "string", [1, 2, 3], {"nested": "dict"}],
            },
            {
                "action": "action_with_params",
                "params": {
                    "string": "value",
                    "number": 42,
                    "list": [1, 2, 3],
                    "dict": {"nested": "value"},
                    "boolean": True,
                    "none": None,
                },
            },
        ]
        actor = MockActor()

        errors = validate_actions(actions, actor)

        assert errors == []
