import os
import subprocess
import sys
import shutil  # For checking if required executables are available
from setuptools import setup, find_packages
from setuptools.command.install import install


class CustomInstallCommand(install):
    """Custom command to prepare the environment and invoke full_install.sh or full_install.bat."""

    def run(self):
        # Ensure pip is installed and upgraded in the current Python environment
        try:
            subprocess.run(
                [sys.executable, "-m", "ensurepip", "--upgrade"],
                check=True,
            )
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Failed to install or upgrade pip: {e}")
            sys.exit(1)

        # Run the standard installation process
        install.run(self)

        # Determine the appropriate installation script based on the OS
        script = "full_install.bat" if os.name == "nt" else "full_install.sh"
        script_path = os.path.join(os.path.dirname(__file__), script)

        # Check if the required executable (bash for .sh files) is available
        if script.endswith(".sh") and not shutil.which("bash"):
            print("Error: 'bash' is required to run full_install.sh but is not installed.")
            sys.exit(1)

        # Check if the script exists
        if os.path.exists(script_path):
            print(f"Running {script}...")

            # Redirect the script's output to a log file for better debugging
            with open("install_log.txt", "w") as log_file:
                try:
                    # Use 'bash' explicitly for .sh scripts or invoke directly for .bat
                    result = subprocess.run(
                        ["bash", script_path] if script.endswith(".sh") else [script_path],
                        stdout=log_file,
                        stderr=subprocess.STDOUT,
                        check=True,
                    )
                    if result.returncode != 0:
                        raise RuntimeError(f"{script} failed with exit code {result.returncode}")
                except subprocess.CalledProcessError as e:
                    print(f"Error occurred while running {script}: {e}")
                    sys.exit(1)
        else:
            print(f"{script} not found. Skipping custom installation step.")


setup(
    name="autogluon",
    version="1.2.0",
    description="Forked version of AutoGluon",
    author="Saeid",
    author_email="saeid@example.com",
    license="Apache-2.0",
    url="https://github.com/Saeidjamali/autogluon",
    packages=find_packages(
        include=["autogluon*", "core*", "tabular*", "timeseries*", "multimodal*", "features*", "eda*"],
        exclude=["examples", "docs", "CI", "release_instructions", "tests"],
    ),
    cmdclass={
        "install": CustomInstallCommand,
    },
)
