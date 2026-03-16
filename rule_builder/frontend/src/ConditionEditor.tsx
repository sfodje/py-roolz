import { useState, useCallback, useRef, useEffect, useId } from 'react';
import type { Condition, FactCondition, FactInfo, OperatorInfo } from './types';
import { isFactCondition, isAll, isAny, isNot } from './types';

type Props = {
  value: Condition;
  onChange: (c: Condition) => void;
  operators: OperatorInfo[];
  facts: FactInfo[];
  depth?: number;
};

// Icons
const IconPlus = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
);
const IconTrash = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
);

function getValueType(hint: Record<string, unknown> | undefined): 'none' | 'string' | 'number' | 'array' | 'any' {
  if (!hint) return 'any';
  const t = hint.type as string | undefined;
  if (t === 'none') return 'none';
  if (t === 'string') return 'string';
  if (t === 'number') return 'number';
  if (t === 'array') return 'array';
  return 'any';
}

function parseValue(val: unknown, type: 'string' | 'number' | 'array' | 'any'): unknown {
  if (val === undefined || val === null) return type === 'array' ? [] : type === 'number' ? 0 : '';
  if (type === 'array') {
    if (Array.isArray(val)) return val;
    if (typeof val === 'string') {
      try {
        const a = JSON.parse(val);
        return Array.isArray(a) ? a : [a];
      } catch {
        return val ? [val] : [];
      }
    }
    return [val];
  }
  if (type === 'number') return typeof val === 'number' ? val : Number(val);
  return val;
}

const defaultFactCondition = (operators: OperatorInfo[]): FactCondition => ({
  fact: '',
  operator: operators[0]?.name ?? 'equal_to',
  value: '',
});

