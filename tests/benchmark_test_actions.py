from roolz._actions import execute_actions, validate_actions


class TestActionBenchmarks:
    """Benchmark tests for action execution and validation."""

    def test_simple_action_execution_benchmark(self, benchmark):
        """Benchmark simple action execution."""
        class TestActor:
            def __init__(self):
                self.counter = 0
                self.name = "test"
            
            def increment(self):
                self.counter += 1
            
            def set_name(self, name):
                self.name = name
            
            def add_numbers(self, a, b):
                return a + b
        
        actor = TestActor()
        
        actions = [
            {"action": "increment"},
            {"action": "set_name", "args": ["new_name"]},
            {"action": "add_numbers", "args": [5, 3]},
        ]
        
        def run_simple_actions():
            execute_actions(actor, actions)
        
        benchmark(run_simple_actions)

    def test_complex_action_execution_benchmark(self, benchmark):
        """Benchmark complex action execution with parameters."""
        class TestActor:
            def __init__(self):
                self.data = {}
                self.log = []
            
            def set_data(self, key, value):
                self.data[key] = value
            
            def log_message(self, message, level="info"):
                self.log.append(f"[{level}] {message}")
            
            def process_list(self, items, prefix=""):
                return [f"{prefix}{item}" for item in items]
        
        actor = TestActor()
        
        actions = [
            {"action": "set_data", "args": ["user_id", 12345]},
            {"action": "set_data", "args": ["status", "active"]},
            {"action": "log_message", "args": ["User processed", "info"]},
            {"action": "process_list", "args": [["a", "b", "c"], "item_"]},
        ]
        
        def run_complex_actions():
            execute_actions(actor, actions)
        
        benchmark(run_complex_actions)

    def test_large_action_list_benchmark(self, benchmark):
        """Benchmark execution of large action lists."""
        class TestActor:
            def __init__(self):
                self.counter = 0
            
            def increment(self):
                self.counter += 1
            
            def double_increment(self):
                self.counter += 2
        
        actor = TestActor()
        
        # Create a large list of simple actions
        large_action_list = [
            {"action": "increment"} if i % 2 == 0 else {"action": "double_increment"}
            for i in range(1000)
        ]
        
        def run_large_action_list():
            execute_actions(actor, large_action_list)
        
        benchmark(run_large_action_list)

    def test_action_validation_benchmark(self, benchmark):
        """Benchmark action validation."""
        class TestActor:
            def valid_action(self):
                pass
            
            def action_with_args(self, arg1, arg2):
                pass
        
        actor = TestActor()
        
        valid_actions = [
            [{"action": "valid_action"}],
            [{"action": "action_with_args", "args": [1, 2]}],
            [{"action": "action_with_args", "params": {"arg1": 1, "arg2": 2}}],
            [{"action": "valid_action"}, {"action": "action_with_args", "args": [1, 2]}],
        ]
        
        def run_validation():
            for actions in valid_actions:
                validate_actions(actions, actor)
        
        benchmark(run_validation)

    def test_action_with_different_parameter_types_benchmark(self, benchmark):
        """Benchmark actions with different parameter types."""
        class TestActor:
            def process_string(self, text):
                return text.upper()
            
            def process_number(self, num):
                return num * 2
            
            def process_list(self, items):
                return len(items)
            
            def process_dict(self, data):
                return list(data.keys())
        
        actor = TestActor()
        
        actions = [
            {"action": "process_string", "args": ["hello world"]},
            {"action": "process_number", "args": [42]},
            {"action": "process_list", "args": [[1, 2, 3, 4, 5]]},
            {"action": "process_dict", "args": [{"a": 1, "b": 2, "c": 3}]},
        ]
        
        def run_parameter_actions():
            execute_actions(actor, actions)
        
        benchmark(run_parameter_actions)

    def test_nested_action_execution_benchmark(self, benchmark):
        """Benchmark nested action execution patterns."""
        class TestActor:
            def __init__(self):
                self.state = {}
                self.history = []
            
            def initialize(self):
                self.state["initialized"] = True
                self.history.append("init")
            
            def configure(self, config):
                self.state.update(config)
                self.history.append("config")
            
            def validate(self):
                if not self.state.get("initialized"):
                    raise ValueError("Not initialized")
                self.history.append("validate")
            
            def execute(self):
                self.history.append("execute")
                return "success"
        
        actor = TestActor()
        
        # Simulate a typical workflow
        workflow_actions = [
            {"action": "initialize"},
            {"action": "configure", "args": [{"mode": "test", "debug": True}]},
            {"action": "validate"},
            {"action": "execute"},
        ]
        
        def run_workflow():
            execute_actions(actor, workflow_actions)
        
        benchmark(run_workflow)

    def test_action_error_handling_benchmark(self, benchmark):
        """Benchmark action execution with error handling."""
        class TestActor:
            def safe_action(self):
                return "ok"
            
            def risky_action(self):
                # Simulate a potentially failing action
                if hasattr(self, '_counter'):
                    self._counter += 1
                else:
                    self._counter = 1
                
                if self._counter % 10 == 0:
                    raise ValueError("Simulated error")
                return "ok"
        
        actor = TestActor()
        
        actions = [
            {"action": "safe_action"},
            {"action": "risky_action"},
            {"action": "safe_action"},
        ]
        
        def run_with_error_handling():
            try:
                execute_actions(actor, actions)
            except Exception:
                pass  # Expected in some cases
        
        benchmark(run_with_error_handling)

    def test_action_performance_with_large_data_benchmark(self, benchmark):
        """Benchmark actions that process large amounts of data."""
        class TestActor:
            def process_large_list(self, items):
                return sum(items)
            
            def filter_data(self, data, threshold):
                return [item for item in data if item > threshold]
            
            def transform_data(self, data, multiplier):
                return [item * multiplier for item in data]
        
        actor = TestActor()
        
        large_data = list(range(10000))
        
        actions = [
            {"action": "process_large_list", "args": [large_data]},
            {"action": "filter_data", "args": [large_data, 5000]},
            {"action": "transform_data", "args": [large_data[:1000], 2]},
        ]
        
        def run_large_data_actions():
            execute_actions(actor, actions)
        
        benchmark(run_large_data_actions) 