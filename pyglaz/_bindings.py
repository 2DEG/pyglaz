import os
import sys
import ctypes
from ctypes import c_int, c_double, c_char_p, c_bool, POINTER, byref, c_uint16

# Error codes
ERROR_NONE = 0
ERROR_NOT_INITIALISED = 1
ERROR_SCRIPT = 2
ERROR_CONNECTING_TO_CAMERAS = 3
ERROR_DOWNLOADING_CALIBRATIONS = 4
ERROR_INVALID_WAVELENGTHS = 5
ERROR_INVALID_AVERAGING = 6
ERROR_INVALID_SCAN_COUNT = 7
ERROR_INVALID_TRIGGER_MODE = 8
ERROR_INVALID_TRIGGER_DELAY = 9
ERROR_INVALID_INTEGRATION_TIME = 10
ERROR_INVALID_SCAN_CLOCK_SPEED = 11
ERROR_INVALID_SETTINGS = 12
ERROR_CAPTURING_BACKGROUNDS = 13
ERROR_RUNNING_MEASUREMENT = 14
ERROR_INVALID_CALCULATION_INDEX = 15
ERROR_INVALID_RESULT_DATA_SIZE = 16
ERROR_INVALID_PD_NUMBER = 17
ERROR_INVALID_PD_CHANNEL = 18
ERROR_INVALID_CAMERA_NUMBER = 19
ERROR_INVALID_TRIGGER_FREQUENCY = 20
ERROR_NO_MEASUREMENT_RUN = 21
ERROR_INITIALISING_SINGEL_DEVICE = 22
ERROR_INVALID_SINGLE_DEVICE_TYPE = 23
ERROR_INVALID_SYNC_OUT_MODE = 24
ERROR_INVALID_INTEGRATION_MODE = 25
ERROR_CLOCK_SPEED_UNSUPPORTED = 26
ERROR_INVALID_AUX_OUT_MODE = 27
ERROR_CYCLE_COUNT_UNSUPPORTED = 28
ERROR_INVALID_CYCLE_COUNT = 29
ERROR_INVALID_TEST_MODE = 30
ERROR_OUT_POLARITY_NOT_SUPPORTED = 31
ERROR_INVALID_OUT_POLARITY = 32
ERROR_RESOLUTION_OUT_OF_RANGE = 33
ERROR_RESOLUTION_NOT_SUPPORTED = 34
ERROR_RUNNING_USB_COMMS_TEST = 35
ERROR_MEASUREMENT_STREAM = 36
ERROR_AUX_STATES_NOT_SUPPORTED = 37
ERROR_INTEGRATION_TIME_NOT_SUPPORTED = 38
ERROR_INVALID_ADC_GAIN = 39
ERROR_AUX_CYCLE_COUNT_INVALID = 40

# Device types
GLAZ_LINESCAN_I_PULSESYNC_S10453_SINGLE_DEVICE_TYPE = 1
GLAZ_LINESCAN_I_PULSESYNC_S11639_SINGLE_DEVICE_TYPE = 2
GLAZ_LINESCAN_I_TIMEFILL_S11639_SINGLE_DEVICE_TYPE = 3
GLAZ_LINESCAN_I_SPECTROCAM_S11639_SINGLE_DEVICE_TYPE = 4
GLAZ_LINESCAN_II_SINGLE_DEVICE_TYPE = 5
GLAZ_LINESCAN_II_V2_SINGLE_DEVICE_TYPE = 6
GLAZ_LINESCAN_LS_SINGLE_DEVICE_TYPE = 7
GLAZ_LINESCAN_EC_SINGLE_DEVICE_TYPE = 8

# Averaging constants
AVERAGING_X1 = 0
AVERAGING_X2 = 1
AVERAGING_X4 = 2
AVERAGING_X8 = 3
AVERAGING_X16 = 4
AVERAGING_X32 = 5
AVERAGING_X64 = 6
AVERAGING_X128 = 7
AVERAGING_X256 = 8
AVERAGING_X512 = 9
AVERAGING_X1024 = 10
AVERAGING_X2048 = 11
AVERAGING_X4096 = 12

