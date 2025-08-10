"""
Barcode utilities for generation and scanning functionality.
"""
import io
import cv2
import numpy as np
from PIL import Image
from pyzbar import pyzbar
import barcode
from barcode.writer import ImageWriter
from PySide6.QtWidgets import QMessageBox, QFileDialog, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
from PySide6.QtCore import QTimer, QThread, Signal
from PySide6.QtGui import QPixmap, QImage
import tempfile
import os


class BarcodeGenerator:
    """Utility class for generating barcodes"""
    
    @staticmethod
    def generate_barcode(data, barcode_type='code128'):
        """
        Generate a barcode image from data
        
        Args:
            data (str): The data to encode in the barcode
            barcode_type (str): Type of barcode (code128, ean13, etc.)
        
        Returns:
            PIL.Image: Generated barcode image
        """
        try:
            # Get barcode class
            barcode_class = barcode.get_barcode_class(barcode_type)
            
            # Create barcode instance
            barcode_instance = barcode_class(data, writer=ImageWriter())
            
            # Generate barcode image
            buffer = io.BytesIO()
            barcode_instance.write(buffer)
            buffer.seek(0)
            
            # Return PIL image
            return Image.open(buffer)
            
        except Exception as e:
            print(f"Error generating barcode: {e}")
            return None
    
    @staticmethod
    def generate_product_barcode(product_id):
        """
        Generate a barcode for a product ID
        
        Args:
            product_id (str): Product ID to encode
        
        Returns:
            PIL.Image: Generated barcode image
        """
        # Pad product ID to ensure it's long enough for barcode
        padded_id = str(product_id).zfill(12)
        return BarcodeGenerator.generate_barcode(padded_id)
    
    @staticmethod
    def save_barcode_image(barcode_image, filepath):
        """
        Save barcode image to file
        
        Args:
            barcode_image (PIL.Image): Barcode image to save
            filepath (str): Path to save the image
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            barcode_image.save(filepath)
            return True
        except Exception as e:
            print(f"Error saving barcode image: {e}")
            return False


class BarcodeScanner:
    """Utility class for scanning barcodes from images and camera"""
    
    @staticmethod
    def scan_barcode_from_image(image_path):
        """
        Scan barcode from an image file
        
        Args:
            image_path (str): Path to the image file
        
        Returns:
            list: List of decoded barcode data
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return []
            
            # Decode barcodes
            barcodes = pyzbar.decode(image)
            
            # Extract barcode data
            results = []
            for barcode_obj in barcodes:
                barcode_data = barcode_obj.data.decode('utf-8')
                barcode_type = barcode_obj.type
                results.append({
                    'data': barcode_data,
                    'type': barcode_type,
                    'rect': barcode_obj.rect
                })
            
            return results
            
        except Exception as e:
            print(f"Error scanning barcode from image: {e}")
            return []
    
    @staticmethod
    def scan_barcode_from_camera_frame(frame):
        """
        Scan barcode from a camera frame
        
        Args:
            frame (numpy.ndarray): Camera frame
        
        Returns:
            list: List of decoded barcode data
        """
        try:
            # Decode barcodes
            barcodes = pyzbar.decode(frame)
            
            # Extract barcode data
            results = []
            for barcode_obj in barcodes:
                barcode_data = barcode_obj.data.decode('utf-8')
                barcode_type = barcode_obj.type
                results.append({
                    'data': barcode_data,
                    'type': barcode_type,
                    'rect': barcode_obj.rect
                })
            
            return results
            
        except Exception as e:
            print(f"Error scanning barcode from frame: {e}")
            return []


class CameraScannerThread(QThread):
    """Thread for camera-based barcode scanning"""
    
    barcode_detected = Signal(str)
    frame_ready = Signal(np.ndarray)
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.camera = None
    
    def run(self):
        """Main thread execution"""
        try:
            # Initialize camera
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                self.error_occurred.emit("Could not open camera")
                return
            
            self.running = True
            
            while self.running:
                # Read frame
                ret, frame = self.camera.read()
                if not ret:
                    continue
                
                # Emit frame for display
                self.frame_ready.emit(frame.copy())
                
                # Scan for barcodes
                barcodes = BarcodeScanner.scan_barcode_from_camera_frame(frame)
                
                # If barcode found, emit signal
                if barcodes:
                    barcode_data = barcodes[0]['data']  # Take first barcode found
                    self.barcode_detected.emit(barcode_data)
                    break  # Stop scanning after first barcode
                
                # Small delay to prevent excessive CPU usage
                self.msleep(50)
                
        except Exception as e:
            self.error_occurred.emit(f"Camera error: {str(e)}")
        finally:
            if self.camera:
                self.camera.release()
    
    def stop(self):
        """Stop the scanning thread"""
        self.running = False
        self.wait()


