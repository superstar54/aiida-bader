import pathlib
from setuptools import setup, find_packages


def test_suite():
    import unittest

    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover("tests", pattern="test_*.py")
    return test_suite


# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="aiida-bader",
    version="0.0.6",
    description="AiiDA plugin for bader code.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/superstart54/aiida-bader",
    author="Xing Wang",
    author_email="xingwang1991@gmail.com",
    license="MIT License",
    classifiers=[],
    packages=find_packages(),
    install_requires=[
        "aiida-core",
        "aiida-workgraph",
        "aiida-quantumespresso~=4.4",
        "aiida-cp2k",
        "weas-widget",
        "pytest",
        "pytest-cov",
        "pre-commit",
    ],
    entry_points={
        "aiida.calculations": [
            "bader = aiida_bader.calculations:BaderCalculation",
        ],
        "aiida.parsers": [
            "bader = aiida_bader.parsers:BaderParser",
        ],
        "aiida.workflows": [
            "bader.qe = aiida_bader.workchains:QeBaderWorkChain",
        ],
        "aiidalab_qe.properties": [
            "bader = aiida_bader.qeapp:bader",
        ],
    },
    package_data={
        "aiida_bader.workchains.protocols": ["bader.yaml"],
    },
    python_requires=">=3.9",
    test_suite="setup.test_suite",
)
