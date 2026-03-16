from typing import List

from roolz.errors import InvalidActionError


def execute_actions(actor: object, actions: List[dict]) -> None:
    """
    Execute a list of actions on the given actor.

    Args:
        actor: The object that will execute the actions
        actions: List of action dictionaries with 'action', 'args', and 'params' keys

    Raises:
        AttributeError: If the action method doesn't exist on the actor
        TypeError: If the action method is called with invalid arguments
    """
    for action in actions:
        action_method_name = action["action"]
        try:
            action_method = getattr(actor, action_method_name)
        except AttributeError:
            raise AttributeError(
                f"Action method '{action_method_name}' not found on {type(actor).__name__}"
            )

        args = action.get("args", [])
        params = action.get("params", {})
        action_method(*args, **params)


def validate_actions(actions: List[dict], actor: object) -> List[InvalidActionError]:
    """
    Validate a list of actions against the given actor.

    Args:
        actions: List of action dictionaries to validate
        actor: The object that would execute the actions

    Returns:
        List of validation errors, empty if all actions are valid
    """
    return __validate_actions(actions, "actions", actor)


def __validate_actions(
    actions: List[dict], path: str, actor: object
) -> List[InvalidActionError]:
    """
    Internal validation function for actions.

    Args:
        actions: List of action dictionaries to validate
        path: Current validation path for error reporting
        actor: The object that would execute the actions

    Returns:
        List of validation errors
    """
    if actor is None:
        return [InvalidActionError(path, "Actor is required")]

    validation_errors = []
    for i, action in enumerate(actions):
        new_path = f"{path}[{i}]"

        # Validate action structure
        if not isinstance(action, dict):
            validation_errors.append(
                InvalidActionError(new_path, "Action must be a dictionary")
            )
            continue

        invalid_keys = set(action.keys()) - {
            "action",
            "args",
            "params",
        }
        if invalid_keys:
            validation_errors.append(
                InvalidActionError(new_path, f"Invalid keys: {', '.join(invalid_keys)}")
            )

        # Validate action method
        action_method_name = action.get("action")
        if not action_method_name:
            validation_errors.append(
                InvalidActionError(new_path, "'action' is required")
            )
        elif not hasattr(actor, action_method_name):
            validation_errors.append(
                InvalidActionError(
                    new_path,
                    f"Action method '{action_method_name}' is not defined in '{actor.__class__.__name__}'",
                )
            )

        # Validate args
        args = action.get("args")
        if args is not None and not isinstance(args, list):
            validation_errors.append(
                InvalidActionError(new_path, "'args' must be a list")
            )

        # Validate params
        params = action.get("params")
        if params is not None and not isinstance(params, dict):
            validation_errors.append(
                InvalidActionError(new_path, "'params' must be a dictionary")
            )

    return validation_errors
