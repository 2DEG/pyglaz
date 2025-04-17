"""
Utility functions for the pyglaz package.

This module provides utility functions for working with Glaz configuration files.
"""

import os
from typing import Optional, List


def find_config_file(config_name: Optional[str] = None, search_dirs: Optional[List[str]] = None) -> str:
    """
    Find a configuration file by name.
    
    Args:
        config_name: Name of the configuration file (with or without .xml extension).
                     If None, it will look for either single_spectrometer.xml or 
                     double_spectrometer.xml.
        search_dirs: List of directories to search for the configuration file.
                     If None, it will search in the standard locations.
                     
    Returns:
        Full path to the configuration file
        
    Raises:
        FileNotFoundError: If the configuration file is not found
    """
    if search_dirs is None:
        # Default search locations
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        search_dirs = [
            os.path.join(os.path.dirname(pkg_dir), 'configs'),  # Look in /configs directory first
            pkg_dir,  # Look in package directory
            os.getcwd(),  # Look in current working directory
        ]
    
    # If config_name is None, look for default configurations
    if config_name is None:
        default_configs = ['single_spectrometer.xml', 'double_spectrometer.xml']
        for config in default_configs:
            for directory in search_dirs:
                filepath = os.path.join(directory, config)
                if os.path.isfile(filepath):
                    return filepath
        raise FileNotFoundError(f"Could not find default configuration files: {', '.join(default_configs)}")
    
    # Add .xml extension if not present
    if not config_name.lower().endswith('.xml'):
        config_name += '.xml'
    
    # Search for the specified config file
    for directory in search_dirs:
        filepath = os.path.join(directory, config_name)
        if os.path.isfile(filepath):
            return filepath
    
    raise FileNotFoundError(f"Could not find configuration file: {config_name}")


def list_available_configs(search_dirs: Optional[List[str]] = None) -> List[str]:
    """
    List all available configuration files.
    
    Args:
        search_dirs: List of directories to search for configuration files.
                     If None, it will search in the standard locations.
                     
    Returns:
        List of paths to configuration files
    """
    if search_dirs is None:
        # Default search locations
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        search_dirs = [
            os.path.join(os.path.dirname(pkg_dir), 'configs'),  # Look in /configs directory first
            pkg_dir,  # Look in package directory
            os.getcwd(),  # Look in current working directory
        ]
    
    config_files = []
    for directory in search_dirs:
        if os.path.isdir(directory):
            for file in os.listdir(directory):
                if file.lower().endswith('.xml'):
                    config_files.append(os.path.join(directory, file))
    
    return config_files