# Resolution constants
RESOLUTION_16BIT = 3
RESOLUTION_14BIT = 2
RESOLUTION_12BIT = 1
RESOLUTION_10BIT = 0

# Trigger modes
TRIGGER_EXTERNAL = 0
TRIGGER_INTERNAL = 1
TRIGGER_BURST = 2

# Integration modes
INT_MODE_PULSESYNC = 0
INT_MODE_TIMEFILL = 1

# Output modes
OUT_INT_WINDOW = 0
OUT_TRIGGER = 1
OUT_BUSY = 2
OUT_TRIGGER_CYCLE_START = 3
OUT_TRIGGER_CYCLE_RUNNING = 4
OUT_OFF = 5

# Output polarities
OUT_POLARITY_ACTIVE_HI = 1
OUT_POLARITY_ACTIVE_LO = 0

# Scan clock speeds
SCAN_CLOCK_FULL_SPEED = 0
SCAN_CLOCK_HALF_SPEED = 1

# Test modes
TEST_OFF = 0
TEST_DAC_ALTERNATING = 1
TEST_DAC_ALL_ONES = 2
TEST_DAC_ALL_ZEROS = 3

# ADC Gain
ADC_GAIN_X1 = 0
ADC_GAIN_X2 = 1
ADC_GAIN_X4 = 2


def _find_library():
    """Find and load the GlazLib DLL."""
    # Determine the platform
    if sys.platform == 'win32':
        if sys.maxsize > 2**32:  # 64-bit Python
            lib_paths = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib', 'win64', 'GlazLib.dll'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib', 'win64-static', 'GlazLib.dll'),
            ]
        else:  # 32-bit Python
            lib_paths = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib', 'win32', 'GlazLib.dll'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib', 'win32-static', 'GlazLib.dll'),
            ]
    elif sys.platform == 'linux':
        lib_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib', 'linux64', 'libGlazLib.so.9.23.0'),
        ]
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")

    # Try to load the library from the paths
    for lib_path in lib_paths:
        if os.path.exists(lib_path):
            try:
                return ctypes.cdll.LoadLibrary(lib_path)
            except OSError as e:
                last_error = e
    
    # If we get here, we couldn't load the library
    error_msg = f"Could not find or load GlazLib library. Looked in: {', '.join(lib_paths)}"
    raise RuntimeError(error_msg)


# Load the GlazLib DLL
_lib = _find_library()

# Define function prototypes
_lib.getVersion.argtypes = [POINTER(c_int), POINTER(c_int)]
_lib.getVersion.restype = None

_lib.getLastErrorMessage.argtypes = [c_char_p]
_lib.getLastErrorMessage.restype = c_int

_lib.getUSBParameters.argtypes = [POINTER(c_int), POINTER(c_int), POINTER(c_int)]
_lib.getUSBParameters.restype = None

_lib.setUSBParameters.argtypes = [c_int, c_int, c_int]
_lib.setUSBParameters.restype = None

_lib.enableDataStreamLog.argtypes = [c_bool]
_lib.enableDataStreamLog.restype = None

_lib.initialiseSession.argtypes = [c_char_p]
_lib.initialiseSession.restype = c_int

_lib.initialiseSingleDeviceSession.argtypes = [c_int, c_bool, c_bool]
_lib.initialiseSingleDeviceSession.restype = c_int

_lib.closeSession.argtypes = []
_lib.closeSession.restype = c_int

_lib.resetAllDevices.argtypes = []
_lib.resetAllDevices.restype = None

_lib.resetAllPorts.argtypes = []
_lib.resetAllPorts.restype = None

_lib.setTestMode.argtypes = [c_int]
_lib.setTestMode.restype = c_int

_lib.setWavelengths.argtypes = [c_double, c_double]
_lib.setWavelengths.restype = c_int

_lib.setHardwareAveraging.argtypes = [c_int]
_lib.setHardwareAveraging.restype = c_int