export function ConditionEditor({ value, onChange, operators, facts }: Props) {
  const [paramsJson, setParamsJson] = useState<string | null>(null);
  const [factDropdownOpen, setFactDropdownOpen] = useState(false);
  const factDropdownRef = useRef<HTMLDivElement>(null);
  const factListId = useId();

  // Derive factName from current value
  const factName = isFactCondition(value)
    ? typeof value.fact === 'string'
      ? value.fact
      : value.fact
      ? Object.keys(value.fact)[0] ?? ''
      : ''
    : '';

  // Reset local state when fact changes
  const [lastFact, setLastFact] = useState(factName);
  if (factName !== lastFact) {
    setLastFact(factName);
    setParamsJson(null);
  }

  const updateFactCondition = useCallback(
    (up: Partial<FactCondition>) => {
      const base = (isFactCondition(value) ? value : {}) as FactCondition;
      const next: FactCondition = {
        fact: up.fact !== undefined ? up.fact : base.fact ?? '',
        operator: up.operator ?? base.operator ?? (operators[0]?.name || 'equal_to'),
        value: up.value !== undefined ? up.value : base.value,
        params: up.params !== undefined ? up.params : base.params,
        args: up.args !== undefined ? up.args : base.args,
      };
      if (Object.keys(next.params || {}).length === 0) delete next.params;
      if (!(next.args && next.args.length)) delete next.args;
      onChange(next);
    },
    [value, operators, onChange]
  );

  // Close fact dropdown when clicking outside (must run unconditionally for hook order)
  useEffect(() => {
    if (!factDropdownOpen) return;
    const handle = (e: MouseEvent) => {
      if (factDropdownRef.current?.contains(e.target as Node)) return;
      setFactDropdownOpen(false);
    };
    document.addEventListener('mousedown', handle);
    return () => document.removeEventListener('mousedown', handle);
  }, [factDropdownOpen]);

  if (isFactCondition(value)) {
    const op = operators.find((o) => o.name === value.operator) ?? operators[0];
    const valueHint = op?.value_hint;
    const valueType = getValueType(valueHint);

    const factOptions = facts.map((f) => f.name);
    const filteredFacts = factOptions.filter((n) =>
      n.toLowerCase().includes(factName.trim().toLowerCase())
    );
    const currentFact = facts.find((f) => f.name.trim() === factName.trim());
    const paramsSchema = currentFact?.params ?? [];

    return (
      <div className="condition-editor fact">
        <div className="row condition-type-row">
          <label>Type</label>
          <select
            value="fact"
            onChange={(e) => {
              const t = e.target.value;
              if (t === 'all') onChange({ all: [value] });
              else if (t === 'any') onChange({ any: [value] });
              else if (t === 'not') onChange({ not: value });
            }}
          >
            <option value="fact">Fact Condition</option>
            <option value="all">ALL of Group</option>
            <option value="any">ANY of Group</option>
            <option value="not">NOT (negation)</option>
          </select>
        </div>
        <div className="row fact-combobox-row" ref={factDropdownRef}>
          <label>Fact</label>
          <div className="fact-combobox">
            <input
              type="text"
              value={factName}
              onChange={(e) => {
                updateFactCondition({ fact: e.target.value });
                setFactDropdownOpen(true);
              }}
              onFocus={() => setFactDropdownOpen(true)}
              onBlur={() => {
                setTimeout(() => setFactDropdownOpen(false), 150);
              }}
              placeholder="Type to search or enter fact name"
              autoComplete="off"
              aria-expanded={factDropdownOpen}
              aria-haspopup="listbox"
              aria-controls={factListId}
            />
            {factDropdownOpen && (
              <ul
                id={factListId}
                className="fact-dropdown"
                role="listbox"
                onMouseDown={(e) => e.preventDefault()}
              >
                {filteredFacts.length === 0 ? (
                  <li className="fact-dropdown-empty">No matching facts. Type to add custom name.</li>
                ) : (
                  filteredFacts.map((n) => (
                    <li
                      key={n}
                      role="option"
                      className={factName === n ? 'selected' : ''}
                      onMouseDown={() => {
                        updateFactCondition({ fact: n });
                        setFactDropdownOpen(false);
                      }}
                    >
                      {n}
                    </li>
                  ))
                )}
              </ul>
            )}
          </div>
        </div>
        <div className="row">
          <label>Operator</label>
          <select
            value={value.operator}
            onChange={(e) => updateFactCondition({ operator: e.target.value })}
          >
            {operators.map((o) => (
              <option key={o.name} value={o.name} title={o.description}>
                {o.name}
              </option>
            ))}
          </select>
        </div>
        {op?.description && (
          <p className="operator-description">{op.description}</p>
        )}
        {valueType !== 'none' && (
          <div className="row">
            <label>Value</label>
            {valueType === 'array' ? (
              <input
                type="text"
                value={
                  Array.isArray(value.value)
                    ? JSON.stringify(value.value)
                    : String(value.value ?? '')
                }
                onChange={(e) => {
                  const v = parseValue(e.target.value, 'array');
                  updateFactCondition({ value: v });
                }}
                placeholder='["val1", "val2"]'
              />
            ) : valueType === 'number' ? (
              <input
                type="number"
                value={typeof value.value === 'number' ? value.value : ''}
                onChange={(e) =>
                  updateFactCondition({
                    value: e.target.value === '' ? undefined : Number(e.target.value),
                  })
                }
              />
            ) : (
              <input
                type="text"
                value={String(value.value ?? '')}
                onChange={(e) => updateFactCondition({ value: e.target.value || undefined })}
                placeholder={valueHint?.description as string}
              />
            )}
          </div>
        )}
        {(paramsSchema.length > 0 || (value.params && Object.keys(value.params).length > 0)) && (
          <div className="row">
            <label>Params</label>
            <input
              type="text"
              value={paramsJson ?? JSON.stringify(value.params ?? {})}
              onChange={(e) => {
                setParamsJson(e.target.value);
                try {
                  const p = JSON.parse(e.target.value || '{}');
                  if (typeof p === 'object' && p !== null)
                    updateFactCondition({ params: p });
                } catch {
                  // ignore invalid json while typing
                }
              }}
              placeholder='{"key": "value"}'
            />
          </div>
        )}
      </div>
    );
  }

  if (isAll(value)) {
    return (
      <div className="condition-editor all">
        <div className="condition-header">
          <span className="group-badge all">ALL of</span>
          <select
            className="compact-select"
            value="all"
            onChange={(e) => {
              const t = e.target.value;
              if (t === 'fact') onChange(defaultFactCondition(operators));
              else if (t === 'any') onChange({ any: value.all });
              else if (t === 'not') onChange({ not: value.all.length === 1 ? value.all[0] : { all: value.all } });
            }}
            style={{ width: '120px' }}
          >
            <option value="all">Group: ALL</option>
            <option value="any">Group: ANY</option>
            <option value="not">Group: NOT</option>
            <option value="fact">Convert to Fact</option>
          </select>
        </div>
        <div className="nested-container">
          {value.all.map((c, i) => (
            <div key={i} className="nested-item">
              <ConditionEditor
                value={c}
                onChange={(c2) => {
                  const next = [...value.all];
                  next[i] = c2;
                  onChange({ all: next });
                }}
                operators={operators}
                facts={facts}
              />
              <button
                type="button"
                className="remove-btn"
                onClick={() => {
                  const next = value.all.filter((_, j) => j !== i);
                  onChange(next.length === 1 ? next[0] : { all: next });
                }}
                title="Remove condition"
                style={{ position: 'absolute', right: 0, top: 0 }}
              >
                <IconTrash />
              </button>
            </div>
          ))}
          <button
            type="button"
            className="add-btn"
            onClick={() => onChange({ all: [...value.all, defaultFactCondition(operators)] })}
          >
            <IconPlus /> Add Condition
          </button>
        </div>
      </div>
    );
  }

  if (isAny(value)) {
    return (
      <div className="condition-editor any">
        <div className="condition-header">
          <span className="group-badge any">ANY of</span>
          <select
            className="compact-select"
            value="any"
            onChange={(e) => {
              const t = e.target.value;
              if (t === 'fact') onChange(defaultFactCondition(operators));
              else if (t === 'all') onChange({ all: value.any });
              else if (t === 'not') onChange({ not: value.any.length === 1 ? value.any[0] : { any: value.any } });
            }}
            style={{ width: '120px' }}
          >
            <option value="any">Group: ANY</option>
            <option value="all">Group: ALL</option>
            <option value="not">Group: NOT</option>
            <option value="fact">Convert to Fact</option>
          </select>
        </div>
        <div className="nested-container">
          {value.any.map((c, i) => (
            <div key={i} className="nested-item">
              <ConditionEditor
                value={c}
                onChange={(c2) => {
                  const next = [...value.any];
                  next[i] = c2;
                  onChange({ any: next });
                }}
                operators={operators}
                facts={facts}
              />
              <button
                type="button"
                className="remove-btn"
                onClick={() => {
                  const next = value.any.filter((_, j) => j !== i);
                  onChange(next.length === 1 ? next[0] : { any: next });
                }}
                title="Remove condition"
                style={{ position: 'absolute', right: 0, top: 0 }}
              >
                <IconTrash />
              </button>
            </div>
          ))}
          <button
            type="button"
            className="add-btn"
            onClick={() => onChange({ any: [...value.any, defaultFactCondition(operators)] })}
          >
            <IconPlus /> Add Condition
          </button>
        </div>
      </div>
    );
  }

  if (isNot(value)) {
    return (
      <div className="condition-editor not">
        <div className="condition-header">
          <span className="group-badge not">NOT</span>
          <select
            className="compact-select"
            value="not"
            onChange={(e) => {
              const t = e.target.value;
              if (t === 'fact') onChange(defaultFactCondition(operators));
              else if (t === 'all') onChange({ all: [value.not] });
              else if (t === 'any') onChange({ any: [value.not] });
            }}
            style={{ width: '120px' }}
          >
            <option value="not">Group: NOT</option>
            <option value="all">Group: ALL</option>
            <option value="any">Group: ANY</option>
            <option value="fact">Convert to Fact</option>
          </select>
        </div>
        <div className="nested-container">
          <div className="nested-item">
            <ConditionEditor
              value={value.not}
              onChange={(c2) => onChange({ not: c2 })}
              operators={operators}
              facts={facts}
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="condition-editor unknown">
      <button type="button" className="add-btn" onClick={() => onChange(defaultFactCondition(operators))}>
        <IconPlus /> Set as fact condition
      </button>
    </div>
  );
}
