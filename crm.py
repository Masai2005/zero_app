"""
Customer Relationship Management (CRM) module for the application.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QLineEdit, QFormLayout, 
    QGroupBox, QMessageBox, QHeaderView, QDialog, QTabWidget,
    QSplitter, QDoubleSpinBox, QComboBox
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QColor
from datetime import datetime

from styles import StyleSheet, Theme
from utils import DataManager, format_date, format_currency, DEFAULT_CUSTOMERS_FILE, DEFAULT_SALES_FILE, DEFAULT_PAYMENTS_FILE, show_message, show_validation_error, handle_data_error, PaymentManager
from validation import CustomerValidator
from search_filter import SearchFilter, AdvancedSearchDialog, QuickSearchWidget
from print_utils import PrintManager


class PaymentRecordDialog(QDialog):
    """Dialog for recording customer payments"""
    
    def __init__(self, customer_data, user_data, parent=None):
        super().__init__(parent)
        self.customer_data = customer_data
        self.user_data = user_data
        
        customer_name = f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}"
        self.setWindowTitle(f"Record Payment - {customer_name}")
        self.setMinimumWidth(400)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Customer info section
        customer_name = f"{self.customer_data.get('first_name', '')} {self.customer_data.get('last_name', '')}"
        customer_label = QLabel(f"Recording payment for: {customer_name}")
        customer_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(customer_label)
        
        # Current balance info
        total_debt, total_payments, outstanding_balance = PaymentManager.calculate_customer_debt(self.customer_data.get("id"))
        balance_info = QLabel(f"Current Outstanding Balance: {format_currency(outstanding_balance)}")
        balance_info.setStyleSheet("font-size: 12px; color: red;" if outstanding_balance > 0 else "font-size: 12px; color: green;")
        layout.addWidget(balance_info)
        
        # Form layout for payment details
        form_layout = QFormLayout()
        
        # Payment amount
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMinimum(0.01)
        self.amount_input.setMaximum(999999.99)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("$")
        form_layout.addRow("Payment Amount:", self.amount_input)
        
        # Payment method
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(["Cash", "Bank Transfer", "Check", "Credit Card", "Mobile Payment"])
        form_layout.addRow("Payment Method:", self.payment_method_combo)
        
        # Notes
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Optional notes about this payment...")
        form_layout.addRow("Notes:", self.notes_input)
        
        layout.addLayout(form_layout)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumWidth(100)
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.clicked.connect(self.reject)
        
        # Record payment button
        self.record_button = QPushButton("Record Payment")
        self.record_button.setMinimumWidth(140)
        self.record_button.setMinimumHeight(35)
        self.record_button.clicked.connect(self.record_payment)
        self.record_button.setStyleSheet("background-color: #28a745; color: white;")
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.record_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def record_payment(self):
        """Record the payment"""
        amount = self.amount_input.value()
        payment_method = self.payment_method_combo.currentText()
        notes = self.notes_input.text().strip()
        
        if amount <= 0:
            show_message(self, "Validation Error", "Payment amount must be greater than zero", QMessageBox.Warning)
            return
        
        # Record the payment
        success, error = PaymentManager.record_payment(
            self.customer_data.get("id"),
            amount,
            payment_method,
            notes,
            self.user_data
        )
        
        if success:
            show_message(self, "Success", f"Payment of {format_currency(amount)} recorded successfully")
            self.accept()
        else:
            show_message(self, "Error", f"Failed to record payment: {error}", QMessageBox.Critical)


class CustomerDetailsDialog(QDialog):
    """Dialog for displaying detailed customer information and transactions"""
    
    def __init__(self, customer_data, sales_data, parent=None):
        super().__init__(parent)
        self.customer_data = customer_data
        self.sales_data = sales_data
        
        self.setWindowTitle(f"Customer Details - {customer_data.get('first_name', '')} {customer_data.get('last_name', '')}")
        self.setMinimumSize(800, 500)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Customer information section
        info_group = QGroupBox("Customer Information")
        info_layout = QFormLayout()
        
        # Full name
        full_name = f"{self.customer_data.get('first_name', '')} {self.customer_data.get('middle_name', '')} {self.customer_data.get('last_name', '')}"
        info_layout.addRow("Name:", QLabel(full_name.strip()))
        
        # Company name
        if self.customer_data.get("company_name"):
            info_layout.addRow("Company:", QLabel(self.customer_data.get("company_name")))
        
        # Contact information
        if self.customer_data.get("mobile"):
            info_layout.addRow("Mobile:", QLabel(self.customer_data.get("mobile")))
        
        if self.customer_data.get("email"):
            info_layout.addRow("Email:", QLabel(self.customer_data.get("email")))
        
        if self.customer_data.get("whatsapp"):
            info_layout.addRow("WhatsApp:", QLabel(self.customer_data.get("whatsapp")))
        
        # Address
        if self.customer_data.get("address"):
            info_layout.addRow("Address:", QLabel(self.customer_data.get("address")))
        
        # Created date
        created_at = format_date(self.customer_data.get("created_at", ""))
        info_layout.addRow("Customer Since:", QLabel(created_at))
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Debt and payment summary section
        debt_group = QGroupBox("Account Summary")
        debt_layout = QFormLayout()
        
        # Calculate debt and payment info
        customer_id = self.customer_data.get("id")
        total_debt, total_payments, outstanding_balance = PaymentManager.calculate_customer_debt(customer_id)
        
        # Total debt from credit sales
        debt_layout.addRow("Total Credit Sales:", QLabel(format_currency(total_debt)))
        
        # Total payments made
        debt_layout.addRow("Total Payments:", QLabel(format_currency(total_payments)))
        
        # Outstanding balance
        balance_label = QLabel(format_currency(outstanding_balance))
        balance_label.setStyleSheet("font-weight: bold; color: red;" if outstanding_balance > 0 else "font-weight: bold; color: green;")
        debt_layout.addRow("Outstanding Balance:", balance_label)
        
        debt_group.setLayout(debt_layout)
        layout.addWidget(debt_group)
        
        # Tab widget for transactions and payments
        tab_widget = QTabWidget()
        
        # Transactions tab
        transactions_tab = QWidget()
        transactions_layout = QVBoxLayout()
        
        # Transactions table
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(5)
        self.transactions_table.setHorizontalHeaderLabels(["Date", "Invoice #", "Items", "Total", "Payment Method"])
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        transactions_layout.addWidget(self.transactions_table)
        
        transactions_tab.setLayout(transactions_layout)
        tab_widget.addTab(transactions_tab, "Sales History")
        
        # Payments tab
        payments_tab = QWidget()
        payments_layout = QVBoxLayout()
        
        # Payments table
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(5)
        self.payments_table.setHorizontalHeaderLabels(["Date", "Amount", "Method", "Notes", "Recorded By"])
        self.payments_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        payments_layout.addWidget(self.payments_table)
        
        payments_tab.setLayout(payments_layout)
        tab_widget.addTab(payments_tab, "Payment History")
        
        layout.addWidget(tab_widget)
        
        # Populate tables
        self.populate_transactions()
        self.populate_payments()
        
        # Button section
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Record payment button
        self.record_payment_btn = QPushButton("Record Payment")
        self.record_payment_btn.setMinimumWidth(140)
        self.record_payment_btn.setMinimumHeight(35)
        self.record_payment_btn.clicked.connect(self.record_payment)
        self.record_payment_btn.setStyleSheet("background-color: #28a745; color: white;")
        button_layout.addWidget(self.record_payment_btn)
        
        # Add spacer
        button_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.setMinimumHeight(35)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def get_customer_sales(self):
        """Get sales for this customer"""
        customer_id = self.customer_data.get("id")
        return [sale for sale in self.sales_data if sale.get("customer_id") == customer_id]
    
    def populate_transactions(self):
        """Populate the transactions table"""
        customer_sales = self.get_customer_sales()
        
        # Sort by date (newest first)
        sorted_sales = sorted(customer_sales, key=lambda x: x.get("created_at", ""), reverse=True)
        
        self.transactions_table.setRowCount(len(sorted_sales))
        
        for row, sale in enumerate(sorted_sales):
            # Date
            self.transactions_table.setItem(row, 0, QTableWidgetItem(format_date(sale.get("created_at", ""))))
            
            # Invoice number
            self.transactions_table.setItem(row, 1, QTableWidgetItem(sale.get("invoice_number", "")))
            
            # Items count
            items_count = len(sale.get("items", []))
            self.transactions_table.setItem(row, 2, QTableWidgetItem(str(items_count)))
            
            # Total
            self.transactions_table.setItem(row, 3, QTableWidgetItem(format_currency(sale.get("total", 0))))
            
            # Payment method
            self.transactions_table.setItem(row, 4, QTableWidgetItem(sale.get("payment_method", "")))
    
    def populate_payments(self):
        """Populate the payments table"""
        customer_id = self.customer_data.get("id")
        payments = PaymentManager.get_customer_payment_history(customer_id)
        
        self.payments_table.setRowCount(len(payments))
        
        for row, payment in enumerate(payments):
            # Date
            self.payments_table.setItem(row, 0, QTableWidgetItem(format_date(payment.get("created_at", ""))))
            
            # Amount
            self.payments_table.setItem(row, 1, QTableWidgetItem(format_currency(payment.get("amount", 0))))
            
            # Payment method
            self.payments_table.setItem(row, 2, QTableWidgetItem(payment.get("payment_method", "")))
            
            # Notes
            self.payments_table.setItem(row, 3, QTableWidgetItem(payment.get("notes", "")))
            
            # Recorded by
            self.payments_table.setItem(row, 4, QTableWidgetItem(payment.get("recorded_by_name", "")))
    
    def record_payment(self):
        """Open payment recording dialog"""
        # We need to get user_data from parent window
        parent_window = self.parent()
        if hasattr(parent_window, 'user_data'):
            user_data = parent_window.user_data
        else:
            # Fallback - create minimal user data
            user_data = {"username": "admin", "name": "Administrator"}
        
        dialog = PaymentRecordDialog(self.customer_data, user_data, self)
        if dialog.exec() == QDialog.Accepted:
            # Refresh the payment table and debt summary
            self.populate_payments()
            # We should also refresh the debt summary, but that requires recreating the dialog
            # For now, show a message that the user should close and reopen to see updated balance
            show_message(self, "Payment Recorded", "Payment recorded successfully. Close and reopen this dialog to see updated balance.")


class NewCustomerDialog(QDialog):
    """Dialog for adding a new customer"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Customer")
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Form layout for inputs
        form_layout = QFormLayout()
        
        # First name field
        self.first_name_input = QLineEdit()
        form_layout.addRow("First Name:", self.first_name_input)
        
        # Middle name field
        self.middle_name_input = QLineEdit()
        form_layout.addRow("Middle Name:", self.middle_name_input)
        
        # Last name field
        self.last_name_input = QLineEdit()
        form_layout.addRow("Last Name:", self.last_name_input)
        
        # Company name field
        self.company_name_input = QLineEdit()
        form_layout.addRow("Company Name:", self.company_name_input)
        
        # Mobile number field
        self.mobile_input = QLineEdit()
        form_layout.addRow("Mobile:", self.mobile_input)
        
        # Email field
        self.email_input = QLineEdit()
        form_layout.addRow("Email:", self.email_input)
        
        # WhatsApp field
        self.whatsapp_input = QLineEdit()
        form_layout.addRow("WhatsApp:", self.whatsapp_input)
        
        # Address field
        self.address_input = QLineEdit()
        form_layout.addRow("Address:", self.address_input)
        
        layout.addLayout(form_layout)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.setMinimumWidth(100)
        self.save_button.setMinimumHeight(35)
        self.save_button.clicked.connect(self.save_customer)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumWidth(100)
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def save_customer(self):
        """Save new customer data with validation"""
        # Create customer object
        customer_data = {
            "id": DataManager.generate_id(),
            "first_name": self.first_name_input.text().strip(),
            "middle_name": self.middle_name_input.text().strip(),
            "last_name": self.last_name_input.text().strip(),
            "company_name": self.company_name_input.text().strip(),
            "mobile": self.mobile_input.text().strip(),
            "email": self.email_input.text().strip(),
            "whatsapp": self.whatsapp_input.text().strip(),
            "address": self.address_input.text().strip(),
            "created_at": datetime.now().isoformat()
        }
        
        # Validate customer data
        is_valid, error_message = CustomerValidator.validate_customer_data(customer_data)
        if not is_valid:
            show_message(self, "Validation Error", error_message, QMessageBox.Warning)
            return
        
        self.customer_data = customer_data
        self.accept()


