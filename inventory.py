"""
Inventory management module for the application.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QLineEdit, QFormLayout, 
    QGroupBox, QMessageBox, QHeaderView, QDialog, QDateEdit,
    QComboBox, QDoubleSpinBox, QSpinBox, QTabWidget
)
from PySide6.QtCore import Qt, QDate
from datetime import datetime

from styles import StyleSheet, Theme
from utils import DataManager, format_currency, format_date, DEFAULT_PRODUCTS_FILE, DEFAULT_MOVEMENTS_FILE, show_message, show_validation_error, handle_data_error
from validation import ProductValidator
from barcode_utils import BarcodeGenerator, BarcodeDisplayWidget
from search_filter import SearchFilter, AdvancedSearchDialog, QuickSearchWidget
from print_utils import PrintManager


class ProductDialog(QDialog):
    """Dialog for adding/editing products"""
    
    def __init__(self, parent=None, product_data=None):
        super().__init__(parent)
        self.product_data = product_data  # None for new product, dict for editing
        
        if product_data:
            self.setWindowTitle("Edit Product")
        else:
            self.setWindowTitle("Add New Product")
        
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Form layout for inputs
        form_layout = QFormLayout()
        
        # Product name field
        self.name_input = QLineEdit()
        form_layout.addRow("Product Name:", self.name_input)
        
        # Barcode field with generation
        barcode_layout = QHBoxLayout()
        self.barcode_input = QLineEdit()
        self.barcode_input.textChanged.connect(self.on_barcode_changed)
        barcode_layout.addWidget(self.barcode_input)
        
        # Generate barcode button
        self.generate_barcode_btn = QPushButton("Generate")
        self.generate_barcode_btn.setMaximumWidth(90)
        self.generate_barcode_btn.setMinimumHeight(30)
        self.generate_barcode_btn.clicked.connect(self.generate_barcode)
        self.generate_barcode_btn.setToolTip("Generate a new barcode")
        barcode_layout.addWidget(self.generate_barcode_btn)
        
        barcode_widget = QWidget()
        barcode_widget.setLayout(barcode_layout)
        form_layout.addRow("Barcode ID:", barcode_widget)
        
        # Buying price field
        self.buying_price_spin = QDoubleSpinBox()
        self.buying_price_spin.setPrefix("$ ")
        self.buying_price_spin.setMaximum(100000.00)
        form_layout.addRow("Buying Price:", self.buying_price_spin)
        
        # Selling price field
        self.selling_price_spin = QDoubleSpinBox()
        self.selling_price_spin.setPrefix("$ ")
        self.selling_price_spin.setMaximum(100000.00)
        form_layout.addRow("Selling Price:", self.selling_price_spin)
        
        # Current quantity field
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMaximum(100000)
        form_layout.addRow("Current Quantity:", self.quantity_spin)
        
        # Minimum quantity field
        self.min_quantity_spin = QSpinBox()
        self.min_quantity_spin.setMaximum(100000)
        form_layout.addRow("Minimum Quantity:", self.min_quantity_spin)
        
        # Unit field
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["Each", "Box", "Kg", "Liter", "Pair", "Set"])
        form_layout.addRow("Unit:", self.unit_combo)
        
        # Expiry date field
        self.expiry_date_edit = QDateEdit()
        self.expiry_date_edit.setCalendarPopup(True)
        self.expiry_date_edit.setDate(QDate.currentDate().addMonths(6))
        form_layout.addRow("Expiry Date:", self.expiry_date_edit)
        
        layout.addLayout(form_layout)
        
        # Barcode display widget
        self.barcode_display = BarcodeDisplayWidget()
        layout.addWidget(self.barcode_display)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.setMinimumWidth(100)
        self.save_button.setMinimumHeight(35)
        self.save_button.clicked.connect(self.save_product)
        
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
        
        # Pre-fill form if editing
        if self.product_data:
            self.name_input.setText(self.product_data.get("name", ""))
            self.barcode_input.setText(self.product_data.get("barcode", ""))
            self.buying_price_spin.setValue(self.product_data.get("buying_price", 0))
            self.selling_price_spin.setValue(self.product_data.get("selling_price", 0))
            self.quantity_spin.setValue(self.product_data.get("quantity", 0))
            self.min_quantity_spin.setValue(self.product_data.get("min_quantity", 0))
            
            # Set unit
            unit_index = self.unit_combo.findText(self.product_data.get("unit", "Each"))
            if unit_index >= 0:
                self.unit_combo.setCurrentIndex(unit_index)
            
            # Set expiry date
            if self.product_data.get("expiry_date"):
                try:
                    expiry_date = datetime.fromisoformat(self.product_data.get("expiry_date"))
                    self.expiry_date_edit.setDate(QDate(expiry_date.year, expiry_date.month, expiry_date.day))
                except (ValueError, TypeError):
                    pass
        
        # Update barcode display if barcode exists
        if self.product_data and self.product_data.get("barcode"):
            self.barcode_display.display_barcode(self.product_data.get("barcode"))
    
    def generate_barcode(self):
        """Generate a new barcode for the product"""
        import time
        import random
        
        # Generate a unique barcode based on timestamp and random number
        timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
        random_part = str(random.randint(100000, 999999))
        new_barcode = f"{timestamp}{random_part}"
        
        # Set the barcode in the input field
        self.barcode_input.setText(new_barcode)
        
        # Display the generated barcode
        self.barcode_display.display_barcode(new_barcode)
        
        show_message(self, "Barcode Generated", f"New barcode generated: {new_barcode}")
    
    def on_barcode_changed(self, barcode_text):
        """Update barcode display when barcode text changes"""
        if barcode_text.strip():
            self.barcode_display.display_barcode(barcode_text.strip())
    
    def save_product(self):
        """Save product data with validation"""
        # Create product object
        product_data = {
            "id": self.product_data.get("id") if self.product_data else DataManager.generate_id(),
            "name": self.name_input.text().strip(),
            "barcode": self.barcode_input.text().strip(),
            "buying_price": self.buying_price_spin.value(),
            "selling_price": self.selling_price_spin.value(),
            "quantity": self.quantity_spin.value(),
            "min_quantity": self.min_quantity_spin.value(),
            "unit": self.unit_combo.currentText(),
            "expiry_date": self.expiry_date_edit.date().toString("yyyy-MM-dd"),
            "updated_at": datetime.now().isoformat()
        }
        
        # Preserve created_at if editing
        if self.product_data and "created_at" in self.product_data:
            product_data["created_at"] = self.product_data["created_at"]
        else:
            product_data["created_at"] = datetime.now().isoformat()
        
        # Validate product data
        is_valid, error_message = ProductValidator.validate_product_data(product_data)
        if not is_valid:
            show_message(self, "Validation Error", error_message, QMessageBox.Warning)
            return
        
        self.product_data = product_data
        self.accept()


class InventoryMovementDialog(QDialog):
    """Dialog for recording inventory movements (in/out)"""
    
    def __init__(self, product_data, user_data, parent=None):
        super().__init__(parent)
        self.product_data = product_data
        self.user_data = user_data
        
        self.setWindowTitle(f"Inventory Movement - {product_data.get('name', '')}")
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Product info section
        info_layout = QFormLayout()
        info_layout.addRow("Product:", QLabel(self.product_data.get("name", "")))
        info_layout.addRow("Current Stock:", QLabel(f"{self.product_data.get('quantity', 0)} {self.product_data.get('unit_type', 'Each')}"))
        layout.addLayout(info_layout)
        
        # Movement form
        movement_group = QGroupBox("Record Movement")
        form_layout = QFormLayout()
        
        # Movement type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Stock In", "Stock Out", "Adjustment", "Transfer", "Damaged", "Expired"])
        form_layout.addRow("Type:", self.type_combo)
        
        # Quantity
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(100000)
        form_layout.addRow("Quantity:", self.quantity_spin)
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Date:", self.date_edit)
        
        # Reason/details
        self.reason_input = QLineEdit()
        self.reason_input.setPlaceholderText("Enter reason for movement")
        form_layout.addRow("Reason:", self.reason_input)
        
        # Reference (optional)
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Reference number (optional)")
        form_layout.addRow("Reference:", self.reference_input)
        
        movement_group.setLayout(form_layout)
        layout.addWidget(movement_group)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.setMinimumWidth(100)
        self.save_button.setMinimumHeight(35)
        self.save_button.clicked.connect(self.save_movement)
        
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
    
    def save_movement(self):
        """Save inventory movement with complete tracking"""
        quantity = self.quantity_spin.value()
        movement_type = self.type_combo.currentText()
        reason = self.reason_input.text().strip()
        reference = self.reference_input.text().strip()
        
        if quantity <= 0:
            show_message(self, "Error", "Quantity must be greater than 0", QMessageBox.Warning)
            return
        
        if not reason:
            show_message(self, "Error", "Please provide a reason for the movement", QMessageBox.Warning)
            return
        
        # Check if enough stock for outbound movements
        if movement_type in ["Stock Out", "Transfer", "Damaged", "Expired"] and self.product_data.get("quantity", 0) < quantity:
            show_message(self, "Error", "Not enough stock available", QMessageBox.Warning)
            return
        
        # Calculate new quantity based on movement type
        current_quantity = self.product_data.get("quantity", 0)
        if movement_type in ["Stock In"]:
            self.new_quantity = current_quantity + quantity
        elif movement_type in ["Stock Out", "Transfer", "Damaged", "Expired"]:
            self.new_quantity = current_quantity - quantity
        elif movement_type == "Adjustment":
            # For adjustments, the quantity field represents the new total quantity
            self.new_quantity = quantity
            # Calculate the actual movement amount
            quantity = quantity - current_quantity
        
        # Create movement record with complete tracking
        self.movement_data = {
            "id": DataManager.generate_id(),
            "product_id": self.product_data.get("id"),
            "product_name": self.product_data.get("name"),
            "product_barcode": self.product_data.get("barcode"),
            "movement_type": movement_type,
            "quantity": quantity,
            "unit_type": self.product_data.get("unit_type", "Each"),
            "previous_quantity": current_quantity,
            "new_quantity": self.new_quantity,
            "movement_date": self.date_edit.date().toString("yyyy-MM-dd"),
            "reason": reason,
            "reference": reference,
            "user_id": self.user_data.get("username"),
            "user_name": self.user_data.get("name"),
            "created_at": datetime.now().isoformat()
        }
        
        self.accept()


class InventoryWindow(QWidget):
    """Inventory management window widget"""
    
    def __init__(self, user_data, theme=Theme.LIGHT):
        super().__init__()
        self.user_data = user_data
        self.theme = theme
        
        # Load products data with error handling
        self.products, error = DataManager.load_data(DEFAULT_PRODUCTS_FILE)
        if error:
            handle_data_error(self, "load products", error)
        
        # Load movements data with error handling
        self.movements, movements_error = DataManager.load_data(DEFAULT_MOVEMENTS_FILE)
        if movements_error:
            handle_data_error(self, "load movements", movements_error)
        
        self.setup_ui()
        
        # Initialize search filters
        self.current_filters = {}
        self.filtered_products = self.products.copy()
        
        self.refresh_products()
        self.refresh_movements()
    
    def setup_ui(self):
        """Setup UI components"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Title
        title = QLabel("Inventory Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Products tab
        self.products_tab = QWidget()
        products_layout = QVBoxLayout()
        
        # Search and add section
        search_layout = QHBoxLayout()
        
        # Quick search widget
        self.quick_search = QuickSearchWidget("Search products...")
        self.quick_search.search_changed.connect(self.on_quick_search)
        self.quick_search.advanced_search_requested.connect(self.show_advanced_search)
        search_layout.addWidget(self.quick_search)
        
        # Add product button
        self.add_product_btn = QPushButton("Add New Product")
        self.add_product_btn.setMinimumWidth(150)
        self.add_product_btn.setMinimumHeight(35)
        self.add_product_btn.clicked.connect(self.add_product)
        search_layout.addWidget(self.add_product_btn)
        
        products_layout.addLayout(search_layout)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(7)
        self.products_table.setHorizontalHeaderLabels([
            "Product Name", "Barcode", "Stock", "Min Stock", "Buy Price", "Sell Price", "Expiry Date"
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setSelectionMode(QTableWidget.SingleSelection)
        products_layout.addWidget(self.products_table)
        
        # Button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Edit product button
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setMinimumWidth(80)
        self.edit_btn.setMinimumHeight(35)
        self.edit_btn.clicked.connect(self.edit_product)
        button_layout.addWidget(self.edit_btn)
        
        # Delete product button
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setMinimumWidth(80)
        self.delete_btn.setMinimumHeight(35)
        self.delete_btn.clicked.connect(self.delete_product)
        button_layout.addWidget(self.delete_btn)
        
        # Record movement button
        self.movement_btn = QPushButton("Record Movement")
        self.movement_btn.setMinimumWidth(140)
        self.movement_btn.setMinimumHeight(35)
        self.movement_btn.clicked.connect(self.record_movement)
        button_layout.addWidget(self.movement_btn)
        
        # Print inventory report button
        self.print_report_btn = QPushButton("Print Inventory Report")
        self.print_report_btn.setMinimumWidth(170)
        self.print_report_btn.setMinimumHeight(35)
        self.print_report_btn.clicked.connect(self.print_inventory_report)
        button_layout.addWidget(self.print_report_btn)

        button_layout.addStretch()
        
        products_layout.addLayout(button_layout)
        self.products_tab.setLayout(products_layout)
        
        # Movements tab
        self.movements_tab = QWidget()
        movements_layout = QVBoxLayout()
        
        # Movements filter section
        filter_layout = QHBoxLayout()
        
        # Date range filter
        filter_layout.addWidget(QLabel("From:"))
        self.from_date_filter = QDateEdit()
        self.from_date_filter.setDate(QDate.currentDate().addDays(-30))
        self.from_date_filter.setCalendarPopup(True)
        self.from_date_filter.dateChanged.connect(self.refresh_movements)
        filter_layout.addWidget(self.from_date_filter)
        
        filter_layout.addWidget(QLabel("To:"))
        self.to_date_filter = QDateEdit()
        self.to_date_filter.setDate(QDate.currentDate())
        self.to_date_filter.setCalendarPopup(True)
        self.to_date_filter.dateChanged.connect(self.refresh_movements)
        filter_layout.addWidget(self.to_date_filter)
        
        # Product filter
        filter_layout.addWidget(QLabel("Product:"))
        self.product_filter = QComboBox()
        self.product_filter.addItem("All Products", "")
        for product in self.products:
            self.product_filter.addItem(product.get("name", ""), product.get("id"))
        self.product_filter.currentTextChanged.connect(self.refresh_movements)
        filter_layout.addWidget(self.product_filter)
        
        # Movement type filter
        filter_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Types", "Stock In", "Stock Out", "Adjustment", "Transfer", "Damaged", "Expired"])
        self.type_filter.currentTextChanged.connect(self.refresh_movements)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addStretch()
        movements_layout.addLayout(filter_layout)
        
        # Movements table
        self.movements_table = QTableWidget()
        self.movements_table.setColumnCount(9)
        self.movements_table.setHorizontalHeaderLabels([
            "Date", "Product", "Type", "Quantity", "Previous", "New", "Reason", "Reference", "User"
        ])
        self.movements_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        movements_layout.addWidget(self.movements_table)
        
        # Movement analytics section
        analytics_group = QGroupBox("Movement Analytics")
        analytics_layout = QHBoxLayout()
        
        self.total_movements_label = QLabel("Total Movements: 0")
        analytics_layout.addWidget(self.total_movements_label)
        
        self.stock_in_label = QLabel("Stock In: 0")
        analytics_layout.addWidget(self.stock_in_label)
        
        self.stock_out_label = QLabel("Stock Out: 0")
        analytics_layout.addWidget(self.stock_out_label)
        
        analytics_layout.addStretch()
        analytics_group.setLayout(analytics_layout)
        movements_layout.addWidget(analytics_group)
        
        self.movements_tab.setLayout(movements_layout)
        
        # Add tabs to tab widget
        self.tabs.addTab(self.products_tab, "Products")
        self.tabs.addTab(self.movements_tab, "Movement History")
        
        main_layout.addWidget(self.tabs)
        
        self.setLayout(main_layout)
    
    def refresh_products(self):
        """Refresh products table with filtered data"""
        products_to_show = self.filtered_products if hasattr(self, 'filtered_products') else self.products
        self.products_table.setRowCount(len(products_to_show))
        
        for row, product in enumerate(products_to_show):
            # Store product ID for reference
            name_item = QTableWidgetItem(product.get("name", ""))
            name_item.setData(Qt.UserRole, product.get("id"))
            self.products_table.setItem(row, 0, name_item)
            
            # Barcode
            self.products_table.setItem(row, 1, QTableWidgetItem(product.get("barcode", "")))
            
            # Stock
            quantity = product.get("quantity", 0)
            unit = product.get("unit", "Each")
            self.products_table.setItem(row, 2, QTableWidgetItem(f"{quantity} {unit}"))
            
            # Min stock
            self.products_table.setItem(row, 3, QTableWidgetItem(str(product.get("min_quantity", 0))))
            
            # Buy price
            self.products_table.setItem(row, 4, QTableWidgetItem(format_currency(product.get("buying_price", 0))))
            
            # Sell price
            self.products_table.setItem(row, 5, QTableWidgetItem(format_currency(product.get("selling_price", 0))))
            
            # Expiry date
            self.products_table.setItem(row, 6, QTableWidgetItem(product.get("expiry_date", "")))
    
    def on_quick_search(self, search_text):
        """Handle quick search text change"""
        if search_text.strip():
            self.current_filters = {"text_search": search_text.strip()}
        else:
            self.current_filters = {}
        self.apply_filters()
    
    def show_advanced_search(self):
        """Show advanced search dialog"""
        dialog = AdvancedSearchDialog("products", self)
        
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
        """Apply current filters to products"""
        self.filtered_products = SearchFilter.filter_products(self.products, self.current_filters)
        self.refresh_products()
    
    def filter_products(self):
        """Legacy method - kept for compatibility"""
        # This method is now handled by the new search system
        pass
    
    def get_selected_product_id(self):
        """Get the ID of the selected product"""
        selected_row = self.products_table.currentRow()
        if selected_row >= 0:
            return self.products_table.item(selected_row, 0).data(Qt.UserRole)
        return None
    
    def get_product_by_id(self, product_id):
        """Get product data by ID"""
        for product in self.products:
            if product.get("id") == product_id:
                return product
        return None
    
    def add_product(self):
        """Add a new product"""
        dialog = ProductDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # Add new product to data
            new_product = dialog.product_data
            self.products.append(new_product)
            
            # Save data
            success, error = DataManager.save_data(self.products, DEFAULT_PRODUCTS_FILE)
            if success:
                # Refresh table
                self.refresh_products()
                show_message(self, "Success", "Product added successfully")
            else:
                handle_data_error(self, "save product data", error)
                # Remove the product from memory since save failed
                self.products.pop()
    
    def edit_product(self):
        """Edit selected product"""
        product_id = self.get_selected_product_id()
        if not product_id:
            show_message(self, "Error", "No product selected", QMessageBox.Warning)
            return
        
        product = self.get_product_by_id(product_id)
        if not product:
            return
        
        dialog = ProductDialog(self, product)
        if dialog.exec() == QDialog.Accepted:
            # Update product in list
            updated_product = dialog.product_data
            
            for i, p in enumerate(self.products):
                if p.get("id") == product_id:
                    self.products[i] = updated_product
                    break
            
            # Save data
            success, error = DataManager.save_data(self.products, DEFAULT_PRODUCTS_FILE)
            if success:
                # Refresh table
                self.refresh_products()
                show_message(self, "Success", "Product updated successfully")
            else:
                handle_data_error(self, "update product", error)
                # Restore original data since save failed
                for i, p in enumerate(self.products):
                    if p.get("id") == product_id:
                        self.products[i] = product
                        break
    
    def delete_product(self):
        """Delete selected product"""
        product_id = self.get_selected_product_id()
        if not product_id:
            show_message(self, "Error", "No product selected", QMessageBox.Warning)
            return
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this product?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Remove product from list
            self.products = [p for p in self.products if p.get("id") != product_id]
            
            # Save data
            success, error = DataManager.save_data(self.products, DEFAULT_PRODUCTS_FILE)
            if success:
                # Refresh table
                self.refresh_products()
                show_message(self, "Success", "Product deleted successfully")
            else:
                handle_data_error(self, "delete product", error)
                # Restore the product since delete failed - this would need the original product data
                # For now, just refresh to show current state
                self.refresh_products()
    
    def record_movement(self):
        """Record inventory movement for selected product"""
        product_id = self.get_selected_product_id()
        if not product_id:
            show_message(self, "Error", "No product selected", QMessageBox.Warning)
            return
        
        product = self.get_product_by_id(product_id)
        if not product:
            return
        
        dialog = InventoryMovementDialog(product, self.user_data, self)
        if dialog.exec() == QDialog.Accepted:
            # Save movement record first
            self.movements.append(dialog.movement_data)
            movements_success, movements_error = DataManager.save_data(self.movements, DEFAULT_MOVEMENTS_FILE)
            
            if not movements_success:
                handle_data_error(self, "save movement record", movements_error)
                self.movements.pop()  # Remove from memory since save failed
                return
            
            # Update product quantity
            for i, p in enumerate(self.products):
                if p.get("id") == product_id:
                    self.products[i]["quantity"] = dialog.new_quantity
                    self.products[i]["updated_at"] = datetime.now().isoformat()
                    break
            
            # Save updated product data
            products_success, products_error = DataManager.save_data(self.products, DEFAULT_PRODUCTS_FILE)
            if products_success:
                # Refresh both tables
                self.refresh_products()
                self.refresh_movements()
                show_message(self, "Success", "Inventory movement recorded successfully")
            else:
                handle_data_error(self, "update inventory", products_error)
                # Restore original quantity since save failed
                for i, p in enumerate(self.products):
                    if p.get("id") == product_id:
                        self.products[i]["quantity"] = product["quantity"]
                        break
    
    def refresh_movements(self):
        """Refresh movements table with filtering and analytics"""
        # Get filter values
        from_date = self.from_date_filter.date().toPython()
        to_date = self.to_date_filter.date().toPython()
        selected_product_id = self.product_filter.currentData()
        selected_type = self.type_filter.currentText()
        
        # Filter movements
        filtered_movements = []
        for movement in self.movements:
            # Date filter
            try:
                movement_date = datetime.fromisoformat(movement.get("movement_date", "")).date()
                if not (from_date <= movement_date <= to_date):
                    continue
            except (ValueError, TypeError):
                continue
            
            # Product filter
            if selected_product_id and movement.get("product_id") != selected_product_id:
                continue
            
            # Type filter
            if selected_type != "All Types" and movement.get("movement_type") != selected_type:
                continue
            
            filtered_movements.append(movement)
        
        # Sort by date (newest first)
        filtered_movements.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Populate table
        self.movements_table.setRowCount(len(filtered_movements))
        
        for row, movement in enumerate(filtered_movements):
            # Date
            self.movements_table.setItem(row, 0, QTableWidgetItem(movement.get("movement_date", "")))
            
            # Product
            self.movements_table.setItem(row, 1, QTableWidgetItem(movement.get("product_name", "")))
            
            # Type
            self.movements_table.setItem(row, 2, QTableWidgetItem(movement.get("movement_type", "")))
            
            # Quantity
            quantity = movement.get("quantity", 0)
            unit = movement.get("unit_type", "Each")
            quantity_text = f"{quantity:+} {unit}" if movement.get("movement_type") in ["Stock Out", "Transfer", "Damaged", "Expired"] else f"+{quantity} {unit}"
            self.movements_table.setItem(row, 3, QTableWidgetItem(quantity_text))
            
            # Previous quantity
            self.movements_table.setItem(row, 4, QTableWidgetItem(str(movement.get("previous_quantity", 0))))
            
            # New quantity
            self.movements_table.setItem(row, 5, QTableWidgetItem(str(movement.get("new_quantity", 0))))
            
            # Reason
            self.movements_table.setItem(row, 6, QTableWidgetItem(movement.get("reason", "")))
            
            # Reference
            self.movements_table.setItem(row, 7, QTableWidgetItem(movement.get("reference", "")))
            
            # User
            self.movements_table.setItem(row, 8, QTableWidgetItem(movement.get("user_name", "")))
        
        # Update analytics
        self.update_movement_analytics(filtered_movements)
    
    def update_movement_analytics(self, movements):
        """Update movement analytics labels"""
        total_movements = len(movements)
        stock_in_count = len([m for m in movements if m.get("movement_type") == "Stock In"])
        stock_out_count = len([m for m in movements if m.get("movement_type") in ["Stock Out", "Transfer", "Damaged", "Expired"]])
        
        self.total_movements_label.setText(f"Total Movements: {total_movements}")
        self.stock_in_label.setText(f"Stock In: {stock_in_count}")
        self.stock_out_label.setText(f"Stock Out: {stock_out_count}")
    
    def print_inventory_report(self):
        """Print inventory report"""
        try:
            if not self.products:
                show_message(self, "No Data", "No products available to print.", QMessageBox.Warning)
                return
            
            PrintManager.print_inventory_report(self.products, self)
        except Exception as e:
            show_message(self, "Print Error", f"Failed to print inventory report: {str(e)}", QMessageBox.Critical)
    
    def update_theme(self, theme):
        """Update the theme"""
        self.theme = theme