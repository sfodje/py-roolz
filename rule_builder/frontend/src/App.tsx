import { useState, useEffect, useCallback } from 'react';
import { RuleEditor } from './RuleEditor';
import type { Condition, FactInfo, OperatorInfo, Ruleset } from './types';
import {
  fetchOperators,
  fetchFactsFromDefinition,
  fetchFactsFromPython,
  validateRuleset,
} from './api';
import './App.css';

const DEFAULT_CONDITION: Condition = {
  fact: '',
  operator: 'equal_to',
  value: '',
};

type Toast = { id: string; message: string; type: 'success' | 'error' | 'info' };

// Icons
const IconPlus = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
);
const IconTrash = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
);
const IconCheck = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
);
const IconDownload = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
);
const IconDatabase = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>
);
const IconSearch = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
);
const IconX = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
);
const IconUpload = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
);
const IconCopy = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
);

function App() {
  const [ruleset, setRuleset] = useState<Ruleset>(() => {
    try {
      const s = localStorage.getItem('roolz-ruleset');
      if (s) return JSON.parse(s);
    } catch {}
    return {};
  });
  const [selectedRuleId, setSelectedRuleId] = useState<string | null>(() => {
    try {
      const s = localStorage.getItem('roolz-ruleset');
      if (s) {
        const parsed = JSON.parse(s);
        const keys = Object.keys(parsed);
        return keys[0] ?? null;
      }
    } catch {}
    return null;
  });
  const [operators, setOperators] = useState<OperatorInfo[]>([]);
  const [facts, setFacts] = useState<FactInfo[]>([]);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [factSource, setFactSource] = useState<'none' | 'definition' | 'python'>('none');
  const [definitionInput, setDefinitionInput] = useState('');
  const [definitionFormat, setDefinitionFormat] = useState<'json' | 'yaml'>('json');
  const [pythonInput, setPythonInput] = useState('');
  const [loadModal, setLoadModal] = useState<'none' | 'definition' | 'python'>('none');
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [showImportModal, setShowImportModal] = useState(false);
  const [importInput, setImportInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [isLoadingFacts, setIsLoadingFacts] = useState(false);

  useEffect(() => {
    fetchOperators()
      .then(setOperators)
      .catch(() => setOperators([]));
  }, []);

  useEffect(() => {
    localStorage.setItem('roolz-ruleset', JSON.stringify(ruleset));
  }, [ruleset]);

  const showToast = useCallback((message: string, type: Toast['type'] = 'info') => {
    const id = Math.random().toString(36).slice(2);
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 4000);
  }, []);

  const addRule = useCallback(() => {
    const base = 'new_rule';
    let id = base;
    let n = 0;
    while (id in ruleset) id = `${base}_${++n}`;
    setRuleset((prev) => ({ ...prev, [id]: { ...DEFAULT_CONDITION } }));
    setSelectedRuleId(id);
  }, [ruleset]);

  const removeRule = useCallback((ruleId: string) => {
    setRuleset((prev) => {
      const next = { ...prev };
      delete next[ruleId];
      return next;
    });
    if (selectedRuleId === ruleId) {
      const ids = Object.keys(ruleset).filter((k) => k !== ruleId);
      setSelectedRuleId(ids[0] ?? null);
    }
  }, [ruleset, selectedRuleId]);

  const duplicateRule = useCallback((ruleId: string) => {
    const condition = ruleset[ruleId];
    if (!condition) return;
    const deepCopy = JSON.parse(JSON.stringify(condition));
    let newId = `${ruleId}_copy`;
    let n = 0;
    while (newId in ruleset) newId = `${ruleId}_copy_${++n}`;
    setRuleset((prev) => ({ ...prev, [newId]: deepCopy }));
    setSelectedRuleId(newId);
  }, [ruleset]);

  const setRuleId = useCallback((oldId: string, newId: string) => {
    if (!newId || oldId === newId) return;
    setRuleset((prev) => {
      const next = { ...prev };
      const cond = next[oldId];
      delete next[oldId];
      next[newId] = cond;
      return next;
    });
    if (selectedRuleId === oldId) setSelectedRuleId(newId);
  }, [selectedRuleId]);

  const setCondition = useCallback((ruleId: string, condition: Condition) => {
    setRuleset((prev) => ({ ...prev, [ruleId]: condition }));
  }, []);

  const runValidation = useCallback(async () => {
    setValidationErrors([]);
    const ids = Object.keys(ruleset);
    if (ids.length === 0) return;
    setIsValidating(true);
    try {
      const res = await validateRuleset(ruleset, null, facts.length > 0 ? facts : undefined);
      if (!res.valid && res.errors?.length) {
        setValidationErrors(
          res.errors.map((e) => `[${e.rule_id ?? '?'}] ${e.path}: ${e.message}`)
        );
      } else {
        showToast('All rules are valid', 'success');
      }
    } catch (e) {
      showToast(String(e), 'error');
    } finally {
      setIsValidating(false);
    }
  }, [ruleset, showToast]);

  const loadFactsFromDefinition = useCallback(async () => {
    setIsLoadingFacts(true);
    try {
      const list = await fetchFactsFromDefinition(definitionInput, definitionFormat);
      setFacts(list);
      setFactSource('definition');
      setLoadModal('none');
      showToast(`Loaded ${list.length} facts from definition`, 'success');
    } catch (e) {
      showToast(String(e), 'error');
    } finally {
      setIsLoadingFacts(false);
    }
  }, [definitionInput, definitionFormat, showToast]);

  const loadFactsFromPython = useCallback(async () => {
    setIsLoadingFacts(true);
    try {
      const list = await fetchFactsFromPython(pythonInput);
      setFacts(list);
      setFactSource('python');
      setLoadModal('none');
      showToast(`Loaded ${list.length} facts from Python source`, 'success');
    } catch (e) {
      showToast(String(e), 'error');
    } finally {
      setIsLoadingFacts(false);
    }
  }, [pythonInput, showToast]);

  const exportJson = useCallback(() => {
    const json = JSON.stringify(ruleset, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ruleset.json';
    a.click();
    URL.revokeObjectURL(url);
    showToast('Ruleset exported', 'success');
  }, [ruleset, showToast]);

  const importJson = useCallback(() => {
    try {
      const parsed = JSON.parse(importInput);
      if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
        showToast('Invalid ruleset: expected a JSON object', 'error');
        return;
      }
      const keys = Object.keys(parsed);
      if (keys.length === 0) {
        showToast('Cannot import an empty ruleset', 'error');
        return;
      }
      setRuleset(parsed);
      setSelectedRuleId(keys[0]);
      setShowImportModal(false);
      setImportInput('');
      showToast(`Imported ${keys.length} rule(s)`, 'success');
    } catch (e) {
      showToast(`Invalid JSON: ${String(e)}`, 'error');
    }
  }, [importInput, showToast]);

  const ruleIds = Object.keys(ruleset);
  const filteredRuleIds = ruleIds.filter(id => id.toLowerCase().includes(searchQuery.toLowerCase()));

  useEffect(() => {
    const handle = (e: KeyboardEvent) => {
      const mod = e.metaKey || e.ctrlKey;
      if (!mod) return;
      if (e.key === 's') { e.preventDefault(); runValidation(); }
      else if (e.key === 'e') { e.preventDefault(); if (ruleIds.length > 0) exportJson(); }
      else if (e.key === 'n') { e.preventDefault(); addRule(); }
      else if (e.key === 'i') { e.preventDefault(); setShowImportModal(true); }
    };
    document.addEventListener('keydown', handle);
    return () => document.removeEventListener('keydown', handle);
  }, [runValidation, exportJson, addRule, ruleIds.length]);

  return (
    <div className="app">
      <header className="app-header">
        <h1>
          <img src="/logo.png" alt="Roolz" className="header-logo" />
          Roolz <span className="subtitle">Rule Builder</span>
        </h1>
        {factSource !== 'none' && (
          <span className="fact-source">Facts: {factSource} ({facts.length})</span>
        )}
      </header>

      <nav className="toolbar">
        <button type="button" className="primary" onClick={addRule} title="Add a new rule (Ctrl+N)">
          <IconPlus /> Add Rule
        </button>
        <button type="button" onClick={() => setLoadModal('definition')} disabled={isLoadingFacts} title="Load facts from a definition file">
          <IconDatabase /> Load Definition
        </button>
        <button type="button" onClick={() => setLoadModal('python')} disabled={isLoadingFacts} title="Load facts by introspecting Python source">
          <IconSearch /> Introspect Python
        </button>
        <button type="button" onClick={runValidation} disabled={isValidating} title="Validate all rules (Ctrl+S)">
          {isValidating ? <span className="spinner" /> : <IconCheck />} Validate All
        </button>
        <button type="button" onClick={exportJson} disabled={ruleIds.length === 0} title="Export ruleset as JSON (Ctrl+E)">
          <IconDownload /> Export JSON
        </button>
        <button type="button" onClick={() => setShowImportModal(true)} title="Import ruleset from JSON (Ctrl+I)">
          <IconUpload /> Import JSON
        </button>
      </nav>

      <div className="layout">
        <aside className="rule-list">
          <header>
            <h2>Rules</h2>
            <span className="fact-source">{ruleIds.length}</span>
          </header>
          <div className="rule-search">
            <input
              type="text"
              placeholder="Search rules..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
            />
          </div>
          {ruleIds.length === 0 ? (
            <div className="placeholder" style={{ padding: '2rem' }}>
              <p>No rules yet.</p>
            </div>
          ) : filteredRuleIds.length === 0 ? (
            <div className="placeholder" style={{ padding: '2rem' }}>
              <p>No matches.</p>
            </div>
          ) : (
            <div className="rule-list-items">
              {filteredRuleIds.map((id) => (
                <div className="rule-list-item" key={id}>
                  <button
                    type="button"
                    className={selectedRuleId === id ? 'selected' : ''}
                    onClick={() => setSelectedRuleId(id)}
                  >
                    <span className="rule-name">{id}</span>
                    {selectedRuleId === id && <IconCheck />}
                  </button>
                  <button
                    type="button"
                    className="dup-btn"
                    onClick={(e) => { e.stopPropagation(); duplicateRule(id); }}
                    title="Duplicate rule"
                  >
                    <IconCopy />
                  </button>
                </div>
              ))}
            </div>
          )}
        </aside>

        <main className="main">
          {validationErrors.length > 0 && (
            <div className="validation-errors">
              <strong>Validation errors:</strong>
              <ul>
                {validationErrors.map((err, i) => (
                  <li key={i}>{err}</li>
                ))}
              </ul>
            </div>
          )}

          {selectedRuleId && ruleset[selectedRuleId] !== undefined ? (
            <RuleEditor
              key={selectedRuleId}
              ruleId={selectedRuleId}
              condition={ruleset[selectedRuleId]}
              ruleset={ruleset}
              onRuleIdChange={setRuleId}
              onConditionChange={setCondition}
              onRemove={removeRule}
              operators={operators}
              facts={facts}
            />
          ) : (
            <div className="placeholder">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="9" y1="15" x2="15" y2="15"></line></svg>
              <h3>No Rule Selected</h3>
              <p>Select a rule from the sidebar or create a new one to start building.</p>
            </div>
          )}
        </main>
      </div>

      {loadModal === 'definition' && (
        <div className="modal-overlay" onClick={() => setLoadModal('none')}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Load Facts from Definition</h3>
            <p>Paste JSON or YAML with a <code>facts</code> array.</p>
            <div className="row" style={{ marginBottom: '1rem' }}>
              <select
                value={definitionFormat}
                onChange={(e) => setDefinitionFormat(e.target.value as 'json' | 'yaml')}
                style={{ width: '100%' }}
              >
                <option value="json">JSON</option>
                <option value="yaml">YAML</option>
              </select>
            </div>
            <textarea
              value={definitionInput}
              onChange={(e) => setDefinitionInput(e.target.value)}
              placeholder='{"facts": [{"name": "parcel_weight", "params": [{"name": "unit", "type": "string", "default": "lb"}]}]}'
            />
            <div className="modal-actions">
              <button type="button" className="btn-cancel" onClick={() => setLoadModal('none')}>
                Cancel
              </button>
              <button type="button" className="btn-primary" onClick={loadFactsFromDefinition} disabled={isLoadingFacts}>
                {isLoadingFacts ? <span className="spinner" style={{ marginRight: '0.5rem' }} /> : null}Load Facts
              </button>
            </div>
          </div>
        </div>
      )}

      {loadModal === 'python' && (
        <div className="modal-overlay" onClick={() => setLoadModal('none')}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Load Facts from Python</h3>
            <p>Paste Python code. Public methods will be used as fact names.</p>
            <textarea
              value={pythonInput}
              onChange={(e) => setPythonInput(e.target.value)}
              placeholder="class ShipmentFacts:\n    def parcel_weight(self, unit: str = 'lb'): ..."
            />
            <div className="modal-actions">
              <button type="button" className="btn-cancel" onClick={() => setLoadModal('none')}>
                Cancel
              </button>
              <button type="button" className="btn-primary" onClick={loadFactsFromPython} disabled={isLoadingFacts}>
                {isLoadingFacts ? <span className="spinner" style={{ marginRight: '0.5rem' }} /> : null}Introspect Source
              </button>
            </div>
          </div>
        </div>
      )}

      {showImportModal && (
        <div className="modal-overlay" onClick={() => setShowImportModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Import Ruleset from JSON</h3>
            <p>
              Paste a JSON ruleset object below. The keys should be rule IDs and values should be conditions.
              {ruleIds.length > 0 && (
                <span style={{ display: 'block', marginTop: '0.5rem', color: '#b45309', fontWeight: 500 }}>
                  Warning: this will replace your current ruleset ({ruleIds.length} rule{ruleIds.length !== 1 ? 's' : ''}).
                </span>
              )}
            </p>
            <textarea
              value={importInput}
              onChange={(e) => setImportInput(e.target.value)}
              placeholder='{"my_rule": {"fact": "age", "operator": "greater_than", "value": 18}}'
            />
            <div className="modal-actions">
              <button type="button" className="btn-cancel" onClick={() => setShowImportModal(false)}>
                Cancel
              </button>
              <button type="button" className="btn-primary" onClick={importJson}>
                Import
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="toast-container">
        {toasts.map(t => (
          <div key={t.id} className={`toast ${t.type}`}>
            {t.type === 'success' && <IconCheck />}
            {t.type === 'error' && <IconX />}
            {t.message}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
