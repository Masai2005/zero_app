"""
Print utilities module for the ZERO Business Management System.
Handles receipt printing, invoice generation, and report printing.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QGroupBox, QFormLayout, QComboBox, QSpinBox,
    QCheckBox, QMessageBox, QFileDialog, QProgressBar
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QTextDocument, QTextCursor
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

from utils import DataManager, format_currency, format_date, APP_NAME
from styles import StyleSheet, Theme


class PrintFormatter:
    """Handles formatting of different document types for printing"""
    
    @staticmethod
    def format_receipt(sale_data: Dict[str, Any], company_info: Optional[Dict] = None) -> str:
        """Format a sales receipt for printing"""
        
        # Default company info if not provided
        if not company_info:
            company_info = {
                "name": "ZERO Business Management",
                "address": "123 Business Street",
                "phone": "+1 (555) 123-4567",
                "email": "info@zerobusiness.com"
            }
        
        receipt_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Courier New', monospace; font-size: 12px; margin: 0; padding: 20px; }}
                .header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 15px; }}
                .company-name {{ font-size: 18px; font-weight: bold; }}
                .company-info {{ font-size: 10px; margin-top: 5px; }}
                .receipt-title {{ font-size: 16px; font-weight: bold; margin: 15px 0; }}
                .receipt-info {{ margin-bottom: 15px; }}
                .items-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                .items-table th, .items-table td {{ padding: 5px; text-align: left; border-bottom: 1px solid #ccc; }}
                .items-table th {{ font-weight: bold; background-color: #f0f0f0; }}
                .total-section {{ margin-top: 15px; padding-top: 10px; border-top: 2px solid #000; }}
                .total-line {{ display: flex; justify-content: space-between; margin: 3px 0; }}
                .grand-total {{ font-weight: bold; font-size: 14px; border-top: 1px solid #000; padding-top: 5px; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 10px; border-top: 1px solid #ccc; padding-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="company-name">{company_info['name']}</div>
                <div class="company-info">
                    {company_info['address']}<br>
                    Phone: {company_info['phone']} | Email: {company_info['email']}
                </div>
            </div>
            
            <div class="receipt-title">SALES RECEIPT</div>
            
            <div class="receipt-info">
                <strong>Invoice #:</strong> {sale_data.get('invoice_number', 'N/A')}<br>
                <strong>Date:</strong> {format_date(sale_data.get('created_at', ''))}<br>
                <strong>Customer:</strong> {sale_data.get('customer_name', 'Walk-in Customer')}<br>
                <strong>Served by:</strong> {sale_data.get('created_by', 'N/A')}<br>
                <strong>Payment Method:</strong> {sale_data.get('payment_method', 'N/A')}
            </div>
            
            <table class="items-table">
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Unit</th>
                        <th>Qty</th>
                        <th>Price</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add items
        for item in sale_data.get('items', []):
            receipt_html += f"""
                    <tr>
                        <td>{item.get('product_name', 'Unknown')}</td>
                        <td>{item.get('unit', 'Each')}</td>
                        <td>{item.get('quantity', 0)}</td>
                        <td>{format_currency(item.get('unit_price', 0))}</td>
                        <td>{format_currency(item.get('total_price', 0))}</td>
                    </tr>
            """
        
        # Add totals
        receipt_html += f"""
                </tbody>
            </table>
            
            <div class="total-section">
                <div class="total-line">
                    <span>Subtotal:</span>
                    <span>{format_currency(sale_data.get('subtotal', 0))}</span>
                </div>
                <div class="total-line">
                    <span>Discount:</span>
                    <span>-{format_currency(sale_data.get('discount', 0))}</span>
                </div>
                <div class="total-line grand-total">
                    <span>TOTAL:</span>
                    <span>{format_currency(sale_data.get('total', 0))}</span>
                </div>
            </div>
            
            <div class="footer">
                Thank you for your business!<br>
                Generated on {format_date(datetime.now().isoformat())}
            </div>
        </body>
        </html>
        """
        
        return receipt_html
    
    @staticmethod
    def format_invoice(sale_data: Dict[str, Any], company_info: Optional[Dict] = None) -> str:
        """Format a formal invoice for printing"""
        
        # Default company info if not provided
        if not company_info:
            company_info = {
                "name": "ZERO Business Management",
                "address": "123 Business Street",
                "city": "Business City, BC 12345",
                "phone": "+1 (555) 123-4567",
                "email": "info@zerobusiness.com",
                "tax_id": "TAX123456789"
            }
        
        invoice_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; font-size: 11px; margin: 0; padding: 30px; }}
                .header {{ display: flex; justify-content: space-between; margin-bottom: 30px; }}
                .company-info {{ flex: 1; }}
                .company-name {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
                .company-details {{ margin-top: 10px; line-height: 1.4; }}
                .invoice-info {{ flex: 1; text-align: right; }}
                .invoice-title {{ font-size: 28px; font-weight: bold; color: #e74c3c; }}
                .invoice-details {{ margin-top: 15px; }}
                .customer-section {{ margin: 30px 0; }}
                .customer-title {{ font-size: 14px; font-weight: bold; margin-bottom: 10px; }}
                .items-table {{ width: 100%; border-collapse: collapse; margin: 30px 0; }}
                .items-table th {{ background-color: #34495e; color: white; padding: 12px; text-align: left; }}
                .items-table td {{ padding: 10px; border-bottom: 1px solid #ecf0f1; }}
                .items-table tr:nth-child(even) {{ background-color: #f8f9fa; }}
                .totals-section {{ margin-top: 30px; }}
                .totals-table {{ width: 300px; margin-left: auto; }}
                .totals-table td {{ padding: 8px; }}
                .total-row {{ font-weight: bold; font-size: 14px; border-top: 2px solid #34495e; }}
                .footer {{ margin-top: 50px; text-align: center; font-size: 10px; color: #7f8c8d; }}
                .payment-terms {{ margin-top: 30px; padding: 15px; background-color: #ecf0f1; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="company-info">
                    <div class="company-name">{company_info['name']}</div>
                    <div class="company-details">
                        {company_info['address']}<br>
                        {company_info.get('city', '')}<br>
                        Phone: {company_info['phone']}<br>
                        Email: {company_info['email']}<br>
                        Tax ID: {company_info.get('tax_id', 'N/A')}
                    </div>
                </div>
                <div class="invoice-info">
                    <div class="invoice-title">INVOICE</div>
                    <div class="invoice-details">
                        <strong>Invoice #:</strong> {sale_data.get('invoice_number', 'N/A')}<br>
                        <strong>Date:</strong> {format_date(sale_data.get('created_at', ''))}<br>
                        <strong>Due Date:</strong> {format_date(sale_data.get('due_date', sale_data.get('created_at', '')))}<br>
                        <strong>Terms:</strong> {sale_data.get('payment_terms', 'Net 30')}
                    </div>
                </div>
            </div>
            
            <div class="customer-section">
                <div class="customer-title">Bill To:</div>
                <div>
                    <strong>{sale_data.get('customer_name', 'Walk-in Customer')}</strong><br>
        """
        
        # Add customer details if available
        customer_id = sale_data.get('customer_id')
        if customer_id:
            # Try to load customer details
            customers_data, _ = DataManager.load_data('customers.json')
            customer = next((c for c in customers_data if c.get('id') == customer_id), None)
            if customer:
                invoice_html += f"""
                    {customer.get('company_name', '')}<br>
                    {customer.get('address', '')}<br>
                    Phone: {customer.get('mobile', 'N/A')}<br>
                    Email: {customer.get('email', 'N/A')}
                """
        
        invoice_html += """
                </div>
            </div>
            
            <table class="items-table">
                <thead>
                    <tr>
                        <th>Description</th>
                        <th>Unit</th>
                        <th>Quantity</th>
                        <th>Unit Price</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add items
        for item in sale_data.get('items', []):
            invoice_html += f"""
                    <tr>
                        <td>{item.get('product_name', 'Unknown')}</td>
                        <td>{item.get('unit', 'Each')}</td>
                        <td>{item.get('quantity', 0)}</td>
                        <td>{format_currency(item.get('unit_price', 0))}</td>
                        <td>{format_currency(item.get('total_price', 0))}</td>
                    </tr>
            """
        
        # Add totals
        invoice_html += f"""
                </tbody>
            </table>
            
            <div class="totals-section">
                <table class="totals-table">
                    <tr>
                        <td>Subtotal:</td>
                        <td style="text-align: right;">{format_currency(sale_data.get('subtotal', 0))}</td>
                    </tr>
                    <tr>
                        <td>Discount:</td>
                        <td style="text-align: right;">-{format_currency(sale_data.get('discount', 0))}</td>
                    </tr>
                    <tr class="total-row">
                        <td>TOTAL:</td>
                        <td style="text-align: right;">{format_currency(sale_data.get('total', 0))}</td>
                    </tr>
                </table>
            </div>
            
            <div class="payment-terms">
                <strong>Payment Information:</strong><br>
                Payment Method: {sale_data.get('payment_method', 'N/A')}<br>
                Please remit payment within the specified terms. Thank you for your business!
            </div>
            
            <div class="footer">
                This invoice was generated electronically by {APP_NAME} on {format_date(datetime.now().isoformat())}
            </div>
        </body>
        </html>
        """
        
        return invoice_html
    
    @staticmethod
    def format_sales_report(sales_data: List[Dict[str, Any]], date_range: str = "") -> str:
        """Format a sales report for printing"""
        
        # Calculate totals
        total_sales = len(sales_data)
        total_revenue = sum(sale.get('total', 0) for sale in sales_data)
        total_discount = sum(sale.get('discount', 0) for sale in sales_data)
        
        # Group by payment method
        payment_methods = {}
        for sale in sales_data:
            method = sale.get('payment_method', 'Unknown')
            if method not in payment_methods:
                payment_methods[method] = {'count': 0, 'total': 0}
            payment_methods[method]['count'] += 1
            payment_methods[method]['total'] += sale.get('total', 0)
        
        # Group by customer
        top_customers = {}
        for sale in sales_data:
            customer = sale.get('customer_name', 'Walk-in Customer')
            if customer not in top_customers:
                top_customers[customer] = {'count': 0, 'total': 0}
            top_customers[customer]['count'] += 1
            top_customers[customer]['total'] += sale.get('total', 0)
        
        # Sort top customers by total sales
        top_customers = dict(sorted(top_customers.items(), key=lambda x: x[1]['total'], reverse=True)[:10])
        
        report_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; font-size: 11px; margin: 0; padding: 30px; }}
                .header {{ text-align: center; border-bottom: 3px solid #2c3e50; padding-bottom: 20px; margin-bottom: 30px; }}
                .company-name {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
                .report-title {{ font-size: 20px; font-weight: bold; color: #e74c3c; margin-top: 10px; }}
                .date-range {{ font-size: 12px; color: #7f8c8d; margin-top: 5px; }}
                .summary-section {{ margin-bottom: 30px; }}
                .summary-title {{ font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 15px; }}
                .summary-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }}
                .summary-card {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; text-align: center; }}
                .summary-value {{ font-size: 18px; font-weight: bold; color: #2c3e50; }}
                .summary-label {{ font-size: 12px; color: #7f8c8d; margin-top: 5px; }}
                .table-section {{ margin: 30px 0; }}
                .section-title {{ font-size: 14px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }}
                .data-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                .data-table th {{ background-color: #34495e; color: white; padding: 10px; text-align: left; }}
                .data-table td {{ padding: 8px; border-bottom: 1px solid #ecf0f1; }}
                .data-table tr:nth-child(even) {{ background-color: #f8f9fa; }}
                .footer {{ text-align: center; margin-top: 50px; font-size: 10px; color: #7f8c8d; border-top: 1px solid #ecf0f1; padding-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="company-name">ZERO Business Management</div>
                <div class="report-title">SALES REPORT</div>
                <div class="date-range">{date_range if date_range else 'All Time'}</div>
            </div>
            
            <div class="summary-section">
                <div class="summary-title">Summary</div>
                <div class="summary-grid">
                    <div class="summary-card">
                        <div class="summary-value">{total_sales}</div>
                        <div class="summary-label">Total Sales</div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-value">{format_currency(total_revenue)}</div>
                        <div class="summary-label">Total Revenue</div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-value">{format_currency(total_discount)}</div>
                        <div class="summary-label">Total Discounts</div>
                    </div>
                </div>
            </div>
            
            <div class="table-section">
                <div class="section-title">Payment Methods Breakdown</div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Payment Method</th>
                            <th>Number of Sales</th>
                            <th>Total Amount</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for method, data in payment_methods.items():
            percentage = (data['total'] / total_revenue * 100) if total_revenue > 0 else 0
            report_html += f"""
                        <tr>
                            <td>{method}</td>
                            <td>{data['count']}</td>
                            <td>{format_currency(data['total'])}</td>
                            <td>{percentage:.1f}%</td>
                        </tr>
            """
        
        report_html += """
                    </tbody>
                </table>
            </div>
            
            <div class="table-section">
                <div class="section-title">Top Customers</div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Customer Name</th>
                            <th>Number of Orders</th>
                            <th>Total Spent</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for customer, data in top_customers.items():
            report_html += f"""
                        <tr>
                            <td>{customer}</td>
                            <td>{data['count']}</td>
                            <td>{format_currency(data['total'])}</td>
                        </tr>
            """
        
        report_html += """
                    </tbody>
                </table>
            </div>
            
            <div class="table-section">
                <div class="section-title">Recent Sales Transactions</div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Invoice #</th>
                            <th>Date</th>
                            <th>Customer</th>
                            <th>Payment Method</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Show recent 20 sales
        recent_sales = sorted(sales_data, key=lambda x: x.get('created_at', ''), reverse=True)[:20]
        for sale in recent_sales:
            report_html += f"""
                        <tr>
                            <td>{sale.get('invoice_number', 'N/A')}</td>
                            <td>{format_date(sale.get('created_at', ''))}</td>
                            <td>{sale.get('customer_name', 'Walk-in Customer')}</td>
                            <td>{sale.get('payment_method', 'N/A')}</td>
                            <td>{format_currency(sale.get('total', 0))}</td>
                        </tr>
            """
        
        report_html += f"""
                    </tbody>
                </table>
            </div>
            
            <div class="footer">
                Report generated by {APP_NAME} on {format_date(datetime.now().isoformat())}
            </div>
        </body>
        </html>
        """
        
        return report_html
    
    @staticmethod
    def format_inventory_report(products_data: List[Dict[str, Any]]) -> str:
        """Format an inventory report for printing"""
        
        # Calculate inventory totals
        total_products = len(products_data)
        total_value = sum(product.get('selling_price', 0) * product.get('quantity', 0) for product in products_data)
        low_stock_count = sum(1 for product in products_data if product.get('quantity', 0) <= product.get('minimum_quantity', 0))
        
        report_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; font-size: 11px; margin: 0; padding: 30px; }}
                .header {{ text-align: center; border-bottom: 3px solid #2c3e50; padding-bottom: 20px; margin-bottom: 30px; }}
                .company-name {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
                .report-title {{ font-size: 20px; font-weight: bold; color: #e74c3c; margin-top: 10px; }}
                .summary-section {{ margin-bottom: 30px; }}
                .summary-title {{ font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 15px; }}
                .summary-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }}
                .summary-card {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; text-align: center; }}
                .summary-value {{ font-size: 18px; font-weight: bold; color: #2c3e50; }}
                .summary-label {{ font-size: 12px; color: #7f8c8d; margin-top: 5px; }}
                .data-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .data-table th {{ background-color: #34495e; color: white; padding: 10px; text-align: left; font-size: 10px; }}
                .data-table td {{ padding: 8px; border-bottom: 1px solid #ecf0f1; font-size: 10px; }}
                .data-table tr:nth-child(even) {{ background-color: #f8f9fa; }}
                .low-stock {{ background-color: #fee; }}
                .footer {{ text-align: center; margin-top: 50px; font-size: 10px; color: #7f8c8d; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="company-name">ZERO Business Management</div>
                <div class="report-title">INVENTORY REPORT</div>
                <div class="date-range">Generated on {format_date(datetime.now().isoformat())}</div>
            </div>
            
            <div class="summary-section">
                <div class="summary-title">Inventory Summary</div>
                <div class="summary-grid">
                    <div class="summary-card">
                        <div class="summary-value">{total_products}</div>
                        <div class="summary-label">Total Products</div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-value">{format_currency(total_value)}</div>
                        <div class="summary-label">Total Value</div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-value">{low_stock_count}</div>
                        <div class="summary-label">Low Stock Items</div>
                    </div>
                </div>
            </div>
            
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Product Name</th>
                        <th>Barcode</th>
                        <th>Unit</th>
                        <th>Current Stock</th>
                        <th>Min. Stock</th>
                        <th>Buying Price</th>
                        <th>Selling Price</th>
                        <th>Stock Value</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for product in products_data:
            is_low_stock = product.get('quantity', 0) <= product.get('minimum_quantity', 0)
            stock_value = product.get('selling_price', 0) * product.get('quantity', 0)
            row_class = 'low-stock' if is_low_stock else ''
            
            report_html += f"""
                    <tr class="{row_class}">
                        <td>{product.get('name', 'Unknown')}</td>
                        <td>{product.get('barcode', 'N/A')}</td>
                        <td>{product.get('unit_type', 'Each')}</td>
                        <td>{product.get('quantity', 0)}</td>
                        <td>{product.get('minimum_quantity', 0)}</td>
                        <td>{format_currency(product.get('buying_price', 0))}</td>
                        <td>{format_currency(product.get('selling_price', 0))}</td>
                        <td>{format_currency(stock_value)}</td>
                    </tr>
            """
        
        report_html += f"""
                </tbody>
            </table>
            
            <div class="footer">
                Report generated by {APP_NAME} • Low stock items highlighted in red
            </div>
        </body>
        </html>
        """
        
        return report_html
    
    @staticmethod
    def format_customer_report(customers_data: List[Dict[str, Any]]) -> str:
        """Format a customer report for printing"""
        
        # Calculate customer statistics
        total_customers = len(customers_data)
        customers_with_email = sum(1 for customer in customers_data if customer.get('email'))
        customers_with_company = sum(1 for customer in customers_data if customer.get('company_name'))
        
        # Load sales data to get customer purchase information
        sales_data, _ = DataManager.load_data('sales.json')
        payments_data, _ = DataManager.load_data('payments.json')
        
        # Calculate customer purchase totals
        customer_purchases = {}
        customer_payments = {}
        
        for sale in sales_data:
            customer_id = sale.get('customer_id')
            customer_name = sale.get('customer_name', 'Walk-in Customer')
            
            if customer_id and customer_id not in customer_purchases:
                customer_purchases[customer_id] = {'total_spent': 0, 'order_count': 0}
            
            if customer_id:
                customer_purchases[customer_id]['total_spent'] += sale.get('total', 0)
                customer_purchases[customer_id]['order_count'] += 1
        
        for payment in payments_data:
            customer_id = payment.get('customer_id')
            if customer_id and customer_id not in customer_payments:
                customer_payments[customer_id] = 0
            if customer_id:
                customer_payments[customer_id] += payment.get('amount', 0)
        
        report_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; font-size: 11px; margin: 0; padding: 30px; }}
                .header {{ text-align: center; border-bottom: 3px solid #2c3e50; padding-bottom: 20px; margin-bottom: 30px; }}
                .company-name {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
                .report-title {{ font-size: 20px; font-weight: bold; color: #e74c3c; margin-top: 10px; }}
                .summary-section {{ margin-bottom: 30px; }}
                .summary-title {{ font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 15px; }}
                .summary-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }}
                .summary-card {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; text-align: center; }}
                .summary-value {{ font-size: 18px; font-weight: bold; color: #2c3e50; }}
                .summary-label {{ font-size: 12px; color: #7f8c8d; margin-top: 5px; }}
                .data-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .data-table th {{ background-color: #34495e; color: white; padding: 10px; text-align: left; font-size: 10px; }}
                .data-table td {{ padding: 8px; border-bottom: 1px solid #ecf0f1; font-size: 10px; }}
                .data-table tr:nth-child(even) {{ background-color: #f8f9fa; }}
                .footer {{ text-align: center; margin-top: 50px; font-size: 10px; color: #7f8c8d; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="company-name">ZERO Business Management</div>
                <div class="report-title">CUSTOMER REPORT</div>
                <div class="date-range">Generated on {format_date(datetime.now().isoformat())}</div>
            </div>
            
            <div class="summary-section">
                <div class="summary-title">Customer Summary</div>
                <div class="summary-grid">
                    <div class="summary-card">
                        <div class="summary-value">{total_customers}</div>
                        <div class="summary-label">Total Customers</div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-value">{customers_with_email}</div>
                        <div class="summary-label">With Email Address</div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-value">{customers_with_company}</div>
                        <div class="summary-label">Business Customers</div>
                    </div>
                </div>
            </div>
            
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Customer Name</th>
                        <th>Company</th>
                        <th>Mobile</th>
                        <th>Email</th>
                        <th>Total Orders</th>
                        <th>Total Spent</th>
                        <th>Outstanding Balance</th>
                        <th>Registration Date</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for customer in customers_data:
            customer_id = customer.get('id')
            full_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
            
            purchase_data = customer_purchases.get(customer_id, {'total_spent': 0, 'order_count': 0})
            payments_total = customer_payments.get(customer_id, 0)
            outstanding_balance = purchase_data['total_spent'] - payments_total
            
            report_html += f"""
                    <tr>
                        <td>{full_name or 'N/A'}</td>
                        <td>{customer.get('company_name', '') or '-'}</td>
                        <td>{customer.get('mobile', '') or '-'}</td>
                        <td>{customer.get('email', '') or '-'}</td>
                        <td>{purchase_data['order_count']}</td>
                        <td>{format_currency(purchase_data['total_spent'])}</td>
                        <td>{format_currency(outstanding_balance)}</td>
                        <td>{format_date(customer.get('created_at', ''))}</td>
                    </tr>
            """
        
        report_html += f"""
                </tbody>
            </table>
            
            <div class="footer">
                Report generated by {APP_NAME}
            </div>
        </body>
        </html>
        """
        
        return report_html


class PrintPreviewDialog(QDialog):
    """Dialog for print preview functionality"""
    
    def __init__(self, document_html: str, document_title: str = "Document", parent=None):
        super().__init__(parent)
        self.document_html = document_html
        self.document_title = document_title
        self.setWindowTitle(f"Print Preview - {document_title}")
        self.setMinimumSize(800, 600)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the print preview UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"Print Preview - {self.document_title}")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Preview area
        self.preview_text = QTextEdit()
        self.preview_text.setHtml(self.document_html)
        self.preview_text.setReadOnly(True)
        layout.addWidget(self.preview_text)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Print button
        self.print_btn = QPushButton("Print")
        self.print_btn.clicked.connect(self.print_document)
        button_layout.addWidget(self.print_btn)
        
        # Save as PDF button
        self.save_pdf_btn = QPushButton("Save as PDF")
        self.save_pdf_btn.clicked.connect(self.save_as_pdf)
        button_layout.addWidget(self.save_pdf_btn)
        
        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.close_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def print_document(self):
        """Print the document"""
        try:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSize(QPrinter.A4)
            
            print_dialog = QPrintDialog(printer, self)
            if print_dialog.exec() == QPrintDialog.Accepted:
                # Create document and print
                document = QTextDocument()
                document.setHtml(self.document_html)
                document.print(printer)
                
                QMessageBox.information(self, "Print Successful", "Document sent to printer successfully!")
                
        except Exception as e:
            QMessageBox.critical(self, "Print Error", f"Failed to print document: {str(e)}")
    
    def save_as_pdf(self):
        """Save the document as PDF"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save as PDF",
                f"{self.document_title.replace(' ', '_')}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                printer = QPrinter(QPrinter.HighResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setOutputFileName(file_path)
                printer.setPageSize(QPrinter.A4)
                
                document = QTextDocument()
                document.setHtml(self.document_html)
                document.print(printer)
                
                QMessageBox.information(self, "PDF Saved", f"Document saved as PDF: {file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save PDF: {str(e)}")


