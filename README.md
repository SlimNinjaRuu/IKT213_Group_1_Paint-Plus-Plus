# Photo Editing Desktop Application - Group 1

A comprehensive desktop photo editing application built with Python and tkinter, featuring all essential image editing tools and capabilities.

## Features

### File Operations
- **New**: Create a new blank image with custom dimensions
- **Open**: Load images in various formats (JPEG, PNG, BMP, GIF, TIFF)
- **Save**: Save the current image
- **Save As**: Save the image with a new name or format
- **Quit**: Exit the application

### Clipboard Operations
- **Copy**: Copy selected area to clipboard
- **Cut**: Cut selected area to clipboard (removes from image)
- **Paste**: Paste clipboard content to the image

### Image Operations
- **Selections**: Select rectangular areas for operations
- **Crop**: Crop image to selected area
- **Resize**: Resize image with optional aspect ratio maintenance
- **Rotate**: Rotate image 90° clockwise or counterclockwise
- **Flip**: Flip image horizontally or vertically

### Tools
- **Zoom**: Zoom in, zoom out, and fit to canvas
- **Erase**: Eraser tool with adjustable size
- **Color Picker**: Pick colors from the image
- **Brushes**: Paint brush with color and size selection
- **Text**: Add text to images
- **Filters**: Apply blur, sharpen, edge enhance, and emboss filters
- **Histogram**: View RGB channel histograms

### Shapes
- **Rectangle**: Draw rectangles with customizable color and line width
- **Circle**: Draw circles/ellipses with customizable color and line width

### Colors
- **Color Chooser**: Select colors using a color picker dialog
- **Current Color Display**: Shows the currently selected color
- **Color Picker Tool**: Pick colors directly from the image

## Requirements

- Python 3.7 or higher
- tkinter (usually included with Python)
- Pillow (PIL) >= 9.0.0
- numpy >= 1.21.0
- matplotlib >= 3.5.0

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd IKT213_Group_1_Photo_Editing_Desktop_Application-
   ```

2. Run the setup script:
   ```bash
   python setup.py
   ```

   Or install dependencies manually:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python photo_editor.py
```

### Basic Workflow

1. **Create or Open an Image**:
   - File → New to create a blank canvas
   - File → Open to load an existing image

2. **Select Tools**:
   - Use the toolbar to select different tools (Select, Brush, Eraser, Text, Rectangle, Circle)
   - Adjust brush size using the slider
   - Choose colors using the color button

3. **Edit Your Image**:
   - Make selections and crop, resize, or apply filters
   - Draw with brushes or add shapes
   - Add text annotations
   - Use the eraser to remove unwanted parts

4. **Save Your Work**:
   - File → Save or Save As to export your edited image

### Keyboard Shortcuts

- `Ctrl + N`: New image
- `Ctrl + O`: Open image
- `Ctrl + S`: Save image
- `Ctrl + C`: Copy selection
- `Ctrl + X`: Cut selection
- `Ctrl + V`: Paste
- `Ctrl + Q`: Quit application
- `+`: Zoom in
- `-`: Zoom out

## Project Structure

```
IKT213_Group_1_Photo_Editing_Desktop_Application-/
├── photo_editor.py          # Main application file
├── requirements.txt         # Python dependencies
├── setup.py                # Setup and installation script
└── README.md               # This file
```

## Technical Details

### Architecture
- **GUI Framework**: tkinter for cross-platform desktop interface
- **Image Processing**: Pillow (PIL) for image manipulation
- **Data Analysis**: numpy for efficient array operations
- **Visualization**: matplotlib for histogram display

### Core Classes
- `PhotoEditor`: Main application class handling UI and image operations

### Key Components
1. **Menu System**: Comprehensive menu bar with all features
2. **Toolbar**: Quick access to tools and settings
3. **Canvas**: Scrollable image display with zoom capabilities
4. **Status Bar**: Real-time feedback and information

## Development Team

Group 1 - IKT213 Project

## License

This project is developed as part of the IKT213 course curriculum.

## Contributing

This is a team project for IKT213. Team members can contribute by:
1. Forking the repository
2. Creating feature branches
3. Submitting pull requests
4. Following the coding standards established in the main application

## Troubleshooting

### Common Issues

1. **"No module named 'PIL'"**: Install Pillow using `pip install Pillow`
2. **"No module named 'tkinter'"**: tkinter should be included with Python. On Linux, install `python3-tk`
3. **Font errors when adding text**: The application will fall back to default font if system fonts are not available

### System Requirements

- **Windows**: Python 3.7+ with tkinter
- **macOS**: Python 3.7+ with tkinter
- **Linux**: Python 3.7+ with tkinter and python3-tk package

## Future Enhancements

Potential additions for future versions:
- Layer support for advanced editing
- More sophisticated filters and effects
- Undo/Redo functionality
- Plugin system for custom tools
- Batch processing capabilities
