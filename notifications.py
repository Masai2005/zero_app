"""
Notifications window module for the application.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QCheckBox, QSpinBox, QComboBox, QGroupBox, QDialog,
    QDialogButtonBox, QFormLayout, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from datetime import datetime, timedelta
from typing import Dict, List, Any

from styles import StyleSheet, Theme, Colors
from utils import DataManager, DEFAULT_PRODUCTS_FILE, DEFAULT_NOTIFICATIONS_FILE, format_date, handle_data_error, show_message


class NotificationRule:
    """Represents a business rule for generating notifications"""
    
    def __init__(self, rule_id: str, name: str, rule_type: str, condition: Dict[str, Any], 
                 message_template: str, priority: str = "medium", enabled: bool = True):
        self.rule_id = rule_id
        self.name = name
        self.rule_type = rule_type  # 'inventory', 'expiry', 'trend', 'custom'
        self.condition = condition
        self.message_template = message_template
        self.priority = priority  # 'low', 'medium', 'high', 'critical'
        self.enabled = enabled
        self.created_at = datetime.now().isoformat()


class NotificationManager:
    """Manages notification generation, persistence, and user preferences"""
    
    @staticmethod
    def get_default_rules() -> List[NotificationRule]:
        """Get default notification rules"""
        return [
            NotificationRule(
                "low_stock", "Low Stock Alert", "inventory",
                {"threshold_type": "min_quantity", "operator": "<="},
                "Product '{product_name}' is running low (Current: {current_qty}, Min: {min_qty})",
                "high"
            ),
            NotificationRule(
                "out_of_stock", "Out of Stock Alert", "inventory", 
                {"threshold_type": "quantity", "operator": "==", "value": 0},
                "Product '{product_name}' is out of stock",
                "critical"
            ),
            NotificationRule(
                "expiring_soon", "Expiring Soon Alert", "expiry",
                {"days_threshold": 7, "operator": "<="},
                "Product '{product_name}' expires in {days_left} days (Expiry: {expiry_date})",
                "medium"
            ),
            NotificationRule(
                "expired", "Expired Product Alert", "expiry",
                {"days_threshold": 0, "operator": "<"},
                "Product '{product_name}' has expired (Expired: {days_overdue} days ago)",
                "critical"
            ),
            NotificationRule(
                "sales_trend_down", "Sales Declining Alert", "trend",
                {"trend_direction": "down", "change_threshold": -20},
                "Product '{product_name}' sales are declining ({change_percent}% change)",
                "medium"
            )
        ]
    
    @staticmethod
    def generate_notifications(user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate notifications based on business rules and user preferences"""
        try:
            # Load existing notifications
            notifications, error = DataManager.load_data(DEFAULT_NOTIFICATIONS_FILE)
            if error:
                DataManager.logger.error(f"Failed to load notifications: {error}")
                notifications = []
            
            # Load user preferences
            preferences = NotificationManager.get_user_preferences(user_data.get("username", ""))
            
            # Load business rules
            rules = NotificationManager.get_notification_rules()
            
            # Generate new notifications
            new_notifications = []
            
            # Generate inventory notifications
            inventory_notifications = NotificationManager._generate_inventory_notifications(rules, preferences)
            new_notifications.extend(inventory_notifications)
            
            # Generate expiry notifications
            expiry_notifications = NotificationManager._generate_expiry_notifications(rules, preferences)
            new_notifications.extend(expiry_notifications)
            
            # Generate trend notifications
            trend_notifications = NotificationManager._generate_trend_notifications(rules, preferences)
            new_notifications.extend(trend_notifications)
            
            # Filter out duplicates and add to existing notifications
            existing_keys = {f"{n.get('type')}_{n.get('reference_id')}" for n in notifications}
            
            for notification in new_notifications:
                notification_key = f"{notification.get('type')}_{notification.get('reference_id')}"
                if notification_key not in existing_keys:
                    notification["id"] = DataManager.generate_id()
                    notification["user_id"] = user_data.get("username", "")
                    notification["created_at"] = datetime.now().isoformat()
                    notification["read"] = False
                    notifications.append(notification)
            
            # Clean up old notifications (older than 30 days)
            cutoff_date = datetime.now() - timedelta(days=30)
            notifications = [n for n in notifications if datetime.fromisoformat(n.get("created_at", "")) > cutoff_date]
            
            # Save updated notifications
            success, save_error = DataManager.save_data(notifications, DEFAULT_NOTIFICATIONS_FILE)
            if not success:
                DataManager.logger.error(f"Failed to save notifications: {save_error}")
            
            return notifications
            
        except Exception as e:
            DataManager.logger.error(f"Error generating notifications: {e}")
            return []
    
    @staticmethod
    def generate_notifications_for_all_users() -> bool:
        """Generate notifications for all users in the system"""
        try:
            # Load all users
            users, error = DataManager.load_data("users.json")
            if error:
                DataManager.logger.error(f"Failed to load users: {error}")
                return False
            
            # Generate notifications for each user
            for user in users:
                user_data = {
                    "username": user.get("username", ""),
                    "role": user.get("role", "salesman")
                }
                NotificationManager.generate_notifications(user_data)
            
            DataManager.logger.info("Notifications generated for all users")
            return True
            
        except Exception as e:
            DataManager.logger.error(f"Error generating notifications for all users: {e}")
            return False
    
    @staticmethod
    def _generate_inventory_notifications(rules: List[NotificationRule], preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate inventory-related notifications"""
        notifications = []
        
        if not preferences.get("inventory_alerts", True):
            return notifications
        
        try:
            products, error = DataManager.load_data(DEFAULT_PRODUCTS_FILE)
            if error:
                return notifications
            
            inventory_rules = [r for r in rules if r.rule_type == "inventory" and r.enabled]
            
            for product in products:
                product_id = product.get("id")
                product_name = product.get("name", "Unknown")
                current_qty = product.get("quantity", 0)
                min_qty = product.get("minimum_quantity", 0)
                
                for rule in inventory_rules:
                    condition = rule.condition
                    should_notify = False
                    
                    if rule.rule_id == "low_stock":
                        should_notify = current_qty <= min_qty and current_qty > 0
                    elif rule.rule_id == "out_of_stock":
                        should_notify = current_qty == 0
                    
                    if should_notify:
                        message = rule.message_template.format(
                            product_name=product_name,
                            current_qty=current_qty,
                            min_qty=min_qty
                        )
                        
                        notifications.append({
                            "type": "inventory",
                            "rule_id": rule.rule_id,
                            "reference_id": product_id,
                            "title": rule.name,
                            "message": message,
                            "priority": rule.priority,
                            "data": {
                                "product_id": product_id,
                                "product_name": product_name,
                                "current_quantity": current_qty,
                                "min_quantity": min_qty
                            }
                        })
        
        except Exception as e:
            DataManager.logger.error(f"Error generating inventory notifications: {e}")
        
        return notifications
    
    @staticmethod
    def _generate_expiry_notifications(rules: List[NotificationRule], preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate expiry-related notifications"""
        notifications = []
        
        if not preferences.get("expiry_alerts", True):
            return notifications
        
        try:
            products, error = DataManager.load_data(DEFAULT_PRODUCTS_FILE)
            if error:
                return notifications
            
            expiry_rules = [r for r in rules if r.rule_type == "expiry" and r.enabled]
            now = datetime.now()
            
            for product in products:
                expiry_date_str = product.get("expiry_date")
                if not expiry_date_str:
                    continue
                
                try:
                    expiry_date = datetime.fromisoformat(expiry_date_str)
                    days_left = (expiry_date - now).days
                    
                    product_id = product.get("id")
                    product_name = product.get("name", "Unknown")
                    
                    for rule in expiry_rules:
                        condition = rule.condition
                        should_notify = False
                        
                        if rule.rule_id == "expiring_soon":
                            threshold = condition.get("days_threshold", 7)
                            should_notify = 0 <= days_left <= threshold
                        elif rule.rule_id == "expired":
                            should_notify = days_left < 0
                        
                        if should_notify:
                            if days_left >= 0:
                                message = rule.message_template.format(
                                    product_name=product_name,
                                    days_left=days_left,
                                    expiry_date=format_date(expiry_date_str)
                                )
                            else:
                                message = rule.message_template.format(
                                    product_name=product_name,
                                    days_overdue=abs(days_left)
                                )
                            
                            notifications.append({
                                "type": "expiry",
                                "rule_id": rule.rule_id,
                                "reference_id": product_id,
                                "title": rule.name,
                                "message": message,
                                "priority": rule.priority,
                                "data": {
                                    "product_id": product_id,
                                    "product_name": product_name,
                                    "expiry_date": expiry_date_str,
                                    "days_left": days_left
                                }
                            })
                
                except (ValueError, TypeError):
                    continue
        
        except Exception as e:
            DataManager.logger.error(f"Error generating expiry notifications: {e}")
        
        return notifications
    
    @staticmethod
    def _generate_trend_notifications(rules: List[NotificationRule], preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate trend-related notifications"""
        notifications = []
        
        if not preferences.get("trend_alerts", True):
            return notifications
        
        try:
            # Trend analysis functionality removed - return empty list
            return notifications
            
            for product_id, trend_info in trends_data.items():
                product_name = trend_info.get("product_name", "Unknown")
                trend_direction = trend_info.get("trend_direction", "stable")
                change_percent = trend_info.get("quantity_change_percent", 0)
                
                for rule in trend_rules:
                    condition = rule.condition
                    should_notify = False
                    
                    if rule.rule_id == "sales_trend_down":
                        threshold = condition.get("change_threshold", -20)
                        should_notify = (trend_direction == "down" and change_percent <= threshold)
                    
                    if should_notify:
                        message = rule.message_template.format(
                            product_name=product_name,
                            change_percent=f"{change_percent:+.1f}"
                        )
                        
                        notifications.append({
                            "type": "trend",
                            "rule_id": rule.rule_id,
                            "reference_id": product_id,
                            "title": rule.name,
                            "message": message,
                            "priority": rule.priority,
                            "data": {
                                "product_id": product_id,
                                "product_name": product_name,
                                "trend_direction": trend_direction,
                                "change_percent": change_percent
                            }
                        })
        
        except Exception as e:
            DataManager.logger.error(f"Error generating trend notifications: {e}")
        
        return notifications
    
    @staticmethod
    def get_notification_rules() -> List[NotificationRule]:
        """Get notification rules from settings or return defaults"""
        try:
            # Try to load custom rules from settings
            settings_file = "notification_rules.json"
            rules_data, error = DataManager.load_data(settings_file)
            
            if error or not rules_data:
                # Return default rules
                return NotificationManager.get_default_rules()
            
            # Convert data to NotificationRule objects
            rules = []
            for rule_data in rules_data:
                rule = NotificationRule(
                    rule_data.get("rule_id"),
                    rule_data.get("name"),
                    rule_data.get("rule_type"),
                    rule_data.get("condition", {}),
                    rule_data.get("message_template"),
                    rule_data.get("priority", "medium"),
                    rule_data.get("enabled", True)
                )
                rules.append(rule)
            
            return rules
            
        except Exception as e:
            DataManager.logger.error(f"Error loading notification rules: {e}")
            return NotificationManager.get_default_rules()
    
    @staticmethod
    def get_user_preferences(username: str) -> Dict[str, Any]:
        """Get notification preferences for a user"""
        try:
            prefs_file = "notification_preferences.json"
            prefs_data, error = DataManager.load_data(prefs_file)
            
            if error or not prefs_data:
                prefs_data = {}
            
            # Return user preferences or defaults
            return prefs_data.get(username, {
                "inventory_alerts": True,
                "expiry_alerts": True,
                "trend_alerts": True,
                "priority_filter": "all",  # 'all', 'high', 'critical'
                "auto_refresh": True,
                "refresh_interval": 300  # 5 minutes
            })
            
        except Exception as e:
            DataManager.logger.error(f"Error loading user preferences: {e}")
            return {
                "inventory_alerts": True,
                "expiry_alerts": True,
                "trend_alerts": True,
                "priority_filter": "all",
                "auto_refresh": True,
                "refresh_interval": 300
            }
    
    @staticmethod
    def save_user_preferences(username: str, preferences: Dict[str, Any]) -> bool:
        """Save notification preferences for a user"""
        try:
            prefs_file = "notification_preferences.json"
            prefs_data, error = DataManager.load_data(prefs_file)
            
            if error:
                prefs_data = {}
            
            prefs_data[username] = preferences
            
            success, save_error = DataManager.save_data(prefs_data, prefs_file)
            if success:
                DataManager.logger.info(f"Notification preferences saved for user {username}")
                return True
            else:
                DataManager.logger.error(f"Failed to save preferences: {save_error}")
                return False
                
        except Exception as e:
            DataManager.logger.error(f"Error saving user preferences: {e}")
            return False
    
    @staticmethod
    def mark_notification_read(notification_id: str) -> bool:
        """Mark a notification as read"""
        try:
            notifications, error = DataManager.load_data(DEFAULT_NOTIFICATIONS_FILE)
            if error:
                return False
            
            for notification in notifications:
                if notification.get("id") == notification_id:
                    notification["read"] = True
                    notification["read_at"] = datetime.now().isoformat()
                    break
            
            success, save_error = DataManager.save_data(notifications, DEFAULT_NOTIFICATIONS_FILE)
            if success:
                DataManager.logger.info(f"Notification {notification_id} marked as read")
                return True
            else:
                DataManager.logger.error(f"Failed to mark notification as read: {save_error}")
                return False
                
        except Exception as e:
            DataManager.logger.error(f"Error marking notification as read: {e}")
            return False
    
    @staticmethod
    def mark_all_read(user_id: str) -> bool:
        """Mark all notifications as read for a user"""
        try:
            notifications, error = DataManager.load_data(DEFAULT_NOTIFICATIONS_FILE)
            if error:
                return False
            
            for notification in notifications:
                if notification.get("user_id") == user_id and not notification.get("read", False):
                    notification["read"] = True
                    notification["read_at"] = datetime.now().isoformat()
            
            success, save_error = DataManager.save_data(notifications, DEFAULT_NOTIFICATIONS_FILE)
            if success:
                DataManager.logger.info(f"All notifications marked as read for user {user_id}")
                return True
            else:
                DataManager.logger.error(f"Failed to mark all notifications as read: {save_error}")
                return False
                
        except Exception as e:
            DataManager.logger.error(f"Error marking all notifications as read: {e}")
            return False
    
    @staticmethod
    def get_user_notifications(user_id: str, include_read: bool = True) -> List[Dict[str, Any]]:
        """Get notifications for a specific user"""
        try:
            notifications, error = DataManager.load_data(DEFAULT_NOTIFICATIONS_FILE)
            if error:
                return []
            
            user_notifications = []
            for notification in notifications:
                if notification.get("user_id") == user_id:
                    if include_read or not notification.get("read", False):
                        user_notifications.append(notification)
            
            # Sort by creation date (newest first)
            user_notifications.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return user_notifications
            
        except Exception as e:
            DataManager.logger.error(f"Error getting user notifications: {e}")
            return []


class NotificationRuleDialog(QDialog):
    """Dialog for managing notification rules"""
    
    def __init__(self, parent, rule=None):
        super().__init__(parent)
        self.rule = rule
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the rule dialog UI"""
        self.setWindowTitle("Notification Rule" if not self.rule else "Edit Notification Rule")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # Basic Information
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        if self.rule:
            self.name_edit.setText(self.rule.name)
        basic_layout.addRow("Rule Name:", self.name_edit)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["inventory", "expiry", "trend", "custom"])
        if self.rule:
            index = self.type_combo.findText(self.rule.rule_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        basic_layout.addRow("Rule Type:", self.type_combo)
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["low", "medium", "high", "critical"])
        if self.rule:
            index = self.priority_combo.findText(self.rule.priority)
            if index >= 0:
                self.priority_combo.setCurrentIndex(index)
        basic_layout.addRow("Priority:", self.priority_combo)
        
        self.enabled_check = QCheckBox("Enabled")
        self.enabled_check.setChecked(True if not self.rule else self.rule.enabled)
        basic_layout.addRow(self.enabled_check)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Message Template
        message_group = QGroupBox("Message Template")
        message_layout = QVBoxLayout()
        
        self.message_edit = QLineEdit()
        if self.rule:
            self.message_edit.setText(self.rule.message_template)
        else:
            self.message_edit.setText("Product '{product_name}' requires attention")
        message_layout.addWidget(self.message_edit)
        
        help_label = QLabel("Available placeholders: {product_name}, {current_qty}, {min_qty}, {days_left}, {change_percent}")
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: gray; font-size: 10px;")
        message_layout.addWidget(help_label)
        
        message_group.setLayout(message_layout)
        layout.addWidget(message_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_rule_data(self):
        """Get the rule data from the dialog"""
        return {
            "name": self.name_edit.text(),
            "rule_type": self.type_combo.currentText(),
            "priority": self.priority_combo.currentText(),
            "enabled": self.enabled_check.isChecked(),
            "message_template": self.message_edit.text(),
            "condition": {}  # Basic condition, can be enhanced
        }


class NotificationPreferencesDialog(QDialog):
    """Dialog for managing notification preferences"""
    
    def __init__(self, parent, user_data, current_preferences):
        super().__init__(parent)
        self.user_data = user_data
        self.preferences = current_preferences.copy()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the preferences dialog UI"""
        self.setWindowTitle("Notification Preferences")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        
        # Alert Types Group
        alert_group = QGroupBox("Alert Types")
        alert_layout = QVBoxLayout()
        
        self.inventory_check = QCheckBox("Inventory Alerts")
        self.inventory_check.setChecked(self.preferences.get("inventory_alerts", True))
        alert_layout.addWidget(self.inventory_check)
        
        self.expiry_check = QCheckBox("Expiry Alerts")
        self.expiry_check.setChecked(self.preferences.get("expiry_alerts", True))
        alert_layout.addWidget(self.expiry_check)
        
        self.trend_check = QCheckBox("Trend Alerts")
        self.trend_check.setChecked(self.preferences.get("trend_alerts", True))
        alert_layout.addWidget(self.trend_check)
        
        alert_group.setLayout(alert_layout)
        layout.addWidget(alert_group)
        
        # Priority Filter Group
        priority_group = QGroupBox("Priority Filter")
        priority_layout = QFormLayout()
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["All", "Medium and Above", "High and Above", "Critical Only"])
        
        priority_map = {"all": 0, "medium": 1, "high": 2, "critical": 3}
        current_priority = self.preferences.get("priority_filter", "all")
        self.priority_combo.setCurrentIndex(priority_map.get(current_priority, 0))
        
        priority_layout.addRow("Show notifications:", self.priority_combo)
        priority_group.setLayout(priority_layout)
        layout.addWidget(priority_group)
        
        # Auto Refresh Group
        refresh_group = QGroupBox("Auto Refresh")
        refresh_layout = QFormLayout()
        
        self.auto_refresh_check = QCheckBox("Enable auto refresh")
        self.auto_refresh_check.setChecked(self.preferences.get("auto_refresh", True))
        refresh_layout.addRow(self.auto_refresh_check)
        
        self.refresh_interval_spin = QSpinBox()
        self.refresh_interval_spin.setRange(60, 3600)  # 1 minute to 1 hour
        self.refresh_interval_spin.setValue(self.preferences.get("refresh_interval", 300))
        self.refresh_interval_spin.setSuffix(" seconds")
        refresh_layout.addRow("Refresh interval:", self.refresh_interval_spin)
        
        refresh_group.setLayout(refresh_layout)
        layout.addWidget(refresh_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_preferences(self):
        """Get the updated preferences"""
        priority_map = {0: "all", 1: "medium", 2: "high", 3: "critical"}
        
        return {
            "inventory_alerts": self.inventory_check.isChecked(),
            "expiry_alerts": self.expiry_check.isChecked(),
            "trend_alerts": self.trend_check.isChecked(),
            "priority_filter": priority_map[self.priority_combo.currentIndex()],
            "auto_refresh": self.auto_refresh_check.isChecked(),
            "refresh_interval": self.refresh_interval_spin.value()
        }


class NotificationsWindow(QWidget):
    """Advanced notifications window widget with persistence and preferences"""
    
    def __init__(self, user_data, theme=Theme.LIGHT):
        super().__init__()
        self.user_data = user_data
        self.theme = theme
        self.preferences = NotificationManager.get_user_preferences(user_data.get("username", ""))
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh_notifications)
        
        # Load data with error handling
        self.products, products_error = DataManager.load_data(DEFAULT_PRODUCTS_FILE)
        if products_error:
            handle_data_error(self, "load products", products_error)
        
        self.setup_ui()
        self.refresh_notifications()
        self.setup_auto_refresh()
    
    def setup_ui(self):
        """Setup UI components"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header with title and controls
        header_layout = QHBoxLayout()
        
        title = QLabel("Notifications")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Unread count label
        self.unread_label = QLabel("Unread: 0")
        self.unread_label.setStyleSheet("font-weight: bold; color: red;")
        header_layout.addWidget(self.unread_label)
        
        # Mark all read button
        mark_all_btn = QPushButton("Mark All Read")
        mark_all_btn.setMinimumWidth(120)
        mark_all_btn.setMinimumHeight(35)
        mark_all_btn.clicked.connect(self.mark_all_read)
        header_layout.addWidget(mark_all_btn)
        
        # Preferences button
        prefs_btn = QPushButton("Preferences")
        prefs_btn.setMinimumWidth(100)
        prefs_btn.setMinimumHeight(35)
        prefs_btn.clicked.connect(self.show_preferences)
        header_layout.addWidget(prefs_btn)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setMinimumWidth(80)
        refresh_btn.setMinimumHeight(35)
        refresh_btn.clicked.connect(self.refresh_notifications)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # All Notifications tab
        self.all_tab = QWidget()
        all_layout = QVBoxLayout()
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Show:"))
        self.show_filter = QComboBox()
        self.show_filter.addItems(["All", "Unread Only", "Read Only"])
        self.show_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.show_filter)
        
        filter_layout.addWidget(QLabel("Priority:"))
        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["All", "Critical", "High", "Medium", "Low"])
        self.priority_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.priority_filter)
        
        filter_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", "Inventory", "Expiry", "Trend"])
        self.type_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addStretch()
        all_layout.addLayout(filter_layout)
        
        # All notifications table
        self.all_table = QTableWidget()
        self.all_table.setColumnCount(6)
        self.all_table.setHorizontalHeaderLabels(["", "Priority", "Type", "Title", "Message", "Created"])
        self.all_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.all_table.setColumnWidth(0, 30)  # Read status column
        self.all_table.cellClicked.connect(self.on_notification_clicked)
        all_layout.addWidget(self.all_table)
        
        self.all_tab.setLayout(all_layout)
        
        # Inventory tab
        self.inventory_tab = QWidget()
        inventory_layout = QVBoxLayout()
        
        # Inventory notifications table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(5)
        self.inventory_table.setHorizontalHeaderLabels(["Product", "Current Stock", "Min Stock", "Status", "Last Updated"])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        inventory_layout.addWidget(self.inventory_table)
        
        self.inventory_tab.setLayout(inventory_layout)
        
        # Expiry tab
        self.expiry_tab = QWidget()
        expiry_layout = QVBoxLayout()
        
        # Expiry notifications table
        self.expiry_table = QTableWidget()
        self.expiry_table.setColumnCount(4)
        self.expiry_table.setHorizontalHeaderLabels(["Product", "Expiry Date", "Days Left", "Status"])
        self.expiry_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        expiry_layout.addWidget(self.expiry_table)
        
        self.expiry_tab.setLayout(expiry_layout)
        
        # Trends tab
        self.trends_tab = QWidget()
        trends_layout = QVBoxLayout()
        
        # Trends table
        self.trends_table = QTableWidget()
        self.trends_table.setColumnCount(4)
        self.trends_table.setHorizontalHeaderLabels(["Product", "Sales (Last 30 Days)", "Change", "Trend"])
        self.trends_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        trends_layout.addWidget(self.trends_table)
        
        self.trends_tab.setLayout(trends_layout)
        
        # Rules Management tab (Admin only)
        if self.user_data.get("role") == "admin":
            self.rules_tab = QWidget()
            rules_layout = QVBoxLayout()
            
            # Rules controls
            rules_controls = QHBoxLayout()
            rules_controls.setSpacing(10)
            
            add_rule_btn = QPushButton("Add Rule")
            add_rule_btn.setMinimumWidth(100)
            add_rule_btn.setMinimumHeight(35)
            add_rule_btn.clicked.connect(self.add_notification_rule)
            rules_controls.addWidget(add_rule_btn)
            
            edit_rule_btn = QPushButton("Edit Rule")
            edit_rule_btn.setMinimumWidth(100)
            edit_rule_btn.setMinimumHeight(35)
            edit_rule_btn.clicked.connect(self.edit_notification_rule)
            rules_controls.addWidget(edit_rule_btn)
            
            delete_rule_btn = QPushButton("Delete Rule")
            delete_rule_btn.setMinimumWidth(100)
            delete_rule_btn.setMinimumHeight(35)
            delete_rule_btn.clicked.connect(self.delete_notification_rule)
            rules_controls.addWidget(delete_rule_btn)
            
            rules_controls.addStretch()
            rules_layout.addLayout(rules_controls)
            
            # Rules table
            self.rules_table = QTableWidget()
            self.rules_table.setColumnCount(5)
            self.rules_table.setHorizontalHeaderLabels(["Name", "Type", "Priority", "Enabled", "Message Template"])
            self.rules_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.rules_table.setSelectionBehavior(QTableWidget.SelectRows)
            rules_layout.addWidget(self.rules_table)
            
            self.rules_tab.setLayout(rules_layout)
            self.tabs.addTab(self.rules_tab, "Rules")
        
        # Add tabs to tab widget
        self.tabs.addTab(self.all_tab, "All Notifications")
        self.tabs.addTab(self.inventory_tab, "Inventory")
        self.tabs.addTab(self.expiry_tab, "Expiry")
        self.tabs.addTab(self.trends_tab, "Trends")
        
        main_layout.addWidget(self.tabs)
        
        self.setLayout(main_layout)
    
    def setup_auto_refresh(self):
        """Setup auto-refresh based on user preferences"""
        if self.preferences.get("auto_refresh", True):
            interval = self.preferences.get("refresh_interval", 300) * 1000  # Convert to milliseconds
            self.refresh_timer.start(interval)
    
    def auto_refresh_notifications(self):
        """Auto-refresh notifications"""
        self.refresh_notifications()
    
    def refresh_notifications(self):
        """Refresh notification data using advanced notification system"""
        try:
            # Generate new notifications based on business rules
            self.all_notifications = NotificationManager.generate_notifications(self.user_data)
            
            # Reload data with error handling
            self.products, products_error = DataManager.load_data(DEFAULT_PRODUCTS_FILE)
            if products_error:
                handle_data_error(self, "reload products", products_error)
            
            # Update all displays
            self.refresh_all_notifications()
            self.refresh_inventory_notifications()
            self.refresh_expiry_notifications()
            self.refresh_trends()
            self.update_unread_count()
            
            # Update rules table if admin
            if self.user_data.get("role") == "admin":
                self.refresh_rules_table()
            
        except Exception as e:
            DataManager.logger.error(f"Error refreshing notifications: {e}")
            show_message(self, "Error", f"Failed to refresh notifications: {e}", QMessageBox.Critical)
    
    def refresh_all_notifications(self):
        """Refresh the all notifications table"""
        try:
            # Get user notifications
            user_notifications = NotificationManager.get_user_notifications(
                self.user_data.get("username", ""), include_read=True
            )
            
            # Apply current filters
            filtered_notifications = self.apply_notification_filters(user_notifications)
            
            # Update table
            self.all_table.setRowCount(len(filtered_notifications))
            
            for row, notification in enumerate(filtered_notifications):
                # Read status indicator
                read_item = QTableWidgetItem("●" if not notification.get("read", False) else "○")
                read_item.setTextAlignment(Qt.AlignCenter)
                if not notification.get("read", False):
                    read_item.setForeground(QColor(Colors.LIGHT_ERROR if self.theme == Theme.LIGHT else Colors.DARK_ERROR))
                self.all_table.setItem(row, 0, read_item)
                
                # Priority with color
                priority = notification.get("priority", "medium")
                priority_item = QTableWidgetItem(priority.title())
                priority_color = self.get_priority_color(priority)
                priority_item.setForeground(priority_color)
                self.all_table.setItem(row, 1, priority_item)
                
                # Type
                self.all_table.setItem(row, 2, QTableWidgetItem(notification.get("type", "").title()))
                
                # Title
                self.all_table.setItem(row, 3, QTableWidgetItem(notification.get("title", "")))
                
                # Message
                self.all_table.setItem(row, 4, QTableWidgetItem(notification.get("message", "")))
                
                # Created date
                created_at = notification.get("created_at", "")
                self.all_table.setItem(row, 5, QTableWidgetItem(format_date(created_at)))
                
                # Store notification ID for click handling
                self.all_table.item(row, 0).setData(Qt.UserRole, notification.get("id"))
            
        except Exception as e:
            DataManager.logger.error(f"Error refreshing all notifications: {e}")
    
    def apply_notification_filters(self, notifications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply current filters to notifications"""
        filtered = notifications
        
        # Show filter
        show_filter = self.show_filter.currentText()
        if show_filter == "Unread Only":
            filtered = [n for n in filtered if not n.get("read", False)]
        elif show_filter == "Read Only":
            filtered = [n for n in filtered if n.get("read", False)]
        
        # Priority filter
        priority_filter = self.priority_filter.currentText()
        if priority_filter != "All":
            filtered = [n for n in filtered if n.get("priority", "").lower() == priority_filter.lower()]
        
        # Type filter
        type_filter = self.type_filter.currentText()
        if type_filter != "All":
            filtered = [n for n in filtered if n.get("type", "").lower() == type_filter.lower()]
        
        return filtered
    
    def apply_filters(self):
        """Apply filters when filter controls change"""
        self.refresh_all_notifications()
    
    def get_priority_color(self, priority: str):
        """Get color for priority level"""
        if priority == "critical":
            return QColor(Colors.LIGHT_ERROR if self.theme == Theme.LIGHT else Colors.DARK_ERROR)
        elif priority == "high":
            return QColor(Colors.LIGHT_WARNING if self.theme == Theme.LIGHT else Colors.DARK_WARNING)
        elif priority == "medium":
            return QColor(Colors.LIGHT_INFO if self.theme == Theme.LIGHT else Colors.DARK_INFO)
        else:
            return QColor(Colors.LIGHT_FOREGROUND if self.theme == Theme.LIGHT else Colors.DARK_FOREGROUND)
    
    def update_unread_count(self):
        """Update the unread notifications count"""
        try:
            user_notifications = NotificationManager.get_user_notifications(
                self.user_data.get("username", ""), include_read=False
            )
            unread_count = len(user_notifications)
            self.unread_label.setText(f"Unread: {unread_count}")
            
            if unread_count > 0:
                self.unread_label.setStyleSheet("font-weight: bold; color: red;")
            else:
                self.unread_label.setStyleSheet("font-weight: bold; color: green;")
                
        except Exception as e:
            DataManager.logger.error(f"Error updating unread count: {e}")
    
    def on_notification_clicked(self, row, column):
        """Handle notification click to mark as read"""
        try:
            notification_id = self.all_table.item(row, 0).data(Qt.UserRole)
            if notification_id:
                success = NotificationManager.mark_notification_read(notification_id)
                if success:
                    self.refresh_all_notifications()
                    self.update_unread_count()
                    
        except Exception as e:
            DataManager.logger.error(f"Error handling notification click: {e}")
    
    def mark_all_read(self):
        """Mark all notifications as read"""
        try:
            success = NotificationManager.mark_all_read(self.user_data.get("username", ""))
            if success:
                self.refresh_all_notifications()
                self.update_unread_count()
                show_message(self, "Success", "All notifications marked as read", QMessageBox.Information)
            else:
                show_message(self, "Error", "Failed to mark notifications as read", QMessageBox.Warning)
                
        except Exception as e:
            DataManager.logger.error(f"Error marking all notifications as read: {e}")
            show_message(self, "Error", f"Failed to mark notifications as read: {e}", QMessageBox.Critical)
    
    def show_preferences(self):
        """Show notification preferences dialog"""
        try:
            dialog = NotificationPreferencesDialog(self, self.user_data, self.preferences)
            if dialog.exec() == QDialog.Accepted:
                new_preferences = dialog.get_preferences()
                success = NotificationManager.save_user_preferences(
                    self.user_data.get("username", ""), new_preferences
                )
                
                if success:
                    self.preferences = new_preferences
                    self.setup_auto_refresh()  # Update auto-refresh settings
                    self.refresh_notifications()  # Refresh with new preferences
                    show_message(self, "Success", "Preferences saved successfully", QMessageBox.Information)
                else:
                    show_message(self, "Error", "Failed to save preferences", QMessageBox.Warning)
                    
        except Exception as e:
            DataManager.logger.error(f"Error showing preferences: {e}")
            show_message(self, "Error", f"Failed to show preferences: {e}", QMessageBox.Critical)
    
    def refresh_inventory_notifications(self):
        """Refresh inventory notifications table"""
        low_stock_items = []
        
        for product in self.products:
            quantity = product.get("quantity", 0)
            min_quantity = product.get("minimum_quantity", 0)
            
            if quantity <= min_quantity:
                status = "Out of Stock" if quantity == 0 else "Low Stock"
                status_color = Colors.LIGHT_ERROR if self.theme == Theme.LIGHT else Colors.DARK_ERROR
                
                low_stock_items.append({
                    "product": product.get("name", "Unknown"),
                    "quantity": quantity,
                    "min_quantity": min_quantity,
                    "status": status,
                    "status_color": status_color,
                    "updated_at": product.get("updated_at", datetime.now().isoformat())
                })
        
        # Update table
        self.inventory_table.setRowCount(len(low_stock_items))
        
        for row, item in enumerate(low_stock_items):
            self.inventory_table.setItem(row, 0, QTableWidgetItem(item.get("product")))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(str(item.get("quantity"))))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(str(item.get("min_quantity"))))
            
            # Status with color
            status_item = QTableWidgetItem(item.get("status"))
            status_item.setForeground(QColor(item.get("status_color")))
            self.inventory_table.setItem(row, 3, status_item)
            
            # Last updated date
            self.inventory_table.setItem(row, 4, QTableWidgetItem(format_date(item.get("updated_at", ""))))
    
    def refresh_expiry_notifications(self):
        """Refresh expiry notifications table"""
        now = datetime.now()
        expiring_items = []
        
        for product in self.products:
            expiry_date_str = product.get("expiry_date")
            if not expiry_date_str:
                continue
            
            try:
                expiry_date = datetime.fromisoformat(expiry_date_str)
                days_left = (expiry_date - now).days
                
                if days_left <= 30:  # Show products expiring within 30 days
                    if days_left < 0:
                        status = "Expired"
                        status_color = Colors.LIGHT_ERROR if self.theme == Theme.LIGHT else Colors.DARK_ERROR
                    elif days_left <= 7:
                        status = "Expiring Soon"
                        status_color = Colors.LIGHT_WARNING if self.theme == Theme.LIGHT else Colors.DARK_WARNING
                    else:
                        status = "Expiring"
                        status_color = Colors.LIGHT_INFO if self.theme == Theme.LIGHT else Colors.DARK_INFO
                    
                    expiring_items.append({
                        "product": product.get("name", "Unknown"),
                        "expiry_date": expiry_date,
                        "days_left": days_left,
                        "status": status,
                        "status_color": status_color
                    })
            except (ValueError, TypeError):
                # Skip if date parsing fails
                continue
        
        # Sort by days left (ascending)
        expiring_items.sort(key=lambda x: x.get("days_left", 0))
        
        # Update table
        self.expiry_table.setRowCount(len(expiring_items))
        
        for row, item in enumerate(expiring_items):
            self.expiry_table.setItem(row, 0, QTableWidgetItem(item.get("product")))
            self.expiry_table.setItem(row, 1, QTableWidgetItem(format_date(item.get("expiry_date"))))
            
            days_left = item.get("days_left")
            days_text = f"{days_left} days" if days_left >= 0 else f"{abs(days_left)} days overdue"
            self.expiry_table.setItem(row, 2, QTableWidgetItem(days_text))
            
            # Status with color
            status_item = QTableWidgetItem(item.get("status"))
            status_item.setForeground(QColor(item.get("status_color")))
            self.expiry_table.setItem(row, 3, status_item)
    
    def refresh_trends(self):
        """Refresh trends data - functionality removed"""
        try:
            # Trend analysis functionality has been removed
            # Clear the trends table
            self.trends_table.setRowCount(0)
            
        except Exception as e:
                # Save rule
                success = self.save_notification_rule(new_rule)
                if success:
                    self.refresh_rules_table()
                    show_message(self, "Success", "Notification rule added successfully", QMessageBox.Information)
                else:
                    show_message(self, "Error", "Failed to save notification rule", QMessageBox.Warning)
                    
        except Exception as e:
            DataManager.logger.error(f"Error adding notification rule: {e}")
            show_message(self, "Error", f"Failed to add notification rule: {e}", QMessageBox.Critical)
    
    def edit_notification_rule(self):
        """Edit selected notification rule"""
        try:
            current_row = self.rules_table.currentRow()
            if current_row < 0:
                show_message(self, "Warning", "Please select a rule to edit", QMessageBox.Warning)
                return
            
            rule_id = self.rules_table.item(current_row, 0).data(Qt.UserRole)
            rules = NotificationManager.get_notification_rules()
            
            # Find the rule to edit
            rule_to_edit = None
            for rule in rules:
                if rule.rule_id == rule_id:
                    rule_to_edit = rule
                    break
            
            if not rule_to_edit:
                show_message(self, "Error", "Rule not found", QMessageBox.Warning)
                return
            
            dialog = NotificationRuleDialog(self, rule_to_edit)
            if dialog.exec() == QDialog.Accepted:
                rule_data = dialog.get_rule_data()
                
                # Update rule
                rule_to_edit.name = rule_data["name"]
                rule_to_edit.rule_type = rule_data["rule_type"]
                rule_to_edit.priority = rule_data["priority"]
                rule_to_edit.enabled = rule_data["enabled"]
                rule_to_edit.message_template = rule_data["message_template"]
                
                # Save updated rules
                success = self.save_all_notification_rules(rules)
                if success:
                    self.refresh_rules_table()
                    show_message(self, "Success", "Notification rule updated successfully", QMessageBox.Information)
                else:
                    show_message(self, "Error", "Failed to update notification rule", QMessageBox.Warning)
                    
        except Exception as e:
            DataManager.logger.error(f"Error editing notification rule: {e}")
            show_message(self, "Error", f"Failed to edit notification rule: {e}", QMessageBox.Critical)
    
    def delete_notification_rule(self):
        """Delete selected notification rule"""
        try:
            current_row = self.rules_table.currentRow()
            if current_row < 0:
                show_message(self, "Warning", "Please select a rule to delete", QMessageBox.Warning)
                return
            
            rule_name = self.rules_table.item(current_row, 0).text()
            reply = QMessageBox.question(
                self, "Confirm Delete", 
                f"Are you sure you want to delete the rule '{rule_name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                rule_id = self.rules_table.item(current_row, 0).data(Qt.UserRole)
                rules = NotificationManager.get_notification_rules()
                
                # Remove the rule
                rules = [rule for rule in rules if rule.rule_id != rule_id]
                
                # Save updated rules
                success = self.save_all_notification_rules(rules)
                if success:
                    self.refresh_rules_table()
                    show_message(self, "Success", "Notification rule deleted successfully", QMessageBox.Information)
                else:
                    show_message(self, "Error", "Failed to delete notification rule", QMessageBox.Warning)
                    
        except Exception as e:
            DataManager.logger.error(f"Error deleting notification rule: {e}")
            show_message(self, "Error", f"Failed to delete notification rule: {e}", QMessageBox.Critical)
    
    def save_notification_rule(self, rule: NotificationRule) -> bool:
        """Save a single notification rule"""
        try:
            rules = NotificationManager.get_notification_rules()
            rules.append(rule)
            return self.save_all_notification_rules(rules)
        except Exception as e:
            DataManager.logger.error(f"Error saving notification rule: {e}")
            return False
    
    def save_all_notification_rules(self, rules: List[NotificationRule]) -> bool:
        """Save all notification rules"""
        try:
            rules_data = []
            for rule in rules:
                rules_data.append({
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "rule_type": rule.rule_type,
                    "condition": rule.condition,
                    "message_template": rule.message_template,
                    "priority": rule.priority,
                    "enabled": rule.enabled,
                    "created_at": rule.created_at
                })
            
            success, error = DataManager.save_data(rules_data, "notification_rules.json")
            if success:
                DataManager.logger.info("Notification rules saved successfully")
                return True
            else:
                DataManager.logger.error(f"Failed to save notification rules: {error}")
                return False
                
        except Exception as e:
            DataManager.logger.error(f"Error saving notification rules: {e}")
            return False
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.refresh_timer.isActive():
            self.refresh_timer.stop()
        event.accept()