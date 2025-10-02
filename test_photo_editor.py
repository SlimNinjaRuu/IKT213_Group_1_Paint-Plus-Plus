#!/usr/bin/env python3
"""
Basic tests for Photo Editor Application
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add the parent directory to the path to import the photo_editor module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from photo_editor import PhotoEditor
    import tkinter as tk
    from PIL import Image
except ImportError as e:
    print(f"Warning: Could not import required modules for testing: {e}")
    print("Please run 'python setup.py' to install dependencies")
    sys.exit(1)


class TestPhotoEditor(unittest.TestCase):
    """Basic tests for PhotoEditor functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.root = tk.Tk()
        self.app = PhotoEditor(self.root)
        # Hide the window during testing
        self.root.withdraw()
        
    def tearDown(self):
        """Clean up after tests"""
        try:
            self.root.destroy()
        except:
            pass
    
    def test_initialization(self):
        """Test that the application initializes correctly"""
        self.assertIsNotNone(self.app)
        self.assertEqual(self.app.current_tool, "select")
        self.assertEqual(self.app.zoom_factor, 1.0)
        self.assertEqual(self.app.current_color, "#000000")
        self.assertEqual(self.app.brush_size, 5)
    
    def test_new_image_creation(self):
        """Test creating a new blank image"""
        # Create a simple 100x100 white image
        test_image = Image.new("RGB", (100, 100), "white")
        self.app.current_image = test_image
        
        self.assertIsNotNone(self.app.current_image)
        self.assertEqual(self.app.current_image.size, (100, 100))
        self.assertEqual(self.app.current_image.mode, "RGB")
    
    def test_tool_change(self):
        """Test changing tools"""
        self.app.tool_var.set("brush")
        self.app.change_tool()
        self.assertEqual(self.app.current_tool, "brush")
        
        self.app.tool_var.set("eraser")
        self.app.change_tool()
        self.assertEqual(self.app.current_tool, "eraser")
    
    def test_zoom_operations(self):
        """Test zoom functionality"""
        initial_zoom = self.app.zoom_factor
        
        self.app.zoom_in()
        self.assertGreater(self.app.zoom_factor, initial_zoom)
        
        zoom_after_in = self.app.zoom_factor
        self.app.zoom_out()
        self.assertLess(self.app.zoom_factor, zoom_after_in)
    
    def test_color_setting(self):
        """Test color setting"""
        test_color = "#FF0000"  # Red
        self.app.current_color = test_color
        self.assertEqual(self.app.current_color, test_color)
    
    def test_brush_size_change(self):
        """Test brush size changes"""
        self.app.change_brush_size("10")
        self.assertEqual(self.app.brush_size, 10)
        
        self.app.change_brush_size("25.5")
        self.assertEqual(self.app.brush_size, 25)
    
    def test_image_rotation(self):
        """Test image rotation"""
        # Create a test image
        test_image = Image.new("RGB", (100, 50), "white")
        self.app.current_image = test_image
        
        original_size = self.app.current_image.size
        
        # Rotate 90 degrees
        self.app.rotate_image(90)
        
        # Size should be swapped after 90-degree rotation
        self.assertEqual(self.app.current_image.size, (original_size[1], original_size[0]))
    
    def test_image_flip(self):
        """Test image flipping"""
        # Create a simple test image with different colors
        test_image = Image.new("RGB", (2, 1), "white")
        test_image.putpixel((0, 0), (255, 0, 0))  # Red pixel at left
        test_image.putpixel((1, 0), (0, 255, 0))  # Green pixel at right
        
        self.app.current_image = test_image
        
        # Test horizontal flip
        self.app.flip_horizontal()
        
        # After horizontal flip, colors should be swapped
        left_pixel = self.app.current_image.getpixel((0, 0))
        right_pixel = self.app.current_image.getpixel((1, 0))
        
        self.assertEqual(left_pixel, (0, 255, 0))  # Green should now be on left
        self.assertEqual(right_pixel, (255, 0, 0))  # Red should now be on right
    
    def test_clipboard_operations(self):
        """Test clipboard copy functionality"""
        # Create a test image
        test_image = Image.new("RGB", (100, 100), "white")
        self.app.current_image = test_image
        
        # Set up a selection
        self.app.selection_start = (0, 0)
        self.app.selection_end = (50, 50)
        
        # Test copy
        self.app.copy_selection()
        
        self.assertIsNotNone(self.app.clipboard_image)
        self.assertEqual(self.app.clipboard_image.size, (50, 50))


class TestImageFilters(unittest.TestCase):
    """Test image filter functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.root = tk.Tk()
        self.app = PhotoEditor(self.root)
        self.root.withdraw()
        
        # Create a test image
        self.test_image = Image.new("RGB", (100, 100), "white")
        self.app.current_image = self.test_image
        
    def tearDown(self):
        """Clean up after tests"""
        try:
            self.root.destroy()
        except:
            pass
    
    def test_filter_application(self):
        """Test that filters can be applied without errors"""
        original_size = self.app.current_image.size
        
        # Test blur filter
        self.app.apply_filter("blur")
        self.assertEqual(self.app.current_image.size, original_size)
        
        # Reset image
        self.app.current_image = self.test_image.copy()
        
        # Test sharpen filter
        self.app.apply_filter("sharpen")
        self.assertEqual(self.app.current_image.size, original_size)


def run_basic_functionality_test():
    """Run a basic functionality test without unittest framework"""
    print("Running basic functionality tests...")
    
    try:
        # Test 1: Application creation
        root = tk.Tk()
        app = PhotoEditor(root)
        root.withdraw()
        print("✓ Application initialization: PASSED")
        
        # Test 2: Image creation
        test_image = Image.new("RGB", (100, 100), "white")
        app.current_image = test_image
        print("✓ Image creation: PASSED")
        
        # Test 3: Tool change
        app.tool_var.set("brush")
        app.change_tool()
        assert app.current_tool == "brush"
        print("✓ Tool change: PASSED")
        
        # Test 4: Zoom
        initial_zoom = app.zoom_factor
        app.zoom_in()
        assert app.zoom_factor > initial_zoom
        print("✓ Zoom functionality: PASSED")
        
        # Test 5: Image rotation
        original_size = app.current_image.size
        app.rotate_image(90)
        expected_size = (original_size[1], original_size[0])
        assert app.current_image.size == expected_size
        print("✓ Image rotation: PASSED")
        
        root.destroy()
        print("\n✓ All basic functionality tests PASSED!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


if __name__ == "__main__":
    print("Photo Editor Application Tests")
    print("=" * 40)
    
    # Check if we're in a headless environment
    try:
        root = tk.Tk()
        root.withdraw()
        root.destroy()
        can_run_gui_tests = True
    except tk.TclError:
        can_run_gui_tests = False
        print("Warning: GUI tests cannot run in headless environment")
    
    if can_run_gui_tests:
        # Run basic functionality test
        if run_basic_functionality_test():
            print("\nRunning detailed unit tests...\n")
            # Run unittest suite
            unittest.main(verbosity=2, exit=False)
        else:
            print("Basic functionality tests failed. Skipping detailed tests.")
            sys.exit(1)
    else:
        print("Skipping GUI tests (no display available)")
        print("Manual testing required when display is available")