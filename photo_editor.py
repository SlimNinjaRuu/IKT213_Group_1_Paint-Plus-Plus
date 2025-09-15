#!/usr/bin/env python3
"""
Photo Editing Desktop Application
Group 1 - IKT213 Project

A comprehensive photo editing application with core features including:
- File operations (New, Open, Save, Quit)
- Clipboard operations (Copy, Cut, Paste)
- Image operations (Selections, Crop, Resize, Rotate, Flip)
- Tools (Zoom, Erase, Color Picker, Brushes, Text, Filters, Histogram)
- Shapes and Colors
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import io


class PhotoEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Editor - Group 1")
        self.root.geometry("1200x800")
        
        # Initialize variables
        self.current_image = None
        self.display_image = None
        self.photo_tk = None
        self.zoom_factor = 1.0
        self.clipboard_image = None
        self.current_tool = "select"
        self.current_color = "#000000"
        self.brush_size = 5
        self.selection_start = None
        self.selection_end = None
        self.selection_rect = None
        
        # Setup UI
        self.setup_menu()
        self.setup_toolbar()
        self.setup_canvas()
        self.setup_status_bar()
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
    def setup_menu(self):
        """Create the main menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_image, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_image, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_image, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_image, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.quit_app, accelerator="Ctrl+Q")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy", command=self.copy_selection, accelerator="Ctrl+C")
        edit_menu.add_command(label="Cut", command=self.cut_selection, accelerator="Ctrl+X")
        edit_menu.add_command(label="Paste", command=self.paste_clipboard, accelerator="Ctrl+V")
        
        # Image menu
        image_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Image", menu=image_menu)
        image_menu.add_command(label="Crop", command=self.crop_image)
        image_menu.add_command(label="Resize", command=self.resize_image)
        image_menu.add_command(label="Rotate 90° CW", command=lambda: self.rotate_image(90))
        image_menu.add_command(label="Rotate 90° CCW", command=lambda: self.rotate_image(-90))
        image_menu.add_command(label="Flip Horizontal", command=self.flip_horizontal)
        image_menu.add_command(label="Flip Vertical", command=self.flip_vertical)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="+")
        tools_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="-")
        tools_menu.add_command(label="Zoom Fit", command=self.zoom_fit)
        tools_menu.add_command(label="Color Picker", command=self.color_picker)
        tools_menu.add_command(label="Show Histogram", command=self.show_histogram)
        
        # Filters menu
        filters_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Filters", menu=filters_menu)
        filters_menu.add_command(label="Blur", command=lambda: self.apply_filter("blur"))
        filters_menu.add_command(label="Sharpen", command=lambda: self.apply_filter("sharpen"))
        filters_menu.add_command(label="Edge Enhance", command=lambda: self.apply_filter("edge"))
        filters_menu.add_command(label="Emboss", command=lambda: self.apply_filter("emboss"))
        
        # Keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self.new_image())
        self.root.bind("<Control-o>", lambda e: self.open_image())
        self.root.bind("<Control-s>", lambda e: self.save_image())
        self.root.bind("<Control-q>", lambda e: self.quit_app())
        self.root.bind("<Control-c>", lambda e: self.copy_selection())
        self.root.bind("<Control-x>", lambda e: self.cut_selection())
        self.root.bind("<Control-v>", lambda e: self.paste_clipboard())
        self.root.bind("<plus>", lambda e: self.zoom_in())
        self.root.bind("<minus>", lambda e: self.zoom_out())
        
    def setup_toolbar(self):
        """Create the toolbar with tools and options"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Tool selection
        ttk.Label(toolbar, text="Tool:").grid(row=0, column=0, padx=5)
        self.tool_var = tk.StringVar(value="select")
        tools = [("Select", "select"), ("Brush", "brush"), ("Eraser", "eraser"), 
                ("Text", "text"), ("Rectangle", "rectangle"), ("Circle", "circle")]
        
        for i, (name, tool) in enumerate(tools):
            ttk.Radiobutton(toolbar, text=name, variable=self.tool_var, 
                          value=tool, command=self.change_tool).grid(row=0, column=i+1, padx=5)
        
        # Color selection
        ttk.Label(toolbar, text="Color:").grid(row=0, column=len(tools)+1, padx=5)
        self.color_button = tk.Button(toolbar, bg=self.current_color, width=3,
                                    command=self.choose_color)
        self.color_button.grid(row=0, column=len(tools)+2, padx=5)
        
        # Brush size
        ttk.Label(toolbar, text="Size:").grid(row=0, column=len(tools)+3, padx=5)
        self.size_var = tk.IntVar(value=5)
        size_scale = ttk.Scale(toolbar, from_=1, to=50, variable=self.size_var,
                             orient=tk.HORIZONTAL, length=100,
                             command=self.change_brush_size)
        size_scale.grid(row=0, column=len(tools)+4, padx=5)
        
        # Zoom controls
        ttk.Label(toolbar, text="Zoom:").grid(row=0, column=len(tools)+5, padx=5)
        ttk.Button(toolbar, text="+", command=self.zoom_in).grid(row=0, column=len(tools)+6, padx=2)
        ttk.Button(toolbar, text="-", command=self.zoom_out).grid(row=0, column=len(tools)+7, padx=2)
        ttk.Button(toolbar, text="Fit", command=self.zoom_fit).grid(row=0, column=len(tools)+8, padx=2)
        
    def setup_canvas(self):
        """Create the main canvas area with scrollbars"""
        canvas_frame = ttk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create canvas with scrollbars
        self.canvas = tk.Canvas(canvas_frame, bg="white", cursor="crosshair")
        
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        h_scroll.grid(row=1, column=0, sticky="ew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
    def setup_status_bar(self):
        """Create the status bar"""
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def update_status(self, message):
        """Update the status bar message"""
        self.status_bar.config(text=message)
        
    # File Operations
    def new_image(self):
        """Create a new blank image"""
        try:
            # Ask for dimensions
            dialog = tk.Toplevel(self.root)
            dialog.title("New Image")
            dialog.geometry("300x150")
            dialog.transient(self.root)
            dialog.grab_set()
            
            ttk.Label(dialog, text="Width:").grid(row=0, column=0, padx=5, pady=5)
            width_var = tk.IntVar(value=800)
            width_entry = ttk.Entry(dialog, textvariable=width_var)
            width_entry.grid(row=0, column=1, padx=5, pady=5)
            
            ttk.Label(dialog, text="Height:").grid(row=1, column=0, padx=5, pady=5)
            height_var = tk.IntVar(value=600)
            height_entry = ttk.Entry(dialog, textvariable=height_var)
            height_entry.grid(row=1, column=1, padx=5, pady=5)
            
            def create_image():
                width = width_var.get()
                height = height_var.get()
                self.current_image = Image.new("RGB", (width, height), "white")
                self.update_display()
                self.update_status(f"Created new image: {width}x{height}")
                dialog.destroy()
                
            ttk.Button(dialog, text="Create", command=create_image).grid(row=2, column=0, columnspan=2, pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create new image: {str(e)}")
            
    def open_image(self):
        """Open an image file"""
        try:
            file_path = filedialog.askopenfilename(
                title="Open Image",
                filetypes=[
                    ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                    ("JPEG files", "*.jpg *.jpeg"),
                    ("PNG files", "*.png"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                self.current_image = Image.open(file_path)
                self.current_image_path = file_path
                self.update_display()
                self.update_status(f"Opened: {os.path.basename(file_path)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {str(e)}")
            
    def save_image(self):
        """Save the current image"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image to save")
            return
            
        try:
            if hasattr(self, 'current_image_path'):
                self.current_image.save(self.current_image_path)
                self.update_status(f"Saved: {os.path.basename(self.current_image_path)}")
            else:
                self.save_as_image()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")
            
    def save_as_image(self):
        """Save the current image with a new name"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image to save")
            return
            
        try:
            file_path = filedialog.asksaveasfilename(
                title="Save Image As",
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                self.current_image.save(file_path)
                self.current_image_path = file_path
                self.update_status(f"Saved: {os.path.basename(file_path)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")
            
    def quit_app(self):
        """Quit the application"""
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.root.quit()
            
    # Display and Canvas Operations
    def update_display(self):
        """Update the canvas display with the current image"""
        if not self.current_image:
            return
            
        # Calculate display size based on zoom
        width = int(self.current_image.width * self.zoom_factor)
        height = int(self.current_image.height * self.zoom_factor)
        
        # Resize image for display
        self.display_image = self.current_image.resize((width, height), Image.Resampling.LANCZOS)
        self.photo_tk = ImageTk.PhotoImage(self.display_image)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_tk)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def change_tool(self):
        """Change the current tool"""
        self.current_tool = self.tool_var.get()
        self.update_status(f"Tool: {self.current_tool}")
        
    def choose_color(self):
        """Open color chooser dialog"""
        color = colorchooser.askcolor(color=self.current_color)[1]
        if color:
            self.current_color = color
            self.color_button.config(bg=color)
            
    def change_brush_size(self, value):
        """Change brush size"""
        self.brush_size = int(float(value))
        
    # Zoom Operations
    def zoom_in(self):
        """Zoom in the image"""
        self.zoom_factor *= 1.2
        self.update_display()
        self.update_status(f"Zoom: {self.zoom_factor:.1f}x")
        
    def zoom_out(self):
        """Zoom out the image"""
        self.zoom_factor /= 1.2
        self.update_display()
        self.update_status(f"Zoom: {self.zoom_factor:.1f}x")
        
    def zoom_fit(self):
        """Fit image to canvas"""
        if not self.current_image:
            return
            
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            zoom_x = canvas_width / self.current_image.width
            zoom_y = canvas_height / self.current_image.height
            self.zoom_factor = min(zoom_x, zoom_y)
            self.update_display()
            self.update_status(f"Zoom: {self.zoom_factor:.1f}x (fit)")


    # Canvas Event Handlers
    def on_canvas_click(self, event):
        """Handle canvas click events"""
        if not self.current_image:
            return
            
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.current_tool == "select":
            self.selection_start = (x, y)
            if self.selection_rect:
                self.canvas.delete(self.selection_rect)
                
        elif self.current_tool == "brush":
            self.draw_brush(x, y)
            
        elif self.current_tool == "eraser":
            self.erase_area(x, y)
            
        elif self.current_tool == "text":
            self.add_text(x, y)
            
    def on_canvas_drag(self, event):
        """Handle canvas drag events"""
        if not self.current_image:
            return
            
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.current_tool == "select" and self.selection_start:
            if self.selection_rect:
                self.canvas.delete(self.selection_rect)
            self.selection_rect = self.canvas.create_rectangle(
                self.selection_start[0], self.selection_start[1], x, y,
                outline="red", dash=(5, 5)
            )
            
        elif self.current_tool == "brush":
            self.draw_brush(x, y)
            
        elif self.current_tool == "eraser":
            self.erase_area(x, y)
            
    def on_canvas_release(self, event):
        """Handle canvas release events"""
        if not self.current_image:
            return
            
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.current_tool == "select" and self.selection_start:
            self.selection_end = (x, y)
            
        elif self.current_tool in ["rectangle", "circle"]:
            self.draw_shape(self.current_tool, event)
            
    # Drawing Operations
    def draw_brush(self, x, y):
        """Draw with brush tool"""
        if self.display_image:
            # Convert canvas coordinates to image coordinates
            img_x = int(x / self.zoom_factor)
            img_y = int(y / self.zoom_factor)
            
            # Create a drawing context
            draw = ImageDraw.Draw(self.current_image)
            
            # Draw circle at position
            radius = self.brush_size // 2
            draw.ellipse([
                img_x - radius, img_y - radius,
                img_x + radius, img_y + radius
            ], fill=self.current_color)
            
            self.update_display()
            
    def erase_area(self, x, y):
        """Erase area with eraser tool"""
        if self.display_image:
            # Convert canvas coordinates to image coordinates
            img_x = int(x / self.zoom_factor)
            img_y = int(y / self.zoom_factor)
            
            # Create a drawing context
            draw = ImageDraw.Draw(self.current_image)
            
            # Draw white circle (erase)
            radius = self.brush_size // 2
            draw.ellipse([
                img_x - radius, img_y - radius,
                img_x + radius, img_y + radius
            ], fill="white")
            
            self.update_display()
            
    def add_text(self, x, y):
        """Add text at clicked position"""
        text = tk.simpledialog.askstring("Add Text", "Enter text:")
        if text and self.display_image:
            try:
                # Convert canvas coordinates to image coordinates
                img_x = int(x / self.zoom_factor)
                img_y = int(y / self.zoom_factor)
                
                # Create a drawing context
                draw = ImageDraw.Draw(self.current_image)
                
                # Try to use a font, fallback to default
                try:
                    font = ImageFont.truetype("arial.ttf", size=20)
                except:
                    font = ImageFont.load_default()
                
                # Draw text
                draw.text((img_x, img_y), text, fill=self.current_color, font=font)
                
                self.update_display()
                self.update_status(f"Added text: {text}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add text: {str(e)}")
                
    def draw_shape(self, shape, event):
        """Draw shapes"""
        if not self.selection_start or not self.display_image:
            return
            
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # Convert canvas coordinates to image coordinates
        start_x = int(self.selection_start[0] / self.zoom_factor)
        start_y = int(self.selection_start[1] / self.zoom_factor)
        end_x = int(x / self.zoom_factor)
        end_y = int(y / self.zoom_factor)
        
        # Create a drawing context
        draw = ImageDraw.Draw(self.current_image)
        
        if shape == "rectangle":
            draw.rectangle([start_x, start_y, end_x, end_y], 
                         outline=self.current_color, width=self.brush_size)
        elif shape == "circle":
            draw.ellipse([start_x, start_y, end_x, end_y], 
                       outline=self.current_color, width=self.brush_size)
                       
        self.update_display()
        self.selection_start = None
        
    # Clipboard Operations
    def copy_selection(self):
        """Copy selected area to clipboard"""
        if not self.current_image or not self.selection_start or not self.selection_end:
            messagebox.showwarning("Warning", "No selection to copy")
            return
            
        try:
            # Convert canvas coordinates to image coordinates
            x1 = int(min(self.selection_start[0], self.selection_end[0]) / self.zoom_factor)
            y1 = int(min(self.selection_start[1], self.selection_end[1]) / self.zoom_factor)
            x2 = int(max(self.selection_start[0], self.selection_end[0]) / self.zoom_factor)
            y2 = int(max(self.selection_start[1], self.selection_end[1]) / self.zoom_factor)
            
            # Crop the selection
            self.clipboard_image = self.current_image.crop((x1, y1, x2, y2))
            self.update_status("Selection copied to clipboard")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy selection: {str(e)}")
            
    def cut_selection(self):
        """Cut selected area to clipboard"""
        if not self.current_image or not self.selection_start or not self.selection_end:
            messagebox.showwarning("Warning", "No selection to cut")
            return
            
        try:
            # Copy first
            self.copy_selection()
            
            # Convert canvas coordinates to image coordinates
            x1 = int(min(self.selection_start[0], self.selection_end[0]) / self.zoom_factor)
            y1 = int(min(self.selection_start[1], self.selection_end[1]) / self.zoom_factor)
            x2 = int(max(self.selection_start[0], self.selection_end[0]) / self.zoom_factor)
            y2 = int(max(self.selection_start[1], self.selection_end[1]) / self.zoom_factor)
            
            # Fill selection with white (cut)
            draw = ImageDraw.Draw(self.current_image)
            draw.rectangle([x1, y1, x2, y2], fill="white")
            
            self.update_display()
            self.update_status("Selection cut to clipboard")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to cut selection: {str(e)}")
            
    def paste_clipboard(self):
        """Paste clipboard image"""
        if not self.clipboard_image:
            messagebox.showwarning("Warning", "No image in clipboard")
            return
            
        if not self.current_image:
            # If no image is open, create new one with clipboard image
            self.current_image = self.clipboard_image.copy()
            self.update_display()
            self.update_status("Pasted image as new image")
            return
            
        try:
            # Paste at top-left corner
            self.current_image.paste(self.clipboard_image, (0, 0))
            self.update_display()
            self.update_status("Image pasted")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste image: {str(e)}")
            
    # Image Operations
    def crop_image(self):
        """Crop image to selection"""
        if not self.current_image or not self.selection_start or not self.selection_end:
            messagebox.showwarning("Warning", "No selection to crop")
            return
            
        try:
            # Convert canvas coordinates to image coordinates
            x1 = int(min(self.selection_start[0], self.selection_end[0]) / self.zoom_factor)
            y1 = int(min(self.selection_start[1], self.selection_end[1]) / self.zoom_factor)
            x2 = int(max(self.selection_start[0], self.selection_end[0]) / self.zoom_factor)
            y2 = int(max(self.selection_start[1], self.selection_end[1]) / self.zoom_factor)
            
            # Crop the image
            self.current_image = self.current_image.crop((x1, y1, x2, y2))
            self.clear_selection()
            self.update_display()
            self.update_status("Image cropped")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to crop image: {str(e)}")
            
    def resize_image(self):
        """Resize the current image"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image to resize")
            return
            
        try:
            # Create resize dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Resize Image")
            dialog.geometry("300x200")
            dialog.transient(self.root)
            dialog.grab_set()
            
            current_width = self.current_image.width
            current_height = self.current_image.height
            
            ttk.Label(dialog, text=f"Current size: {current_width} x {current_height}").grid(row=0, column=0, columnspan=2, pady=5)
            
            ttk.Label(dialog, text="New Width:").grid(row=1, column=0, padx=5, pady=5)
            width_var = tk.IntVar(value=current_width)
            width_entry = ttk.Entry(dialog, textvariable=width_var)
            width_entry.grid(row=1, column=1, padx=5, pady=5)
            
            ttk.Label(dialog, text="New Height:").grid(row=2, column=0, padx=5, pady=5)
            height_var = tk.IntVar(value=current_height)
            height_entry = ttk.Entry(dialog, textvariable=height_var)
            height_entry.grid(row=2, column=1, padx=5, pady=5)
            
            maintain_ratio = tk.BooleanVar(value=True)
            ttk.Checkbutton(dialog, text="Maintain aspect ratio", 
                          variable=maintain_ratio).grid(row=3, column=0, columnspan=2, pady=5)
            
            def on_width_change(*args):
                if maintain_ratio.get():
                    ratio = current_height / current_width
                    new_height = int(width_var.get() * ratio)
                    height_var.set(new_height)
                    
            def on_height_change(*args):
                if maintain_ratio.get():
                    ratio = current_width / current_height
                    new_width = int(height_var.get() * ratio)
                    width_var.set(new_width)
                    
            width_var.trace('w', on_width_change)
            height_var.trace('w', on_height_change)
            
            def apply_resize():
                new_width = width_var.get()
                new_height = height_var.get()
                self.current_image = self.current_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.update_display()
                self.update_status(f"Image resized to {new_width} x {new_height}")
                dialog.destroy()
                
            ttk.Button(dialog, text="Apply", command=apply_resize).grid(row=4, column=0, columnspan=2, pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to resize image: {str(e)}")
            
    def rotate_image(self, angle):
        """Rotate image by specified angle"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image to rotate")
            return
            
        try:
            self.current_image = self.current_image.rotate(angle, expand=True)
            self.update_display()
            self.update_status(f"Image rotated {angle}°")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rotate image: {str(e)}")
            
    def flip_horizontal(self):
        """Flip image horizontally"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image to flip")
            return
            
        try:
            self.current_image = self.current_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            self.update_display()
            self.update_status("Image flipped horizontally")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to flip image: {str(e)}")
            
    def flip_vertical(self):
        """Flip image vertically"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image to flip")
            return
            
        try:
            self.current_image = self.current_image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            self.update_display()
            self.update_status("Image flipped vertically")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to flip image: {str(e)}")
            
    # Tools
    def color_picker(self):
        """Pick color from image"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image loaded")
            return
            
        self.current_tool = "color_picker"
        self.update_status("Click on image to pick color")
        
        def pick_color(event):
            if self.current_tool == "color_picker":
                x = int(self.canvas.canvasx(event.x) / self.zoom_factor)
                y = int(self.canvas.canvasy(event.y) / self.zoom_factor)
                
                try:
                    if 0 <= x < self.current_image.width and 0 <= y < self.current_image.height:
                        rgb = self.current_image.getpixel((x, y))
                        if isinstance(rgb, tuple):
                            color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
                        else:
                            color = f"#{rgb:02x}{rgb:02x}{rgb:02x}"
                        
                        self.current_color = color
                        self.color_button.config(bg=color)
                        self.current_tool = "select"
                        self.tool_var.set("select")
                        self.update_status(f"Color picked: {color}")
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to pick color: {str(e)}")
                    
        self.canvas.bind("<Button-1>", pick_color, add="+")
        
    def show_histogram(self):
        """Show histogram of the current image"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image loaded")
            return
            
        try:
            # Create histogram window
            hist_window = tk.Toplevel(self.root)
            hist_window.title("Image Histogram")
            hist_window.geometry("600x400")
            
            # Convert image to numpy array
            img_array = np.array(self.current_image)
            
            # Create matplotlib figure
            fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 4))
            
            if len(img_array.shape) == 3:  # Color image
                # Red channel
                ax1.hist(img_array[:,:,0].flatten(), bins=256, color='red', alpha=0.7)
                ax1.set_title('Red Channel')
                ax1.set_xlim(0, 255)
                
                # Green channel
                ax2.hist(img_array[:,:,1].flatten(), bins=256, color='green', alpha=0.7)
                ax2.set_title('Green Channel')
                ax2.set_xlim(0, 255)
                
                # Blue channel
                ax3.hist(img_array[:,:,2].flatten(), bins=256, color='blue', alpha=0.7)
                ax3.set_title('Blue Channel')
                ax3.set_xlim(0, 255)
            else:  # Grayscale image
                ax1.hist(img_array.flatten(), bins=256, color='gray', alpha=0.7)
                ax1.set_title('Grayscale Histogram')
                ax1.set_xlim(0, 255)
                ax2.axis('off')
                ax3.axis('off')
            
            plt.tight_layout()
            
            # Embed matplotlib in tkinter
            canvas = FigureCanvasTkAgg(fig, hist_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show histogram: {str(e)}")
            
    def apply_filter(self, filter_type):
        """Apply various filters to the image"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image loaded")
            return
            
        try:
            if filter_type == "blur":
                self.current_image = self.current_image.filter(ImageFilter.BLUR)
            elif filter_type == "sharpen":
                self.current_image = self.current_image.filter(ImageFilter.SHARPEN)
            elif filter_type == "edge":
                self.current_image = self.current_image.filter(ImageFilter.EDGE_ENHANCE)
            elif filter_type == "emboss":
                self.current_image = self.current_image.filter(ImageFilter.EMBOSS)
                
            self.update_display()
            self.update_status(f"Applied {filter_type} filter")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply filter: {str(e)}")
            
    def clear_selection(self):
        """Clear current selection"""
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
            self.selection_rect = None
        self.selection_start = None
        self.selection_end = None


# Import missing modules
import tkinter.simpledialog


if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoEditor(root)
    root.mainloop()