class CRMWindow(QWidget):
    """CRM window widget"""
    
    def __init__(self, user_data, theme=Theme.LIGHT):
        super().__init__()
        self.user_data = user_data
        self.theme = theme
        
        # Load data with error handling
        self.customers, customers_error = DataManager.load_data(DEFAULT_CUSTOMERS_FILE)
        if customers_error:
            handle_data_error(self, "load customers", customers_error)
        
        self.sales_data, sales_error = DataManager.load_data(DEFAULT_SALES_FILE)
        if sales_error:
            handle_data_error(self, "load sales data", sales_error)
        
        self.setup_ui()
        
        # Initialize search filters
        self.current_filters = {}
        self.filtered_customers = self.customers.copy()
        
        self.refresh_customers()
    
    def setup_ui(self):
        """Setup UI components"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Title
        title = QLabel("Customer Relationship Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title)
        
        # Search and add section
        search_layout = QHBoxLayout()
        
        # Quick search widget
        self.quick_search = QuickSearchWidget("Search customers...")
        self.quick_search.search_changed.connect(self.on_quick_search)
        self.quick_search.advanced_search_requested.connect(self.show_advanced_search)
        search_layout.addWidget(self.quick_search)
        
        # Add customer button
        self.add_customer_btn = QPushButton("Add New Customer")
        self.add_customer_btn.setMinimumWidth(150)
        self.add_customer_btn.setMinimumHeight(35)
        self.add_customer_btn.clicked.connect(self.add_customer)
        search_layout.addWidget(self.add_customer_btn)
        
        main_layout.addLayout(search_layout)
        
        # Customers table
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(7)
        self.customers_table.setHorizontalHeaderLabels(["Name", "Company", "Contact", "Total Debt", "Total Payments", "Outstanding Balance", "Customer Since"])
        self.customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.customers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.customers_table.setSelectionMode(QTableWidget.SingleSelection)
        self.customers_table.doubleClicked.connect(self.view_customer_details)
        main_layout.addWidget(self.customers_table)
        
        # Button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # View details button
        self.view_btn = QPushButton("View Details")
        self.view_btn.setMinimumWidth(100)
        self.view_btn.setMinimumHeight(35)
        self.view_btn.clicked.connect(self.view_customer_details)
        button_layout.addWidget(self.view_btn)
        
        # Record payment button
        self.record_payment_btn = QPushButton("Record Payment")
        self.record_payment_btn.setMinimumWidth(140)
        self.record_payment_btn.setMinimumHeight(35)
        self.record_payment_btn.clicked.connect(self.record_customer_payment)
        self.record_payment_btn.setStyleSheet("background-color: #28a745; color: white;")
        button_layout.addWidget(self.record_payment_btn)
        
        # Edit button
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setMinimumWidth(80)
        self.edit_btn.setMinimumHeight(35)
        self.edit_btn.clicked.connect(self.edit_customer)
        button_layout.addWidget(self.edit_btn)
        
        # Delete button
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setMinimumWidth(80)
        self.delete_btn.setMinimumHeight(35)
        self.delete_btn.clicked.connect(self.delete_customer)
        button_layout.addWidget(self.delete_btn)
        
        # Print customer report button
        self.print_report_btn = QPushButton("Print Customer Report")
        self.print_report_btn.setMinimumWidth(160)
        self.print_report_btn.setMinimumHeight(35)
        self.print_report_btn.clicked.connect(self.print_customer_report)
        button_layout.addWidget(self.print_report_btn)

        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def refresh_customers(self):
        """Refresh customers table with debt and payment information"""
        customers_to_show = self.filtered_customers if hasattr(self, 'filtered_customers') else self.customers
        self.customers_table.setRowCount(len(customers_to_show))
        
        # Get all customer balances at once for efficiency
        customer_balances = PaymentManager.get_all_customer_balances()
        
        for row, customer in enumerate(customers_to_show):
            customer_id = customer.get("id")
            
            # Name
            full_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}"
            name_item = QTableWidgetItem(full_name)
            name_item.setData(Qt.UserRole, customer_id)  # Store customer ID for reference
            self.customers_table.setItem(row, 0, name_item)
            
            # Company
            self.customers_table.setItem(row, 1, QTableWidgetItem(customer.get("company_name", "")))
            
            # Contact - show mobile or email
            contact = customer.get("mobile", "") or customer.get("email", "")
            self.customers_table.setItem(row, 2, QTableWidgetItem(contact))
            
            # Get balance information
            balance_info = customer_balances.get(customer_id, {
                "total_debt": 0.0,
                "total_payments": 0.0,
                "outstanding_balance": 0.0
            })
            
            # Total debt
            debt_item = QTableWidgetItem(format_currency(balance_info["total_debt"]))
            if balance_info["total_debt"] > 0:
                debt_item.setForeground(QColor("orange"))
            self.customers_table.setItem(row, 3, debt_item)
            
            # Total payments
            payments_item = QTableWidgetItem(format_currency(balance_info["total_payments"]))
            if balance_info["total_payments"] > 0:
                payments_item.setForeground(QColor("green"))
            self.customers_table.setItem(row, 4, payments_item)
            
            # Outstanding balance
            outstanding = balance_info["outstanding_balance"]
            balance_item = QTableWidgetItem(format_currency(outstanding))
            if outstanding > 0:
                balance_item.setForeground(QColor("red"))
            elif outstanding < 0:
                balance_item.setForeground(QColor("blue"))  # Overpayment
            else:
                balance_item.setForeground(QColor("green"))
            self.customers_table.setItem(row, 5, balance_item)
            
            # Customer since
            created_at = format_date(customer.get("created_at", ""))
            self.customers_table.setItem(row, 6, QTableWidgetItem(created_at))
    
    def on_quick_search(self, search_text):
        """Handle quick search text change"""
        if search_text.strip():
            self.current_filters = {"text_search": search_text.strip()}
        else:
            self.current_filters = {}
        self.apply_filters()
    
    def show_advanced_search(self):
        """Show advanced search dialog"""
        dialog = AdvancedSearchDialog("customers", self)
        
        # Pre-populate with current filters
        if self.current_filters:
            dialog.apply_config(self.current_filters)
        
        dialog.search_applied.connect(self.on_advanced_search_applied)
        dialog.exec()
    
    def on_advanced_search_applied(self, filters):
        """Handle advanced search filters"""
        self.current_filters = filters
        self.apply_filters()
        
        # Update quick search text if it was part of the filters
        if filters.get("text_search"):
            self.quick_search.set_search_text(filters["text_search"])
        else:
            self.quick_search.clear_search()
    
    def apply_filters(self):
        """Apply current filters to customers"""
        self.filtered_customers = SearchFilter.filter_customers(self.customers, self.current_filters)
        self.refresh_customers()
    
    def filter_customers(self):
        """Legacy method - kept for compatibility"""
        # This method is now handled by the new search system
        pass
    
    def get_selected_customer_id(self):
        """Get the ID of the selected customer"""
        selected_row = self.customers_table.currentRow()
        if selected_row >= 0:
            return self.customers_table.item(selected_row, 0).data(Qt.UserRole)
        return None
    
    def get_customer_by_id(self, customer_id):
        """Get customer data by ID"""
        for customer in self.customers:
            if customer.get("id") == customer_id:
                return customer
        return None
    
    def add_customer(self):
        """Add a new customer"""
        dialog = NewCustomerDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # Add new customer to data
            new_customer = dialog.customer_data
            self.customers.append(new_customer)
            
            # Save data
            success, error = DataManager.save_data(self.customers, DEFAULT_CUSTOMERS_FILE)
            if success:
                # Refresh table
                self.refresh_customers()
                show_message(self, "Success", "Customer added successfully")
            else:
                handle_data_error(self, "save customer data", error)
                # Remove the customer from memory since save failed
                self.customers.pop()
    
    def edit_customer(self):
        """Edit selected customer"""
        customer_id = self.get_selected_customer_id()
        if not customer_id:
            show_message(self, "Error", "No customer selected", QMessageBox.Warning)
            return
        
        customer = self.get_customer_by_id(customer_id)
        if not customer:
            return
        
        dialog = NewCustomerDialog(self)
        
        # Pre-fill form with existing data
        dialog.first_name_input.setText(customer.get("first_name", ""))
        dialog.middle_name_input.setText(customer.get("middle_name", ""))
        dialog.last_name_input.setText(customer.get("last_name", ""))
        dialog.company_name_input.setText(customer.get("company_name", ""))
        dialog.mobile_input.setText(customer.get("mobile", ""))
        dialog.email_input.setText(customer.get("email", ""))
        dialog.whatsapp_input.setText(customer.get("whatsapp", ""))
        dialog.address_input.setText(customer.get("address", ""))
        
        if dialog.exec() == QDialog.Accepted:
            # Update customer data
            updated_data = dialog.customer_data
            
            # Preserve ID and created_at
            updated_data["id"] = customer.get("id")
            updated_data["created_at"] = customer.get("created_at")
            
            # Update in list
            for i, c in enumerate(self.customers):
                if c.get("id") == customer_id:
                    self.customers[i] = updated_data
                    break
            
            # Save data
            success, error = DataManager.save_data(self.customers, DEFAULT_CUSTOMERS_FILE)
            if success:
                # Refresh table
                self.refresh_customers()
                show_message(self, "Success", "Customer updated successfully")
            else:
                handle_data_error(self, "save customer data", error)
                # Restore original data since save failed
                for i, c in enumerate(self.customers):
                    if c.get("id") == customer_id:
                        self.customers[i] = customer
                        break
    
    def delete_customer(self):
        """Delete selected customer"""
        customer_id = self.get_selected_customer_id()
        if not customer_id:
            show_message(self, "Error", "No customer selected", QMessageBox.Warning)
            return
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this customer?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Check if customer has associated sales
            customer_sales = [sale for sale in self.sales_data if sale.get("customer_id") == customer_id]
            if customer_sales:
                show_message(
                    self, "Error",
                    "Cannot delete customer with associated sales records.",
                    QMessageBox.Warning
                )
                return
            
            # Remove from list
            self.customers = [c for c in self.customers if c.get("id") != customer_id]
            
            # Save data
            success, error = DataManager.save_data(self.customers, DEFAULT_CUSTOMERS_FILE)
            if success:
                # Refresh table
                self.refresh_customers()
                show_message(self, "Success", "Customer deleted successfully")
            else:
                handle_data_error(self, "delete customer", error)
                # Restore the customer since delete failed
                self.customers = [c for c in self.customers] + [customer for customer in self.customers if customer.get("id") == customer_id]
    
    def record_customer_payment(self):
        """Record a payment for the selected customer"""
        customer_id = self.get_selected_customer_id()
        if not customer_id:
            show_message(self, "Error", "No customer selected", QMessageBox.Warning)
            return
        
        customer = self.get_customer_by_id(customer_id)
        if customer:
            dialog = PaymentRecordDialog(customer, self.user_data, self)
            if dialog.exec() == QDialog.Accepted:
                # Refresh the customer table to show updated balances
                self.refresh_customers()
    
    def view_customer_details(self):
        """View detailed customer information"""
        customer_id = self.get_selected_customer_id()
        if not customer_id:
            show_message(self, "Error", "No customer selected", QMessageBox.Warning)
            return
        
        customer = self.get_customer_by_id(customer_id)
        if customer:
            dialog = CustomerDetailsDialog(customer, self.sales_data, self)
            dialog.exec()
            # Refresh the customer table in case payments were recorded in the details dialog
            self.refresh_customers()
    
    def update_theme(self, theme):
        """Update the theme"""
        self.theme = theme
    
    def print_customer_report(self):
        """Print customer report"""
        try:
            if not self.customers:
                show_message(self, "No Data", "No customers available to print.", QMessageBox.Warning)
                return
            
            PrintManager.print_customer_report(self.customers, self)
        except Exception as e:
            show_message(self, "Print Error", f"Failed to print customer report: {str(e)}", QMessageBox.Critical)