"""Business logic for operators, fact definitions, Python introspection, and validation."""

import ast
import json
from typing import Any

import yaml

from roolz._conditions import validate_condition
from roolz._operators import list_operators

from rule_builder.backend.operator_hints import OPERATOR_VALUE_HINTS


def get_operators_with_hints() -> list[dict[str, Any]]:
    """Return all registered operator names with value hints for UI."""
    names = list_operators()
    return [
        {
            "name": name,
            "value_hint": OPERATOR_VALUE_HINTS.get(name),
            "description": OPERATOR_VALUE_HINTS.get(name, {}).get("description"),
        }
        for name in names
    ]


def parse_fact_definition(content: str, format: str) -> list[dict[str, Any]]:
    """
    Parse a fact definition file (JSON or YAML).
    Expected shape: { "facts": [ { "name": "...", "params": [ { "name": "...", "type": "...", "default": ... } ] } ] }
    """
    content = content.strip()
    if format == "yaml":
        data = yaml.safe_load(content)
    else:
        data = json.loads(content)

    if not isinstance(data, dict):
        return []

    facts = data.get("facts", data.get("fact", []))
    if not isinstance(facts, list):
        return []

    out = []
    for f in facts:
        if isinstance(f, str):
            out.append({"name": f, "params": []})
        elif isinstance(f, dict) and "name" in f:
            params = f.get("params", f.get("parameters", []))
            if not isinstance(params, list):
                params = []
            out.append({"name": f["name"], "params": params})
    return out


def introspect_python_source(source: str) -> list[dict[str, Any]]:
    """
    Extract fact-like methods from Python source using AST (no execution).
    Returns public methods (no leading _) of the first class found, or all top-level callables.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    facts: list[dict[str, Any]] = []

    def params_from_args(args: ast.arguments) -> list[dict[str, Any]]:
        params = []
        for i, arg in enumerate(args.args):
            if arg.arg in ("self", "cls"):
                continue
            name = arg.arg
            default = None
            default_idx = i - (len(args.args) - len(args.defaults))
            if default_idx >= 0 and args.defaults:
                default_ast = args.defaults[default_idx]
                if isinstance(default_ast, ast.Constant):
                    default = default_ast.value
                elif isinstance(default_ast, ast.Str):  # Python 3.7 compat
                    default = default_ast.s
            param_type = "string"
            if arg.annotation:
                if isinstance(arg.annotation, ast.Name):
                    param_type = arg.annotation.id
                elif hasattr(arg.annotation, "id"):
                    param_type = getattr(arg.annotation, "id", "string")
            params.append({"name": name, "type": param_type, "default": default, "required": default is None})
        return params

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                    params = params_from_args(item.args)
                    facts.append({"name": item.name, "params": params})
            break  # first class only

    if not facts:
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                params = params_from_args(node.args)
                facts.append({"name": node.name, "params": params})

    return facts


def validate_condition_request(condition: dict[str, Any], fact_class_path: str | None = None) -> dict[str, Any]:
    """
    Run validate_condition. fact_type is optional (no import for safety).
    Returns { "valid": bool, "errors": [ { "path", "message", "input_value" } ] }.
    """
    fact_type = None
    if fact_class_path:
        try:
            mod_path, _, cls_name = fact_class_path.rpartition(".")
            if not mod_path or not cls_name:
                return {"valid": False, "errors": [{"path": "", "message": "Invalid fact_class_path", "input_value": fact_class_path}]}
            import importlib
            mod = importlib.import_module(mod_path)
            fact_type = getattr(mod, cls_name, None)
        except Exception as e:
            return {"valid": False, "errors": [{"path": "", "message": f"Cannot load fact class: {e}", "input_value": fact_class_path}]}

    errors = validate_condition(condition, fact_type)
    if not errors:
        return {"valid": True, "errors": []}
    return {
        "valid": False,
        "errors": [
            {
                "path": getattr(e, "path", ""),
                "message": getattr(e, "message", str(e)),
                "input_value": getattr(e, "input_value", None),
            }
            for e in errors
        ],
    }


def _validate_against_definitions(
    condition: Any,
    facts: list[dict[str, Any]],
    path: str = "*",
) -> list[dict[str, Any]]:
    """
    Validate a condition against loaded fact definitions (names + param schemas).
    Catches unknown fact names and misspelled param keys without requiring a Python class.
    Returns a list of error dicts with path, message, and input_value.
    """
    errors: list[dict[str, Any]] = []

    if not isinstance(condition, dict):
        return errors

    keys = tuple(condition.keys())

    if keys == ("all",):
        for i, sub in enumerate(condition["all"]):
            errors.extend(_validate_against_definitions(sub, facts, f"{path}.all[{i}]"))
    elif keys == ("any",):
        for i, sub in enumerate(condition["any"]):
            errors.extend(_validate_against_definitions(sub, facts, f"{path}.any[{i}]"))
    elif "not" in condition:
        errors.extend(_validate_against_definitions(condition["not"], facts, f"{path}.not"))
    elif "fact" in condition:
        fact_val = condition["fact"]
        params: dict[str, Any] = {}

        if isinstance(fact_val, str):
            fact_name = fact_val
            params = condition.get("params", {}) or {}
        elif isinstance(fact_val, dict) and len(fact_val) == 1:
            fact_name, fact_params = next(iter(fact_val.items()))
            if isinstance(fact_params, dict):
                params = fact_params
        else:
            return errors

        fact_names = [f["name"] for f in facts]
        known = next((f for f in facts if f["name"] == fact_name), None)

        if known is None:
            errors.append({
                "path": path,
                "message": f"Unknown fact '{fact_name}'. Available facts: {fact_names}",
                "input_value": fact_name,
            })
        elif params:
            known_param_names = {p["name"] for p in known.get("params", [])}
            if known_param_names:
                for param_key in params:
                    if param_key not in known_param_names:
                        errors.append({
                            "path": path,
                            "message": (
                                f"Unknown parameter '{param_key}' for fact '{fact_name}'. "
                                f"Known parameters: {sorted(known_param_names)}"
                            ),
                            "input_value": params,
                        })

    return errors


def validate_ruleset_request(
    ruleset: dict[str, Any],
    fact_class_path: str | None = None,
    facts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Validate a ruleset by iterating over the values of the base keys (each condition).
    Does not validate the ruleset structure as a single condition.
    Returns { "valid": bool, "errors": [ { "rule_id", "path", "message", "input_value" } ] }.
    """
    all_errors: list[dict[str, Any]] = []
    for rule_id, condition in ruleset.items():
        result = validate_condition_request(condition, fact_class_path)
        if not result["valid"] and result.get("errors"):
            for err in result["errors"]:
                all_errors.append({"rule_id": rule_id, **err})
        if facts:
            for err in _validate_against_definitions(condition, facts):
                all_errors.append({"rule_id": rule_id, **err})
    return {
        "valid": len(all_errors) == 0,
        "errors": all_errors,
    }
