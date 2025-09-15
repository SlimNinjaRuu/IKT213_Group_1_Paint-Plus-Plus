#!/usr/bin/env python3
"""
Demo script for Photo Editor Application
This script demonstrates the core functionality without requiring GUI
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFilter
import tempfile

def demo_image_operations():
    """Demonstrate core image operations"""
    print("Photo Editor Core Functionality Demo")
    print("=" * 50)
    
    # Create a temporary directory for demo files
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Working in temporary directory: {temp_dir}")
        
        # 1. Create a new image
        print("\n1. Creating a new image...")
        demo_image = Image.new("RGB", (400, 300), "lightblue")
        print(f"   ✓ Created image: {demo_image.size} pixels, mode: {demo_image.mode}")
        
        # 2. Draw some shapes (simulating the drawing tools)
        print("\n2. Adding shapes and text...")
        draw = ImageDraw.Draw(demo_image)
        
        # Rectangle (red)
        draw.rectangle([50, 50, 150, 100], outline="red", width=3)
        print("   ✓ Added red rectangle")
        
        # Circle (green)
        draw.ellipse([200, 50, 300, 150], outline="green", width=3)
        print("   ✓ Added green circle")
        
        # Text
        draw.text((50, 200), "Photo Editor Demo", fill="black")
        print("   ✓ Added text")
        
        # Save original
        original_path = os.path.join(temp_dir, "demo_original.png")
        demo_image.save(original_path)
        print(f"   ✓ Saved original to: {os.path.basename(original_path)}")
        
        # 3. Demonstrate image transformations
        print("\n3. Applying transformations...")
        
        # Resize
        resized = demo_image.resize((200, 150))
        resized_path = os.path.join(temp_dir, "demo_resized.png")
        resized.save(resized_path)
        print(f"   ✓ Resized to {resized.size} and saved")
        
        # Rotate
        rotated = demo_image.rotate(45, expand=True)
        rotated_path = os.path.join(temp_dir, "demo_rotated.png")
        rotated.save(rotated_path)
        print(f"   ✓ Rotated 45° and saved")
        
        # Flip
        flipped = demo_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        flipped_path = os.path.join(temp_dir, "demo_flipped.png")
        flipped.save(flipped_path)
        print("   ✓ Flipped horizontally and saved")
        
        # 4. Demonstrate filters
        print("\n4. Applying filters...")
        
        # Blur
        blurred = demo_image.filter(ImageFilter.BLUR)
        blur_path = os.path.join(temp_dir, "demo_blurred.png")
        blurred.save(blur_path)
        print("   ✓ Applied blur filter")
        
        # Sharpen
        sharpened = demo_image.filter(ImageFilter.SHARPEN)
        sharpen_path = os.path.join(temp_dir, "demo_sharpened.png")
        sharpened.save(sharpen_path)
        print("   ✓ Applied sharpen filter")
        
        # Edge enhance
        edge_enhanced = demo_image.filter(ImageFilter.EDGE_ENHANCE)
        edge_path = os.path.join(temp_dir, "demo_edge.png")
        edge_enhanced.save(edge_path)
        print("   ✓ Applied edge enhancement filter")
        
        # 5. Demonstrate selection and cropping
        print("\n5. Demonstrating selection and cropping...")
        
        # Crop a section (simulating selection)
        cropped = demo_image.crop((50, 50, 250, 200))
        crop_path = os.path.join(temp_dir, "demo_cropped.png")
        cropped.save(crop_path)
        print(f"   ✓ Cropped selection to {cropped.size}")
        
        # 6. List all created files
        print("\n6. Generated demo files:")
        for filename in os.listdir(temp_dir):
            if filename.endswith('.png'):
                filepath = os.path.join(temp_dir, filename)
                size = os.path.getsize(filepath)
                print(f"   - {filename} ({size:,} bytes)")
        
        print(f"\n✓ Demo completed successfully!")
        print(f"   All {len([f for f in os.listdir(temp_dir) if f.endswith('.png')])} demo images were created and processed")
        
    return True

def test_dependencies():
    """Test that all required dependencies are available"""
    print("Testing Dependencies")
    print("=" * 30)
    
    try:
        import PIL
        print(f"✓ Pillow (PIL): {PIL.__version__}")
    except ImportError:
        print("✗ Pillow (PIL): Not installed")
        return False
    
    try:
        import numpy
        print(f"✓ NumPy: {numpy.__version__}")
    except ImportError:
        print("✗ NumPy: Not installed")
        return False
    
    try:
        import matplotlib
        print(f"✓ Matplotlib: {matplotlib.__version__}")
    except ImportError:
        print("✗ Matplotlib: Not installed")
        return False
    
    # Test tkinter availability (but don't fail if not available in headless environment)
    try:
        import tkinter
        print(f"✓ tkinter: Available")
    except ImportError:
        print("⚠ tkinter: Not available (expected in headless environment)")
    
    return True

if __name__ == "__main__":
    print("Photo Editor Application Demo")
    print("=" * 50)
    
    if not test_dependencies():
        print("\n✗ Some dependencies are missing. Please run: python setup.py")
        sys.exit(1)
    
    print("\n")
    
    try:
        demo_image_operations()
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("The photo editor implements all core features:")
        print("• File operations (New, Open, Save)")
        print("• Image transformations (Resize, Rotate, Flip)")
        print("• Drawing tools (Shapes, Text, Brushes)")
        print("• Filters (Blur, Sharpen, Edge Enhancement)")
        print("• Selection and cropping")
        print("• Color operations")
        print("\nTo run the full GUI application, use: python photo_editor.py")
        
    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        sys.exit(1)