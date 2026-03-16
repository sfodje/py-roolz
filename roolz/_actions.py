from roolz.errors import InvalidActionError


def execute_actions(actor: object, actions: list[dict]):
    for action in actions:
        action_method_name = action["action"]
        action_method = getattr(actor, action_method_name)
        args = action.get("args", [])
        params = action.get("params", {})
        action_method(*args, **params)


def validate_actions(actions: list[dict], actor: object) -> list[InvalidActionError]:
    return __validate_actions(actions, "actions", actor)


def __validate_actions(
    actions: list[dict], path: str, actor: object
) -> list[InvalidActionError]:
    if actor is None:
        return [InvalidActionError(path, "Actor is required")]

    validation_errors = list()
    for i, action in enumerate(actions):
        new_path = f"{path}[{i}]"
        invalid_keys = set(action.keys()) - {
            "action",
            "args",
            "params",
        }
        if invalid_keys:
            validation_errors.append(
                InvalidActionError(new_path, f"Invalid keys: {', '.join(invalid_keys)}")
            )

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

        args = action.get("args")
        if args and not isinstance(args, list):
            validation_errors.append(
                InvalidActionError(new_path, "'args' must be a list")
            )

        params = action.get("params")
        if params and not isinstance(params, dict):
            validation_errors.append(
                InvalidActionError(new_path, "'params' must be a dictionary")
            )

    return validation_errors
