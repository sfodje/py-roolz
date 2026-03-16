from datetime import datetime, timezone
from roolz import execute_rules, validate_rules, get_operator, register_operator


class TestIntegrationBenchmarks:
    """Integration benchmark tests for the complete rule engine workflow."""

    def test_ecommerce_workflow_benchmark(self, benchmark):
        """Benchmark a complete e-commerce order processing workflow."""
        class Order:
            def __init__(self, order_id, customer_id, total_amount, items, shipping_address):
                self.order_id = order_id
                self.customer_id = customer_id
                self.total_amount = total_amount
                self.items = items
                self.shipping_address = shipping_address
                self.status = "pending"
                self.discount_applied = 0
                self.shipping_cost = 0
                self.fraud_score = 0
            
            def get_total_amount(self):
                return self.total_amount
            
            def get_item_count(self):
                return len(self.items)
            
            def get_customer_id(self):
                return self.customer_id
            
            def get_shipping_state(self):
                return self.shipping_address.get("state", "")
            
            def has_high_value_items(self):
                return any(item.get("price", 0) > 100 for item in self.items)
        
        class OrderProcessor:
            def __init__(self):
                self.processed_orders = []
                self.fraudulent_orders = []
                self.discounts_given = 0
                self.shipping_upgrades = 0
            
            def apply_discount(self, percentage):
                self.discounts_given += 1
            
            def upgrade_shipping(self):
                self.shipping_upgrades += 1
            
            def flag_for_review(self, reason):
                self.fraudulent_orders.append(reason)
            
            def approve_order(self):
                self.processed_orders.append("approved")
            
            def calculate_shipping(self, state):
                if state in ["CA", "NY", "TX"]:
                    return 5.99
                return 9.99
        
        # Create test orders
        orders = [
            Order("ORD001", "CUST001", 150.00, [{"name": "Laptop", "price": 1200}], {"state": "CA"}),
            Order("ORD002", "CUST002", 45.00, [{"name": "Book", "price": 25}, {"name": "Pen", "price": 20}], {"state": "NY"}),
            Order("ORD003", "CUST003", 2000.00, [{"name": "TV", "price": 2000}], {"state": "TX"}),
        ]
        
        processor = OrderProcessor()
        
        # Define business rules
        rules = [
            {
                "condition": {
                    "all": [
                        {"fact": "get_total_amount", "operator": "greater_than", "value": 100},
                        {"fact": "get_item_count", "operator": "greater_than", "value": 1}
                    ]
                },
                "actions": [
                    {"action": "apply_discount", "args": [10]}
                ]
            },
            {
                "condition": {
                    "all": [
                        {"fact": "has_high_value_items", "operator": "is_true"},
                        {"fact": "get_shipping_state", "operator": "one_of", "value": ["CA", "NY", "TX"]}
                    ]
                },
                "actions": [
                    {"action": "upgrade_shipping"},
                    {"action": "flag_for_review", "args": ["High value item"]}
                ]
            },
            {
                "condition": {"fact": "get_total_amount", "operator": "greater_than", "value": 1000},
                "actions": [
                    {"action": "flag_for_review", "args": ["Large order"]}
                ]
            }
        ]
        
        def run_ecommerce_workflow():
            for order in orders:
                for rule in rules:
                    execute_rules(rule, order, processor)
        
        benchmark(run_ecommerce_workflow)

    def test_user_authentication_workflow_benchmark(self, benchmark):
        """Benchmark a user authentication and authorization workflow."""
        class User:
            def __init__(self, user_id, email, age, login_count, last_login, subscription_type):
                self.user_id = user_id
                self.email = email
                self.age = age
                self.login_count = login_count
                self.last_login = last_login
                self.subscription_type = subscription_type
                self.verified = False
                self.blocked = False
                self.premium_features = False
        
        class AuthSystem:
            def __init__(self):
                self.verification_sent = False
                self.welcome_sent = False
                self.security_alert = False
                self.premium_activated = False
            
            def send_verification_email(self):
                self.verification_sent = True
            
            def send_welcome_email(self):
                self.welcome_sent = True
            
            def send_security_alert(self, reason):
                self.security_alert = True
            
            def activate_premium_features(self):
                self.premium_features = True
        
        # Create test users
        users = [
            User("U001", "new@example.com", 25, 1, None, "free"),
            User("U002", "existing@example.com", 30, 50, datetime(2024, 1, 1, tzinfo=timezone.utc), "premium"),
            User("U003", "suspicious@example.com", 18, 100, datetime(2024, 1, 15, tzinfo=timezone.utc), "free"),
        ]
        
        auth_system = AuthSystem()
        
        # Define authentication rules
        rules = [
            {
                "condition": {
                    "all": [
                        {"fact": "login_count", "operator": "equal_to", "value": 1},
                        {"fact": "verified", "operator": "is_false"}
                    ]
                },
                "actions": [
                    {"action": "send_verification_email"},
                    {"action": "send_welcome_email"}
                ]
            },
            {
                "condition": {
                    "all": [
                        {"fact": "subscription_type", "operator": "equal_to", "value": "premium"},
                        {"fact": "age", "operator": "greater_than", "value": 18}
                    ]
                },
                "actions": [
                    {"action": "activate_premium_features"}
                ]
            },
            {
                "condition": {
                    "all": [
                        {"fact": "login_count", "operator": "greater_than", "value": 50},
                        {"fact": "subscription_type", "operator": "equal_to", "value": "free"}
                    ]
                },
                "actions": [
                    {"action": "send_security_alert", "args": ["High login count for free user"]}
                ]
            }
        ]
        
        def run_auth_workflow():
            for user in users:
                for rule in rules:
                    execute_rules(rule, user, auth_system)
        
        benchmark(run_auth_workflow)

    def test_financial_risk_assessment_benchmark(self, benchmark):
        """Benchmark a financial risk assessment workflow."""
        class LoanApplication:
            def __init__(self, applicant_id, credit_score, income, debt_ratio, employment_years, loan_amount):
                self.applicant_id = applicant_id
                self.credit_score = credit_score
                self.income = income
                self.debt_ratio = debt_ratio
                self.employment_years = employment_years
                self.loan_amount = loan_amount
                self.approved = False
                self.interest_rate = 0
                self.risk_level = "unknown"
            
            def get_credit_score(self):
                return self.credit_score
            
            def get_income(self):
                return self.income
            
            def get_debt_ratio(self):
                return self.debt_ratio
            
            def get_employment_years(self):
                return self.employment_years
            
            def get_loan_amount(self):
                return self.loan_amount
        
        class RiskAssessor:
            def __init__(self):
                self.approved_applications = []
                self.rejected_applications = []
                self.high_risk_applications = []
                self.manual_review_needed = []
            
            def approve_loan(self, interest_rate):
                self.approved_applications.append(interest_rate)
            
            def reject_loan(self, reason):
                self.rejected_applications.append(reason)
            
            def flag_high_risk(self, risk_factors):
                self.high_risk_applications.append(risk_factors)
            
            def require_manual_review(self, reason):
                self.manual_review_needed.append(reason)
        
        # Create test applications
        applications = [
            LoanApplication("APP001", 750, 80000, 0.3, 5, 200000),
            LoanApplication("APP002", 650, 50000, 0.5, 2, 150000),
            LoanApplication("APP003", 820, 120000, 0.2, 8, 300000),
        ]
        
        assessor = RiskAssessor()
        
        # Define risk assessment rules
        rules = [
            {
                "condition": {
                    "all": [
                        {"fact": "get_credit_score", "operator": "greater_than", "value": 700},
                        {"fact": "get_debt_ratio", "operator": "less_than", "value": 0.4},
                        {"fact": "get_employment_years", "operator": "greater_than", "value": 2}
                    ]
                },
                "actions": [
                    {"action": "approve_loan", "args": [3.5]}
                ]
            },
            {
                "condition": {
                    "all": [
                        {"fact": "get_credit_score", "operator": "less_than", "value": 600},
                        {"fact": "get_debt_ratio", "operator": "greater_than", "value": 0.5}
                    ]
                },
                "actions": [
                    {"action": "reject_loan", "args": ["Poor credit and high debt"]}
                ]
            },
            {
                "condition": {
                    "all": [
                        {"fact": "get_loan_amount", "operator": "greater_than", "value": 250000},
                        {"fact": "get_income", "operator": "less_than", "value": 100000}
                    ]
                },
                "actions": [
                    {"action": "require_manual_review", "args": ["Large loan relative to income"]}
                ]
            }
        ]
        
        def run_risk_assessment():
            for application in applications:
                for rule in rules:
                    execute_rules(rule, application, assessor)
        
        benchmark(run_risk_assessment)

    def test_custom_operator_integration_benchmark(self, benchmark):
        """Benchmark integration with custom operators."""
        class DataPoint:
            def __init__(self, value, timestamp, category):
                self.value = value
                self.timestamp = timestamp
                self.category = category
            
            def get_value(self):
                return self.value
            
            def get_timestamp(self):
                return self.timestamp
            
            def get_category(self):
                return self.category
        
        class DataProcessor:
            def __init__(self):
                self.processed_count = 0
                self.alerts_sent = 0
            
            def process_data(self):
                self.processed_count += 1
            
            def send_alert(self, message):
                self.alerts_sent += 1
        
        # Register custom operators
        def is_anomaly(left_operand, right_operand):
            """Custom operator to detect anomalies."""
            if isinstance(left_operand, (int, float)) and isinstance(right_operand, (int, float)):
                return abs(left_operand - right_operand) > (right_operand * 0.2)
            return False
        
        def is_recent(left_operand, right_operand):
            """Custom operator to check if timestamp is recent."""
            if isinstance(left_operand, datetime) and isinstance(right_operand, int):
                now = datetime.now(timezone.utc)
                return (now - left_operand).days <= right_operand
            return False
        
        try:
            register_operator("is_anomaly", is_anomaly)
            register_operator("is_recent", is_recent)
        except ValueError:
            pass  # Operators already registered
        
        # Create test data points
        data_points = [
            DataPoint(100, datetime(2024, 1, 1, tzinfo=timezone.utc), "sales"),
            DataPoint(150, datetime(2024, 1, 15, tzinfo=timezone.utc), "sales"),
            DataPoint(50, datetime(2024, 1, 30, tzinfo=timezone.utc), "sales"),
        ]
        
        processor = DataProcessor()
        
        # Define rules with custom operators
        rules = [
            {
                "condition": {
                    "fact": "get_value",
                    "operator": "is_anomaly",
                    "value": 120
                },
                "actions": [
                    {"action": "send_alert", "args": ["Anomaly detected"]}
                ]
            },
            {
                "condition": {
                    "all": [
                        {"fact": "get_timestamp", "operator": "is_recent", "value": 30},
                        {"fact": "get_category", "operator": "equal_to", "value": "sales"}
                    ]
                },
                "actions": [
                    {"action": "process_data"}
                ]
            }
        ]
        
        def run_custom_operator_integration():
            for data_point in data_points:
                for rule in rules:
                    execute_rules(rule, data_point, processor)
        
        benchmark(run_custom_operator_integration)

    def test_large_scale_rule_processing_benchmark(self, benchmark):
        """Benchmark large-scale rule processing with many rules and data points."""
        class SensorData:
            def __init__(self, sensor_id, temperature, humidity, pressure, timestamp):
                self.sensor_id = sensor_id
                self.temperature = temperature
                self.humidity = humidity
                self.pressure = pressure
                self.timestamp = timestamp
            
            def get_temperature(self):
                return self.temperature
            
            def get_humidity(self):
                return self.humidity
            
            def get_pressure(self):
                return self.pressure
            
            def get_timestamp(self):
                return self.timestamp
        
        class MonitoringSystem:
            def __init__(self):
                self.alerts = []
                self.processed_readings = 0
                self.critical_events = 0
            
            def log_alert(self, sensor_id, message):
                self.alerts.append(f"{sensor_id}: {message}")
            
            def process_reading(self):
                self.processed_readings += 1
            
            def log_critical_event(self, event):
                self.critical_events += 1
        
        # Create large dataset
        sensor_data = [
            SensorData(f"SENSOR_{i}", 20 + (i % 10), 50 + (i % 20), 1013 + (i % 10), 
                      datetime(2024, 1, 1, i % 24, i % 60, tzinfo=timezone.utc))
            for i in range(1000)
        ]
        
        monitoring_system = MonitoringSystem()
        
        # Create comprehensive rule set
        rules = [
            # Temperature rules
            {
                "condition": {"fact": "get_temperature", "operator": "greater_than", "value": 30},
                "actions": [{"action": "log_alert", "args": ["TEMP_HIGH", "High temperature detected"]}]
            },
            {
                "condition": {"fact": "get_temperature", "operator": "less_than", "value": 10},
                "actions": [{"action": "log_alert", "args": ["TEMP_LOW", "Low temperature detected"]}]
            },
            # Humidity rules
            {
                "condition": {"fact": "get_humidity", "operator": "greater_than", "value": 80},
                "actions": [{"action": "log_alert", "args": ["HUMIDITY_HIGH", "High humidity detected"]}]
            },
            # Pressure rules
            {
                "condition": {"fact": "get_pressure", "operator": "less_than", "value": 1000},
                "actions": [{"action": "log_critical_event", "args": ["Low pressure system"]}]
            },
            # Combined conditions
            {
                "condition": {
                    "all": [
                        {"fact": "get_temperature", "operator": "greater_than", "value": 25},
                        {"fact": "get_humidity", "operator": "greater_than", "value": 70}
                    ]
                },
                "actions": [{"action": "log_alert", "args": ["COMFORT_ISSUE", "Uncomfortable conditions"]}]
            }
        ]
        
        def run_large_scale_processing():
            for data_point in sensor_data:
                for rule in rules:
                    execute_rules(rule, data_point, monitoring_system)
        
        benchmark(run_large_scale_processing) 