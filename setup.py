import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="runAM-avd",
    version="0.1.0",
    description="runAM Python modules augment Ansible AVD collection",
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/arista-netdevops-community/runAM-avd',
    author='Petr Ankudinov',
    license="BSD",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX :: Linux",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "argcomplete==3.0.8",
        "glom==23.3.0"
    ],
    entry_points = {
        "console_scripts": ['runAM = runAM.cli:interpreter']
    },
)