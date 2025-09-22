
# imports different classes from the PyQt library
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QMainWindow,
    QLabel,
    QCheckBox,
    QStatusBar,
    QToolBar, QStyle,
)

import sys


def main():

    # creates an object from the QApplication class (classname() means to create object)
    app = QApplication(sys.argv)

    # creates an object from the QWidget class
    window = MainWindow()
    window.show() # IMPORTANT!!!!! Windows are hidden by default, so calle the show method
    window.file_menu()
    window.edit_menu()
    app.exec()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Paint++")
        self.resize(900, 600) # Better then fixed sized





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


    def toolbar_button_clicked(self, s):
        print("click", s)


if __name__ == '__main__':
    main()