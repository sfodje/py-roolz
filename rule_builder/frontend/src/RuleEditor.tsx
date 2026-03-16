import { useCallback, useState } from 'react';
import { ConditionEditor } from './ConditionEditor';
import type { Condition, FactInfo, OperatorInfo, Ruleset } from './types';

type Props = {
  ruleId: string;
  condition: Condition;
  ruleset: Ruleset;
  onRuleIdChange: (oldId: string, newId: string) => void;
  onConditionChange: (ruleId: string, c: Condition) => void;
  onRemove: (ruleId: string) => void;
  operators: OperatorInfo[];
  facts: FactInfo[];
};

const IconTrash = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
);

export function RuleEditor({
  ruleId,
  condition,
  ruleset,
  onRuleIdChange,
  onConditionChange,
  onRemove,
  operators,
  facts,
}: Props) {
  const [localId, setLocalId] = useState(ruleId);

  const handleConditionChange = useCallback(
    (c: Condition) => onConditionChange(ruleId, c),
    [ruleId, onConditionChange]
  );

  const isDuplicateId = (id: string) =>
    id !== ruleId && Object.keys(ruleset).includes(id);

  return (
    <section className="rule-editor">
      <div className="rule-header">
        <div className="rule-id-container">
          <input
            className="rule-id"
            value={localId}
            onChange={(e) => {
              setLocalId(e.target.value);
            }}
            onBlur={(e) => {
              const v = e.target.value.trim();
              if (v && v !== ruleId) {
                onRuleIdChange(ruleId, v);
              } else {
                setLocalId(ruleId);
              }
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.currentTarget.blur();
              }
            }}
            placeholder="rule_id"
            title="Rule identifier (unique key in exported JSON)"
          />
          {isDuplicateId(ruleId) && (
            <p className="warning">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
              Duplicate rule ID. This will overwrite another rule on export.
            </p>
          )}
        </div>
        <button type="button" className="remove-rule" onClick={() => onRemove(ruleId)} title="Remove rule">
          <IconTrash />
        </button>
      </div>
      
      <ConditionEditor
        value={condition}
        onChange={handleConditionChange}
        operators={operators}
        facts={facts}
      />
    </section>
  );
}
