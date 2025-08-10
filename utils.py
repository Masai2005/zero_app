"""
Utility functions for the application.
"""
import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSettings

# Constants
APP_NAME = "ZERO"
APP_VERSION = "1.0.0"
DEFAULT_SETTINGS_FILE = "settings.json"
DEFAULT_USERS_FILE = "users.json"
DEFAULT_CUSTOMERS_FILE = "customers.json"
DEFAULT_PRODUCTS_FILE = "products.json"
DEFAULT_SALES_FILE = "sales.json"
DEFAULT_EXPENSES_FILE = "expenses.json"
DEFAULT_NOTIFICATIONS_FILE = "notifications.json"
DEFAULT_MOVEMENTS_FILE = "movements.json"
DEFAULT_PAYMENTS_FILE = "payments.json"

# User types
USER_TYPE_ADMIN = "admin"
USER_TYPE_SALESMAN = "salesman"


class DataManager:
    """Class to manage data operations like save, load, etc."""
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data/app.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    @staticmethod
    def ensure_data_dir():
        """Ensure the data directory exists"""
        try:
            os.makedirs("data", exist_ok=True)
            return True
        except Exception as e:
            DataManager.logger.error(f"Failed to create data directory: {e}")
            return False
    
    @staticmethod
    def get_file_path(filename: str) -> str:
        """Get the full path to a data file"""
        DataManager.ensure_data_dir()
        return os.path.join("data", filename)

    @staticmethod
    def validate_json_structure(data: Any, filename: str) -> Tuple[bool, str]:
        """Validate JSON data structure based on file type"""
        try:
            if filename == DEFAULT_CUSTOMERS_FILE:
                if not isinstance(data, list):
                    return False, "Customers data must be a list"
                for item in data:
                    if not isinstance(item, dict) or 'id' not in item:
                        return False, "Each customer must be a dictionary with an 'id' field"
            
            elif filename == DEFAULT_PRODUCTS_FILE:
                if not isinstance(data, list):
                    return False, "Products data must be a list"
                for item in data:
                    if not isinstance(item, dict) or 'id' not in item:
                        return False, "Each product must be a dictionary with an 'id' field"
            
            elif filename == DEFAULT_SALES_FILE:
                if not isinstance(data, list):
                    return False, "Sales data must be a list"
                for item in data:
                    if not isinstance(item, dict) or 'id' not in item:
                        return False, "Each sale must be a dictionary with an 'id' field"
            
            elif filename == DEFAULT_EXPENSES_FILE:
                if not isinstance(data, list):
                    return False, "Expenses data must be a list"
                for item in data:
                    if not isinstance(item, dict) or 'id' not in item:
                        return False, "Each expense must be a dictionary with an 'id' field"
            
            elif filename == DEFAULT_MOVEMENTS_FILE:
                if not isinstance(data, list):
                    return False, "Movements data must be a list"
                for item in data:
                    if not isinstance(item, dict) or 'id' not in item:
                        return False, "Each movement must be a dictionary with an 'id' field"
            
            elif filename == DEFAULT_PAYMENTS_FILE:
                if not isinstance(data, list):
                    return False, "Payments data must be a list"
                for item in data:
                    if not isinstance(item, dict) or 'id' not in item:
                        return False, "Each payment must be a dictionary with an 'id' field"
            
            elif filename == DEFAULT_USERS_FILE:
                if not isinstance(data, dict):
                    return False, "Users data must be a dictionary"
            
            return True, ""
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def save_data(data: Any, filename: str) -> Tuple[bool, str]:
        """
        Save data to a JSON file with validation
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Validate data structure
            is_valid, error_msg = DataManager.validate_json_structure(data, filename)
            if not is_valid:
                DataManager.logger.error(f"Data validation failed for {filename}: {error_msg}")
                return False, f"Data validation failed: {error_msg}"
            
            # Save data
            file_path = DataManager.get_file_path(filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            DataManager.logger.info(f"Data saved successfully to {filename}")
            return True, ""
            
        except PermissionError as e:
            error_msg = f"Permission denied when saving {filename}: {e}"
            DataManager.logger.error(error_msg)
            return False, error_msg
        except json.JSONEncodeError as e:
            error_msg = f"JSON encoding error when saving {filename}: {e}"
            DataManager.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error saving {filename}: {e}"
            DataManager.logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def load_data(filename: str) -> Tuple[Any, str]:
        """
        Load data from a JSON file with error handling
        
        Returns:
            Tuple of (data, error_message). If error_message is empty, data is valid.
            If error occurs, returns appropriate default structure and error message.
        """
        try:
            file_path = DataManager.get_file_path(filename)
            
            if not os.path.exists(file_path):
                # Return appropriate default structure
                default_data = DataManager.get_default_data_structure(filename)
                DataManager.logger.info(f"File {filename} doesn't exist, returning default structure")
                return default_data, ""
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate loaded data
            is_valid, error_msg = DataManager.validate_json_structure(data, filename)
            if not is_valid:
                DataManager.logger.error(f"Loaded data validation failed for {filename}: {error_msg}")
                default_data = DataManager.get_default_data_structure(filename)
                return default_data, f"Data corrupted: {error_msg}"
            
            DataManager.logger.info(f"Data loaded successfully from {filename}")
            return data, ""
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON decode error in {filename}: {e}"
            DataManager.logger.error(error_msg)
            default_data = DataManager.get_default_data_structure(filename)
            return default_data, error_msg
        except PermissionError as e:
            error_msg = f"Permission denied when loading {filename}: {e}"
            DataManager.logger.error(error_msg)
            default_data = DataManager.get_default_data_structure(filename)
            return default_data, error_msg
        except Exception as e:
            error_msg = f"Unexpected error loading {filename}: {e}"
            DataManager.logger.error(error_msg)
            default_data = DataManager.get_default_data_structure(filename)
            return default_data, error_msg
    
    @staticmethod
    def get_default_data_structure(filename: str) -> Any:
        """Get default data structure for a given file"""
        if filename in [DEFAULT_CUSTOMERS_FILE, DEFAULT_PRODUCTS_FILE, 
                       DEFAULT_SALES_FILE, DEFAULT_EXPENSES_FILE, DEFAULT_NOTIFICATIONS_FILE, DEFAULT_MOVEMENTS_FILE, DEFAULT_PAYMENTS_FILE]:
            return []
        elif filename == DEFAULT_USERS_FILE:
            return {}
        elif filename == DEFAULT_SETTINGS_FILE:
            return {
                "theme": "light",
                "company_name": "ZERO",
                "last_backup": None
            }
        else:
            return {}

    @staticmethod
    def generate_id() -> str:
        """Generate a unique ID for records"""
        return f"id_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    @staticmethod
    def init_data_files():
        """Initialize all data files with default structure if they don't exist"""
        try:
            # Settings file
            if not os.path.exists(DataManager.get_file_path(DEFAULT_SETTINGS_FILE)):
                settings = {
                    "theme": "light",
                    "company_name": "ZERO",
                    "last_backup": None
                }
                success, error = DataManager.save_data(settings, DEFAULT_SETTINGS_FILE)
                if not success:
                    DataManager.logger.error(f"Failed to initialize settings file: {error}")
            
            # Users file
            if not os.path.exists(DataManager.get_file_path(DEFAULT_USERS_FILE)):
                # Create default admin user
                password = hashlib.sha256("admin".encode()).hexdigest()
                users = {
                    "admin": {
                        "password": password,
                        "type": USER_TYPE_ADMIN,
                        "name": "Administrator",
                        "created_at": datetime.now().isoformat()
                    }
                }
                success, error = DataManager.save_data(users, DEFAULT_USERS_FILE)
                if not success:
                    DataManager.logger.error(f"Failed to initialize users file: {error}")
            
            # Initialize other data files
            for filename in [DEFAULT_CUSTOMERS_FILE, DEFAULT_PRODUCTS_FILE, 
                           DEFAULT_SALES_FILE, DEFAULT_EXPENSES_FILE, DEFAULT_NOTIFICATIONS_FILE, DEFAULT_MOVEMENTS_FILE, DEFAULT_PAYMENTS_FILE]:
                if not os.path.exists(DataManager.get_file_path(filename)):
                    success, error = DataManager.save_data([], filename)
                    if not success:
                        DataManager.logger.error(f"Failed to initialize {filename}: {error}")
            
            DataManager.logger.info("Data files initialization completed")
            
        except Exception as e:
            DataManager.logger.error(f"Error during data files initialization: {e}")
            raise


