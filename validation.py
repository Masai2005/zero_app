"""
Data validation module for the ZERO application.
Provides comprehensive validation functions for all data types.
"""
import re
from datetime import datetime
from typing import Tuple, Optional, Any


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class Validator:
    """Main validation class with static methods for different data types"""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email address format
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return True, ""  # Email is optional
        
        email = email.strip()
        if not email:
            return True, ""
        
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        if len(email) > 254:  # RFC 5321 limit
            return False, "Email address too long"
        
        return True, ""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Validate phone number format
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not phone:
            return True, ""  # Phone is optional
        
        phone = phone.strip()
        if not phone:
            return True, ""
        
        # Remove common separators and spaces
        cleaned_phone = re.sub(r'[\s\-\(\)\+]', '', phone)
        
        # Check if it contains only digits after cleaning
        if not cleaned_phone.isdigit():
            return False, "Phone number should contain only digits, spaces, hyphens, parentheses, and plus sign"
        
        # Check length (international format can be 7-15 digits)
        if len(cleaned_phone) < 7 or len(cleaned_phone) > 15:
            return False, "Phone number should be between 7 and 15 digits"
        
        return True, ""
    
    @staticmethod
    def validate_required_string(value: str, field_name: str, min_length: int = 1, max_length: int = 255) -> Tuple[bool, str]:
        """
        Validate required string field
        
        Args:
            value: String value to validate
            field_name: Name of the field for error messages
            min_length: Minimum required length
            max_length: Maximum allowed length
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value or not value.strip():
            return False, f"{field_name} is required"
        
        value = value.strip()
        
        if len(value) < min_length:
            return False, f"{field_name} must be at least {min_length} characters long"
        
        if len(value) > max_length:
            return False, f"{field_name} must be no more than {max_length} characters long"
        
        return True, ""
    
    @staticmethod
    def validate_optional_string(value: str, field_name: str, max_length: int = 255) -> Tuple[bool, str]:
        """
        Validate optional string field
        
        Args:
            value: String value to validate
            field_name: Name of the field for error messages
            max_length: Maximum allowed length
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value:
            return True, ""
        
        value = value.strip()
        if not value:
            return True, ""
        
        if len(value) > max_length:
            return False, f"{field_name} must be no more than {max_length} characters long"
        
        return True, ""
    
    @staticmethod
    def validate_positive_number(value: float, field_name: str, allow_zero: bool = False) -> Tuple[bool, str]:
        """
        Validate positive number
        
        Args:
            value: Number to validate
            field_name: Name of the field for error messages
            allow_zero: Whether zero is allowed
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            return False, f"{field_name} is required"
        
        if allow_zero and value < 0:
            return False, f"{field_name} must be zero or positive"
        elif not allow_zero and value <= 0:
            return False, f"{field_name} must be positive"
        
        # Check for reasonable upper limit
        if value > 1000000:  # 1 million
            return False, f"{field_name} seems unreasonably large"
        
        return True, ""
    
    @staticmethod
    def validate_integer_range(value: int, field_name: str, min_value: int = 0, max_value: int = 1000000) -> Tuple[bool, str]:
        """
        Validate integer within range
        
        Args:
            value: Integer to validate
            field_name: Name of the field for error messages
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            return False, f"{field_name} is required"
        
        if value < min_value:
            return False, f"{field_name} must be at least {min_value}"
        
        if value > max_value:
            return False, f"{field_name} must be no more than {max_value}"
        
        return True, ""
    
    @staticmethod
    def validate_date(date_str: str, field_name: str) -> Tuple[bool, str]:
        """
        Validate date string format
        
        Args:
            date_str: Date string to validate
            field_name: Name of the field for error messages
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not date_str:
            return False, f"{field_name} is required"
        
        try:
            # Try to parse as ISO format first
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return True, ""
        except ValueError:
            pass
        
        # Try common date formats
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']
        
        for fmt in formats:
            try:
                datetime.strptime(date_str, fmt)
                return True, ""
            except ValueError:
                continue
        
        return False, f"{field_name} has invalid date format"
    
    @staticmethod
    def validate_barcode(barcode: str) -> Tuple[bool, str]:
        """
        Validate barcode format
        
        Args:
            barcode: Barcode to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not barcode:
            return True, ""  # Barcode is optional
        
        barcode = barcode.strip()
        if not barcode:
            return True, ""
        
        # Check if it contains only alphanumeric characters
        if not re.match(r'^[a-zA-Z0-9]+$', barcode):
            return False, "Barcode should contain only letters and numbers"
        
        # Check reasonable length
        if len(barcode) < 3 or len(barcode) > 50:
            return False, "Barcode should be between 3 and 50 characters"
        
        return True, ""


