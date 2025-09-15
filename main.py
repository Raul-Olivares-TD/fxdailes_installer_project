"""
Script for initialize the app.
"""
import sys
from PySide6 import QtWidgets
from fxdailes_installer.main_window import InstallerWindow


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = InstallerWindow()
    window.show()
    sys.exit(app.exec())
