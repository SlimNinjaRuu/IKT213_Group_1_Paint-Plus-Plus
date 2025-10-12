# imports different classes from the PyQt library
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QMainWindow,
    QMenu,
    QLabel,
    QCheckBox,
    QStatusBar,
    QToolBar, QStyle,
)

import sys
import cv2

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Paint++")
        self.setMinimumSize(400, 300)

    #### This method creates the dropdown menu for File #####
    #### It does not contain the operations of the buttons #####
    def file_menu(self):

        menu = self.menuBar()

        ##### New button to create a new image ####
        new_ = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon), "New", self)
        new_.triggered.connect(self.toolbar_button_clicked)

        ##### Open file in File-menu #####
        open_ = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon), "Open", self)
        open_.triggered.connect(self.toolbar_button_clicked)

        ##### Save Button in File-menu #####
        save = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Save", self)
        save.triggered.connect(self.toolbar_button_clicked)

        ##### Save as Button in File-menu #####
        save_as = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Save as", self)
        save_as.triggered.connect(self.toolbar_button_clicked)

        ##### Properties Button in File-menu
        properties = QAction(QIcon("icons/icons8-settings.svg"), "Settings", self)
        properties.triggered.connect(self.toolbar_button_clicked)

        ##### Quit Button in File-menu #####
        quit_ = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserStop), "Exit Program", self)
        quit_.triggered.connect(self.toolbar_button_clicked)

        ##### Adds the Buttons to the menu #####
        file_menu = menu.addMenu("&File")
        file_menu.addAction(new_)
        file_menu.addAction(open_)
        file_menu.addAction(save)
        file_menu.addAction(save_as)
        file_menu.addAction(properties)
        file_menu.addAction(quit_)


    def edit_menu(self):
        menu = self.menuBar()

        edit_menu = menu.addMenu("&Edit")

    def image_menu(self):
        menu = self.menuBar()

        # Top-level Image menu
        image_menu = menu.addMenu("&Image")

        select_menu = QMenu("&Select", self)
        image_menu.addMenu(select_menu)  # add as a submenu under Image

        rectangular = QAction(QIcon("icons/icons8-rectangular.svg"), "Rectangular", self)
        #rectangular.triggered.connect(self.toolbar_button_clicked)

        lasso = QAction(QIcon("icons/icons8-lasso.svg"), "Lasso", self)

        polygon = QAction(QIcon("icons/icons8-polygon.svg"), "Polygon", self)

        select_menu.addAction(rectangular)
        select_menu.addAction(lasso)
        select_menu.addAction(polygon)

        # Regular actions
        crop = QAction(QIcon("icons/icons8-crop.svg"), "Crop", self)

        resize = QAction(QIcon("icons/icons8-resize.svg"), "Resize", self)

        image_menu.addAction(crop)
        image_menu.addAction(resize)

        # ---- Orientation submenu ----
        orientation_menu = QMenu("&Orientation", self)
        image_menu.addMenu(orientation_menu)  # add as a submenu under Image

        rotate_right = QAction(QIcon("icons/icons8-rotate_right.svg"), "Rotate right", self)

        rotate_left = QAction(QIcon("icons/icons8-rotate_left.svg"), "Rotate left", self)

        flip_horizontal = QAction(QIcon("icons/icons8-flip_horizontal.svg"), "Flip horizontal", self)

        flip_vertical = QAction(QIcon("icons/icons8-flip_vertical.svg"), "Flip vertical", self)

        # Add to submenu (grouped with a separator)
        orientation_menu.addAction(rotate_right)
        orientation_menu.addAction(rotate_left)
        orientation_menu.addAction(flip_horizontal)
        orientation_menu.addAction(flip_vertical)

    def toolbar_button_clicked(self):
        print("click", s)

def main():

    # creates an object from the QApplication class (classname() means to create object)
    app = QApplication(sys.argv)

    # creates an object from the QWidget class
    window = MainWindow()
    window.show() # IMPORTANT!!!!! Windows are hidden by default, so call the show method
    window.file_menu()
    window.edit_menu()
    window.image_menu()
    app.exec()

if __name__ == '__main__':
    main()