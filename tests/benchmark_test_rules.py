from datetime import datetime, timezone
from roolz._rules import execute_rules, validate_rules


class TestRuleBenchmarks:
    """Benchmark tests for rule execution and validation."""

    def test_simple_rule_execution_benchmark(self, benchmark):
        """Benchmark simple rule execution."""
        class TestFact:
            def get_value(self):
                return 42
            
            def get_status(self):
                return "active"
        
        class TestActor:
            def __init__(self):
                self.log = []
            
            def log_action(self, message):
                self.log.append(message)
            
            def update_status(self, status):
                self.status = status
        
        fact = TestFact()
        actor = TestActor()
        
        simple_rule = {
            "condition": {"fact": "get_value", "operator": "greater_than", "value": 40},
            "actions": [
                {"action": "log_action", "args": ["Value is greater than 40"]},
                {"action": "update_status", "args": ["processed"]},
            ]
        }
        
        def run_simple_rule():
            execute_rules(simple_rule, fact, actor)
        
        benchmark(run_simple_rule)

    def test_complex_rule_execution_benchmark(self, benchmark):
        """Benchmark complex rule execution with nested conditions."""
        class TestFact:
            def get_age(self):
                return 25
            
            def get_income(self):
                return 75000
            
            def get_credit_score(self):
                return 720
            
            def get_employment_status(self):
                return "employed"
        
        class TestActor:
            def __init__(self):
                self.approved = False
                self.reason = ""
                self.risk_level = "unknown"
            
            def approve_loan(self):
                self.approved = True
                self.reason = "Approved"
            
            def set_risk_level(self, level):
                self.risk_level = level
            
            def log_decision(self, decision):
                self.reason = decision
        
        fact = TestFact()
        actor = TestActor()
        
        complex_rule = {
            "condition": {
                "all": [
                    {"fact": "get_age", "operator": "greater_than", "value": 18},
                    {"fact": "get_age", "operator": "less_than", "value": 65},
                    {"fact": "get_income", "operator": "greater_than", "value": 50000},
                    {
                        "any": [
                            {"fact": "get_credit_score", "operator": "greater_than", "value": 700},
                            {"fact": "get_employment_status", "operator": "equal_to", "value": "employed"},
                        ]
                    }
                ]
            },
            "actions": [
                {"action": "approve_loan"},
                {"action": "set_risk_level", "args": ["low"]},
                {"action": "log_decision", "args": ["Approved based on criteria"]},
            ]
        }
        
        def run_complex_rule():
            execute_rules(complex_rule, fact, actor)
        
        benchmark(run_complex_rule)

    def test_rule_validation_benchmark(self, benchmark):
        """Benchmark rule validation."""
        class TestFact:
            def get_value(self):
                return 42
        
        class TestActor:
            def valid_action(self):
                pass
        
        fact = TestFact()
        actor = TestActor()
        
        valid_rules = [
            {
                "condition": {"fact": "get_value", "operator": "equal_to", "value": 42},
                "actions": [{"action": "valid_action"}],
            },
            {
                "condition": {
                    "all": [
                        {"fact": "get_value", "operator": "greater_than", "value": 40},
                        {"fact": "get_value", "operator": "less_than", "value": 50},
                    ]
                },
                "actions": [{"action": "valid_action"}],
            },
            {
                "condition": True,
                "actions": [{"action": "valid_action"}],
            },
        ]
        
        def run_validation():
            for rule in valid_rules:
                validate_rules(rule, fact, actor)
        
        benchmark(run_validation)

    def test_rule_with_no_condition_benchmark(self, benchmark):
        """Benchmark rule execution when no condition is specified."""
        class TestActor:
            def __init__(self):
                self.executed = False
            
            def execute_action(self):
                self.executed = True
        
        actor = TestActor()
        
        rule_without_condition = {
            "actions": [{"action": "execute_action"}]
        }
        
        def run_rule_without_condition():
            execute_rules(rule_without_condition, {}, actor)
        
        benchmark(run_rule_without_condition)

    def test_rule_with_false_condition_benchmark(self, benchmark):
        """Benchmark rule execution when condition is false."""
        class TestFact:
            def get_value(self):
                return 10
        
        class TestActor:
            def __init__(self):
                self.executed = False
            
            def execute_action(self):
                self.executed = True
        
        fact = TestFact()
        actor = TestActor()
        
        rule_with_false_condition = {
            "condition": {"fact": "get_value", "operator": "greater_than", "value": 50},
            "actions": [{"action": "execute_action"}]
        }
        
        def run_rule_with_false_condition():
            execute_rules(rule_with_false_condition, fact, actor)
        
        benchmark(run_rule_with_false_condition)

    def test_multiple_rules_execution_benchmark(self, benchmark):
        """Benchmark execution of multiple rules."""
        class TestFact:
            def get_score(self):
                return 85
            
            def get_level(self):
                return "intermediate"
        
        class TestActor:
            def __init__(self):
                self.rewards = []
                self.level_up = False
            
            def add_reward(self, reward):
                self.rewards.append(reward)
            
            def promote_level(self):
                self.level_up = True
        
        fact = TestFact()
        actor = TestActor()
        
        rules = [
            {
                "condition": {"fact": "get_score", "operator": "greater_than", "value": 80},
                "actions": [{"action": "add_reward", "args": ["high_score_bonus"]}],
            },
            {
                "condition": {"fact": "get_level", "operator": "equal_to", "value": "intermediate"},
                "actions": [{"action": "promote_level"}],
            },
        ]
        
        def run_multiple_rules():
            for rule in rules:
                execute_rules(rule, fact, actor)
        
        benchmark(run_multiple_rules)

    def test_rule_with_date_conditions_benchmark(self, benchmark):
        """Benchmark rule execution with date-based conditions."""
        class TestFact:
            def get_registration_date(self):
                return datetime(2023, 6, 15, 10, 30, 0, tzinfo=timezone.utc)
            
            def get_last_login(self):
                return datetime(2024, 1, 10, 15, 45, 0, tzinfo=timezone.utc)
        
        class TestActor:
            def __init__(self):
                self.welcome_sent = False
                self.reminder_sent = False
            
            def send_welcome(self):
                self.welcome_sent = True
            
            def send_reminder(self):
                self.reminder_sent = True
        
        fact = TestFact()
        actor = TestActor()
        
        date_rule = {
            "condition": {
                "all": [
                    {
                        "fact": "get_registration_date",
                        "operator": "date_between",
                        "value": [
                            datetime(2023, 1, 1, tzinfo=timezone.utc),
                            datetime(2023, 12, 31, tzinfo=timezone.utc)
                        ]
                    },
                    {
                        "fact": "get_last_login",
                        "operator": "date_between",
                        "value": [
                            "2024-01-01T00:00:00+00:00",
                            "2024-12-31T23:59:59+00:00"
                        ]
                    }
                ]
            },
            "actions": [
                {"action": "send_welcome"},
                {"action": "send_reminder"},
            ]
        }
        
        def run_date_rule():
            execute_rules(date_rule, fact, actor)
        
        benchmark(run_date_rule)

    def test_rule_with_string_conditions_benchmark(self, benchmark):
        """Benchmark rule execution with string-based conditions."""
        class TestFact:
            def get_email(self):
                return "user@example.com"
            
            def get_domain(self):
                return "example.com"
            
            def get_username(self):
                return "john_doe"
        
        class TestActor:
            def __init__(self):
                self.verified = False
                self.premium = False
            
            def verify_email(self):
                self.verified = True
            
            def upgrade_to_premium(self):
                self.premium = True
        
        fact = TestFact()
        actor = TestActor()
        
        string_rule = {
            "condition": {
                "all": [
                    {
                        "fact": "get_email",
                        "operator": "matches_regex",
                        "value": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                    },
                    {
                        "fact": "get_domain",
                        "operator": "equal_to",
                        "value": "example.com"
                    },
                    {
                        "fact": "get_username",
                        "operator": "starts_with",
                        "value": "john"
                    }
                ]
            },
            "actions": [
                {"action": "verify_email"},
                {"action": "upgrade_to_premium"},
            ]
        }
        
        def run_string_rule():
            execute_rules(string_rule, fact, actor)
        
        benchmark(run_string_rule)

    def test_rule_performance_with_large_data_benchmark(self, benchmark):
        """Benchmark rule execution with large data processing."""
        class TestFact:
            def get_large_list(self):
                return list(range(10000))
            
            def get_filtered_data(self):
                return [i for i in range(1000) if i % 2 == 0]
        
        class TestActor:
            def __init__(self):
                self.processed_count = 0
            
            def process_data(self, data):
                self.processed_count = len(data)
            
            def analyze_data(self, data):
                return sum(data) / len(data) if data else 0
        
        fact = TestFact()
        actor = TestActor()
        
        large_data_rule = {
            "condition": {
                "all": [
                    {
                        "fact": "get_large_list",
                        "operator": "contains",
                        "value": 5000
                    },
                    {
                        "fact": "get_filtered_data",
                        "operator": "contains_all",
                        "value": [0, 2, 4, 6, 8]
                    }
                ]
            },
            "actions": [
                {"action": "process_data", "args": [list(range(1000))]},
                {"action": "analyze_data", "args": [list(range(100))]},
            ]
        }
        
        def run_large_data_rule():
            execute_rules(large_data_rule, fact, actor)
        
        benchmark(run_large_data_rule) 