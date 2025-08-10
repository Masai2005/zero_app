"""
Expenses window module for the application.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QLineEdit, QDoubleSpinBox,
    QFormLayout, QGroupBox, QMessageBox, QHeaderView, QDateEdit,
    QComboBox
)
from PySide6.QtCore import Qt, QDate
from datetime import datetime

from styles import StyleSheet, Theme, Colors
from utils import DataManager, format_currency, format_date, DEFAULT_EXPENSES_FILE, show_message, show_validation_error, handle_data_error
from validation import ExpenseValidator
from search_filter import SearchFilter, QuickSearchWidget, AdvancedSearchDialog


class ExpensesWindow(QWidget):
    """Expenses window widget"""
    
    def __init__(self, user_data, theme=Theme.LIGHT):
        super().__init__()
        self.user_data = user_data
        self.theme = theme
        
        # Load expense categories
        self.expense_categories = [
            "Rent", "Utilities", "Salaries", "Supplies", 
            "Marketing", "Maintenance", "Transport", "Other"
        ]
        
        # Load expenses data with error handling
        self.expenses, error = DataManager.load_data(DEFAULT_EXPENSES_FILE)
        if error:
            handle_data_error(self, "load expenses", error)
        
        self.setup_ui()
        
        # Initialize search filters
        self.current_filters = {}
        self.filtered_expenses = self.expenses.copy()
        
        self.refresh_expenses()
    
    def setup_ui(self):
        """Setup UI components"""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Left side - Expense form
        left_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Expenses")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        left_layout.addWidget(title)
        
        # Expense form
        expense_form = QGroupBox("New Expense")
        form_layout = QFormLayout()
        
        # Category
        self.category_combo = QComboBox()
        self.category_combo.addItems(self.expense_categories)
        form_layout.addRow("Category:", self.category_combo)
        
        # Amount
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setPrefix("$ ")
        self.amount_spin.setMinimum(0.01)
        self.amount_spin.setMaximum(100000.00)
        self.amount_spin.setValue(0.01)
        form_layout.addRow("Amount:", self.amount_spin)
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Date:", self.date_edit)
        
        # Details
        self.details_input = QLineEdit()
        self.details_input.setPlaceholderText("Enter expense details")
        form_layout.addRow("Details:", self.details_input)
        
        # Add expense button
        self.add_btn = QPushButton("Add Expense")
        self.add_btn.setMinimumWidth(120)
        self.add_btn.setMinimumHeight(35)
        self.add_btn.clicked.connect(self.add_expense)
        form_layout.addRow("", self.add_btn)
        
        expense_form.setLayout(form_layout)
        left_layout.addWidget(expense_form)
        
        # Add stretch to push everything to the top
        left_layout.addStretch()
        
        # Right side - Expenses list
        right_layout = QVBoxLayout()
        
        # Search section
        search_layout = QHBoxLayout()
        
        # Quick search widget
        self.quick_search = QuickSearchWidget("Search expenses...")
        self.quick_search.search_changed.connect(self.on_quick_search)
        self.quick_search.advanced_search_requested.connect(self.show_advanced_search)
        search_layout.addWidget(self.quick_search)
        
        right_layout.addLayout(search_layout)
        
        # Expenses table
        self.expenses_table = QTableWidget()
        self.expenses_table.setColumnCount(5)
        self.expenses_table.setHorizontalHeaderLabels(["Date", "Category", "Amount", "Details", "Added By"])
        self.expenses_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.expenses_table)
        
        # Delete button
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setMinimumWidth(140)
        self.delete_btn.setMinimumHeight(35)
        self.delete_btn.clicked.connect(self.delete_expense)
        right_layout.addWidget(self.delete_btn, alignment=Qt.AlignRight)
        
        # Total section
        total_layout = QHBoxLayout()
        total_layout.addWidget(QLabel("Total Expenses:"))
        self.total_label = QLabel("$0.00")
        self.total_label.setStyleSheet("font-weight: bold;")
        total_layout.addWidget(self.total_label)
        total_layout.addStretch()
        
        right_layout.addLayout(total_layout)
        
        # Add layouts to main layout
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        
        self.setLayout(main_layout)
    
    def add_expense(self):
        """Add a new expense with validation"""
        # Create expense object
        expense_data = {
            "id": DataManager.generate_id(),
            "category": self.category_combo.currentText(),
            "amount": self.amount_spin.value(),
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "details": self.details_input.text().strip(),
            "added_by": self.user_data.get("name"),
            "created_at": datetime.now().isoformat()
        }
        
        # Validate expense data
        is_valid, error_message = ExpenseValidator.validate_expense_data(expense_data)
        if not is_valid:
            show_message(self, "Validation Error", error_message, QMessageBox.Warning)
            return
        
        # Add to expenses list
        self.expenses.append(expense_data)
        
        # Save data
        success, error = DataManager.save_data(self.expenses, DEFAULT_EXPENSES_FILE)
        if success:
            # Reset form
            self.amount_spin.setValue(0.01)
            self.date_edit.setDate(QDate.currentDate())
            self.details_input.clear()
            
            # Refresh table
            self.refresh_expenses()
            
            show_message(self, "Success", "Expense added successfully")
        else:
            handle_data_error(self, "save expense", error)
            # Remove the expense from memory since save failed
            self.expenses.pop()
    
    def delete_expense(self):
        """Delete selected expense"""
        selected_row = self.expenses_table.currentRow()
        if selected_row < 0:
            show_message(self, "Error", "No expense selected", QMessageBox.Warning)
            return
        
        expense_id = self.expenses_table.item(selected_row, 0).data(Qt.UserRole)
        
        # Remove from list
        self.expenses = [expense for expense in self.expenses if expense.get("id") != expense_id]
        
        # Save data
        success, error = DataManager.save_data(self.expenses, DEFAULT_EXPENSES_FILE)
        if success:
            # Refresh table
            self.refresh_expenses()
            
            show_message(self, "Success", "Expense deleted successfully")
        else:
            handle_data_error(self, "delete expense", error)
            # Restore the expense since delete failed - would need original expense data
            # For now, just refresh to show current state
            self.refresh_expenses()
    
    def on_quick_search(self, search_text):
        """Handle quick search text change"""
        if search_text.strip():
            self.current_filters = {"text_search": search_text.strip()}
        else:
            self.current_filters = {}
        self.apply_filters()
    
    def apply_filters(self):
        """Apply current filters to expenses"""
        self.filtered_expenses = self.filter_expenses(self.expenses, self.current_filters)
        self.refresh_expenses()
    
    def filter_expenses(self, expenses, filters):
        """Filter expenses based on search criteria"""
        filtered = expenses.copy()
        
        # Text search
        if filters.get("text_search"):
            search_text = filters["text_search"].lower()
            filtered = [e for e in filtered if (
                search_text in e.get("category", "").lower() or
                search_text in e.get("details", "").lower() or
                search_text in e.get("added_by", "").lower() or
                search_text in str(e.get("amount", "")).lower()
            )]
        
        return filtered
    
    def refresh_expenses(self, expenses_to_display=None):
        """Refresh expenses table with filtered data"""
        # Use provided expenses or filtered expenses data
        if expenses_to_display is not None:
            expenses_to_show = expenses_to_display
        else:
            expenses_to_show = self.filtered_expenses if hasattr(self, 'filtered_expenses') else self.expenses
        
        # Sort expenses by date (newest first)
        sorted_expenses = sorted(expenses_to_show, key=lambda x: x.get("date", ""), reverse=True)
        
        self.expenses_table.setRowCount(len(sorted_expenses))
        
        total_amount = 0
        
        for row, expense in enumerate(sorted_expenses):
            # Store expense ID for reference
            date_item = QTableWidgetItem(expense.get("date"))
            date_item.setData(Qt.UserRole, expense.get("id"))
            self.expenses_table.setItem(row, 0, date_item)
            
            self.expenses_table.setItem(row, 1, QTableWidgetItem(expense.get("category")))
            
            amount = expense.get("amount", 0)
            total_amount += amount
            self.expenses_table.setItem(row, 2, QTableWidgetItem(format_currency(amount)))
            
            self.expenses_table.setItem(row, 3, QTableWidgetItem(expense.get("details")))
            self.expenses_table.setItem(row, 4, QTableWidgetItem(expense.get("added_by")))
        
        # Update total
        self.total_label.setText(format_currency(total_amount))
    
    def update_theme(self, theme):
        """Update the theme"""
        self.theme = theme
    
    def show_advanced_search(self):
        """Show advanced search dialog"""
        dialog = AdvancedSearchDialog("expenses", self)
        dialog.search_applied.connect(self.apply_advanced_search)
        dialog.exec()
    
    def apply_advanced_search(self, filters):
        """Apply advanced search filters"""
        expenses_data, error = DataManager.load_data("expenses.json")
        if error or not isinstance(expenses_data, list):
            expenses_data = []
        
        # Apply filters
        filtered_expenses = SearchFilter.filter_expenses(expenses_data, filters)
        
        # Update display
        self.refresh_expenses(filtered_expenses)