_lib.setResolution.argtypes = [c_int]
_lib.setResolution.restype = c_int

_lib.setScanCount.argtypes = [c_int]
_lib.setScanCount.restype = c_int

_lib.setScanClockSpeed.argtypes = [c_int]
_lib.setScanClockSpeed.restype = c_int

_lib.setADCGain.argtypes = [c_int]
_lib.setADCGain.restype = c_int

_lib.setTriggerDelay.argtypes = [c_int]
_lib.setTriggerDelay.restype = c_int

_lib.setTriggerMode.argtypes = [c_int]
_lib.setTriggerMode.restype = c_int

_lib.setInternalTriggerFrequency.argtypes = [c_double]
_lib.setInternalTriggerFrequency.restype = c_int

_lib.setIntegrationMode.argtypes = [c_int]
_lib.setIntegrationMode.restype = c_int

_lib.setIntegrationTime.argtypes = [c_int]
_lib.setIntegrationTime.restype = c_int

_lib.setSyncOutMode.argtypes = [c_int]
_lib.setSyncOutMode.restype = c_int

_lib.setSyncOutPolarity.argtypes = [c_int]
_lib.setSyncOutPolarity.restype = c_int

_lib.setAuxOutMode.argtypes = [c_int]
_lib.setAuxOutMode.restype = c_int

_lib.setAuxOutPolarity.argtypes = [c_int]
_lib.setAuxOutPolarity.restype = c_int

_lib.setOutCycleCount.argtypes = [c_int]
_lib.setOutCycleCount.restype = c_int

_lib.setTimeout.argtypes = [c_int]
_lib.setTimeout.restype = c_int

_lib.captureBackground.argtypes = [c_int]
_lib.captureBackground.restype = c_int

_lib.runMeasurement.argtypes = []
_lib.runMeasurement.restype = c_int

_lib.startMeasurement.argtypes = []
_lib.startMeasurement.restype = c_int

_lib.isMeasurementDone.argtypes = [POINTER(c_bool)]
_lib.isMeasurementDone.restype = c_int

_lib.getResult.argtypes = [c_int, POINTER(c_int), POINTER(c_double)]
_lib.getResult.restype = c_int

_lib.getComplexResult.argtypes = [c_int, POINTER(c_int), POINTER(c_double), POINTER(c_double)]
_lib.getComplexResult.restype = c_int

_lib.getTimeStamp.argtypes = [c_int, c_int, POINTER(c_double)]
_lib.getTimeStamp.restype = c_int

_lib.getScan.argtypes = [c_int, c_int, POINTER(c_int), POINTER(c_double)]
_lib.getScan.restype = c_int

_lib.getComplexScan.argtypes = [c_int, c_int, POINTER(c_int), POINTER(c_double), POINTER(c_double)]
_lib.getComplexScan.restype = c_int

_lib.getAllScansSizes.argtypes = [c_int, POINTER(c_int), POINTER(c_int)]
_lib.getAllScansSizes.restype = c_int

_lib.getAllScans.argtypes = [c_int, POINTER(c_uint16)]
_lib.getAllScans.restype = c_int

_lib.writeAllScansToFile.argtypes = [c_int, c_char_p, c_bool]
_lib.writeAllScansToFile.restype = c_int

_lib.getPDValues.argtypes = [c_int, c_int, POINTER(c_int), POINTER(c_double)]
_lib.getPDValues.restype = c_int

_lib.getPDReference.argtypes = [c_int, c_int, POINTER(c_double)]
_lib.getPDReference.restype = c_int

_lib.getAUXStates.argtypes = [c_int, POINTER(c_int), POINTER(c_bool)]
_lib.getAUXStates.restype = c_int

_lib.getAUXCycleCounts.argtypes = [c_int, c_int, POINTER(c_int), POINTER(c_int)]
_lib.getAUXCycleCounts.restype = c_int

_lib.runUSBCommsTest.argtypes = []
_lib.runUSBCommsTest.restype = c_int