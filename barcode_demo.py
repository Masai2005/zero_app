#!/usr/bin/env python3
"""
Demo script showing barcode generation and scanning functionality
"""
import json
import tempfile
import os
from barcode_utils import BarcodeGenerator, BarcodeScanner

def demo_barcode_generation():
    """Demonstrate barcode generation"""
    print("=== Barcode Generation Demo ===")
    
    # Generate barcode for a sample product
    sample_barcode = "123456789012"
    print(f"Generating barcode for: {sample_barcode}")
    
    barcode_image = BarcodeGenerator.generate_barcode(sample_barcode)
    
    if barcode_image:
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_file.close()
        
        success = BarcodeGenerator.save_barcode_image(barcode_image, temp_file.name)
        
        if success:
            print(f"✓ Barcode saved to: {temp_file.name}")
            print(f"  Image size: {barcode_image.size}")
            
            # Clean up
            os.unlink(temp_file.name)
        else:
            print("✗ Failed to save barcode image")
    else:
        print("✗ Failed to generate barcode")

def demo_product_barcode_generation():
    """Demonstrate product-specific barcode generation"""
    print("\n=== Product Barcode Generation Demo ===")
    
    # Load existing products
    try:
        with open('data/products.json', 'r') as f:
            products = json.load(f)
        
        for product in products[:2]:  # Demo with first 2 products
            product_name = product.get('name')
            existing_barcode = product.get('barcode')
            
            print(f"\nProduct: {product_name}")
            print(f"Existing barcode: {existing_barcode}")
            
            # Generate barcode image
            barcode_image = BarcodeGenerator.generate_barcode(existing_barcode)
            if barcode_image:
                print(f"✓ Barcode image generated (size: {barcode_image.size})")
            else:
                print("✗ Failed to generate barcode image")
                
    except Exception as e:
        print(f"✗ Error loading products: {e}")

def demo_barcode_scanning():
    """Demonstrate barcode scanning from generated image"""
    print("\n=== Barcode Scanning Demo ===")
    
    # Generate a barcode and save it
    test_barcode = "987654321098"
    barcode_image = BarcodeGenerator.generate_barcode(test_barcode)
    
    if barcode_image:
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_file.close()
        
        success = BarcodeGenerator.save_barcode_image(barcode_image, temp_file.name)
        
        if success:
            print(f"Generated test barcode: {test_barcode}")
            print(f"Saved to: {temp_file.name}")
            
            # Try to scan it back
            scanned_barcodes = BarcodeScanner.scan_barcode_from_image(temp_file.name)
            
            if scanned_barcodes:
                for barcode_data in scanned_barcodes:
                    scanned_value = barcode_data['data']
                    barcode_type = barcode_data['type']
                    print(f"✓ Scanned barcode: {scanned_value} (type: {barcode_type})")
                    
                    if scanned_value == test_barcode:
                        print("✓ Scanned barcode matches original!")
                    else:
                        print("✗ Scanned barcode doesn't match original")
            else:
                print("✗ No barcodes detected in generated image")
            
            # Clean up
            os.unlink(temp_file.name)
        else:
            print("✗ Failed to save test barcode")
    else:
        print("✗ Failed to generate test barcode")

if __name__ == "__main__":
    print("Barcode Functionality Demo")
    print("=" * 40)
    
    demo_barcode_generation()
    demo_product_barcode_generation()
    demo_barcode_scanning()
    
    print("\n" + "=" * 40)
    print("Demo completed!")
    print("\nBarcode functionality includes:")
    print("• Generate barcodes for products")
    print("• Scan barcodes from camera or image files")
    print("• Lookup products by barcode in sales")
    print("• Display and save barcode images")