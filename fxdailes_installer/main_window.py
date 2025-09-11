import subprocess
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets

from .utils import resource_path
from .ui.components import Header
from .ui.pages import BinPath, ProjectPath, TermsConditions, ProgressBar, Finish
from .installer_logic import InstallerLogic


class InstallerWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FXDailes Pipeline Installer")
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        self.setFixedSize(640, 450)
        self.setWindowIcon(QtGui.QIcon(resource_path("logoApp03.png")))
        self.setObjectName("fondo")

        self._load_stylesheet()

        self.worker = None
        self.thread = None

        self._setup_ui()
        self._update_button_states()

    def _load_stylesheet(self):
        """Loads the external stylesheet."""
        try:
            with open(resource_path("styles.qss"), "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Stylesheet not found.") # Fallback or error logging

    def _setup_ui(self):
        """
        Initializes the UI layout and widgets.
        """
        self.main_lyt = QtWidgets.QVBoxLayout(self)
        self.main_lyt.setContentsMargins(0, 0, 0, 0)

        # Header
        self.main_lyt.addWidget(Header(resource_path("installer2.png")))

        # Stacked widget for pages
        self.stack = QtWidgets.QStackedWidget()
        self.page1 = BinPath(parent=self)
        self.page2 = ProjectPath(parent=self)
        self.page3 = TermsConditions(parent=self)
        self.page4 = ProgressBar(parent=self)
        self.page5 = Finish(parent=self)

        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)
        self.stack.addWidget(self.page3)
        self.stack.addWidget(self.page4)
        self.stack.addWidget(self.page5)

        self.main_lyt.addWidget(self.stack)

        # Navigation buttons
        self.back_btn = QtWidgets.QPushButton("BACK")
        self.back_btn.setObjectName("nav")
        self.next_btn = QtWidgets.QPushButton("NEXT")
        self.next_btn.setObjectName("nav")
        self.install_btn = QtWidgets.QPushButton("INSTALL")
        self.install_btn.setObjectName("nav")
        self.finish_btn = QtWidgets.QPushButton("FINISH")
        self.finish_btn.setObjectName("nav")

        nav_lyt = QtWidgets.QHBoxLayout()
        nav_lyt.setContentsMargins(0, 0, 30, 30)
        nav_lyt.addStretch()
        nav_lyt.addWidget(self.back_btn)
        nav_lyt.addWidget(self.next_btn)
        nav_lyt.addWidget(self.install_btn)
        nav_lyt.addWidget(self.finish_btn)
        self.main_lyt.addLayout(nav_lyt)

        # Connect signals
        self.page1.browse_btn.clicked.connect(lambda: self._browse_folder(self.page1.path_le))
        self.page2.browse_btn.clicked.connect(lambda: self._browse_folder(self.page2.path_le))
        self.stack.currentChanged.connect(self._update_button_states)
        self.next_btn.clicked.connect(self._go_next)
        self.back_btn.clicked.connect(self._go_back)
        self.install_btn.clicked.connect(self.start_installation)
        self.finish_btn.clicked.connect(self.finish_application)

    def _update_button_states(self):
        """
        Manages the visibility of navigation buttons based on the current page.
        """
        current_index = self.stack.currentIndex()
        self.back_btn.setVisible(current_index > 0 and current_index < 3)
        self.next_btn.setVisible(current_index < 2)
        self.install_btn.setVisible(current_index == 2)
        self.finish_btn.setVisible(current_index == 4)

    def _browse_folder(self, line_edit_widget: QtWidgets.QLineEdit):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose Folder", "C:/")
        if folder:
            line_edit_widget.setText(folder.replace("/", "\\"))

    def _go_next(self):
        """
        Logic for the 'Next' button.
        """
        current_index = self.stack.currentIndex()
        if current_index == 0:
            bin_path = self.page1.path_le.text()
            if bin_path == "" or not bin_path.lower().endswith("bin"):
                 QtWidgets.QMessageBox.warning(self, "Warning", "Please select a valid Houdini 'bin' folder!")
                 return
        elif current_index == 1:
            project_path = self.page2.path_le.text()
            if project_path == "":
                QtWidgets.QMessageBox.warning(self, "Warning", "Please select a valid project folder!")
                return
        
        self.stack.setCurrentIndex(current_index + 1)
    
    def _go_back(self):
        """
        Logic for the 'Back' button.
        """
        self.stack.setCurrentIndex(self.stack.currentIndex() - 1)

    def start_installation(self):
        """
        Prepares and starts the installation in a separate thread.
        """
        if not self.page3.accept_check.isChecked():
            QtWidgets.QMessageBox.warning(
                self, "Warning", 
                "You must accept the terms and conditions to install."
            )
            return

        self.stack.setCurrentIndex(3) # Switch to progress bar page
        self.back_btn.setEnabled(False)
        self.install_btn.setEnabled(False)

        bin_path = self.page1.path_le.text()
        project_path = self.page2.path_le.text()

        self.thread = QtCore.QThread()
        self.worker = InstallerLogic(bin_path, project_path)
        self.worker.moveToThread(self.thread)

        # Connect signals from the worker to slots in the UI
        self.thread.started.connect(self.worker.run_installation)
        self.worker.progress_updated.connect(self.on_progress_update)
        self.worker.installation_finished.connect(self.on_installation_finished)
        
        self.thread.start()

    def on_progress_update(self, percentage: int, message: str):
        """
        Updates the progress bar and status label.
        """
        self.page4.progress_bar.setValue(percentage)
        self.page4.status_label.setText(message)

    def on_installation_finished(self, success: bool, message: str):
        """
        Handles the completion of the installation.
        """
        self.page4.status_label.setText(message)
        if success:
            self.stack.setCurrentIndex(4) # Go to finish page
        else:
            QtWidgets.QMessageBox.critical(self, "Installation Failed", message)
            self.stack.setCurrentIndex(2) # Go back to terms page
        
        # Cleanup thread
        self.thread.quit()
        self.thread.wait()
        self.thread = None
        self.worker = None

    def finish_application(self):
        """
        Closes the application and optionally starts Houdini.
        """
        if self.page5.run_houdini_check.isChecked():
            houdini_exe = Path(self.page1.path_le.text()) / "houdini.exe"
            if houdini_exe.exists():
                subprocess.Popen([str(houdini_exe)])
        self.close()

    def closeEvent(self, event: QtGui.QCloseEvent):
        """
        Ensures the worker thread is stopped before closing.
        """
        if self.thread and self.thread.isRunning():
            event.ignore() # Prevent closing while installing
        else:
            event.accept()
