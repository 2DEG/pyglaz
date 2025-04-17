#!/usr/bin/env python
# Basic example of using pyglaz library with XML configuration files

import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import numpy as np
import matplotlib.pyplot as plt
from pyglaz import GlazLib
from pyglaz.utils import find_config_file, list_available_configs
from pyglaz._bindings import (
    TRIGGER_INTERNAL,
    INT_MODE_PULSESYNC,
    RESOLUTION_16BIT
)


def main():
    # List available configuration files
    print("Available configuration files:")
    configs = list_available_configs()
    for config in configs:
        print(f"  - {os.path.basename(config)}")
    print()

    # Create an instance of the GlazLib wrapper
    # It will automatically look for and use an XML config file
    print("Initializing GlazLib...")
    try:
        # Try to use single_spectrometer.xml first
        glaz = GlazLib(config_file="single_spectrometer.xml", allow_demo=True)
    except (RuntimeError, FileNotFoundError) as e:
        print(f"Error with single_spectrometer.xml: {str(e)}")
        print("Trying with default initialization...")
        
        try:
            # If single_spectrometer.xml fails, try default initialization
            # This will look for any available XML config or fall back to device type
            glaz = GlazLib(allow_demo=True)
        except RuntimeError as e:
            print(f"Error initializing GlazLib: {str(e)}")
            return

    try:
        # Print library version
        major, minor = glaz.get_version()
        print(f"GlazLib version: {major}.{minor}")

        # The XML config file should handle most of the configuration,
        # but we can adjust some settings if needed
        print("Fine-tuning device settings...")
        
        # Set to internal trigger mode
        glaz.set_trigger_mode(TRIGGER_INTERNAL)
        
        # Set internal trigger frequency (Hz)
        glaz.set_internal_trigger_frequency(100.0)
        
        # Set hardware averaging to improve signal quality
        # Changed from 16 to 8 to stay within the valid range [0..8]
        glaz.set_hardware_averaging(8)
        
        # Set scan count
        glaz.set_scan_count(10)

        # Capture background (optional but recommended)
        print("Capturing background...")
        glaz.capture_background(count=5)  # Average 5 scans for background

        # Run a measurement
        print("Running measurement...")
        glaz.run_measurement()  # This is blocking until measurement is complete

        # Get the result
        print("Getting measurement results...")
        data, size = glaz.get_result()
        
        if size > 0:
            print(f"Received {size} data points")
            print(f"Data min: {np.min(data)}, max: {np.max(data)}, mean: {np.mean(data):.2f}")
            
            # Plot the results
            plt.figure(figsize=(10, 6))
            plt.plot(data)
            plt.title("Spectrum Measurement")
            plt.xlabel("Pixel")
            plt.ylabel("Intensity")
            plt.grid(True)
            
            # Save the plot
            plt.savefig("spectrum_measurement.png")
            print("Saved plot to 'spectrum_measurement.png'")
            
            # Show the plot (uncomment if running interactively)
            # plt.show()
        else:
            print("No data received from measurement")

        # Example of a non-blocking measurement
        print("Running non-blocking measurement...")
        
        # Start a non-blocking measurement
        glaz.start_measurement()
        
        # Wait for the measurement to complete
        while not glaz.is_measurement_done():
            print("Measurement in progress...")
            time.sleep(0.5)
        
        print("Non-blocking measurement complete")
        
        # Get all scans sizes
        num_scans, pixels_per_scan = glaz.get_all_scans_sizes()
        print(f"Measurement collected {num_scans} scans with {pixels_per_scan} pixels each")
        
        # Get all scans as a 2D array if available
        try:
            all_scans = glaz.get_all_scans()
            if len(all_scans) > 0:
                print(f"All scans shape: {all_scans.shape}")
                
                # Plot a heatmap of all scans
                plt.figure(figsize=(10, 6))
                plt.imshow(all_scans, aspect='auto', interpolation='nearest')
                plt.colorbar(label='Intensity')
                plt.title("All Scans")
                plt.xlabel("Pixel")
                plt.ylabel("Scan Number")
                
                # Save the plot
                plt.savefig("all_scans.png")
                print("Saved all scans plot to 'all_scans.png'")
                
                # Show the plot (uncomment if running interactively)
                # plt.show()
        except RuntimeError as e:
            print(f"Could not retrieve all scans: {str(e)}")

    except RuntimeError as e:
        print(f"Error during operation: {str(e)}")
    finally:
        # Always close the session to release resources
        print("Closing GlazLib session...")
        glaz.close()
        print("Done")


if __name__ == "__main__":
    main()