class UserManager:
    """Class to manage user operations"""
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with username and password
        
        Args:
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            User data dictionary if authentication successful, None otherwise
        """
        try:
            users, error = DataManager.load_data(DEFAULT_USERS_FILE)
            if error:
                DataManager.logger.error(f"Failed to load users for authentication: {error}")
                return None
            
            if username in users:
                stored_password = users[username].get("password", "")
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                if stored_password == hashed_password:
                    user_data = users[username].copy()
                    user_data["username"] = username
                    DataManager.logger.info(f"User {username} authenticated successfully")
                    return user_data
            
            DataManager.logger.warning(f"Authentication failed for user {username}")
            return None
            
        except Exception as e:
            DataManager.logger.error(f"Error during authentication for {username}: {e}")
            return None
    
    @staticmethod
    def add_user(username: str, password: str, user_type: str, name: str) -> Tuple[bool, str]:
        """
        Add a new user
        
        Args:
            username: Username for the new user
            password: Password for the new user
            user_type: Type of user (admin/salesman)
            name: Display name for the user
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate input
            if not username or not username.strip():
                return False, "Username is required"
            
            if not password or len(password) < 4:
                return False, "Password must be at least 4 characters long"
            
            if user_type not in [USER_TYPE_ADMIN, USER_TYPE_SALESMAN]:
                return False, f"User type must be {USER_TYPE_ADMIN} or {USER_TYPE_SALESMAN}"
            
            if not name or not name.strip():
                return False, "Name is required"
            
            users, error = DataManager.load_data(DEFAULT_USERS_FILE)
            if error:
                return False, f"Failed to load users: {error}"
            
            if username in users:
                return False, "Username already exists"
            
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            users[username] = {
                "password": hashed_password,
                "type": user_type,
                "name": name.strip(),
                "created_at": datetime.now().isoformat()
            }
            
            success, save_error = DataManager.save_data(users, DEFAULT_USERS_FILE)
            if success:
                DataManager.logger.info(f"User {username} added successfully")
                return True, "User added successfully"
            else:
                return False, f"Failed to save user: {save_error}"
                
        except Exception as e:
            error_msg = f"Error adding user {username}: {e}"
            DataManager.logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def reset_password(username: str, new_password: str) -> Tuple[bool, str]:
        """
        Reset a user's password
        
        Args:
            username: Username whose password to reset
            new_password: New password
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate input
            if not new_password or len(new_password) < 4:
                return False, "Password must be at least 4 characters long"
            
            users, error = DataManager.load_data(DEFAULT_USERS_FILE)
            if error:
                return False, f"Failed to load users: {error}"
            
            if username not in users:
                return False, "User does not exist"
            
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            users[username]["password"] = hashed_password
            
            success, save_error = DataManager.save_data(users, DEFAULT_USERS_FILE)
            if success:
                DataManager.logger.info(f"Password reset successfully for user {username}")
                return True, "Password reset successfully"
            else:
                return False, f"Failed to save password: {save_error}"
                
        except Exception as e:
            error_msg = f"Error resetting password for {username}: {e}"
            DataManager.logger.error(error_msg)
            return False, error_msg


def show_message(parent, title: str, message: str, icon=QMessageBox.Information):
    """
    Show a message box with proper error logging
    
    Args:
        parent: Parent widget
        title: Message box title
        message: Message to display
        icon: Message box icon type
    """
    try:
        # Log the message
        if icon == QMessageBox.Critical:
            DataManager.logger.error(f"Critical message shown: {title} - {message}")
        elif icon == QMessageBox.Warning:
            DataManager.logger.warning(f"Warning message shown: {title} - {message}")
        else:
            DataManager.logger.info(f"Info message shown: {title} - {message}")
        
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.exec()
        
    except Exception as e:
        # Fallback error handling
        print(f"Error showing message box: {e}")
        print(f"Original message: {title} - {message}")


def show_validation_error(parent, field_errors: List[str]):
    """
    Show validation errors in a formatted message box
    
    Args:
        parent: Parent widget
        field_errors: List of field validation error messages
    """
    if not field_errors:
        return
    
    if len(field_errors) == 1:
        show_message(parent, "Validation Error", field_errors[0], QMessageBox.Warning)
    else:
        error_text = "Please correct the following errors:\n\n"
        for i, error in enumerate(field_errors, 1):
            error_text += f"{i}. {error}\n"
        
        show_message(parent, "Validation Errors", error_text, QMessageBox.Warning)


def handle_data_error(parent, operation: str, error_message: str):
    """
    Handle data operation errors with user-friendly messages
    
    Args:
        parent: Parent widget
        operation: Description of the operation that failed
        error_message: Technical error message
    """
    user_message = f"Failed to {operation}."
    
    if "permission" in error_message.lower():
        user_message += "\n\nPlease check file permissions and try again."
    elif "json" in error_message.lower() or "corrupt" in error_message.lower():
        user_message += "\n\nThe data file may be corrupted. Please contact support."
    else:
        user_message += f"\n\nTechnical details: {error_message}"
    
    show_message(parent, "Data Error", user_message, QMessageBox.Critical)


class AppSettings:
    """Class to manage application settings"""
    
    def __init__(self):
        self.settings = QSettings("ZERO", "ZEROApp")
    
    def get_theme(self):
        """Get current theme setting"""
        return self.settings.value("theme", "light")
    
    def set_theme(self, theme):
        """Set theme setting"""
        self.settings.setValue("theme", theme)
    
    def get_last_user(self):
        """Get last logged in user"""
        return self.settings.value("last_user", "")
    
    def set_last_user(self, username):
        """Set last logged in user"""
        self.settings.setValue("last_user", username)


def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:.2f}"


def format_date(date_str, output_format="%d/%m/%Y"):
    """Format date string"""
    if isinstance(date_str, str):
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime(output_format)
    return date_str.strftime(output_format)


class PaymentManager:
    """Class to manage customer payments and debt tracking"""
    
    @staticmethod
    def calculate_customer_debt(customer_id):
        """
        Calculate total debt for a customer based on credit sales
        
        Args:
            customer_id: Customer ID to calculate debt for
            
        Returns:
            Tuple of (total_debt, total_payments, outstanding_balance)
        """
        try:
            # Load sales data
            sales_data, sales_error = DataManager.load_data(DEFAULT_SALES_FILE)
            if sales_error:
                DataManager.logger.error(f"Failed to load sales data: {sales_error}")
                return 0.0, 0.0, 0.0
            
            # Load payments data
            payments_data, payments_error = DataManager.load_data(DEFAULT_PAYMENTS_FILE)
            if payments_error:
                DataManager.logger.error(f"Failed to load payments data: {payments_error}")
                return 0.0, 0.0, 0.0
            
            # Calculate total debt from credit sales
            total_debt = 0.0
            for sale in sales_data:
                if (sale.get("customer_id") == customer_id and 
                    sale.get("payment_method") == "Credit (Account)"):
                    total_debt += sale.get("total", 0.0)
            
            # Calculate total payments
            total_payments = 0.0
            for payment in payments_data:
                if payment.get("customer_id") == customer_id:
                    total_payments += payment.get("amount", 0.0)
            
            # Calculate outstanding balance
            outstanding_balance = total_debt - total_payments
            
            return total_debt, total_payments, outstanding_balance
            
        except Exception as e:
            DataManager.logger.error(f"Error calculating customer debt: {e}")
            return 0.0, 0.0, 0.0
    
    @staticmethod
    def record_payment(customer_id, amount, payment_method, notes, user_data):
        """
        Record a payment from a customer
        
        Args:
            customer_id: Customer ID making the payment
            amount: Payment amount
            payment_method: Method of payment (Cash, Bank Transfer, etc.)
            notes: Additional notes about the payment
            user_data: User recording the payment
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Validate input
            if not customer_id:
                return False, "Customer ID is required"
            
            if amount <= 0:
                return False, "Payment amount must be greater than zero"
            
            if not payment_method:
                return False, "Payment method is required"
            
            # Load payments data
            payments_data, error = DataManager.load_data(DEFAULT_PAYMENTS_FILE)
            if error:
                return False, f"Failed to load payments data: {error}"
            
            # Create payment record
            payment_record = {
                "id": DataManager.generate_id(),
                "customer_id": customer_id,
                "amount": float(amount),
                "payment_method": payment_method,
                "notes": notes or "",
                "payment_date": datetime.now().strftime("%Y-%m-%d"),
                "recorded_by": user_data.get("username", ""),
                "recorded_by_name": user_data.get("name", ""),
                "created_at": datetime.now().isoformat()
            }
            
            # Add payment to list
            payments_data.append(payment_record)
            
            # Save payments data
            success, save_error = DataManager.save_data(payments_data, DEFAULT_PAYMENTS_FILE)
            if success:
                DataManager.logger.info(f"Payment recorded for customer {customer_id}: ${amount}")
                return True, ""
            else:
                return False, f"Failed to save payment: {save_error}"
                
        except Exception as e:
            error_msg = f"Error recording payment: {e}"
            DataManager.logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def get_customer_payment_history(customer_id):
        """
        Get payment history for a specific customer
        
        Args:
            customer_id: Customer ID to get history for
            
        Returns:
            List of payment records sorted by date (newest first)
        """
        try:
            payments_data, error = DataManager.load_data(DEFAULT_PAYMENTS_FILE)
            if error:
                DataManager.logger.error(f"Failed to load payments data: {error}")
                return []
            
            # Filter payments for the customer
            customer_payments = [p for p in payments_data if p.get("customer_id") == customer_id]
            
            # Sort by date (newest first)
            customer_payments.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return customer_payments
            
        except Exception as e:
            DataManager.logger.error(f"Error getting customer payment history: {e}")
            return []
    
    @staticmethod
    def get_all_customer_balances():
        """
        Get debt and payment balances for all customers
        
        Returns:
            Dictionary with customer_id as key and balance info as value
        """
        try:
            # Load customers data
            customers_data, customers_error = DataManager.load_data(DEFAULT_CUSTOMERS_FILE)
            if customers_error:
                DataManager.logger.error(f"Failed to load customers data: {customers_error}")
                return {}
            
            balances = {}
            for customer in customers_data:
                customer_id = customer.get("id")
                if customer_id:
                    total_debt, total_payments, outstanding_balance = PaymentManager.calculate_customer_debt(customer_id)
                    balances[customer_id] = {
                        "total_debt": total_debt,
                        "total_payments": total_payments,
                        "outstanding_balance": outstanding_balance
                    }
            
            return balances
            
        except Exception as e:
            DataManager.logger.error(f"Error getting all customer balances: {e}")
            return {}


