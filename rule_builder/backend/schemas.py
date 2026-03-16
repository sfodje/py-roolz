"""Pydantic schemas for rule-builder API."""

from typing import Any

from pydantic import BaseModel, Field


class OperatorInfo(BaseModel):
    """Operator name and value hint for UI."""

    name: str
    value_hint: dict[str, Any] | None = None
    description: str | None = None


class FactParam(BaseModel):
    """Parameter for a fact (from definition or introspection)."""

    name: str
    type: str = "string"
    default: Any = None
    required: bool = False


class FactInfo(BaseModel):
    """Fact name and optional params for UI."""

    name: str
    params: list[FactParam] = Field(default_factory=list)


class FactsFromDefinitionRequest(BaseModel):
    """Request body: fact definition file content (JSON or YAML string)."""

    content: str
    format: str = "json"  # "json" | "yaml"


class FactsFromPythonRequest(BaseModel):
    """Request body: Python source code to introspect (no execution)."""

    source: str


class ValidateRequest(BaseModel):
    """Request body: condition and optional fact class path for validation."""

    condition: dict[str, Any]
    fact_class_path: str | None = None  # e.g. "myapp.facts.ShipmentFacts"


class ValidateRulesetRequest(BaseModel):
    """Request body: full ruleset (rule_id -> condition) and optional fact class path."""

    ruleset: dict[str, Any]  # base keys = rule ids, values = conditions to validate
    fact_class_path: str | None = None
    facts: list[FactInfo] | None = None  # loaded fact definitions for name/param validation


class ValidateResponse(BaseModel):
    """Validation result."""

    valid: bool
    errors: list[dict[str, Any]] = Field(default_factory=list)
