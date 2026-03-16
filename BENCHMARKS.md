# Benchmark Tests

This document describes the benchmark tests for the py-roolz rule engine.

## Overview

The benchmark tests are designed to measure the performance of different components of the rule engine under various scenarios. They help identify performance bottlenecks and ensure that optimizations don't regress performance.

## Running Benchmarks

### Run all benchmarks
```bash
make benchmark
```

### Run specific benchmark files
```bash
# Operators only
uv run pytest tests/benchmark_test_operators.py --benchmark-only

# Conditions only
uv run pytest tests/benchmark_test_conditions.py --benchmark-only

# Actions only
uv run pytest tests/benchmark_test_actions.py --benchmark-only

# Rules only
uv run pytest tests/benchmark_test_rules.py --benchmark-only

# Integration tests only
uv run pytest tests/benchmark_test_integration.py --benchmark-only
```

### Benchmark options
```bash
# Sort by mean time (default)
uv run pytest tests/benchmark_test_*.py --benchmark-only --benchmark-sort=mean

# Sort by minimum time
uv run pytest tests/benchmark_test_*.py --benchmark-only --benchmark-sort=min

# Sort by maximum time
uv run pytest tests/benchmark_test_*.py --benchmark-only --benchmark-sort=max

# Show more statistics
uv run pytest tests/benchmark_test_*.py --benchmark-only --benchmark-stddev
```

## Benchmark Categories

### 1. Operator Benchmarks (`benchmark_test_operators.py`)

Tests the performance of individual operator functions:

- **Basic operators**: `is_none`, `is_not_none`, `is_empty`, `is_true`, `is_false`
- **String operators**: `matches_regex`, `starts_with`, `case_fold_equal_to`
- **Comparison operators**: `less_than`, `greater_than`, `equal_to`, `not_equal_to`
- **Collection operators**: `contains`, `does_not_contain`, `contains_all`, `contains_any`, `one_of`
- **Date operators**: `date_between`
- **Operator registration and lookup**: Registration of custom operators and operator retrieval

### 2. Condition Benchmarks (`benchmark_test_conditions.py`)

Tests condition evaluation and validation performance:

- **Simple conditions**: Boolean and string-based conditions
- **Fact-based conditions**: Conditions that call fact methods
- **Complex nested conditions**: Conditions with `all`, `any`, and `not` operators
- **Large condition lists**: Performance with many conditions
- **String conditions**: Regex matching and string operations
- **Date conditions**: Date range checking
- **Collection conditions**: List and set operations
- **Validation**: Condition validation performance

### 3. Action Benchmarks (`benchmark_test_actions.py`)

Tests action execution and validation performance:

- **Simple actions**: Basic action execution
- **Complex actions**: Actions with parameters and arguments
- **Large action lists**: Performance with many actions
- **Action validation**: Validation of action definitions
- **Parameter types**: Different parameter types (strings, numbers, lists, dicts)
- **Nested workflows**: Complex action sequences
- **Error handling**: Performance with error conditions
- **Large data processing**: Actions that process large datasets

### 4. Rule Benchmarks (`benchmark_test_rules.py`)

Tests complete rule execution performance:

- **Simple rules**: Basic rule execution
- **Complex rules**: Rules with nested conditions and multiple actions
- **Rule validation**: Validation of rule definitions
- **Condition variations**: Rules with no conditions, false conditions
- **Multiple rules**: Execution of multiple rules
- **Date-based rules**: Rules using date conditions
- **String-based rules**: Rules using string operations
- **Large data rules**: Rules processing large datasets

### 5. Integration Benchmarks (`benchmark_test_integration.py`)

Tests complete workflows and real-world scenarios:

- **E-commerce workflow**: Order processing with discounts, shipping, and fraud detection
- **User authentication**: User verification, premium features, security alerts
- **Financial risk assessment**: Loan approval workflows with credit scoring
- **Custom operators**: Integration with user-defined operators
- **Large-scale processing**: IoT sensor data monitoring with multiple rules

## Performance Expectations

### Operator Performance
- Basic operators (is_none, equal_to, etc.): < 1 μs per operation
- String operators (regex, contains): < 10 μs per operation
- Collection operators: < 5 μs per operation
- Date operators: < 20 μs per operation

### Condition Performance
- Simple conditions: < 5 μs per evaluation
- Fact-based conditions: < 10 μs per evaluation
- Complex nested conditions: < 50 μs per evaluation
- Large condition lists (100 conditions): < 500 μs per evaluation

### Action Performance
- Simple actions: < 5 μs per action
- Actions with parameters: < 10 μs per action
- Large action lists (1000 actions): < 5 ms per list

### Rule Performance
- Simple rules: < 20 μs per rule
- Complex rules: < 100 μs per rule
- Multiple rules (10 rules): < 1 ms per rule set

### Integration Performance
- E-commerce workflow: < 1 ms per order
- Authentication workflow: < 500 μs per user
- Risk assessment: < 2 ms per application
- Large-scale processing (1000 data points, 5 rules): < 100 ms total

## Interpreting Results

### Good Performance Indicators
- Consistent timing across runs (low standard deviation)
- Linear scaling with data size
- No memory leaks or excessive memory usage
- Fastest operations under 1 μs

### Performance Issues to Watch For
- Operations taking > 100 μs for simple tasks
- Non-linear scaling with data size
- High standard deviation indicating inconsistent performance
- Memory usage growing with each iteration

### Optimization Opportunities
- Cache frequently used operators or conditions
- Optimize regex patterns for common use cases
- Use more efficient data structures for collections
- Batch process multiple rules when possible

## Adding New Benchmarks

When adding new benchmarks:

1. **Follow the naming convention**: `test_*_benchmark`
2. **Use realistic data**: Test with data sizes and types that match real usage
3. **Test edge cases**: Include boundary conditions and error cases
4. **Document the purpose**: Add clear docstrings explaining what is being tested
5. **Use appropriate fixtures**: Reuse common test data and objects
6. **Measure meaningful operations**: Focus on operations that users will actually perform

### Example Benchmark Structure
```python
def test_new_feature_benchmark(self, benchmark):
    """Benchmark the new feature performance."""
    # Setup test data
    test_data = create_realistic_test_data()
    
    def run_feature():
        # Perform the operation being benchmarked
        result = perform_operation(test_data)
        return result
    
    benchmark(run_feature)
```

## Continuous Monitoring

Consider setting up continuous monitoring of benchmark results:

1. **Baseline tracking**: Store baseline performance metrics
2. **Regression detection**: Alert when performance degrades significantly
3. **Trend analysis**: Track performance improvements over time
4. **Environment consistency**: Ensure benchmarks run in consistent environments

## Troubleshooting

### Common Issues

1. **Inconsistent results**: Ensure test data is deterministic
2. **Memory issues**: Check for memory leaks in long-running benchmarks
3. **Slow benchmarks**: Consider reducing data size or simplifying operations
4. **Import errors**: Ensure all dependencies are installed

### Performance Tips

1. **Warm up**: Run a few iterations before benchmarking
2. **Isolate operations**: Test one operation at a time
3. **Use realistic data**: Test with data that matches production usage
4. **Profile first**: Use profiling tools to identify bottlenecks
5. **Measure what matters**: Focus on operations that impact user experience 