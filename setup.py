from setuptools import setup, find_namespace_packages
import os, importlib.util

current_dir = os.path.dirname(os.path.abspath(__file__))
utils_path = os.path.join(current_dir, "core", "src", "autogluon", "core", "_setup_utils.py")

if not os.path.exists(utils_path):
    raise FileNotFoundError(f"Could not find _setup_utils.py at {utils_path}")

spec = importlib.util.spec_from_file_location("ag_min_dependencies", utils_path)
ag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ag)

version = ag.load_version_file()
version = ag.update_version(version)

# Combine your dependencies as before
install_requires = [
    f'autogluon.core=={version}',
    f'autogluon.features=={version}',
    f'autogluon.tabular=={version}',
    f'autogluon.multimodal=={version}',
    f'autogluon.timeseries=={version}',
]
install_requires = ag.get_dependency_version_ranges(install_requires)

submodule = None
ag.create_version_file(version=version, submodule=submodule)

setup_args = ag.default_setup_args(version=version, submodule=submodule)

# Modify setup_args to include the updated package and package_dir values
setup_args['packages'] = find_namespace_packages(where="core/src", include=["autogluon*"])
setup_args['package_dir'] = {"": "core/src"}

# Now just call setup with setup_args (without repeating packages or package_dir)
setup(
    install_requires=install_requires,
    **setup_args,
)
