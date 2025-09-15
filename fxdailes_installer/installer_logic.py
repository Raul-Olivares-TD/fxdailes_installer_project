import configparser
import json
import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
from PySide6.QtCore import QObject, Signal


class InstallerLogic(QObject):
    # Signals to communicate with the UI thread
    progress_updated = Signal(int, str)  # percentage, message
    installation_finished = Signal(bool, str) # success, message

    def __init__(self, bin_path: str, project_path: str):
        """
        Handles all the backend logic for the pipeline installation.
        This runs on a separate thread to avoid freezing the UI.

        Args:
            bin_path (str): Path with the houdini bin folder.
            project_path (str): Path with the project folder.
        """
        super().__init__()
        self.houdini_bin_path = Path(bin_path)
        self.project_path = Path(project_path)
        self.hython_exe = self.houdini_bin_path / "hython.exe"
        
        # Paths for resources needed during installation
        # Note: These paths should be resolved in the main thread before starting
        self.pipeline_source_path = self._resource_path_logic("Pipeline")
        self.get_pip_script_path = self._resource_path_logic("get-pip.py", is_asset=False)

    def _resource_path_logic(self, relative_path, is_asset=True) -> str:
        """
        Internal resource path resolver.
        """
        # This logic is simplified for the backend. A more robust solution might pass
        # the base path during initialization.
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        if is_asset:
             return os.path.join(base_path, 'fxdailes_installer', 'assets', relative_path)
        return os.path.join(base_path, relative_path)

    def run_installation(self):
        """
        The main method that executes the installation steps.
        """
        try:
            total_steps = 8
            
            self.progress_updated.emit(int(1/total_steps * 100), "Getting Houdini preferences directory...")
            time.sleep(0.5)
            pref_dir = self._get_houdini_pref_dir()
            
            self.progress_updated.emit(int(2/total_steps * 100), "Creating environment JSON file...")
            time.sleep(0.5)
            self._create_env_json(pref_dir)

            self.progress_updated.emit(int(3/total_steps * 100), "Creating configuration file...")
            time.sleep(0.5)
            self._create_config_file()

            self.progress_updated.emit(int(4/total_steps * 100), "Copying pipeline files...")
            shutil.copytree(self.pipeline_source_path, self.project_path / "Pipeline", dirs_exist_ok=True)

            self.progress_updated.emit(int(5/total_steps * 100), "Checking and installing pip...")
            if not self._is_pip_installed():
                subprocess.run([str(self.hython_exe), self.get_pip_script_path], check=True, capture_output=True)

            self.progress_updated.emit(int(6/total_steps * 100), "Checking and installing Gazu...")
            if not self._is_package_installed("gazu"):
                subprocess.run([str(self.hython_exe), "-m", "pip", "install", "gazu"], check=True, capture_output=True)

            self.progress_updated.emit(int(7/total_steps * 100), "Checking and installing Ffmpeg...")
            if not self._is_package_installed("ffmpeg-python"):
                subprocess.run([str(self.hython_exe), "-m", "pip", "install", "ffmpeg-python"], check=True, capture_output=True)

            self.progress_updated.emit(int(8/total_steps * 100), "Finishing installation...")
            time.sleep(0.5)

            self.installation_finished.emit(True, "Installation complete!")

        except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
            self.installation_finished.emit(False, f"An error occurred: {e}")

    def _get_houdini_pref_dir(self) -> Path:
        """
        Gets the HOUDINI_USER_PREF_DIR from Houdini.
        """
        cmd = [str(self.hython_exe), "-c", "import hou; print(hou.getenv('HOUDINI_USER_PREF_DIR'))"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return Path(result.stdout.strip())

    def _create_env_json(self, pref_dir: Path):
        """
        Creates the package JSON file for Houdini.
        """
        packages_path = pref_dir / "packages"
        packages_path.mkdir(parents=True, exist_ok=True)
        json_content = {
            "hpath": "$PIPE",
            "env": [{"PIPE": (self.project_path / "Pipeline").as_posix()}]
        }
        with open(packages_path / "fxdpipe.json", "w") as f:
            json.dump(json_content, f, indent=4)

    def _create_config_file(self):
        """
        Creates the credentials.ini file.
        """
        config = configparser.ConfigParser()
        config_path = self.project_path / "Pipeline" / "config"
        config_path.mkdir(parents=True, exist_ok=True)
        config['PROJECT'] = {'folderpath': self.project_path.as_posix()}
        with open(config_path / "credentials.ini", "w") as f:
            config.write(f)

    def _is_pip_installed(self) -> bool:
        """
        Checks if pip is installed in Houdini's Python.
        """
        try:
            subprocess.run([str(self.hython_exe), "-m", "pip", "--version"], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def _is_package_installed(self, package_name: str) -> bool:
        """
        Checks if a specific Python package is installed.
        """
        try:
            subprocess.run([str(self.hython_exe), "-m", "pip", "show", package_name], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