class BarcodeScannerDialog(QDialog):
    """Dialog for barcode scanning using camera or file"""
    
    barcode_scanned = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Barcode Scanner")
        self.setMinimumSize(640, 480)
        
        self.scanner_thread = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Barcode Scanner")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Camera preview area
        self.camera_label = QLabel("Camera preview will appear here")
        self.camera_label.setMinimumSize(400, 300)
        self.camera_label.setStyleSheet("border: 2px dashed #ccc; background-color: #f9f9f9;")
        self.camera_label.setScaledContents(True)
        layout.addWidget(self.camera_label)
        
        # Status label
        self.status_label = QLabel("Ready to scan")
        layout.addWidget(self.status_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Start camera button
        self.start_camera_btn = QPushButton("Start Camera")
        self.start_camera_btn.clicked.connect(self.start_camera_scan)
        button_layout.addWidget(self.start_camera_btn)
        
        # Stop camera button
        self.stop_camera_btn = QPushButton("Stop Camera")
        self.stop_camera_btn.clicked.connect(self.stop_camera_scan)
        self.stop_camera_btn.setEnabled(False)
        button_layout.addWidget(self.stop_camera_btn)
        
        # Scan from file button
        self.scan_file_btn = QPushButton("Scan from File")
        self.scan_file_btn.clicked.connect(self.scan_from_file)
        button_layout.addWidget(self.scan_file_btn)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def start_camera_scan(self):
        """Start camera-based scanning"""
        try:
            self.scanner_thread = CameraScannerThread()
            self.scanner_thread.barcode_detected.connect(self.on_barcode_detected)
            self.scanner_thread.frame_ready.connect(self.update_camera_preview)
            self.scanner_thread.error_occurred.connect(self.on_camera_error)
            
            self.scanner_thread.start()
            
            self.start_camera_btn.setEnabled(False)
            self.stop_camera_btn.setEnabled(True)
            self.status_label.setText("Scanning... Point camera at barcode")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start camera: {str(e)}")
    
    def stop_camera_scan(self):
        """Stop camera-based scanning"""
        if self.scanner_thread:
            self.scanner_thread.stop()
            self.scanner_thread = None
        
        self.start_camera_btn.setEnabled(True)
        self.stop_camera_btn.setEnabled(False)
        self.status_label.setText("Camera stopped")
        self.camera_label.setText("Camera preview will appear here")
    
    def scan_from_file(self):
        """Scan barcode from image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Image File", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if file_path:
            barcodes = BarcodeScanner.scan_barcode_from_image(file_path)
            
            if barcodes:
                barcode_data = barcodes[0]['data']  # Take first barcode found
                self.on_barcode_detected(barcode_data)
            else:
                QMessageBox.information(self, "No Barcode Found", "No barcode was detected in the selected image.")
    
    def update_camera_preview(self, frame):
        """Update camera preview with new frame"""
        try:
            # Convert frame to Qt format
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Convert to pixmap and display
            pixmap = QPixmap.fromImage(qt_image)
            self.camera_label.setPixmap(pixmap)
            
        except Exception as e:
            print(f"Error updating camera preview: {e}")
    
    def on_barcode_detected(self, barcode_data):
        """Handle barcode detection"""
        self.stop_camera_scan()
        self.status_label.setText(f"Barcode detected: {barcode_data}")
        
        # Emit signal and close dialog
        self.barcode_scanned.emit(barcode_data)
        self.accept()
    
    def on_camera_error(self, error_message):
        """Handle camera errors"""
        self.stop_camera_scan()
        QMessageBox.critical(self, "Camera Error", error_message)
    
    def closeEvent(self, event):
        """Handle dialog close event"""
        self.stop_camera_scan()
        super().closeEvent(event)


class BarcodeDisplayWidget(QWidget):
    """Widget for displaying generated barcodes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Barcode display label
        self.barcode_label = QLabel("No barcode generated")
        self.barcode_label.setMinimumSize(300, 100)
        self.barcode_label.setStyleSheet("border: 1px solid #ccc; background-color: white;")
        self.barcode_label.setScaledContents(True)
        layout.addWidget(self.barcode_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Save barcode button
        self.save_btn = QPushButton("Save Barcode")
        self.save_btn.clicked.connect(self.save_barcode)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)
        
        # Print barcode button
        self.print_btn = QPushButton("Print Barcode")
        self.print_btn.clicked.connect(self.print_barcode)
        self.print_btn.setEnabled(False)
        button_layout.addWidget(self.print_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        self.current_barcode_image = None
    
    def display_barcode(self, barcode_data):
        """Display generated barcode"""
        try:
            # Generate barcode
            barcode_image = BarcodeGenerator.generate_barcode(barcode_data)
            
            if barcode_image:
                # Convert PIL image to Qt pixmap
                buffer = io.BytesIO()
                barcode_image.save(buffer, format='PNG')
                buffer.seek(0)
                
                qt_image = QImage()
                qt_image.loadFromData(buffer.getvalue())
                pixmap = QPixmap.fromImage(qt_image)
                
                # Display barcode
                self.barcode_label.setPixmap(pixmap)
                self.current_barcode_image = barcode_image
                
                # Enable buttons
                self.save_btn.setEnabled(True)
                self.print_btn.setEnabled(True)
                
            else:
                self.barcode_label.setText("Failed to generate barcode")
                self.current_barcode_image = None
                self.save_btn.setEnabled(False)
                self.print_btn.setEnabled(False)
                
        except Exception as e:
            self.barcode_label.setText(f"Error: {str(e)}")
            self.current_barcode_image = None
            self.save_btn.setEnabled(False)
            self.print_btn.setEnabled(False)
    
    def save_barcode(self):
        """Save barcode to file"""
        if not self.current_barcode_image:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Barcode", 
            "barcode.png", 
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
        )
        
        if file_path:
            success = BarcodeGenerator.save_barcode_image(self.current_barcode_image, file_path)
            if success:
                QMessageBox.information(self, "Success", f"Barcode saved to {file_path}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save barcode")
    
    def print_barcode(self):
        """Print barcode (placeholder implementation)"""
        if not self.current_barcode_image:
            return
        
        # For now, just show a message
        # In a real implementation, you would integrate with a printing system
        QMessageBox.information(
            self, 
            "Print Barcode", 
            "Printing functionality would be implemented here.\n"
            "For now, please save the barcode and print it using your system's image viewer."
        )