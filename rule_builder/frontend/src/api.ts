import type { FactInfo, OperatorInfo } from './types';

const API = '/api';

export async function fetchOperators(): Promise<OperatorInfo[]> {
  const r = await fetch(`${API}/operators`);
  if (!r.ok) throw new Error('Failed to fetch operators');
  return r.json();
}

export async function fetchFactsFromDefinition(content: string, format: 'json' | 'yaml'): Promise<FactInfo[]> {
  const r = await fetch(`${API}/facts/from-definition`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, format }),
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(err.detail || 'Failed to parse fact definition');
  }
  return r.json();
}

export async function fetchFactsFromPython(source: string): Promise<FactInfo[]> {
  const r = await fetch(`${API}/facts/from-python`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source }),
  });
  if (!r.ok) throw new Error('Failed to introspect Python source');
  return r.json();
}

export type ValidateResult = {
  valid: boolean;
  errors: Array<{ rule_id?: string; path: string; message: string; input_value?: unknown }>;
};

export async function validateCondition(
  condition: unknown,
  factClassPath?: string | null
): Promise<ValidateResult> {
  const r = await fetch(`${API}/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ condition, fact_class_path: factClassPath || null }),
  });
  if (!r.ok) throw new Error('Validation request failed');
  return r.json();
}

/** Validate a ruleset: backend iterates over each condition (values of base keys), not the whole structure. */
export async function validateRuleset(
  ruleset: Record<string, unknown>,
  factClassPath?: string | null,
  facts?: FactInfo[]
): Promise<ValidateResult> {
  const r = await fetch(`${API}/validate-ruleset`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ruleset,
      fact_class_path: factClassPath || null,
      facts: facts && facts.length > 0 ? facts : null,
    }),
  });
  if (!r.ok) throw new Error('Validation request failed');
  return r.json();
}