class CustomerValidator:
    """Specialized validator for customer data"""
    
    @staticmethod
    def validate_customer_data(customer_data: dict) -> Tuple[bool, str]:
        """
        Validate complete customer data
        
        Args:
            customer_data: Dictionary containing customer information
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate required fields
        is_valid, error = Validator.validate_required_string(
            customer_data.get('first_name', ''), 'First name', min_length=1, max_length=50
        )
        if not is_valid:
            return False, error
        
        is_valid, error = Validator.validate_required_string(
            customer_data.get('last_name', ''), 'Last name', min_length=1, max_length=50
        )
        if not is_valid:
            return False, error
        
        # Validate optional fields
        is_valid, error = Validator.validate_optional_string(
            customer_data.get('middle_name', ''), 'Middle name', max_length=50
        )
        if not is_valid:
            return False, error
        
        is_valid, error = Validator.validate_optional_string(
            customer_data.get('company_name', ''), 'Company name', max_length=100
        )
        if not is_valid:
            return False, error
        
        is_valid, error = Validator.validate_phone(customer_data.get('mobile', ''))
        if not is_valid:
            return False, f"Mobile: {error}"
        
        is_valid, error = Validator.validate_email(customer_data.get('email', ''))
        if not is_valid:
            return False, f"Email: {error}"
        
        is_valid, error = Validator.validate_phone(customer_data.get('whatsapp', ''))
        if not is_valid:
            return False, f"WhatsApp: {error}"
        
        is_valid, error = Validator.validate_optional_string(
            customer_data.get('address', ''), 'Address', max_length=500
        )
        if not is_valid:
            return False, error
        
        return True, ""


class ProductValidator:
    """Specialized validator for product data"""
    
    @staticmethod
    def validate_product_data(product_data: dict) -> Tuple[bool, str]:
        """
        Validate complete product data
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate required fields
        is_valid, error = Validator.validate_required_string(
            product_data.get('name', ''), 'Product name', min_length=1, max_length=100
        )
        if not is_valid:
            return False, error
        
        # Validate barcode
        is_valid, error = Validator.validate_barcode(product_data.get('barcode', ''))
        if not is_valid:
            return False, error
        
        # Validate prices
        is_valid, error = Validator.validate_positive_number(
            product_data.get('buying_price', 0), 'Buying price', allow_zero=True
        )
        if not is_valid:
            return False, error
        
        is_valid, error = Validator.validate_positive_number(
            product_data.get('selling_price', 0), 'Selling price', allow_zero=False
        )
        if not is_valid:
            return False, error
        
        # Validate quantities
        is_valid, error = Validator.validate_integer_range(
            product_data.get('quantity', 0), 'Current quantity', min_value=0
        )
        if not is_valid:
            return False, error
        
        is_valid, error = Validator.validate_integer_range(
            product_data.get('min_quantity', 0), 'Minimum quantity', min_value=0
        )
        if not is_valid:
            return False, error
        
        # Validate unit
        valid_units = ["Each", "Box", "Kg", "Liter", "Pair", "Set"]
        unit = product_data.get('unit', '')
        if unit not in valid_units:
            return False, f"Unit must be one of: {', '.join(valid_units)}"
        
        # Validate expiry date
        expiry_date = product_data.get('expiry_date', '')
        if expiry_date:
            is_valid, error = Validator.validate_date(expiry_date, 'Expiry date')
            if not is_valid:
                return False, error
        
        return True, ""


class SaleValidator:
    """Specialized validator for sales data"""
    
    @staticmethod
    def validate_sale_item(item_data: dict) -> Tuple[bool, str]:
        """
        Validate sale item data
        
        Args:
            item_data: Dictionary containing sale item information
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate quantity
        is_valid, error = Validator.validate_integer_range(
            item_data.get('quantity', 0), 'Quantity', min_value=1
        )
        if not is_valid:
            return False, error
        
        # Validate prices
        is_valid, error = Validator.validate_positive_number(
            item_data.get('unit_price', 0), 'Unit price', allow_zero=False
        )
        if not is_valid:
            return False, error
        
        # Validate discount
        discount_percent = item_data.get('discount_percent', 0)
        if discount_percent < 0 or discount_percent > 100:
            return False, "Discount percentage must be between 0 and 100"
        
        return True, ""
    
    @staticmethod
    def validate_sale_data(sale_data: dict) -> Tuple[bool, str]:
        """
        Validate complete sale data
        
        Args:
            sale_data: Dictionary containing sale information
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate items
        items = sale_data.get('items', [])
        if not items:
            return False, "Sale must contain at least one item"
        
        for i, item in enumerate(items):
            is_valid, error = SaleValidator.validate_sale_item(item)
            if not is_valid:
                return False, f"Item {i+1}: {error}"
        
        # Validate payment method
        valid_payment_methods = ["Cash", "Credit Card", "Credit (Account)"]
        payment_method = sale_data.get('payment_method', '')
        if payment_method not in valid_payment_methods:
            return False, f"Payment method must be one of: {', '.join(valid_payment_methods)}"
        
        # Validate totals
        is_valid, error = Validator.validate_positive_number(
            sale_data.get('total', 0), 'Total amount', allow_zero=False
        )
        if not is_valid:
            return False, error
        
        return True, ""


class ExpenseValidator:
    """Specialized validator for expense data"""
    
    @staticmethod
    def validate_expense_data(expense_data: dict) -> Tuple[bool, str]:
        """
        Validate complete expense data
        
        Args:
            expense_data: Dictionary containing expense information
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate category
        valid_categories = [
            "Rent", "Utilities", "Salaries", "Supplies", 
            "Marketing", "Maintenance", "Transport", "Other"
        ]
        category = expense_data.get('category', '')
        if category not in valid_categories:
            return False, f"Category must be one of: {', '.join(valid_categories)}"
        
        # Validate amount
        is_valid, error = Validator.validate_positive_number(
            expense_data.get('amount', 0), 'Amount', allow_zero=False
        )
        if not is_valid:
            return False, error
        
        # Validate date
        is_valid, error = Validator.validate_date(
            expense_data.get('date', ''), 'Date'
        )
        if not is_valid:
            return False, error
        
        # Validate details
        is_valid, error = Validator.validate_required_string(
            expense_data.get('details', ''), 'Details', min_length=3, max_length=500
        )
        if not is_valid:
            return False, error
        
        return True, ""