class MovementManager:
    """Class to manage inventory movements"""
    
    @staticmethod
    def create_sale_movement(sale_data, user_data):
        """
        Create inventory movement records for a sale transaction
        
        Args:
            sale_data: Sale transaction data
            user_data: User who made the sale
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Load current movements
            movements, error = DataManager.load_data(DEFAULT_MOVEMENTS_FILE)
            if error:
                return False, f"Failed to load movements: {error}"
            
            # Load products to get product details
            products, products_error = DataManager.load_data(DEFAULT_PRODUCTS_FILE)
            if products_error:
                return False, f"Failed to load products: {products_error}"
            
            # Create product lookup
            product_lookup = {p.get("id"): p for p in products}
            
            # Create movement records for each item in the sale
            new_movements = []
            
            for item in sale_data.get("items", []):
                product_id = item.get("product_id")
                product = product_lookup.get(product_id)
                
                if product:
                    movement_record = {
                        "id": DataManager.generate_id(),
                        "product_id": product_id,
                        "product_name": product.get("name", "Unknown"),
                        "movement_type": "out",
                        "quantity": item.get("quantity", 0),
                        "unit_price": item.get("unit_price", 0.0),
                        "total_value": item.get("total_price", 0.0),
                        "reference_type": "sale",
                        "reference_id": sale_data.get("id"),
                        "reference_number": sale_data.get("invoice_number"),
                        "notes": f"Sale to {sale_data.get('customer_name', 'Walk-in Customer')}",
                        "created_by": user_data.get("username", ""),
                        "created_by_name": user_data.get("name", ""),
                        "created_at": datetime.now().isoformat()
                    }
                    new_movements.append(movement_record)
            
            # Add new movements to the list
            movements.extend(new_movements)
            
            # Save updated movements
            success, save_error = DataManager.save_data(movements, DEFAULT_MOVEMENTS_FILE)
            if success:
                DataManager.logger.info(f"Created {len(new_movements)} movement records for sale {sale_data.get('id')}")
                return True, ""
            else:
                return False, f"Failed to save movements: {save_error}"
                
        except Exception as e:
            error_msg = f"Error creating sale movements: {e}"
            DataManager.logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def record_stock_adjustment(product_id, quantity_change, adjustment_type, notes, user_data):
        """
        Record a stock adjustment (manual inventory change)
        
        Args:
            product_id: Product ID being adjusted
            quantity_change: Change in quantity (positive for increase, negative for decrease)
            adjustment_type: Type of adjustment (recount, damage, return, etc.)
            notes: Notes about the adjustment
            user_data: User making the adjustment
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Load movements and products
            movements, movements_error = DataManager.load_data(DEFAULT_MOVEMENTS_FILE)
            if movements_error:
                return False, f"Failed to load movements: {movements_error}"
            
            products, products_error = DataManager.load_data(DEFAULT_PRODUCTS_FILE)
            if products_error:
                return False, f"Failed to load products: {products_error}"
            
            # Find the product
            product = next((p for p in products if p.get("id") == product_id), None)
            if not product:
                return False, "Product not found"
            
            # Create movement record
            movement_record = {
                "id": DataManager.generate_id(),
                "product_id": product_id,
                "product_name": product.get("name", "Unknown"),
                "movement_type": "in" if quantity_change > 0 else "out",
                "quantity": abs(quantity_change),
                "unit_price": product.get("buying_price", 0.0),
                "total_value": abs(quantity_change) * product.get("buying_price", 0.0),
                "reference_type": "adjustment",
                "reference_id": None,
                "reference_number": f"ADJ-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "adjustment_type": adjustment_type,
                "notes": notes or "",
                "created_by": user_data.get("username", ""),
                "created_by_name": user_data.get("name", ""),
                "created_at": datetime.now().isoformat()
            }
            
            # Add movement to list
            movements.append(movement_record)
            
            # Save movements
            success, save_error = DataManager.save_data(movements, DEFAULT_MOVEMENTS_FILE)
            if success:
                DataManager.logger.info(f"Stock adjustment recorded for product {product_id}: {quantity_change}")
                return True, ""
            else:
                return False, f"Failed to save movement: {save_error}"
                
        except Exception as e:
            error_msg = f"Error recording stock adjustment: {e}"
            DataManager.logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def get_product_movement_history(product_id, days=None):
        """
        Get movement history for a specific product
        
        Args:
            product_id: Product ID to get history for
            days: Number of days to look back (None for all history)
            
        Returns:
            List of movement records sorted by date (newest first)
        """
        try:
            movements, error = DataManager.load_data(DEFAULT_MOVEMENTS_FILE)
            if error:
                DataManager.logger.error(f"Failed to load movements: {error}")
                return []
            
            # Filter movements for the product
            product_movements = [m for m in movements if m.get("product_id") == product_id]
            
            # Filter by date if specified
            if days:
                cutoff_date = datetime.now() - timedelta(days=days)
                product_movements = [
                    m for m in product_movements 
                    if datetime.fromisoformat(m.get("created_at", "")) >= cutoff_date
                ]
            
            # Sort by date (newest first)
            product_movements.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return product_movements
            
        except Exception as e:
            DataManager.logger.error(f"Error getting product movement history: {e}")
            return []
