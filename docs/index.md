# Getting started
![PyPI Downloads](https://img.shields.io/pypi/dm/EA2P?color=brightgreen&label=PyPI%20downloads&logo=pypi&logoColor=yellow)

EA2P is an energy profiling tool designed to accurately measure the energy consumption of various computer devices, including RAM, CPU, and GPU. It supports multiple hardware vendors such as Nvidia, AMD, and Intel, allowing comprehensive energy measurements across different systems. The particularity of the tool is the flexibility over target device selection feature and the support for AMD devices energy measurement.  

## Features

- **Device Energy Measurement**: Profiling and measuring energy consumption of RAM, CPU, and GPU.
- **Vendor Support**: Compatible with hardware from Nvidia, AMD, and Intel for accurate energy readings.
- **Code Instrumentation**: Ability to annotate code for energy measurement purposes. Very important to drive energy optimization step or give a fine graned knownledge on the most importants parts of our code.
- **Command-Line Interface**: User-friendly CLI for convenient and straightforward usage. Usefull to measure the energy of any application in the whole runtime.
- **Device auto-detection**: The Tool is capable to auto detect devices vendors and set the corresponding low level command or energy sensors paths.

## Requirements
- **RAPL (Running Average Power Limit):** it is a feature found in modern Intel processors that allows monitoring and controlling power consumption. RAPL provides a set of registers that can be used to read power-related information, such as power consumption, and to set power limits for the processor. If it is not installed, you can run the code below:
```bash
sudo apt install msr-tools   # For Ubuntu/Debian
```
- **ROCm-SMI :** ROCm-SMI (Radeon Open Compute System Management Interface) is a command-line interface developed by AMD as part of the ROCm (Radeon Open Compute) software stack. It provides a set of tools for managing and monitoring AMD GPUs kernels that are compatible with the ROCm platform. So you should install the ROCm stack for GPU profiling if it is not installed on your AMD GPU platform : [install ROCm](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/tutorial/install-overview.html)
- **Nvidia-SMI :** Nvidia-SMI(Nvidia System Management Interface) is the ROCm-SMI alternative if you are working with Nvidia GPU. Generally it comme with Nvidia drivers installation
- **Perf tools :** It's used to monitore energy for AMD CPU since we didn't found a way to access the AMD RAPL files in Linux systems.


