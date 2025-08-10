"""
Advanced search and filtering functionality for the ZERO Business Management System.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QDateEdit, QCheckBox, QGroupBox,
    QFormLayout, QDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QTabWidget, QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt, QDate, Signal
from datetime import datetime, timedelta
import json
import re
from typing import List, Dict, Any, Optional, Tuple

from utils import DataManager, format_currency, format_date, show_message


class SavedSearchManager:
    """Manager for saved search queries"""
    
    SAVED_SEARCHES_FILE = "saved_searches.json"
    
    @staticmethod
    def save_search(name: str, search_config: Dict[str, Any]) -> Tuple[bool, str]:
        """Save a search configuration"""
        try:
            saved_searches, error = DataManager.load_data(SavedSearchManager.SAVED_SEARCHES_FILE)
            if error or not isinstance(saved_searches, list):
                saved_searches = []
            
            # Check if name already exists
            for i, search in enumerate(saved_searches):
                if search.get("name") == name:
                    saved_searches[i] = {
                        "name": name,
                        "config": search_config,
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                    break
            else:
                # Add new search
                saved_searches.append({
                    "name": name,
                    "config": search_config,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                })
            
            success, save_error = DataManager.save_data(saved_searches, SavedSearchManager.SAVED_SEARCHES_FILE)
            return success, save_error if not success else ""
            
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def load_saved_searches() -> List[Dict[str, Any]]:
        """Load all saved searches"""
        try:
            saved_searches, error = DataManager.load_data(SavedSearchManager.SAVED_SEARCHES_FILE)
            if error or not isinstance(saved_searches, list):
                return []
            return saved_searches
        except Exception:
            return []
    
    @staticmethod
    def delete_saved_search(name: str) -> Tuple[bool, str]:
        """Delete a saved search"""
        try:
            saved_searches, error = DataManager.load_data(SavedSearchManager.SAVED_SEARCHES_FILE)
            if error or not isinstance(saved_searches, list):
                return False, error or "Invalid saved searches data"
            
            saved_searches = [s for s in saved_searches if s.get("name") != name]
            
            success, save_error = DataManager.save_data(saved_searches, SavedSearchManager.SAVED_SEARCHES_FILE)
            return success, save_error if not success else ""
            
        except Exception as e:
            return False, str(e)


class SearchFilter:
    """Advanced search and filtering functionality"""
    
    @staticmethod
    def filter_products(products: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Filter products based on search criteria"""
        filtered = products.copy()
        
        # Text search
        if filters.get("text_search"):
            search_text = filters["text_search"].lower()
            filtered = [p for p in filtered if (
                search_text in p.get("name", "").lower() or
                search_text in p.get("barcode", "").lower() or
                search_text in p.get("unit_type", "").lower()
            )]
        
        # Price range
        if filters.get("min_price") is not None:
            filtered = [p for p in filtered if p.get("selling_price", 0) >= filters["min_price"]]
        
        if filters.get("max_price") is not None:
            filtered = [p for p in filtered if p.get("selling_price", 0) <= filters["max_price"]]
        
        # Stock level
        if filters.get("min_stock") is not None:
            filtered = [p for p in filtered if p.get("quantity", 0) >= filters["min_stock"]]
        
        if filters.get("max_stock") is not None:
            filtered = [p for p in filtered if p.get("quantity", 0) <= filters["max_stock"]]
        
        # Unit type
        if filters.get("unit_type") and filters["unit_type"] != "All":
            filtered = [p for p in filtered if p.get("unit_type") == filters["unit_type"]]
        
        # Low stock filter
        if filters.get("low_stock_only"):
            filtered = [p for p in filtered if p.get("quantity", 0) <= p.get("minimum_quantity", 0)]
        
        # Expiry date range
        if filters.get("expiry_from") or filters.get("expiry_to"):
            expiry_filtered = []
            for p in filtered:
                expiry_date = p.get("expiry_date")
                if not expiry_date:
                    continue
                
                try:
                    product_expiry = datetime.fromisoformat(expiry_date.replace("T00:00:00", ""))
                    
                    if filters.get("expiry_from"):
                        if product_expiry < filters["expiry_from"]:
                            continue
                    
                    if filters.get("expiry_to"):
                        if product_expiry > filters["expiry_to"]:
                            continue
                    
                    expiry_filtered.append(p)
                except (ValueError, TypeError):
                    continue
            
            filtered = expiry_filtered
        
        # Sort results
        sort_by = filters.get("sort_by", "name")
        sort_order = filters.get("sort_order", "asc")
        
        if sort_by == "name":
            filtered.sort(key=lambda x: x.get("name", "").lower(), reverse=(sort_order == "desc"))
        elif sort_by == "price":
            filtered.sort(key=lambda x: x.get("selling_price", 0), reverse=(sort_order == "desc"))
        elif sort_by == "stock":
            filtered.sort(key=lambda x: x.get("quantity", 0), reverse=(sort_order == "desc"))
        elif sort_by == "created_at":
            filtered.sort(key=lambda x: x.get("created_at", ""), reverse=(sort_order == "desc"))
        
        return filtered
    
    @staticmethod
    def filter_customers(customers: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Filter customers based on search criteria"""
        filtered = customers.copy()
        
        # Text search
        if filters.get("text_search"):
            search_text = filters["text_search"].lower()
            filtered = [c for c in filtered if (
                search_text in c.get("first_name", "").lower() or
                search_text in c.get("last_name", "").lower() or
                search_text in c.get("middle_name", "").lower() or
                search_text in c.get("company_name", "").lower() or
                search_text in c.get("mobile", "").lower() or
                search_text in c.get("email", "").lower() or
                search_text in c.get("address", "").lower()
            )]
        
        # Registration date range
        if filters.get("date_from") or filters.get("date_to"):
            date_filtered = []
            for c in filtered:
                created_at = c.get("created_at")
                if not created_at:
                    continue
                
                try:
                    customer_date = datetime.fromisoformat(created_at)
                    
                    if filters.get("date_from"):
                        if customer_date.date() < filters["date_from"]:
                            continue
                    
                    if filters.get("date_to"):
                        if customer_date.date() > filters["date_to"]:
                            continue
                    
                    date_filtered.append(c)
                except (ValueError, TypeError):
                    continue
            
            filtered = date_filtered
        
        # Company filter
        if filters.get("has_company_only"):
            filtered = [c for c in filtered if c.get("company_name", "").strip()]
        
        # Contact method filter
        if filters.get("contact_method") and filters["contact_method"] != "All":
            if filters["contact_method"] == "Mobile":
                filtered = [c for c in filtered if c.get("mobile", "").strip()]
            elif filters["contact_method"] == "Email":
                filtered = [c for c in filtered if c.get("email", "").strip()]
            elif filters["contact_method"] == "WhatsApp":
                filtered = [c for c in filtered if c.get("whatsapp", "").strip()]
        
        # Sort results
        sort_by = filters.get("sort_by", "name")
        sort_order = filters.get("sort_order", "asc")
        
        if sort_by == "name":
            filtered.sort(key=lambda x: f"{x.get('first_name', '')} {x.get('last_name', '')}".lower(), 
                         reverse=(sort_order == "desc"))
        elif sort_by == "company":
            filtered.sort(key=lambda x: x.get("company_name", "").lower(), reverse=(sort_order == "desc"))
        elif sort_by == "created_at":
            filtered.sort(key=lambda x: x.get("created_at", ""), reverse=(sort_order == "desc"))
        
        return filtered
    
    @staticmethod
    def filter_sales(sales: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Filter sales based on search criteria"""
        filtered = sales.copy()
        
        # Text search
        if filters.get("text_search"):
            search_text = filters["text_search"].lower()
            filtered = [s for s in filtered if (
                search_text in s.get("invoice_number", "").lower() or
                search_text in s.get("customer_name", "").lower() or
                search_text in s.get("created_by", "").lower() or
                any(search_text in item.get("product_name", "").lower() for item in s.get("items", []))
            )]
        
        # Date range
        if filters.get("date_from") or filters.get("date_to"):
            date_filtered = []
            for s in filtered:
                created_at = s.get("created_at")
                if not created_at:
                    continue
                
                try:
                    sale_date = datetime.fromisoformat(created_at)
                    
                    if filters.get("date_from"):
                        if sale_date.date() < filters["date_from"]:
                            continue
                    
                    if filters.get("date_to"):
                        if sale_date.date() > filters["date_to"]:
                            continue
                    
                    date_filtered.append(s)
                except (ValueError, TypeError):
                    continue
            
            filtered = date_filtered
        
        # Amount range
        if filters.get("min_amount") is not None:
            filtered = [s for s in filtered if s.get("total", 0) >= filters["min_amount"]]
        
        if filters.get("max_amount") is not None:
            filtered = [s for s in filtered if s.get("total", 0) <= filters["max_amount"]]
        
        # Payment method
        if filters.get("payment_method") and filters["payment_method"] != "All":
            filtered = [s for s in filtered if s.get("payment_method") == filters["payment_method"]]
        
        # Customer type
        if filters.get("customer_type") and filters["customer_type"] != "All":
            if filters["customer_type"] == "Walk-in":
                filtered = [s for s in filtered if not s.get("customer_id")]
            elif filters["customer_type"] == "Registered":
                filtered = [s for s in filtered if s.get("customer_id")]
        
        # Created by (salesperson)
        if filters.get("created_by") and filters["created_by"] != "All":
            filtered = [s for s in filtered if s.get("created_by") == filters["created_by"]]
        
        # Sort results
        sort_by = filters.get("sort_by", "created_at")
        sort_order = filters.get("sort_order", "desc")
        
        if sort_by == "created_at":
            filtered.sort(key=lambda x: x.get("created_at", ""), reverse=(sort_order == "desc"))
        elif sort_by == "total":
            filtered.sort(key=lambda x: x.get("total", 0), reverse=(sort_order == "desc"))
        elif sort_by == "customer":
            filtered.sort(key=lambda x: x.get("customer_name", "").lower(), reverse=(sort_order == "desc"))
        elif sort_by == "invoice":
            filtered.sort(key=lambda x: x.get("invoice_number", "").lower(), reverse=(sort_order == "desc"))
        
        return filtered
    
    @staticmethod
    def filter_expenses(expenses: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Filter expenses based on search criteria"""
        filtered = expenses.copy()
        
        # Text search
        if filters.get("text_search"):
            search_text = filters["text_search"].lower()
            filtered = [e for e in filtered if (
                search_text in e.get("category", "").lower() or
                search_text in e.get("details", "").lower() or
                search_text in e.get("added_by", "").lower()
            )]
        
        # Date range
        if filters.get("date_from") or filters.get("date_to"):
            date_filtered = []
            for e in filtered:
                expense_date = e.get("date")
                if not expense_date:
                    continue
                
                try:
                    # Handle both string dates and date objects
                    if isinstance(expense_date, str):
                        expense_date_obj = datetime.fromisoformat(expense_date).date()
                    else:
                        expense_date_obj = expense_date
                    
                    if filters.get("date_from"):
                        if expense_date_obj < filters["date_from"]:
                            continue
                    
                    if filters.get("date_to"):
                        if expense_date_obj > filters["date_to"]:
                            continue
                    
                    date_filtered.append(e)
                except (ValueError, TypeError):
                    continue
            
            filtered = date_filtered
        
        # Amount range
        if filters.get("min_amount") is not None:
            filtered = [e for e in filtered if e.get("amount", 0) >= filters["min_amount"]]
        
        if filters.get("max_amount") is not None:
            filtered = [e for e in filtered if e.get("amount", 0) <= filters["max_amount"]]
        
        # Category filter
        if filters.get("category") and filters["category"] != "All":
            filtered = [e for e in filtered if e.get("category") == filters["category"]]
        
        # Added by filter
        if filters.get("added_by") and filters["added_by"] != "All":
            filtered = [e for e in filtered if e.get("added_by") == filters["added_by"]]
        
        # Sort results
        sort_by = filters.get("sort_by", "date")
        sort_order = filters.get("sort_order", "desc")
        
        if sort_by == "date":
            filtered.sort(key=lambda x: x.get("date", ""), reverse=(sort_order == "desc"))
        elif sort_by == "amount":
            filtered.sort(key=lambda x: x.get("amount", 0), reverse=(sort_order == "desc"))
        elif sort_by == "category":
            filtered.sort(key=lambda x: x.get("category", "").lower(), reverse=(sort_order == "desc"))
        elif sort_by == "details":
            filtered.sort(key=lambda x: x.get("details", "").lower(), reverse=(sort_order == "desc"))
        
        return filtered


class AdvancedSearchDialog(QDialog):
    """Dialog for advanced search and filtering"""
    
    search_applied = Signal(dict)  # Signal emitted when search is applied
    
    def __init__(self, search_type: str, parent=None):
        super().__init__(parent)
        self.search_type = search_type  # "products", "customers", or "sales"
        self.setWindowTitle(f"Advanced Search - {search_type.title()}")
        self.setMinimumSize(500, 600)
        
        self.setup_ui()
        self.load_saved_searches()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Saved searches section
        saved_group = QGroupBox("Saved Searches")
        saved_layout = QHBoxLayout()
        saved_layout.setSpacing(10)
        
        self.saved_combo = QComboBox()
        self.saved_combo.addItem("Select a saved search...", None)
        saved_layout.addWidget(self.saved_combo)
        
        self.load_search_btn = QPushButton("Load")
        self.load_search_btn.setMinimumWidth(80)
        self.load_search_btn.setMinimumHeight(35)
        self.load_search_btn.clicked.connect(self.load_saved_search)
        saved_layout.addWidget(self.load_search_btn)
        
        self.save_search_btn = QPushButton("Save Current")
        self.save_search_btn.setMinimumWidth(120)
        self.save_search_btn.setMinimumHeight(35)
        self.save_search_btn.clicked.connect(self.save_current_search)
        saved_layout.addWidget(self.save_search_btn)
        
        self.delete_search_btn = QPushButton("Delete")
        self.delete_search_btn.setMinimumWidth(80)
        self.delete_search_btn.setMinimumHeight(35)
        self.delete_search_btn.clicked.connect(self.delete_saved_search)
        saved_layout.addWidget(self.delete_search_btn)
        
        saved_group.setLayout(saved_layout)
        layout.addWidget(saved_group)
        
        # Search criteria tabs
        self.tabs = QTabWidget()
        
        # Basic search tab
        self.basic_tab = self.create_basic_search_tab()
        self.tabs.addTab(self.basic_tab, "Basic Search")
        
        # Advanced filters tab
        self.advanced_tab = self.create_advanced_filters_tab()
        self.tabs.addTab(self.advanced_tab, "Advanced Filters")
        
        # Sorting tab
        self.sorting_tab = self.create_sorting_tab()
        self.tabs.addTab(self.sorting_tab, "Sorting")
        
        layout.addWidget(self.tabs)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setMinimumWidth(100)
        self.clear_btn.setMinimumHeight(35)
        self.clear_btn.clicked.connect(self.clear_all_filters)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.setMinimumHeight(35)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.apply_btn = QPushButton("Apply Search")
        self.apply_btn.setMinimumWidth(120)
        self.apply_btn.setMinimumHeight(35)
        self.apply_btn.clicked.connect(self.apply_search)
        self.apply_btn.setStyleSheet("background-color: #007bff; color: white;")
        button_layout.addWidget(self.apply_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_basic_search_tab(self):
        """Create basic search tab"""
        tab = QWidget()
        layout = QFormLayout()
        
        # Text search
        self.text_search_input = QLineEdit()
        self.text_search_input.setPlaceholderText("Search in names, descriptions, etc...")
        layout.addRow("Text Search:", self.text_search_input)
        
        if self.search_type == "products":
            # Unit type filter
            self.unit_filter = QComboBox()
            self.unit_filter.addItems(["All", "Each", "Box", "Kg", "Liter", "Pair", "Set"])
            layout.addRow("Unit Type:", self.unit_filter)
            
            # Low stock only
            self.low_stock_check = QCheckBox("Show only low stock items")
            layout.addRow("", self.low_stock_check)
        
        elif self.search_type == "customers":
            # Contact method filter
            self.contact_filter = QComboBox()
            self.contact_filter.addItems(["All", "Mobile", "Email", "WhatsApp"])
            layout.addRow("Has Contact Method:", self.contact_filter)
            
            # Company filter
            self.company_check = QCheckBox("Has company information")
            layout.addRow("", self.company_check)
        
        elif self.search_type == "sales":
            # Payment method filter
            self.payment_filter = QComboBox()
            self.payment_filter.addItems(["All", "Cash", "Credit Card", "Credit (Account)"])
            layout.addRow("Payment Method:", self.payment_filter)
            
            # Customer type filter
            self.customer_type_filter = QComboBox()
            self.customer_type_filter.addItems(["All", "Walk-in", "Registered"])
            layout.addRow("Customer Type:", self.customer_type_filter)
        
        elif self.search_type == "expenses":
            # Category filter
            self.category_filter = QComboBox()
            self.category_filter.addItems([
                "All", "Office Supplies", "Utilities", "Rent", "Marketing", 
                "Travel", "Equipment", "Software", "Training", "Other"
            ])
            layout.addRow("Category:", self.category_filter)
            
            # Added by filter
            self.added_by_filter = QComboBox()
            self.added_by_filter.addItem("All", "All")
            # This would need to be populated with actual users
            layout.addRow("Added By:", self.added_by_filter)
        
        tab.setLayout(layout)
        return tab
    
    def create_advanced_filters_tab(self):
        """Create advanced filters tab"""
        tab = QWidget()
        layout = QFormLayout()
        
        if self.search_type == "products":
            # Price range
            price_layout = QHBoxLayout()
            self.min_price_spin = QDoubleSpinBox()
            self.min_price_spin.setPrefix("$")
            self.min_price_spin.setMaximum(999999.99)
            price_layout.addWidget(self.min_price_spin)
            
            price_layout.addWidget(QLabel("to"))
            
            self.max_price_spin = QDoubleSpinBox()
            self.max_price_spin.setPrefix("$")
            self.max_price_spin.setMaximum(999999.99)
            self.max_price_spin.setValue(999999.99)
            price_layout.addWidget(self.max_price_spin)
            
            price_widget = QWidget()
            price_widget.setLayout(price_layout)
            layout.addRow("Price Range:", price_widget)
            
            # Stock range
            stock_layout = QHBoxLayout()
            self.min_stock_spin = QSpinBox()
            self.min_stock_spin.setMaximum(999999)
            stock_layout.addWidget(self.min_stock_spin)
            
            stock_layout.addWidget(QLabel("to"))
            
            self.max_stock_spin = QSpinBox()
            self.max_stock_spin.setMaximum(999999)
            self.max_stock_spin.setValue(999999)
            stock_layout.addWidget(self.max_stock_spin)
            
            stock_widget = QWidget()
            stock_widget.setLayout(stock_layout)
            layout.addRow("Stock Range:", stock_widget)
            
            # Expiry date range
            expiry_layout = QHBoxLayout()
            self.expiry_from_date = QDateEdit()
            self.expiry_from_date.setCalendarPopup(True)
            self.expiry_from_date.setDate(QDate.currentDate())
            expiry_layout.addWidget(self.expiry_from_date)
            
            expiry_layout.addWidget(QLabel("to"))
            
            self.expiry_to_date = QDateEdit()
            self.expiry_to_date.setCalendarPopup(True)
            self.expiry_to_date.setDate(QDate.currentDate().addYears(2))
            expiry_layout.addWidget(self.expiry_to_date)
            
            expiry_widget = QWidget()
            expiry_widget.setLayout(expiry_layout)
            layout.addRow("Expiry Date Range:", expiry_widget)
        
        elif self.search_type == "customers":
            # Registration date range
            date_layout = QHBoxLayout()
            self.date_from = QDateEdit()
            self.date_from.setCalendarPopup(True)
            self.date_from.setDate(QDate.currentDate().addYears(-1))
            date_layout.addWidget(self.date_from)
            
            date_layout.addWidget(QLabel("to"))
            
            self.date_to = QDateEdit()
            self.date_to.setCalendarPopup(True)
            self.date_to.setDate(QDate.currentDate())
            date_layout.addWidget(self.date_to)
            
            date_widget = QWidget()
            date_widget.setLayout(date_layout)
            layout.addRow("Registration Date:", date_widget)
        
        elif self.search_type == "sales":
            # Date range
            date_layout = QHBoxLayout()
            self.date_from = QDateEdit()
            self.date_from.setCalendarPopup(True)
            self.date_from.setDate(QDate.currentDate().addDays(-30))
            date_layout.addWidget(self.date_from)
            
            date_layout.addWidget(QLabel("to"))
            
            self.date_to = QDateEdit()
            self.date_to.setCalendarPopup(True)
            self.date_to.setDate(QDate.currentDate())
            date_layout.addWidget(self.date_to)
            
            date_widget = QWidget()
            date_widget.setLayout(date_layout)
            layout.addRow("Sale Date:", date_widget)
            
            # Amount range
            amount_layout = QHBoxLayout()
            self.min_amount_spin = QDoubleSpinBox()
            self.min_amount_spin.setPrefix("$")
            self.min_amount_spin.setMaximum(999999.99)
            amount_layout.addWidget(self.min_amount_spin)
            
            amount_layout.addWidget(QLabel("to"))
            
            self.max_amount_spin = QDoubleSpinBox()
            self.max_amount_spin.setPrefix("$")
            self.max_amount_spin.setMaximum(999999.99)
            self.max_amount_spin.setValue(999999.99)
            amount_layout.addWidget(self.max_amount_spin)
            
            amount_widget = QWidget()
            amount_widget.setLayout(amount_layout)
            layout.addRow("Amount Range:", amount_widget)
            
            # Created by filter
            self.created_by_filter = QComboBox()
            self.created_by_filter.addItem("All", "All")
            # Load users for filter - this would need to be populated from user data
            layout.addRow("Created By:", self.created_by_filter)
        
        elif self.search_type == "expenses":
            # Date range
            date_layout = QHBoxLayout()
            self.date_from = QDateEdit()
            self.date_from.setCalendarPopup(True)
            self.date_from.setDate(QDate.currentDate().addDays(-30))
            date_layout.addWidget(self.date_from)
            
            date_layout.addWidget(QLabel("to"))
            
            self.date_to = QDateEdit()
            self.date_to.setCalendarPopup(True)
            self.date_to.setDate(QDate.currentDate())
            date_layout.addWidget(self.date_to)
            
            date_widget = QWidget()
            date_widget.setLayout(date_layout)
            layout.addRow("Expense Date:", date_widget)
            
            # Amount range
            amount_layout = QHBoxLayout()
            self.min_amount_spin = QDoubleSpinBox()
            self.min_amount_spin.setPrefix("$")
            self.min_amount_spin.setMaximum(999999.99)
            amount_layout.addWidget(self.min_amount_spin)
            
            amount_layout.addWidget(QLabel("to"))
            
            self.max_amount_spin = QDoubleSpinBox()
            self.max_amount_spin.setPrefix("$")
            self.max_amount_spin.setMaximum(999999.99)
            self.max_amount_spin.setValue(999999.99)
            amount_layout.addWidget(self.max_amount_spin)
            
            amount_widget = QWidget()
            amount_widget.setLayout(amount_layout)
            layout.addRow("Amount Range:", amount_widget)
        
        tab.setLayout(layout)
        return tab
    
    def create_sorting_tab(self):
        """Create sorting options tab"""
        tab = QWidget()
        layout = QFormLayout()
        
        # Sort by
        self.sort_by_combo = QComboBox()
        if self.search_type == "products":
            self.sort_by_combo.addItems(["name", "price", "stock", "created_at"])
        elif self.search_type == "customers":
            self.sort_by_combo.addItems(["name", "company", "created_at"])
        elif self.search_type == "sales":
            self.sort_by_combo.addItems(["created_at", "total", "customer", "invoice"])
        elif self.search_type == "expenses":
            self.sort_by_combo.addItems(["date", "amount", "category", "details"])
        
        layout.addRow("Sort By:", self.sort_by_combo)
        
        # Sort order
        self.sort_order_combo = QComboBox()
        self.sort_order_combo.addItems(["Ascending", "Descending"])
        layout.addRow("Sort Order:", self.sort_order_combo)
        
        tab.setLayout(layout)
        return tab
    
    def get_search_filters(self) -> Dict[str, Any]:
        """Get current search filters"""
        filters = {}
        
        # Basic search
        if self.text_search_input.text().strip():
            filters["text_search"] = self.text_search_input.text().strip()
        
        if self.search_type == "products":
            if self.unit_filter.currentText() != "All":
                filters["unit_type"] = self.unit_filter.currentText()
            
            if self.low_stock_check.isChecked():
                filters["low_stock_only"] = True
            
            # Advanced filters
            if self.min_price_spin.value() > 0:
                filters["min_price"] = self.min_price_spin.value()
            
            if self.max_price_spin.value() < 999999.99:
                filters["max_price"] = self.max_price_spin.value()
            
            if self.min_stock_spin.value() > 0:
                filters["min_stock"] = self.min_stock_spin.value()
            
            if self.max_stock_spin.value() < 999999:
                filters["max_stock"] = self.max_stock_spin.value()
            
            # Expiry date filters
            filters["expiry_from"] = self.expiry_from_date.date().toPython()
            filters["expiry_to"] = self.expiry_to_date.date().toPython()
        
        elif self.search_type == "customers":
            if self.contact_filter.currentText() != "All":
                filters["contact_method"] = self.contact_filter.currentText()
            
            if self.company_check.isChecked():
                filters["has_company_only"] = True
            
            # Date range
            filters["date_from"] = self.date_from.date().toPython()
            filters["date_to"] = self.date_to.date().toPython()
        
        elif self.search_type == "sales":
            if self.payment_filter.currentText() != "All":
                filters["payment_method"] = self.payment_filter.currentText()
            
            if self.customer_type_filter.currentText() != "All":
                filters["customer_type"] = self.customer_type_filter.currentText()
            
            # Date range
            filters["date_from"] = self.date_from.date().toPython()
            filters["date_to"] = self.date_to.date().toPython()
            
            # Amount range
            if self.min_amount_spin.value() > 0:
                filters["min_amount"] = self.min_amount_spin.value()
            
            if self.max_amount_spin.value() < 999999.99:
                filters["max_amount"] = self.max_amount_spin.value()
            
            if self.created_by_filter.currentData() != "All":
                filters["created_by"] = self.created_by_filter.currentData()
        
        elif self.search_type == "expenses":
            if self.category_filter.currentText() != "All":
                filters["category"] = self.category_filter.currentText()
            
            if self.added_by_filter.currentData() != "All":
                filters["added_by"] = self.added_by_filter.currentData()
            
            # Date range
            filters["date_from"] = self.date_from.date().toPython()
            filters["date_to"] = self.date_to.date().toPython()
            
            # Amount range
            if self.min_amount_spin.value() > 0:
                filters["min_amount"] = self.min_amount_spin.value()
            
            if self.max_amount_spin.value() < 999999.99:
                filters["max_amount"] = self.max_amount_spin.value()
        
        # Sorting
        filters["sort_by"] = self.sort_by_combo.currentText()
        filters["sort_order"] = "asc" if self.sort_order_combo.currentText() == "Ascending" else "desc"
        
        return filters
    
    def apply_search(self):
        """Apply the search filters"""
        filters = self.get_search_filters()
        self.search_applied.emit(filters)
        self.accept()
    
    def clear_all_filters(self):
        """Clear all filter inputs"""
        self.text_search_input.clear()
        
        if self.search_type == "products":
            self.unit_filter.setCurrentIndex(0)
            self.low_stock_check.setChecked(False)
            self.min_price_spin.setValue(0)
            self.max_price_spin.setValue(999999.99)
            self.min_stock_spin.setValue(0)
            self.max_stock_spin.setValue(999999)
            self.expiry_from_date.setDate(QDate.currentDate())
            self.expiry_to_date.setDate(QDate.currentDate().addYears(2))
        
        elif self.search_type == "customers":
            self.contact_filter.setCurrentIndex(0)
            self.company_check.setChecked(False)
            self.date_from.setDate(QDate.currentDate().addYears(-1))
            self.date_to.setDate(QDate.currentDate())
        
        elif self.search_type == "sales":
            self.payment_filter.setCurrentIndex(0)
            self.customer_type_filter.setCurrentIndex(0)
            self.date_from.setDate(QDate.currentDate().addDays(-30))
            self.date_to.setDate(QDate.currentDate())
            self.min_amount_spin.setValue(0)
            self.max_amount_spin.setValue(999999.99)
            self.created_by_filter.setCurrentIndex(0)
        
        elif self.search_type == "expenses":
            self.category_filter.setCurrentIndex(0)
            self.added_by_filter.setCurrentIndex(0)
            self.date_from.setDate(QDate.currentDate().addDays(-30))
            self.date_to.setDate(QDate.currentDate())
            self.min_amount_spin.setValue(0)
            self.max_amount_spin.setValue(999999.99)
        
        self.sort_by_combo.setCurrentIndex(0)
        self.sort_order_combo.setCurrentIndex(0)
    
    def load_saved_searches(self):
        """Load saved searches into combo box"""
        self.saved_combo.clear()
        self.saved_combo.addItem("Select a saved search...", None)
        
        saved_searches = SavedSearchManager.load_saved_searches()
        for search in saved_searches:
            if search.get("config", {}).get("search_type") == self.search_type:
                self.saved_combo.addItem(search.get("name", "Unnamed"), search)
    
    def load_saved_search(self):
        """Load a saved search configuration"""
        current_data = self.saved_combo.currentData()
        if not current_data:
            return
        
        config = current_data.get("config", {})
        self.apply_config(config)
    
    def apply_config(self, config: Dict[str, Any]):
        """Apply a search configuration to the UI"""
        # Clear current filters first
        self.clear_all_filters()
        
        # Apply basic search
        if config.get("text_search"):
            self.text_search_input.setText(config["text_search"])
        
        if self.search_type == "products":
            if config.get("unit_type"):
                index = self.unit_filter.findText(config["unit_type"])
                if index >= 0:
                    self.unit_filter.setCurrentIndex(index)
            
            if config.get("low_stock_only"):
                self.low_stock_check.setChecked(True)
            
            if config.get("min_price") is not None:
                self.min_price_spin.setValue(config["min_price"])
            
            if config.get("max_price") is not None:
                self.max_price_spin.setValue(config["max_price"])
            
            if config.get("min_stock") is not None:
                self.min_stock_spin.setValue(config["min_stock"])
            
            if config.get("max_stock") is not None:
                self.max_stock_spin.setValue(config["max_stock"])
        
        # Apply sorting
        if config.get("sort_by"):
            index = self.sort_by_combo.findText(config["sort_by"])
            if index >= 0:
                self.sort_by_combo.setCurrentIndex(index)
        
        if config.get("sort_order"):
            order_text = "Ascending" if config["sort_order"] == "asc" else "Descending"
            index = self.sort_order_combo.findText(order_text)
            if index >= 0:
                self.sort_order_combo.setCurrentIndex(index)
    
    def save_current_search(self):
        """Save current search configuration"""
        from PySide6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(self, "Save Search", "Enter a name for this search:")
        if ok and name.strip():
            config = self.get_search_filters()
            config["search_type"] = self.search_type
            
            success, error = SavedSearchManager.save_search(name.strip(), config)
            if success:
                show_message(self, "Success", "Search saved successfully")
                self.load_saved_searches()
            else:
                show_message(self, "Error", f"Failed to save search: {error}", QMessageBox.Critical)
    
    def delete_saved_search(self):
        """Delete the selected saved search"""
        current_data = self.saved_combo.currentData()
        if not current_data:
            show_message(self, "Error", "No search selected", QMessageBox.Warning)
            return
        
        name = current_data.get("name", "")
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the saved search '{name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            success, error = SavedSearchManager.delete_saved_search(name)
            if success:
                show_message(self, "Success", "Search deleted successfully")
                self.load_saved_searches()
            else:
                show_message(self, "Error", f"Failed to delete search: {error}", QMessageBox.Critical)


class QuickSearchWidget(QWidget):
    """Quick search widget for embedding in main windows"""
    
    search_changed = Signal(str)  # Signal emitted when search text changes
    advanced_search_requested = Signal()  # Signal emitted when advanced search is requested
    
    def __init__(self, placeholder_text="Search...", parent=None):
        super().__init__(parent)
        self.setup_ui(placeholder_text)
    
    def setup_ui(self, placeholder_text):
        """Setup UI components"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(placeholder_text)
        self.search_input.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self.search_input)
        
        # Advanced search button
        self.advanced_btn = QPushButton("Advanced")
        self.advanced_btn.clicked.connect(self.advanced_search_requested.emit)
        self.advanced_btn.setMinimumWidth(100)
        self.advanced_btn.setMaximumWidth(120)
        self.advanced_btn.setMinimumHeight(30)
        layout.addWidget(self.advanced_btn)
        
        # Clear button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_search)
        self.clear_btn.setMaximumWidth(70)
        self.clear_btn.setMinimumHeight(30)
        layout.addWidget(self.clear_btn)
        
        self.setLayout(layout)
    
    def clear_search(self):
        """Clear the search input"""
        self.search_input.clear()
    
    def get_search_text(self) -> str:
        """Get current search text"""
        return self.search_input.text().strip()
    
    def set_search_text(self, text: str):
        """Set search text"""
        self.search_input.setText(text)