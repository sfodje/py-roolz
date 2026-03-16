import pytest
from datetime import datetime, timezone
from roolz._operators import _Operators, get_operator, register_operator


class TestOperatorBenchmarks:
    """Benchmark tests for operator functions."""

    def test_is_none_benchmark(self, benchmark):
        """Benchmark the is_none operator."""
        operator = get_operator("is_none")
        
        def run_is_none():
            operator(None, None)
            operator("test", None)
            operator(123, None)
            operator([], None)
        
        benchmark(run_is_none)

    def test_is_not_none_benchmark(self, benchmark):
        """Benchmark the is_not_none operator."""
        operator = get_operator("is_not_none")
        
        def run_is_not_none():
            operator(None, None)
            operator("test", None)
            operator(123, None)
            operator([], None)
        
        benchmark(run_is_not_none)

    def test_is_empty_benchmark(self, benchmark):
        """Benchmark the is_empty operator."""
        operator = get_operator("is_empty")
        
        def run_is_empty():
            operator("", None)
            operator("test", None)
            operator([], None)
            operator([1, 2, 3], None)
            operator(0, None)
            operator(1, None)
        
        benchmark(run_is_empty)

    def test_is_true_benchmark(self, benchmark):
        """Benchmark the is_true operator."""
        operator = get_operator("is_true")
        
        def run_is_true():
            operator(True, None)
            operator(False, None)
            operator("true", None)
            operator("false", None)
            operator(1, None)
            operator(0, None)
        
        benchmark(run_is_true)

    def test_matches_regex_benchmark(self, benchmark):
        """Benchmark the matches_regex operator."""
        operator = get_operator("matches_regex")
        
        def run_matches_regex():
            operator("test@example.com", r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
            operator("invalid-email", r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
            operator("12345", r"^\d{5}$")
            operator("1234", r"^\d{5}$")
        
        benchmark(run_matches_regex)

    def test_date_between_benchmark(self, benchmark):
        """Benchmark the date_between operator."""
        operator = get_operator("date_between")
        now = datetime.now(timezone.utc)
        start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 12, 31, tzinfo=timezone.utc)
        
        def run_date_between():
            operator(now, (start_date, end_date))
            operator("2023-06-15T10:30:00+00:00", ("2023-01-01", "2024-12-31"))
            operator("2025-01-01T00:00:00+00:00", ("2023-01-01", "2024-12-31"))
        
        benchmark(run_date_between)

    def test_one_of_benchmark(self, benchmark):
        """Benchmark the one_of operator."""
        operator = get_operator("one_of")
        
        def run_one_of():
            operator("apple", ["apple", "banana", "cherry"])
            operator("orange", ["apple", "banana", "cherry"])
            operator(5, [1, 2, 3, 4, 5])
            operator(10, [1, 2, 3, 4, 5])
        
        benchmark(run_one_of)

    def test_comparison_operators_benchmark(self, benchmark):
        """Benchmark comparison operators."""
        less_than = get_operator("less_than")
        greater_than = get_operator("greater_than")
        equal_to = get_operator("equal_to")
        
        def run_comparisons():
            less_than(5, 10)
            less_than(10, 5)
            greater_than(10, 5)
            greater_than(5, 10)
            equal_to(5, 5)
            equal_to(5, 10)
        
        benchmark(run_comparisons)

    def test_string_operators_benchmark(self, benchmark):
        """Benchmark string operators."""
        starts_with = get_operator("starts_with")
        ends_with = get_operator("ends_with")
        contains = get_operator("contains")
        
        def run_string_ops():
            starts_with("hello world", "hello")
            starts_with("hello world", "world")
            ends_with("hello world", "world")
            ends_with("hello world", "hello")
            contains("hello world", "lo wo")
            contains("hello world", "xyz")
        
        benchmark(run_string_ops)

    def test_collection_operators_benchmark(self, benchmark):
        """Benchmark collection operators."""
        contains = get_operator("contains")
        does_not_contain = get_operator("does_not_contain")
        contains_all = get_operator("contains_all")
        contains_any = get_operator("contains_any")
        
        test_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        def run_collection_ops():
            contains(test_list, 5)
            contains(test_list, 15)
            does_not_contain(test_list, 15)
            does_not_contain(test_list, 5)
            contains_all(test_list, [1, 3, 5])
            contains_all(test_list, [1, 15, 5])
            contains_any(test_list, [15, 20, 5])
            contains_any(test_list, [15, 20, 25])
        
        benchmark(run_collection_ops)

    def test_operator_registration_benchmark(self, benchmark):
        """Benchmark operator registration."""
        def test_operator(left, right):
            return left == right
        
        def run_registration():
            try:
                register_operator("test_op", test_operator)
            except ValueError:
                pass  # Operator already registered
        
        benchmark(run_registration)

    def test_operator_lookup_benchmark(self, benchmark):
        """Benchmark operator lookup."""
        def run_lookup():
            get_operator("is_none")
            get_operator("equal_to")
            get_operator("contains")
            get_operator("less_than")
        
        benchmark(run_lookup) 