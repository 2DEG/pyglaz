# pyglaz

pyglaz is a Python package that provides bindings and a Pythonic wrapper for the Glaz C API. This package allows you to easily interact with the high-performance Glaz spectroscopic library from within Python, enabling seamless integration of C-based functionality into Python projects.

## Features

- Complete Python wrapper for the Glaz C API
- Clean, Pythonic interface for all library functions
- Automatic conversion between C types and Python types (including NumPy arrays)
- Comprehensive error handling with detailed error messages
- Support for Windows (32/64 bit) and Linux (64 bit) platforms
- Example scripts demonstrating library usage

## Installation

### Requirements

- Python 3.6 or higher
- NumPy
- Matplotlib (for examples and visualization)

### Installing from PyPI

```bash
pip install pyglaz
```

### Installing from source

```bash
git clone https://github.com/yourusername/pyglaz.git
cd pyglaz
pip install -e .
```

## Usage

Here's a simple example of using the pyglaz library:

```python
from pyglaz import GlazLib
from pyglaz._bindings import GLAZ_LINESCAN_II_V2_SINGLE_DEVICE_TYPE, TRIGGER_INTERNAL

# Initialize the library
glaz = GlazLib(device_type=GLAZ_LINESCAN_II_V2_SINGLE_DEVICE_TYPE, allow_demo=True)

# Configure device settings
glaz.set_wavelengths(min_wavelength=400.0, max_wavelength=800.0)
glaz.set_trigger_mode(TRIGGER_INTERNAL)
glaz.set_integration_time(100)  # in microseconds
glaz.set_hardware_averaging(16)

# Capture background (optional but recommended)
glaz.capture_background(count=5)

# Run a measurement and get results
glaz.run_measurement()
data, size = glaz.get_result()

# Always close the session when done
glaz.close()
```

For more detailed examples, see the `examples` directory.

## API Documentation

For detailed API documentation, see the [API Reference](docs/API.md) or refer to the inline documentation in the source code.

## Device Support

pyglaz supports various Glaz spectroscopic devices, including:

- Glaz LineScan I (PulseSync S10453)
- Glaz LineScan I (PulseSync S11639)
- Glaz LineScan I (TimeFill S11639)
- Glaz LineScan I (SpectroCam S11639)
- Glaz LineScan II
- Glaz LineScan II V2
- Glaz LineScan LS
- Glaz LineScan EC

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The Glaz team for providing the C API
- Contributors to this Python wrapper
