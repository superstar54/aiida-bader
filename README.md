# AiiDA-Bader

[![PyPI version](https://badge.fury.io/py/aiida-bader.svg)](https://badge.fury.io/py/aiida-bader)
[![Unit test](https://github.com/superstar54/aiida-bader/actions/workflows/ci.yaml/badge.svg)](https://github.com/superstar54/aiida-bader/actions/workflows/ci.yaml)
[![Docs status](https://readthedocs.org/projects/aiida-bader/badge)](http://aiida-bader.readthedocs.io/)

AiiDA plugin for [Bader](https://theory.cm.utexas.edu/henkelman/code/bader/) charge analysis.

## Installation
To install from PyPI, simply execute:

    pip install aiida-bader

or when installing from source:

    git clone https://github.com/superstar54/aiida-bader
    pip install aiida-bader

## Development

### Running tests
To run the tests, simply clone and install the package locally with the [tests] optional dependencies:

```shell
git clone https://github.com/superstar54/aiida-bader .
cd aiida-bader
pip install -e .[tests]  # install extra dependencies for test
pytest # run tests
```

### Pre-commit
To contribute to this repository, please enable pre-commit so the code in commits are conform to the standards.
Simply install the repository with the `pre-commit` extra dependencies:
```shell
cd aiida-bader
pip install -e .[pre-commit]
pre-commit install
```

## License
The `aiida-bader` plugin package is released under the MIT license.
See the `LICENSE` file for more details.

## Acknowledgements
We acknowledge support from:
* the [NCCR MARVEL](http://nccr-marvel.ch/) funded by the Swiss National Science Foundation;

<img src="docs/source/_static/images/MARVEL.png" width="250px" height="131px"/>
