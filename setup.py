import os
from setuptools import setup, find_packages

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyglaz",
    version="0.1.0",
    author="Nick",
    author_email="nick@example.com",
    description="Python bindings for the Glaz spectroscopic library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pyglaz",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.6",
    install_requires=[
        "numpy>=1.16.0",
    ],
    extras_require={
        "examples": ["matplotlib>=3.1.0"],
    },
    # Include C libraries
    package_data={
        "pyglaz": [
            "lib/win32/*.dll",
            "lib/win32/*.lib",
            "lib/win32-static/*.dll", 
            "lib/win64/*.dll",
            "lib/win64/*.lib",
            "lib/win64-static/*.dll",
            "lib/linux64/*.so*"
        ],
    },
    include_package_data=True,
)