<h1>
  <img src="../logo.png" alt="Roolz" height="48" style="vertical-align: middle; margin-right: 0.5rem" />
  Roolz Rule Builder
</h1>

A visual web UI for building, validating, and exporting roolz rulesets — without writing JSON by hand. Rules are saved automatically in the browser and can be exported as JSON ready for use with `roolz.execute_rules()`.

## Setup

From the **project root**:

```bash
# Install backend dependencies
uv sync --extra rule-builder

# Install frontend dependencies
cd rule_builder/frontend && npm install
```

## Running

Start both servers (each in its own terminal, from the project root):

```bash
# Terminal 1 — API (port 8000)
uv run uvicorn rule_builder.backend.main:app --reload --port 8000

# Terminal 2 — UI (port 5173)
cd rule_builder/frontend && npm run dev
```

Open **http://localhost:5173**. The Vite dev server proxies all `/api` requests to the backend.

---

## UI Overview

### Toolbar

| Button | Shortcut | Description |
|---|---|---|
| **Add Rule** | `Ctrl/Cmd+N` | Creates a new rule with a default ID |
| **Load Definition** | — | Load fact names and params from a JSON/YAML definition file |
| **Introspect Python** | — | Extract facts by pasting Python source code (AST, no execution) |
| **Validate All** | `Ctrl/Cmd+S` | Validate every rule's condition structure and, if facts are loaded, fact names and parameter keys |
| **Export JSON** | `Ctrl/Cmd+E` | Download the full ruleset as `ruleset.json` |
| **Import JSON** | `Ctrl/Cmd+I` | Load a previously exported ruleset JSON into the editor |

### Rule List (sidebar)

- **Select** a rule by clicking its name.
- **Search** rules by typing in the filter box at the top of the sidebar — filters by rule ID in real time.
- **Duplicate** a rule by hovering over it and clicking the copy icon. The duplicate is named `<original_id>_copy`.
- **Delete** a rule from the rule editor header (trash icon).

Rules persist automatically in `localStorage` — your work survives page refreshes.

---

## Building Conditions

Each rule has a single top-level condition. Click the **Type** selector to choose the condition shape.

### Fact Condition

Evaluates a method on the fact object.

| Field | Description |
|---|---|
| **Fact** | Method name on the fact object. Supports free-text or autocomplete from loaded facts. |
| **Operator** | One of the 20+ registered roolz operators. A description hint appears below the selector. |
| **Value** | The comparison value. Input type adapts to the operator (text, number, or JSON array). |
| **Params** | Optional keyword arguments passed to the fact method, as a JSON object e.g. `{"unit": "in"}`. Shown only when the selected fact has known parameters. |

### Composite Conditions

| Type | Behaviour |
|---|---|
| **ALL of** | All nested conditions must be true (logical AND) |
| **ANY of** | At least one nested condition must be true (logical OR) |
| **NOT** | Negates a single nested condition |

Groups can be nested to any depth. Use the **Add Condition** button to append a child condition, and the trash icon on each child to remove it. The group type (ALL / ANY / NOT) can be changed in-place via the dropdown without losing nested conditions.

---

## Loading Facts

Loading facts enables autocomplete in the Fact field and enables **parameter-key validation** when you run Validate All.

### From a Definition File

Click **Load Definition** and paste a JSON or YAML document with a `facts` array.

```json
{
  "facts": [
    {
      "name": "parcel_weight",
      "params": [{ "name": "unit", "type": "string", "default": "lb" }]
    },
    { "name": "destination_country_code" },
    { "name": "parcel_volume", "params": [{ "name": "unit", "type": "string", "default": "in3" }] }
  ]
}
```

Each fact entry:
- `name` — fact method name (required)
- `params` — optional list of `{ "name", "type", "default", "required" }`

YAML format is also accepted — select **YAML** from the format dropdown before pasting.

### From Python Source

Click **Introspect Python** and paste your fact class source code. The backend parses it with the Python AST (no code is executed). Public methods of the first class in the file are extracted as facts; their parameters and type annotations become the param schema.

```python
class ShipmentFacts:
    def parcel_weight(self, unit: str = "lb") -> float: ...
    def parcel_volume(self, unit: str = "in3") -> float: ...
    def destination_country_code(self) -> str: ...
```

Private methods (prefixed with `_`) are ignored. If no class is found, top-level functions are used instead.

---

## Validation

Click **Validate All** (or press `Ctrl/Cmd+S`) to validate every rule.

Two layers of validation run simultaneously:

1. **Structural** — checks that each condition has a valid shape: known operator, required fields, no unexpected keys.
2. **Definition-based** (when facts are loaded) — checks that every fact name exists in the loaded facts list, and that every param key in a `params` object matches the known parameter names for that fact. This catches typos like `parcel_volum` or `{"unt": "in"}`.

Errors are displayed above the rule editor with the rule ID and the path within the condition tree, e.g.:
```
[my_rule] *.all[0]: Unknown fact 'parcel_volum'. Available facts: [parcel_volume, ...]
[my_rule] *.all[0]: Unknown parameter 'unt' for fact 'parcel_weight'. Known parameters: ['unit']
```

---

## Export / Import

**Export JSON** (`Ctrl/Cmd+E`) downloads a `ruleset.json` file. The format is a plain object where each key is a rule ID and each value is a condition:

```json
{
  "check_weight": {
    "fact": "parcel_weight",
    "operator": "less_than_or_equal_to",
    "value": 50,
    "params": { "unit": "lb" }
  },
  "check_destination": {
    "all": [
      { "fact": "destination_country_code", "operator": "one_of", "value": ["US", "CA"] }
    ]
  }
}
```

This JSON is directly compatible with `roolz.execute_rules()`:

```python
from roolz import execute_rules
import json

with open("ruleset.json") as f:
    ruleset = json.load(f)

for rule_id, condition in ruleset.items():
    execute_rules({"condition": condition, "actions": [...]}, fact, actor)
```

**Import JSON** (`Ctrl/Cmd+I`) loads a previously exported ruleset back into the editor, replacing the current ruleset.
