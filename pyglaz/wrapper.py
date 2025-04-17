import numpy as np
import ctypes
import os
import time
from ctypes import byref, c_int, c_double, c_bool, c_char_p, c_uint16, create_string_buffer, POINTER
from typing import Tuple, List, Optional, Dict, Any, Union

from . import _bindings as lib
from .utils import find_config_file


class GlazLib:
    """
    Python wrapper for the GlazLib C library.
    
    This class provides a Pythonic interface to the GlazLib spectroscopic library.
    """
    
    def __init__(self, config_file: Optional[str] = None, device_type: int = lib.GLAZ_LINESCAN_II_V2_SINGLE_DEVICE_TYPE, 
                 use_defaults: bool = True, allow_demo: bool = True):
        """
        Initialize the GlazLib session.
        
        Args:
            config_file: Path to a configuration file, or None for default configuration.
                         Can be a full path or just the name of a config file.
            device_type: Type of device to initialize if config_file is None and no default config is found
            use_defaults: Whether to use default settings when initializing with device_type
            allow_demo: Whether to allow demo mode if no device is connected
            
        Raises:
            RuntimeError: If initialization fails
            FileNotFoundError: If the specified config file is not found
        """
        self._initialized = False
        
        try:
            # Try to find a config file first
            if config_file is not None:
                # Check if config_file is a full path or just a name
                if os.path.isfile(config_file):
                    config_path = config_file
                else:
                    # Try to find the config file
                    config_path = find_config_file(config_file)
            else:
                # Look for default config files
                try:
                    config_path = find_config_file()
                except FileNotFoundError:
                    # No config file found, will use device_type instead
                    config_path = None
            
            # Initialize with config file if found
            if config_path is not None:
                print(f"Initializing with configuration file: {config_path}")
                status = lib._lib.initialiseSession(c_char_p(config_path.encode('utf-8')))
                if status != lib.ERROR_NONE:
                    error_msg = self.get_last_error_message()
                    raise RuntimeError(f"Failed to initialize GlazLib session with config file: {error_msg}")
            else:
                # Fall back to device type initialization
                print(f"No configuration file found. Initializing device type: {device_type}")
                status = lib._lib.initialiseSingleDeviceSession(device_type, use_defaults, allow_demo)
                if status != lib.ERROR_NONE:
                    error_msg = self.get_last_error_message()
                    raise RuntimeError(f"Failed to initialize GlazLib session with device type: {error_msg}")
            
            self._initialized = True
        
        except Exception as e:
            if isinstance(e, RuntimeError):
                raise
            elif isinstance(e, FileNotFoundError):
                raise
            else:
                raise RuntimeError(f"Failed to initialize GlazLib session: {str(e)}")
    
    def __del__(self):
        """Clean up resources when object is destroyed."""
        self.close()
    
    def close(self):
        """
        Close the current GlazLib session.
        
        This method attempts to gracefully close the GlazLib session. If the session
        is already closed or if closing fails, appropriate messages will be logged.
        
        Raises:
            RuntimeError: If closing the session fails with a critical error
        """
        if not self._initialized:
            return
            
        print("Closing GlazLib session...")
        try:
            # Attempt to close the session
            status = lib._lib.closeSession()
            print("Here")
            self._initialized = False
            
            # Check if closing was successful
            if status != lib.ERROR_NONE:
                error_msg = self.get_last_error_message()
                print(f"Warning: GlazLib session close returned error code {status}: {error_msg}")
                
                # Only raise exception for critical errors
                if status not in [lib.ERROR_NOT_INITIALISED]:  # Add other non-critical errors if needed
                    raise RuntimeError(f"Failed to close GlazLib session: {error_msg}")
        except Exception as e:
            print(f"Exception during GlazLib session close: {str(e)}")
            # Set initialized to False anyway to prevent further access attempts
            self._initialized = False
            
            # Re-raise RuntimeError but other exceptions are just logged
            if isinstance(e, RuntimeError):
                raise
    
    def get_version(self) -> Tuple[int, int]:
        """
        Get the version of the GlazLib library.
        
        Returns:
            Tuple containing (major_version, minor_version)
        """
        major = c_int()
        minor = c_int()
        lib._lib.getVersion(byref(major), byref(minor))
        return (major.value, minor.value)
    
    def get_last_error_message(self) -> str:
        """
        Get the last error message from the library.
        
        Returns:
            String containing the last error message
        """
        buffer_size = 1024
        buffer = create_string_buffer(buffer_size)
        lib._lib.getLastErrorMessage(buffer)
        return buffer.value.decode('utf-8')
    
    def get_usb_parameters(self) -> Dict[str, int]:
        """
        Get the current USB parameters.
        
        Returns:
            Dictionary with keys 'timeout', 'bulk_size', and 'queue_size'
        """
        timeout = c_int()
        bulk_size = c_int()
        queue_size = c_int()
        lib._lib.getUSBParameters(byref(timeout), byref(bulk_size), byref(queue_size))
        return {
            'timeout': timeout.value,
            'bulk_size': bulk_size.value,
            'queue_size': queue_size.value
        }
    
    def set_usb_parameters(self, timeout: int, bulk_size: int, queue_size: int) -> None:
        """
        Set the USB parameters.
        
        Args:
            timeout: USB timeout in milliseconds
            bulk_size: Size of bulk transfers
            queue_size: Size of the queue
            
        Raises:
            RuntimeError: If setting the parameters fails
        """
        status = lib._lib.setUSBParameters(timeout, bulk_size, queue_size)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to set USB parameters: {error_msg}")
    
    def enable_data_stream_log(self, enable: bool) -> None:
        """
        Enable or disable data stream logging.
        
        Args:
            enable: True to enable logging, False to disable
        """
        lib._lib.enableDataStreamLog(enable)
    
    def reset_all_devices(self) -> None:
        """Reset all connected devices."""
        lib._lib.resetAllDevices()
    
    def reset_all_ports(self) -> None:
        """Reset all USB ports."""
        lib._lib.resetAllPorts()
    
    def set_test_mode(self, mode: int) -> None:
        """
        Set the test mode.
        
        Args:
            mode: Test mode (lib.TEST_OFF, lib.TEST_DAC_ALTERNATING, etc.)
            
        Raises:
            RuntimeError: If setting the test mode fails
        """
        status = lib._lib.setTestMode(mode)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to set test mode: {error_msg}")
    
    def set_wavelengths(self, min_wavelength: float, max_wavelength: float) -> None:
        """
        Set the wavelength range.
        
        Args:
            min_wavelength: Minimum wavelength in nm
            max_wavelength: Maximum wavelength in nm
            
        Raises:
            RuntimeError: If setting the wavelength range fails
        """
        status = lib._lib.setWavelengths(c_double(min_wavelength), c_double(max_wavelength))
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to set wavelength range: {error_msg}")
    
    def set_hardware_averaging(self, averaging: int) -> None:
        """
        Set the hardware averaging factor.
        
        Args:
            averaging: Averaging factor (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, or 4096)
            
        Raises:
            RuntimeError: If setting the hardware averaging fails
        """
        status = lib._lib.setHardwareAveraging(averaging)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to set hardware averaging: {error_msg}")
    
    def set_resolution(self, resolution: int) -> None:
        """
        Set the resolution.
        
        Args:
            resolution: Resolution (lib.RESOLUTION_16BIT, lib.RESOLUTION_14BIT, etc.)
            
        Raises:
            RuntimeError: If setting the resolution fails
        """
        status = lib._lib.setResolution(resolution)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to set resolution: {error_msg}")
    
    def set_scan_count(self, count: int) -> None:
        """
        Set the scan count.
        
        Args:
            count: Number of scans to perform
            
        Raises:
            RuntimeError: If setting the scan count fails
        """
        status = lib._lib.setScanCount(count)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to set scan count: {error_msg}")
    
    def set_scan_clock_speed(self, speed: int) -> None:
        """
        Set the scan clock speed.
        
        Args:
            speed: Speed (lib.SCAN_CLOCK_FULL_SPEED or lib.SCAN_CLOCK_HALF_SPEED)
            
        Raises:
            RuntimeError: If setting the scan clock speed fails
        """
        status = lib._lib.setScanClockSpeed(speed)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to set scan clock speed: {error_msg}")
    
    def set_adc_gain(self, gain: int) -> None:
        """
        Set the ADC gain.
        
        Args:
            gain: Gain (lib.ADC_GAIN_X1, lib.ADC_GAIN_X2, or lib.ADC_GAIN_X4)
            
        Raises:
            RuntimeError: If setting the ADC gain fails
        """
        status = lib._lib.setADCGain(gain)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to set ADC gain: {error_msg}")
    
    def set_trigger_delay(self, delay: int) -> None:
        """
        Set the trigger delay.
        
        Args:
            delay: Delay in microseconds
            
        Raises:
            RuntimeError: If setting the trigger delay fails
        """
        status = lib._lib.setTriggerDelay(delay)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to set trigger delay: {error_msg}")
    
    def set_trigger_mode(self, mode: int) -> None:
        """
        Set the trigger mode.
        
        Args:
            mode: Trigger mode (lib.TRIGGER_EXTERNAL, lib.TRIGGER_INTERNAL, or lib.TRIGGER_BURST)
            
        Raises:
            RuntimeError: If setting the trigger mode fails
        """
        status = lib._lib.setTriggerMode(mode)
        print("Status:", status)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to set trigger mode: {error_msg}")
    
    def set_internal_trigger_frequency(self, frequency: float) -> None:
        """
        Set the internal trigger frequency.
        
        Args:
            frequency: Frequency in Hz
            
        Raises:
            RuntimeError: If setting the internal trigger frequency fails
        """
        status = lib._lib.setInternalTriggerFrequency(c_double(frequency))
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to set internal trigger frequency: {error_msg}")
    
    def set_integration_mode(self, mode: int) -> None:
        """
        Set the integration mode.
        
        Args:
            mode: Integration mode (lib.INT_MODE_PULSESYNC or lib.INT_MODE_TIMEFILL)
            
        Raises:
            RuntimeError: If setting the integration mode fails
        """
        status = lib._lib.setIntegrationMode(mode)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to set integration mode: {error_msg}")
    
    def set_integration_time(self, time: int) -> None:
        """
        Set the integration time.
        
        Args:
            time: Integration time in microseconds
            
        Raises:
            RuntimeError: If setting the integration time fails
        """
        status = lib._lib.setIntegrationTime(time)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to set integration time: {error_msg}")
    
    def set_sync_out_mode(self, mode: int) -> None:
        """
        Set the sync output mode.
        
        Args:
            mode: Mode (lib.OUT_INT_WINDOW, lib.OUT_TRIGGER, etc.)
            
        Raises:
            RuntimeError: If setting the sync output mode fails
        """
        status = lib._lib.setSyncOutMode(mode)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to set sync output mode: {error_msg}")
    
    def set_sync_out_polarity(self, polarity: int) -> None:
        """
        Set the sync output polarity.
        
        Args:
            polarity: Polarity (lib.OUT_POLARITY_ACTIVE_HI or lib.OUT_POLARITY_ACTIVE_LO)
            
        Raises:
            RuntimeError: If setting the sync output polarity fails
        """
        status = lib._lib.setSyncOutPolarity(polarity)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to set sync output polarity: {error_msg}")
    
    def set_aux_out_mode(self, mode: int) -> None:
        """
        Set the auxiliary output mode.
        
        Args:
            mode: Mode (lib.OUT_INT_WINDOW, lib.OUT_TRIGGER, etc.)
            
        Raises:
            RuntimeError: If setting the auxiliary output mode fails
        """
        status = lib._lib.setAuxOutMode(mode)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to set auxiliary output mode: {error_msg}")
    
    def set_aux_out_polarity(self, polarity: int) -> None:
        """
        Set the auxiliary output polarity.
        
        Args:
            polarity: Polarity (lib.OUT_POLARITY_ACTIVE_HI or lib.OUT_POLARITY_ACTIVE_LO)
            
        Raises:
            RuntimeError: If setting the auxiliary output polarity fails
        """
        status = lib._lib.setAuxOutPolarity(polarity)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to set auxiliary output polarity: {error_msg}")
    
    def set_out_cycle_count(self, count: int) -> None:
        """
        Set the output cycle count.
        
        Args:
            count: Number of output cycles
            
        Raises:
            RuntimeError: If setting the output cycle count fails
        """
        status = lib._lib.setOutCycleCount(count)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to set output cycle count: {error_msg}")
    
    def set_timeout(self, timeout: int) -> None:
        """
        Set the operation timeout.
        
        Args:
            timeout: Timeout in milliseconds
            
        Raises:
            RuntimeError: If setting the timeout fails
        """
        status = lib._lib.setTimeout(timeout)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to set timeout: {error_msg}")
    
    def capture_background(self, count: int = 1) -> None:
        """
        Capture background data.
        
        Args:
            count: Number of background scans to capture and average
            
        Raises:
            RuntimeError: If capturing the background fails
        """
        status = lib._lib.captureBackground(count)
        print("Status:", status)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to capture background: {error_msg}")
    
    def run_measurement(self) -> None:
        """
        Run a measurement (blocking).
        
        Raises:
            RuntimeError: If running the measurement fails
        """
        status = lib._lib.runMeasurement()
        print("Status:", status)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to run measurement: {error_msg}")
    
    def start_measurement(self) -> None:
        """
        Start a measurement (non-blocking).
        
        Raises:
            RuntimeError: If starting the measurement fails
        """
        status = lib._lib.startMeasurement()
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to start measurement: {error_msg}")
    
    def is_measurement_done(self) -> bool:
        """
        Check if a non-blocking measurement is complete.
        
        Returns:
            True if the measurement is complete, False otherwise
            
        Raises:
            RuntimeError: If checking the measurement status fails
        """
        done = c_bool()
        status = lib._lib.isMeasurementDone(byref(done))
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to check if measurement is done: {error_msg}")
        return done.value
    
    def get_result(self, index: int = 0) -> Tuple[np.ndarray, int]:
        """
        Get a measurement result.
        
        Args:
            index: Result index
            
        Returns:
            Tuple containing (data, size)
            
        Raises:
            RuntimeError: If getting the result fails
        """
        size = c_int()
        status = lib._lib.getResult(index, byref(size), None)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to get result size: {error_msg}")
        
        if size.value <= 0:
            return np.array([]), 0
        
        data = (c_double * size.value)()
        status = lib._lib.getResult(index, byref(size), data)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to get result data: {error_msg}")
        
        return np.array([data[i] for i in range(size.value)]), size.value
    
    def get_complex_result(self, index: int = 0) -> Tuple[np.ndarray, np.ndarray, int]:
        """
        Get a complex measurement result.
        
        Args:
            index: Result index
            
        Returns:
            Tuple containing (real_data, imag_data, size)
            
        Raises:
            RuntimeError: If getting the complex result fails
        """
        size = c_int()
        status = lib._lib.getComplexResult(index, byref(size), None, None)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to get complex result size: {error_msg}")
        
        if size.value <= 0:
            return np.array([]), np.array([]), 0
        
        real_data = (c_double * size.value)()
        imag_data = (c_double * size.value)()
        status = lib._lib.getComplexResult(index, byref(size), real_data, imag_data)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to get complex result data: {error_msg}")
        
        real_arr = np.array([real_data[i] for i in range(size.value)])
        imag_arr = np.array([imag_data[i] for i in range(size.value)])
        return real_arr, imag_arr, size.value
    
    def get_time_stamp(self, index: int = 0, channel: int = 0) -> float:
        """
        Get a time stamp.
        
        Args:
            index: Result index
            channel: Channel index
            
        Returns:
            Time stamp value
            
        Raises:
            RuntimeError: If getting the time stamp fails
        """
        value = c_double()
        status = lib._lib.getTimeStamp(index, channel, byref(value))
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to get time stamp: {error_msg}")
        return value.value
    
    def get_scan(self, index: int = 0, scan_index: int = 0) -> Tuple[np.ndarray, int]:
        """
        Get a scan.
        
        Args:
            index: Result index
            scan_index: Scan index
            
        Returns:
            Tuple containing (data, size)
            
        Raises:
            RuntimeError: If getting the scan fails
        """
        size = c_int()
        status = lib._lib.getScan(index, scan_index, byref(size), None)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to get scan size: {error_msg}")
        
        if size.value <= 0:
            return np.array([]), 0
        
        data = (c_double * size.value)()
        status = lib._lib.getScan(index, scan_index, byref(size), data)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to get scan data: {error_msg}")
        
        return np.array([data[i] for i in range(size.value)]), size.value
    
    def get_complex_scan(self, index: int = 0, scan_index: int = 0) -> Tuple[np.ndarray, np.ndarray, int]:
        """
        Get a complex scan.
        
        Args:
            index: Result index
            scan_index: Scan index
            
        Returns:
            Tuple containing (real_data, imag_data, size)
            
        Raises:
            RuntimeError: If getting the complex scan fails
        """
        size = c_int()
        status = lib._lib.getComplexScan(index, scan_index, byref(size), None, None)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to get complex scan size: {error_msg}")
        
        if size.value <= 0:
            return np.array([]), np.array([]), 0
        
        real_data = (c_double * size.value)()
        imag_data = (c_double * size.value)()
        status = lib._lib.getComplexScan(index, scan_index, byref(size), real_data, imag_data)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to get complex scan data: {error_msg}")
        
        real_arr = np.array([real_data[i] for i in range(size.value)])
        imag_arr = np.array([imag_data[i] for i in range(size.value)])
        return real_arr, imag_arr, size.value
    
    def get_all_scans_sizes(self, index: int = 0) -> Tuple[int, int]:
        """
        Get the sizes of all scans for a result.
        
        Args:
            index: Result index
            
        Returns:
            Tuple containing (num_scans, pixels_per_scan)
            
        Raises:
            RuntimeError: If getting the scan sizes fails
        """
        num_scans = c_int()
        pixels_per_scan = c_int()
        status = lib._lib.getAllScansSizes(index, byref(num_scans), byref(pixels_per_scan))
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to get all scans sizes: {error_msg}")
        return num_scans.value, pixels_per_scan.value
    
    def get_all_scans(self, index: int = 0) -> np.ndarray:
        """
        Get all scans for a result.
        
        Args:
            index: Result index
            
        Returns:
            2D array of scan data
            
        Raises:
            RuntimeError: If getting all scans fails
        """
        num_scans, pixels_per_scan = self.get_all_scans_sizes(index)
        if num_scans <= 0 or pixels_per_scan <= 0:
            return np.array([])
        
        total_size = num_scans * pixels_per_scan
        data = (c_uint16 * total_size)()
        status = lib._lib.getAllScans(index, data)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to get all scans: {error_msg}")
        
        # Convert to numpy array and reshape
        array_data = np.array([data[i] for i in range(total_size)], dtype=np.uint16)
        return array_data.reshape((num_scans, pixels_per_scan))
    
    def write_all_scans_to_file(self, index: int = 0, filename: str = "scans.dat", include_header: bool = True) -> None:
        """
        Write all scans to a file.
        
        Args:
            index: Result index
            filename: Output file name
            include_header: Whether to include a header in the file
            
        Raises:
            RuntimeError: If writing the scans to file fails
        """
        status = lib._lib.writeAllScansToFile(index, c_char_p(filename.encode('utf-8')), include_header)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to write all scans to file: {error_msg}")
    
    def get_pd_values(self, index: int = 0, channel: int = 0) -> Tuple[np.ndarray, int]:
        """
        Get photodiode values.
        
        Args:
            index: Result index
            channel: Channel index
            
        Returns:
            Tuple containing (values, size)
            
        Raises:
            RuntimeError: If getting the photodiode values fails
        """
        size = c_int()
        status = lib._lib.getPDValues(index, channel, byref(size), None)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to get photodiode values size: {error_msg}")
        
        if size.value <= 0:
            return np.array([]), 0
        
        values = (c_double * size.value)()
        status = lib._lib.getPDValues(index, channel, byref(size), values)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to get photodiode values: {error_msg}")
        
        return np.array([values[i] for i in range(size.value)]), size.value
    
    def get_pd_reference(self, index: int = 0, channel: int = 0) -> float:
        """
        Get photodiode reference value.
        
        Args:
            index: Result index
            channel: Channel index
            
        Returns:
            Reference value
            
        Raises:
            RuntimeError: If getting the photodiode reference value fails
        """
        value = c_double()
        status = lib._lib.getPDReference(index, channel, byref(value))
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to get photodiode reference: {error_msg}")
        return value.value
    
    def get_aux_states(self, index: int = 0) -> Tuple[List[bool], int]:
        """
        Get auxiliary states.
        
        Args:
            index: Result index
            
        Returns:
            Tuple containing (states, size)
            
        Raises:
            RuntimeError: If getting the auxiliary states fails
        """
        size = c_int()
        status = lib._lib.getAUXStates(index, byref(size), None)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to get auxiliary states size: {error_msg}")
        
        if size.value <= 0:
            return [], 0
        
        states = (c_bool * size.value)()
        status = lib._lib.getAUXStates(index, byref(size), states)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to get auxiliary states: {error_msg}")
        
        return [bool(states[i]) for i in range(size.value)], size.value
    
    def get_aux_cycle_counts(self, index: int = 0, channel: int = 0) -> Tuple[List[int], int]:
        """
        Get auxiliary cycle counts.
        
        Args:
            index: Result index
            channel: Channel index
            
        Returns:
            Tuple containing (counts, size)
            
        Raises:
            RuntimeError: If getting the auxiliary cycle counts fails
        """
        size = c_int()
        status = lib._lib.getAUXCycleCounts(index, channel, byref(size), None)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to get auxiliary cycle counts size: {error_msg}")
        
        if size.value <= 0:
            return [], 0
        
        counts = (c_int * size.value)()
        status = lib._lib.getAUXCycleCounts(index, channel, byref(size), counts)
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"Failed to get auxiliary cycle counts: {error_msg}")
        
        return [counts[i] for i in range(size.value)], size.value
    
    def run_usb_comms_test(self) -> None:
        """
        Run a USB communications test.
        
        Raises:
            RuntimeError: If the USB communications test fails
        """
        status = lib._lib.runUSBCommsTest()
        if status != lib.ERROR_NONE:
            error_msg = self.get_last_error_message()
            raise RuntimeError(f"USB communications test failed: {error_msg}")