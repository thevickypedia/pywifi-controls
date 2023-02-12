**Platform Supported**

![Generic badge](https://img.shields.io/badge/Platform-Linux|MacOS|Windows-1f425f.svg)

**Deployments**

[![pages-build-deployment](https://github.com/thevickypedia/pynotification/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/thevickypedia/pynotification/actions/workflows/pages/pages-build-deployment)
[![pypi-publish](https://github.com/thevickypedia/pynotification/actions/workflows/python-publish.yml/badge.svg)](https://github.com/thevickypedia/pynotification/actions/workflows/python-publish.yml)

# PyWiFi-controls
Python module to control `WiFi` on Linux, Windows and macOS

### Installation
```shell
python -m pip install pynotification
```

### Usage
**Enable or disable Wi-Fi**
```python
from pywifi import ControlPeripheral

ControlPeripheral().enable()  # Turn on Wi-Fi
ControlPeripheral().disable()  # Turn off Wi-Fi
```

**Connect to a Wi-Fi SSID**
```python
from pywifi import ControlConnection

ControlConnection().wifi_connector()
```

### Arguments
- **wifi_ssid** - SSID of the Wi-Fi connection.
- **wifi_password** - Password for the Wi-Fi connection.

## [Release Notes](https://github.com/thevickypedia/pynotification/blob/main/release_notes.rst)
**Requirement**
```shell
python -m pip install changelog-generator
```

**Usage**
```shell
changelog reverse -f release_notes.rst -t 'Release Notes'
```

## Linting
`PreCommit` will ensure linting, and the doc creation are run on every commit.

**Requirement**
```shell
pip install sphinx==5.1.1 pre-commit recommonmark
```

**Usage**
```shell
pre-commit run --all-files
```

## Pypi Package
[![pypi-module](https://img.shields.io/badge/Software%20Repository-pypi-1f425f.svg)](https://packaging.python.org/tutorials/packaging-projects/)

[https://pypi.org/project/pynotification/](https://pypi.org/project/pynotification/)

## Runbook
[![made-with-sphinx-doc](https://img.shields.io/badge/Code%20Docs-Sphinx-1f425f.svg)](https://www.sphinx-doc.org/en/master/man/sphinx-autogen.html)

[https://thevickypedia.github.io/pynotification/](https://thevickypedia.github.io/pynotification/)

## License & copyright

&copy; Vignesh Rao

Licensed under the [MIT License](https://github.com/thevickypedia/pynotification/blob/main/LICENSE)
