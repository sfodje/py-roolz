from datetime import datetime, timezone
from roolz._conditions import evaluate_condition, validate_condition


class TestConditionBenchmarks:
    """Benchmark tests for condition evaluation and validation."""

    def test_simple_boolean_condition_benchmark(self, benchmark):
        """Benchmark simple boolean conditions."""
        def run_boolean_conditions():
            evaluate_condition({}, True)
            evaluate_condition({}, False)
            evaluate_condition({}, "true")
            evaluate_condition({}, "false")
        
        benchmark(run_boolean_conditions)

    def test_fact_condition_benchmark(self, benchmark):
        """Benchmark fact-based conditions."""
        class TestFact:
            def get_value(self):
                return 42
            
            def get_name(self):
                return "test"
            
            def get_list(self):
                return [1, 2, 3, 4, 5]
        
        fact = TestFact()
        
        conditions = [
            {"fact": "get_value", "operator": "equal_to", "value": 42},
            {"fact": "get_name", "operator": "equal_to", "value": "test"},
            {"fact": "get_list", "operator": "contains", "value": 3},
            {"fact": "get_value", "operator": "greater_than", "value": 40},
        ]
        
        def run_fact_conditions():
            for condition in conditions:
                evaluate_condition(fact, condition)
        
        benchmark(run_fact_conditions)

    def test_complex_nested_conditions_benchmark(self, benchmark):
        """Benchmark complex nested conditions."""
        class TestFact:
            def get_age(self):
                return 25
            
            def get_status(self):
                return "active"
            
            def get_scores(self):
                return [85, 90, 78, 92]
        
        fact = TestFact()
        
        complex_condition = {
            "all": [
                {"fact": "get_age", "operator": "greater_than", "value": 18},
                {"fact": "get_age", "operator": "less_than", "value": 65},
                {
                    "any": [
                        {"fact": "get_status", "operator": "equal_to", "value": "active"},
                        {"fact": "get_status", "operator": "equal_to", "value": "pending"},
                    ]
                },
                {
                    "not": {
                        "fact": "get_scores",
                        "operator": "contains",
                        "value": 0
                    }
                }
            ]
        }
        
        def run_complex_condition():
            evaluate_condition(fact, complex_condition)
        
        benchmark(run_complex_condition)

    def test_validation_benchmark(self, benchmark):
        """Benchmark condition validation."""
        class TestFact:
            def get_value(self):
                return 42
        
        fact_type = type(TestFact())
        
        valid_conditions = [
            True,
            False,
            "true",
            "false",
            {"fact": "get_value", "operator": "equal_to", "value": 42},
            {"all": [{"fact": "get_value", "operator": "greater_than", "value": 40}]},
            {"any": [{"fact": "get_value", "operator": "less_than", "value": 50}]},
            {"not": {"fact": "get_value", "operator": "equal_to", "value": 0}},
        ]
        
        def run_validation():
            for condition in valid_conditions:
                validate_condition(condition, fact_type)
        
        benchmark(run_validation)

    def test_large_condition_list_benchmark(self, benchmark):
        """Benchmark evaluation of large condition lists."""
        class TestFact:
            def get_value(self, index):
                return index
        
        fact = TestFact()
        
        # Create a large list of simple conditions
        large_condition_list = {
            "all": [
                {"fact": "get_value", "operator": "greater_than", "value": i, "args": [i]}
                for i in range(100)
            ]
        }
        
        def run_large_condition_list():
            evaluate_condition(fact, large_condition_list)
        
        benchmark(run_large_condition_list)

    def test_string_conditions_benchmark(self, benchmark):
        """Benchmark string-based conditions."""
        class TestFact:
            def get_text(self):
                return "Hello, World! This is a test string for benchmarking."
            
            def get_email(self):
                return "user@example.com"
        
        fact = TestFact()
        
        string_conditions = [
            {"fact": "get_text", "operator": "starts_with", "value": "Hello"},
            {"fact": "get_text", "operator": "ends_with", "value": "benchmarking."},
            {"fact": "get_text", "operator": "contains", "value": "test"},
            {"fact": "get_email", "operator": "matches_regex", "value": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"},
        ]
        
        def run_string_conditions():
            for condition in string_conditions:
                evaluate_condition(fact, condition)
        
        benchmark(run_string_conditions)

    def test_date_conditions_benchmark(self, benchmark):
        """Benchmark date-based conditions."""
        class TestFact:
            def get_date(self):
                return datetime(2023, 6, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        fact = TestFact()
        
        date_conditions = [
            {
                "fact": "get_date",
                "operator": "date_between",
                "value": [
                    datetime(2023, 1, 1, tzinfo=timezone.utc),
                    datetime(2023, 12, 31, tzinfo=timezone.utc)
                ]
            },
            {
                "fact": "get_date",
                "operator": "date_between",
                "value": [
                    "2023-01-01T00:00:00+00:00",
                    "2023-12-31T23:59:59+00:00"
                ]
            },
        ]
        
        def run_date_conditions():
            for condition in date_conditions:
                evaluate_condition(fact, condition)
        
        benchmark(run_date_conditions)

    def test_collection_conditions_benchmark(self, benchmark):
        """Benchmark collection-based conditions."""
        class TestFact:
            def get_numbers(self):
                return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            
            def get_names(self):
                return ["Alice", "Bob", "Charlie", "David", "Eve"]
        
        fact = TestFact()
        
        collection_conditions = [
            {"fact": "get_numbers", "operator": "contains", "value": 5},
            {"fact": "get_numbers", "operator": "contains_all", "value": [1, 3, 5]},
            {"fact": "get_numbers", "operator": "contains_any", "value": [15, 20, 5]},
            {"fact": "get_names", "operator": "one_of", "value": ["Alice", "Bob", "Charlie"]},
        ]
        
        def run_collection_conditions():
            for condition in collection_conditions:
                evaluate_condition(fact, condition)
        
        benchmark(run_collection_conditions) 