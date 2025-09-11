from PySide6 import QtCore, QtGui, QtWidgets


class Header(QtWidgets.QWidget):
    """
    A simple header widget that displays an image.
    """
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(640, 200)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        image_label = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(image_path).scaled(
            self.size(),
            QtCore.Qt.KeepAspectRatioByExpanding,
            QtCore.Qt.SmoothTransformation
        )
        image_label.setPixmap(pixmap)
        
        layout.addWidget(image_label)