class PrintManager:
    """Main class for managing print operations"""
    
    @staticmethod
    def print_receipt(sale_data: Dict[str, Any], parent=None):
        """Print a sales receipt"""
        try:
            receipt_html = PrintFormatter.format_receipt(sale_data)
            preview_dialog = PrintPreviewDialog(receipt_html, f"Receipt - {sale_data.get('invoice_number', 'N/A')}", parent)
            preview_dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(parent, "Print Error", f"Failed to generate receipt: {str(e)}")
    
    @staticmethod
    def print_invoice(sale_data: Dict[str, Any], parent=None):
        """Print a formal invoice"""
        try:
            invoice_html = PrintFormatter.format_invoice(sale_data)
            preview_dialog = PrintPreviewDialog(invoice_html, f"Invoice - {sale_data.get('invoice_number', 'N/A')}", parent)
            preview_dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(parent, "Print Error", f"Failed to generate invoice: {str(e)}")
    
    @staticmethod
    def print_sales_report(sales_data: List[Dict[str, Any]], date_range: str = "", parent=None):
        """Print a sales report"""
        try:
            report_html = PrintFormatter.format_sales_report(sales_data, date_range)
            preview_dialog = PrintPreviewDialog(report_html, f"Sales Report - {date_range}", parent)
            preview_dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(parent, "Print Error", f"Failed to generate sales report: {str(e)}")
    
    @staticmethod
    def print_inventory_report(products_data: List[Dict[str, Any]], parent=None):
        """Print an inventory report"""
        try:
            report_html = PrintFormatter.format_inventory_report(products_data)
            preview_dialog = PrintPreviewDialog(report_html, "Inventory Report", parent)
            preview_dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(parent, "Print Error", f"Failed to generate inventory report: {str(e)}")
    
    @staticmethod
    def print_customer_report(customers_data: List[Dict[str, Any]], parent=None):
        """Print a customer report"""
        try:
            report_html = PrintFormatter.format_customer_report(customers_data)
            preview_dialog = PrintPreviewDialog(report_html, "Customer Report", parent)
            preview_dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(parent, "Print Error", f"Failed to generate customer report: {str(e)}")
    
    @staticmethod
    def quick_print_receipt(sale_data: Dict[str, Any], parent=None) -> bool:
        """Quick print a receipt without preview"""
        try:
            receipt_html = PrintFormatter.format_receipt(sale_data)
            
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSize(QPrinter.A4)
            
            document = QTextDocument()
            document.setHtml(receipt_html)
            document.print(printer)
            
            return True
            
        except Exception as e:
            QMessageBox.critical(parent, "Print Error", f"Failed to print receipt: {str(e)}")
            return False