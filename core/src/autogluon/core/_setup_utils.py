"""Setup utils for autogluon. Only used for installing the code via setup.py, do not import after installation."""

import os

AUTOGLUON = "autogluon"
PACKAGE_NAME = os.getenv("AUTOGLUON_PACKAGE_NAME", AUTOGLUON)
# TODO: make it more explicit, maybe use another env variable
LITE_MODE = "lite" in PACKAGE_NAME

# Set AUTOGLUON_ROOT_PATH to the project root relative to this file
# Assuming this file is located at core/src/autogluon/core/_setup_utils.py
AUTOGLUON_ROOT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..")
)
# AUTOGLUON_ROOT_PATH now points to /Users/saeid/Workspace/GitHub/autogluon

PYTHON_REQUIRES = ">=3.9, <3.13"

# Only put packages here that would otherwise appear multiple times across different module's setup.py files.
DEPENDENT_PACKAGES = {
    "boto3": ">=1.10,<2",
    "numpy": ">=1.25.0,<2.1.4",
    "pandas": ">=2.0.0,<2.3.0",
    "scikit-learn": ">=1.4.0,<1.5.3",
    "scipy": ">=1.5.4,<1.16",
    "matplotlib": ">=3.7.0,<3.11",
    "psutil": ">=5.7.3,<7.0.0",
    "s3fs": ">=2023.1,<2025",
    "networkx": ">=3.0,<4",
    "tqdm": ">=4.38,<5",
    "Pillow": ">=10.0.1,<12",
    "torch": ">=2.2,<2.6",
    "lightning": ">=2.2,<2.6",
    "async_timeout": ">=4.0,<6",
    "transformers[sentencepiece]": ">=4.38.0,<5",
    "accelerate": ">=0.34.0,<1.0",
}

if LITE_MODE:
    DEPENDENT_PACKAGES = {
        package: version
        for package, version in DEPENDENT_PACKAGES.items()
        if package not in ["psutil", "Pillow", "timm"]
    }

DEPENDENT_PACKAGES = {
    package: package + version for package, version in DEPENDENT_PACKAGES.items()
}

# TODO: Use DOCS_PACKAGES and TEST_PACKAGES
DOCS_PACKAGES = []
TEST_PACKAGES = [
    "flake8",
    "pytest",
]


def load_version_file():
    """
    Load the version from the VERSION file located at the project root.
    """
    version_file_path = os.path.join(AUTOGLUON_ROOT_PATH, "core", "src", "autogluon", "VERSION")
    print(f"Looking for VERSION file at: {version_file_path}")  # Debugging path

    if not os.path.isfile(version_file_path):
        raise FileNotFoundError(f"VERSION file not found at {version_file_path}")

    with open(version_file_path, "r") as version_file:
        version = version_file.read().strip()

    return version


def get_dependency_version_ranges(packages: list) -> list:
    """
    Get the version ranges for the given list of packages.
    """
    return [
        package if package not in DEPENDENT_PACKAGES else DEPENDENT_PACKAGES[package]
        for package in packages
    ]


def update_version(version, use_file_if_exists=True, create_file=False):
    """
    Update the version string by appending the current date or a minor version.

    To release a new stable version on PyPi, simply tag the release on GitHub, and the GitHub CI will
    automatically publish a new stable version to PyPi using the configurations in .github/workflows/pypi_release.yml.
    You need to increase the version number after a stable release, so that the nightly PyPi can work properly.
    """
    try:
        if not os.getenv("RELEASE"):
            from datetime import date

            minor_version_file_path = os.path.join(AUTOGLUON_ROOT_PATH, "core", "src", "autogluon", "VERSION.minor")
            if use_file_if_exists and os.path.isfile(minor_version_file_path):
                with open(minor_version_file_path) as f:
                    day = f.read().strip()
            else:
                today = date.today()
                day = today.strftime("b%Y%m%d")
            version += day
    except Exception:
        pass
    if create_file and not os.getenv("RELEASE"):
        with open(os.path.join(AUTOGLUON_ROOT_PATH, "core", "src", "autogluon", "VERSION.minor"), "w") as f:
            f.write(day)
    return version


def create_version_file(*, version, submodule):
    """
    Create a version.py file with the specified version and lite mode flag.
    """
    print("-- Building version " + version)

    # Construct the path to the version.py file
    if submodule is not None:
        # Submodule-specific version file
        version_path = os.path.join(
            AUTOGLUON_ROOT_PATH, "core", "src", "autogluon", submodule, "version.py"
        )
    else:
        # Root version file
        version_path = os.path.join(
            AUTOGLUON_ROOT_PATH, "core", "src", "autogluon", "version.py"
        )

    print(f"Creating version file at: {version_path}")  # Debugging path

    # Ensure the directory exists
    os.makedirs(os.path.dirname(version_path), exist_ok=True)

    # Write the version information to the version.py file
    with open(version_path, "w") as f:
        f.write(f'"""This is the {AUTOGLUON} version file."""\n')
        f.write("__version__ = '{}'\n".format(version))
        f.write("__lite__ = {}\n".format(LITE_MODE))


def default_setup_args(*, version, submodule):
    """
    Generate the default setup arguments for setuptools.
    """
    from setuptools import find_namespace_packages

    long_description_path = os.path.join(AUTOGLUON_ROOT_PATH, "README.md")
    with open(long_description_path, "r", encoding="utf-8") as f:
        long_description = f.read()

    if submodule is None:
        name = PACKAGE_NAME
    else:
        name = f"{PACKAGE_NAME}.{submodule}"

    if os.getenv("RELEASE"):
        development_status = "Development Status :: 5 - Production/Stable"
    else:
        development_status = "Development Status :: 4 - Beta"

    setup_args = dict(
        name=name,
        version=version,
        author="AutoGluon Community",
        url="https://github.com/autogluon/autogluon",
        description="Fast and Accurate ML in 3 Lines of Code",
        long_description=long_description,
        long_description_content_type="text/markdown",
        license="Apache-2.0",
        license_files=("../LICENSE", "../NOTICE"),
        # Package info
        packages=find_namespace_packages("src", include=["autogluon.*"]),
        package_dir={"": "src"},
        # Removed namespace_packages as it's deprecated; using implicit namespaces (PEP 420)
        zip_safe=True,
        include_package_data=True,
        python_requires=PYTHON_REQUIRES,
        package_data={AUTOGLUON: ["LICENSE"]},
        classifiers=[
            development_status,
            "Intended Audience :: Education",
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: MacOS",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Topic :: Software Development",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",
            "Topic :: Scientific/Engineering :: Information Analysis",
            "Topic :: Scientific/Engineering :: Image Recognition",
        ],
        project_urls={
            "Documentation": "https://auto.gluon.ai",
            "Bug Reports": "https://github.com/autogluon/autogluon/issues",
            "Source": "https://github.com/autogluon/autogluon/",
            "Contribute!": "https://github.com/autogluon/autogluon/blob/master/CONTRIBUTING.md",
        },
    )
    return setup_args
