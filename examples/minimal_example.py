#!/usr/bin/env python3
"""
Minimal example of using the PyGlaz library with a single spectrometer.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add the parent directory to the path to be able to import pyglaz
sys.path.insert(0, str(Path(__file__).parent.parent))
from pyglaz import GlazLib

def main():
    # Path to the single_spectrometer.xml config file in the configs directory
    config_file = os.path.join(Path(__file__).parent.parent, "configs", "single_spectrometer.xml")
    
    # Create a GlazLib instance
    print("Initializing GlazLib...")
    try:
        # Initialize using a config file
        glaz = GlazLib(config_file)
        
        # Alternatively, initialize using device type (uncomment to use this method):
        # glaz = GlazLib(device_type=glaz.GLAZ_LINESCAN_II_V2_SINGLE_DEVICE_TYPE)
        
        # Print the library version
        major, minor = glaz.get_version()
        print(f"GlazLib version: {major}.{minor}")
        
        # Capture background with 10 scans
        print("Capturing background...")
        glaz.capture_background(10)
        
        # Run a measurement
        print("Running measurement...")
        glaz.run_measurement()
        
        # Get results
        data, size = glaz.get_result()
        print(f"Got {size} data points")
        
        # Plot the results if data is available
        if size > 0:
            plt.figure(figsize=(10, 6))
            plt.plot(data)
            plt.title("Spectrometer Data")
            plt.xlabel("Pixel")
            plt.ylabel("Intensity")
            plt.grid(True)
            plt.tight_layout()
            plt.show()
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Always make sure to close the connection gracefully
        if 'glaz' in locals():
            print("Closing GlazLib...")
            glaz.close()
    
    print("Done.")

# Constants from GlazLib to make the example more readable
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

TRIGGER_EXTERNAL = 0
TRIGGER_INTERNAL = 1
TRIGGER_BURST = 2

if __name__ == "__main__":
    main()