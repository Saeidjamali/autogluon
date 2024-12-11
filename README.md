Below is the revised documentation with concrete version and file names that were used as examples during our building and testing process.

---

## Overview

We refactored the packaging and build process of AutoGluon to produce a single wheel (`.whl`) file that includes all submodules, aligns with PEP 517/518 standards, and integrates cleanly with external dependency managers like Poetry.

Previously, each submodule (`core`, `tabular`, `multimodal`, `timeseries`, `eda`, `features`, `common`) had its own `setup.py` and separate installation logic. Dependencies and version handling were spread across multiple files, and `version.py` files were attempted to be created multiple times at different build steps, causing confusion and errors when generating source distributions (sdist) and wheels.

Our changes centralize the build logic into a top-level `setup.py` and a single `_setup_utils.py`, ensuring:

- A single, unified wheel containing all modules.
- A consistent `version.py` file creation process.
- Proper inclusion of all necessary metadata files (`VERSION`, `LICENSE`, `NOTICE`, `README.md`) in the source distribution and wheel.
- Consistent handling of `install_requires` and dependency version ranges so that Poetry and other tools can correctly parse and install dependencies.

---

## Key Changes Made

1. **Centralized the Top-Level `setup.py`**  
   Instead of relying on multiple `setup.py` files in submodules, we introduced a top-level `setup.py` at the project root. This file:
   - Invokes `_setup_utils.py` to load version and dependency logic.
   - Collects dependencies for all submodules into a single `install_requires` list.
   - Uses `find_namespace_packages` and `package_dir` to discover packages under `core/src` without referencing multiple separate `src` directories.
   - Calls `create_version_file` only once, ensuring a single `version.py` file is created in the correct location.

2. **Adjusting `_setup_utils.py`**  
   In `_setup_utils.py`, we:
   - Standardized `AUTOGLUON_ROOT_PATH` to point to the project root.
   - Updated `create_version_file` to write `version.py` into `core/src/autogluon/`.
   - Ensured `VERSION` and `VERSION.minor` files are read from the project root and included in the sdist.
   - Removed or avoided duplication of paths that previously caused `FileNotFoundError`.

3. **Manifest and Inclusion of Files**  
   We ensured that `MANIFEST.in` at the project root includes `VERSION`, `LICENSE`, `NOTICE`, and any other required files. This ensures the sdist (`.tar.gz`) distribution is complete and that no files go missing when the sdist is used to build the wheel.

4. **Removing Multiple Calls to `create_version_file`**  
   Previously, each module’s `setup.py` might have called `create_version_file`. We removed these extra calls, leaving a single call in the top-level `setup.py`. This avoids path conflicts and ensures `version.py` is only created once.

5. **Aligning Package Directories**  
   We used:
   ```python
   packages=find_namespace_packages(where="core/src", include=["autogluon*"])
   package_dir={"": "core/src"}
   ```
   in the top-level `setup.py`. This instructs setuptools that the root of our package code is at `core/src`, and that all `autogluon.*` packages live under this directory.

6. **Namespace Packages and PEP 420**  
   We removed explicit `namespace_packages` usage (or plan to remove it), relying on PEP 420 implicit namespaces. This avoids deprecation warnings and simplifies package discovery.

---

## How to Generate a New Wheel Each Time

After applying all the changes described above, you can follow these steps to produce a new wheel each time you modify the code.

### Example Version and Filenames Used

- Version used in testing: `1.2.1b20241211`
- Generated sdist: `autogluon-1.2.1b20241211.tar.gz`
- Generated wheel: `autogluon-1.2.1b20241211-py3-none-any.whl`

### Steps to Build the Wheel

1. **Ensure a Clean Working Directory**  
   Remove previous build artifacts:
   ```bash
   rm -rf build dist *.egg-info
   ```

2. **Check Files and MANIFEST.in**  
   - Ensure `VERSION` is in the project root.
   - Ensure `MANIFEST.in` includes `VERSION`, `LICENSE`, `NOTICE`, and `README.md`.
   - Confirm that `_setup_utils.py` points to `core/src/autogluon/version.py` correctly and that `create_version_file` references the correct directories.

3. **Build the sdist and Wheel**  
   Run:
   ```bash
   python -m build
   ```
   After this command, you should see the following files in `dist/`:
   - `autogluon-1.2.1b20241211.tar.gz`
   - `autogluon-1.2.1b20241211-py3-none-any.whl`

4. **Verify the Artifacts**  
   Check the contents of the sdist:
   ```bash
   tar -tzvf dist/autogluon-1.2.1b20241211.tar.gz | grep VERSION
   ```
   Should show `VERSION` included.

   Check the wheel:
   ```bash
   unzip -l dist/autogluon-1.2.1b20241211-py3-none-any.whl | grep version.py
   ```
   Should show `autogluon/version.py` included.

5. **Test Installation**  
   Install the wheel in a fresh environment:
   ```bash
   python3 -m venv test_env
   source test_env/bin/activate   # Unix
   # On Windows: test_env\Scripts\activate

   pip install dist/autogluon-1.2.1b20241211-py3-none-any.whl
   python -c "import autogluon; print(autogluon.__version__)"
   ```
   This should print `1.2.1b20241211`, confirming that `version.py` is created and `__version__` is correctly set.

6. **Repeat for Each Update**  
   After making code changes, just increment or adjust the version if needed and repeat the build steps:
   ```bash
   rm -rf build dist *.egg-info
   python -m build
   ```

---

## Optional: Test Dependency Resolution with Poetry

If you want to ensure Poetry compatibility:

1. Inside another directory:
   ```bash
   mkdir poetry_test && cd poetry_test
   poetry init --no-interaction
   ```

2. Add the wheel:
   ```bash
   poetry add ../autogluon/dist/autogluon-1.2.1b20241211-py3-none-any.whl
   poetry install
   ```

   If Poetry successfully installs the package and dependencies, it confirms that the wheel metadata is correct.

---

## Conclusion

By consolidating builds under a single `setup.py` and `_setup_utils.py`, ensuring proper inclusion of `VERSION` and other metadata files, and standardizing the package directory structure (`core/src`), you can now reliably produce a wheel that includes all requirements and metadata. The wheel can be easily tested, installed, and integrated into Poetry-based projects or other dependency management environments.