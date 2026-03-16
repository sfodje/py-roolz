"""FastAPI app for rule-builder: operators, facts, validation."""

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from rule_builder.backend.schemas import (
    FactInfo,
    FactsFromDefinitionRequest,
    FactsFromPythonRequest,
    OperatorInfo,
    ValidateRequest,
    ValidateRulesetRequest,
    ValidateResponse,
)
from rule_builder.backend.services import (
    get_operators_with_hints,
    introspect_python_source,
    parse_fact_definition,
    validate_condition_request,
    validate_ruleset_request,
)

app = FastAPI(title="Roolz Rule Builder API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/operators", response_model=list[OperatorInfo])
def api_operators() -> list[dict[str, Any]]:
    """List all registered operators with value hints for UI auto-fill."""
    return get_operators_with_hints()


@app.post("/api/facts/from-definition", response_model=list[FactInfo])
def api_facts_from_definition(body: FactsFromDefinitionRequest) -> list[dict[str, Any]]:
    """Parse a fact definition file (JSON or YAML) and return fact names and params."""
    try:
        return parse_fact_definition(body.content, body.format)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/facts/from-python", response_model=list[FactInfo])
def api_facts_from_python(body: FactsFromPythonRequest) -> list[dict[str, Any]]:
    """Introspect Python source (AST only, no execution) and return fact methods and params."""
    return introspect_python_source(body.source)


@app.post("/api/validate", response_model=ValidateResponse)
def api_validate(body: ValidateRequest) -> ValidateResponse:
    """Validate a single condition. Optionally pass fact_class_path for type-aware validation."""
    result = validate_condition_request(body.condition, body.fact_class_path)
    return ValidateResponse(valid=result["valid"], errors=result["errors"])


@app.post("/api/validate-ruleset", response_model=ValidateResponse)
def api_validate_ruleset(body: ValidateRulesetRequest) -> ValidateResponse:
    """Validate a ruleset by iterating over each condition (values of base keys). Not the entire structure at once."""
    facts = [f.model_dump() for f in body.facts] if body.facts else None
    result = validate_ruleset_request(body.ruleset, body.fact_class_path, facts)
    return ValidateResponse(valid=result["valid"], errors=result["errors"])
