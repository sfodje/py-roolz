/** Condition shape accepted by roolz evaluate_condition */

export type FactCondition = {
  fact: string | Record<string, unknown>;
  operator: string;
  value?: unknown;
  params?: Record<string, unknown>;
  args?: unknown[];
};

export type Condition =
  | FactCondition
  | { all: Condition[] }
  | { any: Condition[] }
  | { not: Condition };

export function isFactCondition(c: Condition): c is FactCondition {
  return c !== null && typeof c === 'object' && 'fact' in c;
}

export function isAll(c: Condition): c is { all: Condition[] } {
  return c !== null && typeof c === 'object' && 'all' in c && Array.isArray((c as { all: Condition[] }).all);
}

export function isAny(c: Condition): c is { any: Condition[] } {
  return c !== null && typeof c === 'object' && 'any' in c && Array.isArray((c as { any: Condition[] }).any);
}

export function isNot(c: Condition): c is { not: Condition } {
  return c !== null && typeof c === 'object' && 'not' in c;
}

export type Ruleset = Record<string, Condition>;

export type OperatorInfo = { name: string; value_hint?: Record<string, unknown>; description?: string };

export type FactParam = { name: string; type?: string; default?: unknown; required?: boolean };

export type FactInfo = { name: string; params: FactParam[] };
