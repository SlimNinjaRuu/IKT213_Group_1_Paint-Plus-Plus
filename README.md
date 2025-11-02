# IKT213_Group_1_Photo_Editing_Desktop_Application-
This is the Repo for group 1 where the project will be.

# Paint++

Paint++ is a desktop image editor built with PyQt6 and OpenCV. It provides a scrollable canvas for viewing images, file management actions, and standalone helpers for resizing, cropping, rotating, and flipping pictures.

## Requirements
- Python 3.11+
- PyQt6
- OpenCV (cv2)

Install dependencies with [Pipenv](https://pipenv.pypa.io/en/latest/):

```bash
pipenv install
```

## Running the App
Launch the GUI from the project root:

```bash
pipenv run python Paint++/main.py
```

The main window lets you open images, pan around the canvas, and experiment with future editing features exposed in the menu bar.

## Repository Structure
- `Paint++/main.py` – application entry point and menu setup.
- `Paint++/img_canvas.py` – custom widget that displays the current image with panning support.
- `Paint++/image_menu.py` – sample OpenCV routines for crop/resize/rotate/flip operations.
- `Paint++/selection tools.py` – experimental lasso, polygon, and rectangular selection tools.
- `Paint++/icons/` – SVG assets used by menu actions.

## License
This project is maintained by IKT213 Group 1. See repository history for details.
