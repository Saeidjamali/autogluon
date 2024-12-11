import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py


class CustomBuildCommand(build_py):
    """Custom build command to execute full_install.sh during wheel creation."""

    def run(self):
        # Run the standard build process
        build_py.run(self)

        # Run the full_install.sh script
        script = "full_install.bat" if os.name == "nt" else "full_install.sh"
        script_path = os.path.join(os.path.dirname(__file__), script)

        if os.path.exists(script_path):
            print(f"Running {script} during wheel build...")
            try:
                # Execute the script
                subprocess.run(
                    ["bash", script_path] if script.endswith(".sh") else [script_path],
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                print(f"Error running {script}: {e}")
                raise RuntimeError(f"Failed to execute {script}")
        else:
            print(f"{script} not found. Skipping custom build step.")


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
        "build_py": CustomBuildCommand,
    },
)
