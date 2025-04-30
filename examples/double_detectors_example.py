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
from pyglaz import GlazLib, constants

CALCULATION_INDEX = 1 # Index for calculation mode (one can change detector number here)

def main():
    # Path to the single_spectrometer.xml config file in the configs directory
    config_file = os.path.join(Path(__file__).parent.parent, "configs", "double_spectrometer.xml")
    
    # Create a GlazLib instance
    print("Initializing GlazLib...")
    try:
        # Initialize using a config file
        glaz = GlazLib(config_file)

        # Print the library version
        major, minor = glaz.get_version()
        print(f"GlazLib version: {major}.{minor}")

        #Trigger mode
        print("Setting trigger mode...")
        glaz.set_trigger_mode(constants.TRIGGER_EXTERNAL)
        # glaz.set_internal_trigger_frequency(1000)  # Set frequency to 1 kHz
        
        # Capture 10 scans
        print("Setting up capturing mode...")
        glaz.set_scan_count(10)

        print("Setting integration mode...")
        glaz.set_integration_mode(constants.INT_MODE_PULSESYNC)
        glaz.set_integration_time(100)  # Set exposure time to 10 us
        
        print("Run measurements...")
        glaz.run_measurement()

        # Get the result
        print("Getting measurement results...")
        size = glaz.get_all_scans_sizes(CALCULATION_INDEX)
        print("Size of all scans:", size)
        data = glaz.get_all_scans(CALCULATION_INDEX)
        print("Data of all scans:", data)
        
        # Plotting the data
        print("Plotting measurement results...")
        wavelengths = np.array(range(size[1]))  # Assuming wavelengths are not provided
        num_scans = size[0]

        # Set up real-time plotting
        plt.figure(figsize=(10, 6))
        line_objects = []
        for i in range(num_scans):
            line, = plt.plot(wavelengths, data[i], label=f'Scan {i+1}')
            line_objects.append(line)
        
        plt.xlabel('Pixel Index')
        plt.ylabel('Intensity')
        plt.title('Spectral Data from Multiple Scans')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.ion()  # Turn on interactive mode
        plt.show()
        
        # Real-time update loop
        print("Starting real-time monitoring...")
        try:
            state = plt.gcf().number
            while True:
                glaz.run_measurement()
                data = glaz.get_all_scans(CALCULATION_INDEX)

                # Update plot with new data
                for i in range(num_scans):
                    line_objects[i].set_ydata(data[i])

                plt.draw()
                plt.pause(0.1)  # Short pause to allow plot to update

                # Check if the window was closed
                if not plt.fignum_exists(state):
                    print("Plot window was closed")
                    break
            
        except KeyboardInterrupt:
            print("Real-time monitoring stopped by user")

        # Make sure to close the figure if it's still open
        plt.close('all')
        
        print("Real-time monitoring ended")


    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Always make sure to close the connection gracefully
        if 'glaz' in locals():
            print("Closing GlazLib...")
            glaz.close()
    
    print("Done.")


if __name__ == "__main__":
    main()