# Getting started
![PyPI Downloads](https://img.shields.io/pypi/dm/EA2P?color=brightgreen&label=PyPI%20downloads&logo=pypi&logoColor=yellow)

EA2P is an energy profiling tool designed to accurately measure the energy consumption of various computer devices, including RAM, CPU, and GPU. It supports multiple hardware vendors such as Nvidia, AMD, and Intel, allowing comprehensive energy measurements across different systems. The particularity of the tool is the flexibility over target device selection feature and the support for AMD devices energy measurement.  

## Features

- **Granular Results:** Provides detailed and fine-grained energy measurements per device and power domains, particularly for Intel-based components, offering a comprehensive understanding of energy consumption across the system.

- **Multi-Device Measurement:** Supports measurement for a variety of devices including RAM, AMD GPU & CPU, Nvidia GPU, and Intel CPU. This comprehensive coverage allows for holistic energy analysis.

- **Code Instrumentation:** Offers an API for code instrumentation as well as a Command Line Interface (CLI) for flexible usage, enabling both direct integration into applications and standalone usage for measurement purposes.

- **Sampling Frequency Control:** Provides users with the option to set the sampling frequency, allowing for customizable energy measurement intervals based on specific requirements and precision needs.

- **Automatic Device Detection:** Automatically detects device vendors and selects appropriate commands, simplifying usage for users and ensuring compatibility across different hardware configurations.

- **Selective Device Measurement:** Allows users to select specific devices for measurement, offering the flexibility to focus on a subset of the system components, which can be advantageous for targeted analysis.
- **Ease of Use:** Python's readability and extensive libraries make the tool more accessible to users, promoting ease of understanding, modification, and extension.

## Requirements
- **RAPL (Running Average Power Limit):** it is a feature found in modern Intel processors that allows monitoring and controlling power consumption. RAPL provides a set of registers that can be used to read power-related information, such as power consumption, and to set power limits for the processor. If it is not installed, you can run the code below:
```bash
sudo apt install msr-tools   # For Ubuntu/Debian
```
- **ROCm-SMI :** ROCm-SMI (Radeon Open Compute System Management Interface) is a command-line interface developed by AMD as part of the ROCm (Radeon Open Compute) software stack. It provides a set of tools for managing and monitoring AMD GPUs kernels that are compatible with the ROCm platform. So you should install the ROCm stack for GPU profiling if it is not installed on your AMD GPU platform : [install ROCm](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/tutorial/install-overview.html)
- **Nvidia-SMI :** Nvidia-SMI(Nvidia System Management Interface) is the ROCm-SMI alternative if you are working with Nvidia GPU. Generally it comes with Nvidia drivers installation : [install Nividia Drivers](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#driver-installation)
- **Perf tools :** It is used to monitore energy for AMD CPU since we didn't find a way to access the AMD RAPL files in Linux systems.
