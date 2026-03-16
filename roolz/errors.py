class RoolzError(Exception):
    pass


class UndefinedOperatorError(RoolzError):
    def __init__(self, operator_name):
        self.operator_name = operator_name
        super().__init__(f"Operator '{operator_name}' is not defined.")


class InvalidConditionError(RoolzError):
    def __init__(self, path: str, message: str):
        self.path = path
        self.message = message
        super().__init__(f"Invalid condition at path '{path}': {message}")

    def __eq__(self, other):
        return (
            isinstance(other, InvalidConditionError)
            and self.path == other.path
            and self.message == other.message
        )


class InvalidActionError(RoolzError):
    def __init__(self, path: str, message: str):
        self.path = path
        self.message = message
        super().__init__(f"Invalid action at path '{path}': {message}")

    def __eq__(self, other):
        return (
            isinstance(other, InvalidActionError)
            and self.path == other.path
            and self.message == other.message
        )


class InvalidRuleError(RoolzError):
    def __init__(self, condition_errors: list[InvalidConditionError], action_errors: list[InvalidActionError]):
        self.condition_errors = condition_errors
        self.action_errors = action_errors
        super().__init__(f"Invalid rule: condition errors: {condition_errors}, action errors: {action_errors}")

    def __eq__(self, other):
        return (
            isinstance(other, InvalidRuleError)
            and self.condition_errors == other.condition_errors
            and self.action_errors == other.action_errors
        )
