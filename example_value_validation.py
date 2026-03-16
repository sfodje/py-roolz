#!/usr/bin/env python3
"""
Example demonstrating parameter value validation in roolz conditions.
"""

from roolz import evaluate_condition, validate_condition


class UserFact:
    """Example fact class with typed parameters."""

    def get_age(self, user_id: int) -> int:
        """Get user age by ID."""
        # Simulate database lookup
        ages = {1: 25, 2: 30, 3: 35}
        return ages.get(user_id, 0)

    def get_name(self, user_id: int) -> str:
        """Get user name by ID."""
        # Simulate database lookup
        names = {1: "Alice", 2: "Bob", 3: "Charlie"}
        return names.get(user_id, "")

    def is_active(self, user_id: int, include_deleted: bool = False) -> bool:
        """Check if user is active."""
        # Simulate database lookup
        active_users = {1: True, 2: False, 3: True}
        return active_users.get(user_id, False)

    def get_permissions(self, user_id: int) -> list:
        """Get user permissions."""
        # Simulate database lookup
        permissions = {1: ["read", "write"], 2: ["read"], 3: ["read", "write", "admin"]}
        return permissions.get(user_id, [])

    def get_settings(self, user_id: int) -> dict:
        """Get user settings."""
        # Simulate database lookup
        settings = {1: {"theme": "dark", "notifications": True}, 2: {"theme": "light"}}
        return settings.get(user_id, {})

    def get_user_count(self, count: int) -> int:
        """Get count of users (example for negative validation)."""
        return count


def demonstrate_value_validation():
    """Demonstrate parameter value validation."""

    print("=== Parameter Value Validation Examples ===\n")

    # Valid conditions
    print("✅ Valid conditions:")

    condition = {
        "fact": {"get_age": {"user_id": 1}},
        "operator": "greater_than",
        "value": 20,
    }
    errors = validate_condition(condition, UserFact)
    print(f"  - Valid age check: {len(errors)} errors")

    condition = {
        "fact": {"get_name": {"user_id": 2}},
        "operator": "starts_with",
        "value": "B",
    }
    errors = validate_condition(condition, UserFact)
    print(f"  - Valid name check: {len(errors)} errors")

    condition = {
        "fact": {"is_active": {"user_id": 1, "include_deleted": True}},
        "operator": "is_true",
    }
    errors = validate_condition(condition, UserFact)
    print(f"  - Valid active check: {len(errors)} errors")

    print("\n❌ Invalid conditions (type validation):")

    # Type validation errors
    condition = {
        "fact": {"get_age": {"user_id": "not_a_number"}},
        "operator": "greater_than",
        "value": 20,
    }
    errors = validate_condition(condition, UserFact)
    print(f"  - Invalid user_id type: {errors[0].message}")

    condition = {
        "fact": {"get_name": {"user_id": 3.14}},
        "operator": "starts_with",
        "value": "C",
    }
    errors = validate_condition(condition, UserFact)
    print(f"  - Invalid user_id type (float): {errors[0].message}")

    condition = {
        "fact": {"is_active": {"user_id": 1, "include_deleted": "not_a_bool"}},
        "operator": "is_true",
    }
    errors = validate_condition(condition, UserFact)
    print(f"  - Invalid include_deleted type: {errors[0].message}")

    print("\n❌ Invalid conditions (value constraints):")

    # Value constraint errors
    condition = {
        "fact": {"get_user_count": {"count": -1}},
        "operator": "greater_than",
        "value": 0,
    }
    errors = validate_condition(condition, UserFact)
    if errors:
        print(f"  - Negative count: {errors[0].message}")
    else:
        print("  - Negative count: No validation error (unexpected)")

    condition = {
        "fact": {
            "get_permissions": {"user_id": 999}
        },  # Non-existent user returns empty list
        "operator": "contains",
        "value": "admin",
    }
    errors = validate_condition(condition, UserFact)
    if errors:
        print(f"  - Empty permissions list: {errors[0].message}")
    else:
        print("  - Empty permissions list: No validation error (empty list not caught)")

    # Test empty string validation
    condition = {
        "fact": {
            "get_name": {"user_id": 999}
        },  # Non-existent user returns empty string
        "operator": "starts_with",
        "value": "A",
    }
    errors = validate_condition(condition, UserFact)
    if errors:
        print(f"  - Empty name string: {errors[0].message}")
    else:
        print("  - Empty name string: No validation error (empty string not caught)")

    print("\n✅ Evaluation examples:")

    # Test evaluation with valid conditions
    fact = UserFact()

    condition = {
        "fact": {"get_age": {"user_id": 1}},
        "operator": "greater_than",
        "value": 20,
    }
    result = evaluate_condition(fact, condition)
    print(f"  - User 1 age > 20: {result}")

    condition = {
        "fact": {"get_name": {"user_id": 2}},
        "operator": "starts_with",
        "value": "B",
    }
    result = evaluate_condition(fact, condition)
    print(f"  - User 2 name starts with 'B': {result}")

    condition = {"fact": {"is_active": {"user_id": 1}}, "operator": "is_true"}
    result = evaluate_condition(fact, condition)
    print(f"  - User 1 is active: {result}")


if __name__ == "__main__":
    demonstrate_value_validation()
