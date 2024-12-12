import os
import re
import sys
from setuptools import setup, find_namespace_packages
import subprocess

# Define the root directory of your project
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Directories to exclude (remove 'core' from exclusions)
EXCLUDED_DIRS = {"CI", "release_instructions"}

# Function to validate dependencies
def validate_dependency(dep):
    # Regex for a valid dependency (simplified for common cases)
    pattern = r"^[a-zA-Z0-9_\-\.]+(\[.*\])?(>=|<=|==|!=|<|>|~=)?.*$"
    return re.match(pattern, dep)

# Function to extract dependencies from a setup.py
def extract_dependencies(setup_py_path):
    dependencies = []
    try:
        setup_globals = {"__file__": setup_py_path}  # Define __file__ for execution context
        setup_locals = {}
        with open(setup_py_path, "r") as f:
            setup_content = f.read()
            # Execute the setup.py file to extract dependencies dynamically
            exec(setup_content, setup_globals, setup_locals)
            if "install_requires" in setup_locals:
                dependencies = setup_locals["install_requires"]
        # Validate dependencies
        valid_deps = []
        for dep in dependencies:
            if validate_dependency(dep):
                valid_deps.append(dep)
            else:
                print(f"Warning: Invalid dependency '{dep}' in {setup_py_path}. Skipping...")
        return valid_deps
    except Exception as e:
        print(f"Error reading dependencies from {setup_py_path}: {e}")
    return []

# Function to build a submodule
def build_submodule(setup_py_path):
    print(f"Building submodule: {setup_py_path}")
    try:
        subprocess.check_call([sys.executable, "setup.py", "sdist", "bdist_wheel"], cwd=os.path.dirname(setup_py_path))
        print(f"Successfully built {setup_py_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to build {setup_py_path}: {e}")
        sys.exit(1)

# Function to gather dependencies from all module setup.py files
def gather_all_dependencies():
    dependencies = set()  # Use a set to avoid duplicates
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        if "setup.py" in files and root != PROJECT_ROOT:
            setup_py_path = os.path.join(root, "setup.py")
            module_dependencies = extract_dependencies(setup_py_path)
            if module_dependencies:
                dependencies.update(module_dependencies)
    return list(dependencies)

# Build 'core' first
core_setup_py = os.path.join(PROJECT_ROOT, "core", "setup.py")
if os.path.isfile(core_setup_py):
    build_submodule(core_setup_py)

# Now gather dependencies from other submodules
install_requires = gather_all_dependencies()

# Log all dependencies for debugging
print("Final install_requires dependencies:")
for dep in install_requires:
    print(f"  - {dep}")

# Dynamically load the version
def load_version_file():
    version_file_path = os.path.join(PROJECT_ROOT, "VERSION")
    if not os.path.exists(version_file_path):
        raise FileNotFoundError(f"VERSION file not found at {version_file_path}. Please create one with the desired version.")
    with open(version_file_path, "r") as version_file:
        version = version_file.read().strip()
    return version

# Main setup configuration
setup(
    name="autogluon",
    version=load_version_file(),
    packages=find_namespace_packages(where="core/src", include=["autogluon*"]),
    package_dir={"": "core/src"},
    install_requires=install_requires,
    python_requires=">=3.9, <3.13",
    include_package_data=True,
    zip_safe=False,
)
