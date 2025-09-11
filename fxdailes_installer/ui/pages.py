from PySide6 import QtWidgets, QtCore
from ..utils import resource_path


class BinPath(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_lyt = QtWidgets.QVBoxLayout(self)
        main_lyt.setContentsMargins(30, 25, 30, 0)
        
        title = QtWidgets.QLabel("Select your Houdini 'bin' folder:")
        title.setObjectName("pageTitle")

        info_txt = QtWidgets.QLabel(
            """Select the folder where the Houdini version is installed to get the bin folder.\nExample: 'C:\\Program Files\\Side Effects Software\\Houdini 20.5.684\\bin'"""
        )
        info_txt.setObjectName("infoText")
        info_txt.setWordWrap(True)

        self.path_le = QtWidgets.QLineEdit()
        self.browse_btn = QtWidgets.QToolButton()
        self.browse_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DirIcon))

        path_lyt = QtWidgets.QHBoxLayout()
        path_lyt.addWidget(self.path_le)
        path_lyt.addWidget(self.browse_btn)

        main_lyt.addWidget(title)
        main_lyt.addWidget(info_txt)
        main_lyt.addSpacing(5)
        main_lyt.addLayout(path_lyt)
        main_lyt.addStretch()


class ProjectPath(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_lyt = QtWidgets.QVBoxLayout(self)
        main_lyt.setContentsMargins(30, 25, 30, 0)
        
        title = QtWidgets.QLabel("Select your Project folder:")
        title.setObjectName("pageTitle")
        
        info_txt = QtWidgets.QLabel(
            """This is the folder where all the project files (assets, textures, shots, caches) will be stored.
At least 1Tb of storage (SSD or Nvme m.2) it's recommended."""
        )
        info_txt.setObjectName("infoText")
        info_txt.setWordWrap(True)

        self.path_le = QtWidgets.QLineEdit()
        self.browse_btn = QtWidgets.QToolButton()
        self.browse_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DirIcon))

        path_lyt = QtWidgets.QHBoxLayout()
        path_lyt.addWidget(self.path_le)
        path_lyt.addWidget(self.browse_btn)

        main_lyt.addWidget(title)
        main_lyt.addWidget(info_txt)
        main_lyt.addSpacing(5)
        main_lyt.addLayout(path_lyt)
        main_lyt.addStretch()


class TermsConditions(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_lyt = QtWidgets.QVBoxLayout(self)
        main_lyt.setContentsMargins(30, 15, 30, 0)

        title = QtWidgets.QLabel("Pipeline Usage Agreement.")
        title.setObjectName("pageTitle")
        
        text_edit = QtWidgets.QTextEdit()
        text_edit.setReadOnly(True)
        try:
            with open(resource_path("UseAgreement.txt"), "r") as f:
                text_edit.setText(f.read())
        except FileNotFoundError:
            text_edit.setText("Could not load UseAgreement.txt.")

        self.accept_check = QtWidgets.QCheckBox("Accept Terms and Conditions.")
        
        main_lyt.addWidget(title)
        main_lyt.addWidget(text_edit)
        main_lyt.addWidget(self.accept_check)
        main_lyt.addStretch()


class ProgressBar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_lyt = QtWidgets.QVBoxLayout(self)
        main_lyt.setContentsMargins(30, 20, 30, 0)

        title = QtWidgets.QLabel("Installing Pipeline.")
        title.setObjectName("pageTitle")
        
        info_txt = QtWidgets.QLabel(
            """The installation process may take a few minutes.\nPlease do not close any window while the Pipeline is being installed."""
        )
        info_txt.setObjectName("infoText")

        self.progress_bar = QtWidgets.QProgressBar()
        self.status_label = QtWidgets.QLabel()
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)

        main_lyt.addWidget(title)
        main_lyt.addWidget(info_txt)
        main_lyt.addSpacing(10)
        main_lyt.addWidget(self.progress_bar)
        main_lyt.addWidget(self.status_label)
        main_lyt.addStretch()


class Finish(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_lyt = QtWidgets.QVBoxLayout(self)
        main_lyt.setContentsMargins(30, 45, 30, 0)
        
        title = QtWidgets.QLabel("Pipeline Installed.")
        title.setObjectName("finishTitle")

        self.run_houdini_check = QtWidgets.QCheckBox("Run Houdini")

        main_lyt.addWidget(title)
        main_lyt.addSpacing(15)
        main_lyt.addWidget(self.run_houdini_check)
        main_lyt.addStretch()
