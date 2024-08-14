# EA2P : Energy-Aware Application Profiler
![PyPI Downloads](https://img.shields.io/pypi/dm/EA2P?color=brightgreen&label=PyPI%20downloads&logo=pypi&logoColor=yellow)

EA2P is an energy profiling tool designed to accurately measure the energy consumption of various computer devices, including RAM, CPU, and GPU. It supports multiple hardware vendors such as Nvidia, AMD, and Intel, allowing comprehensive energy measurements across different systems. The particularity of the tool is the flexibility over target device selection feature and the support for AMD devices energy measurement.  

Please consult the [documentation](https://hpc-cri.github.io/EA2P/) or support resources for your specific CPU and GPU models to find the appropriate configuration and instructions for monitoring energy consumption. Keep in mind that the availability of such features may vary depending on your hardware.

## Features

- **Granular Results:** Provides detailed and fine-grained energy measurements per device and power domains, particularly for Intel-based components, offering a comprehensive understanding of energy consumption across the system.

- **Multi-Device Measurement:** Supports measurement for a variety of devices including RAM, AMD GPU & CPU, Nvidia GPU, and Intel CPU. This comprehensive coverage allows for holistic energy analysis.

- **Code Instrumentation:** Offers an API for code instrumentation as well as a Command Line Interface (CLI) for flexible usage, enabling both direct integration into applications and standalone usage for measurement purposes.

- **Sampling Frequency Control:** Provides users with the option to set the sampling frequency, allowing for customizable energy measurement intervals based on specific requirements and precision needs.

- **Automatic Device Detection:** Automatically detects device vendors and selects appropriate commands, simplifying usage for users and ensuring compatibility across different hardware configurations.

- **Selective Device Measurement:** Allows users to select specific devices for measurement, offering the flexibility to focus on a subset of the system components, which can be advantageous for targeted analysis.
- **Multi-node Measurement:** Provides users with the ability to monitor energy consumption across multiple nodes in traditional HPC or cluster computing environments. A comprehensive energy-per-rank (node) breakdown and total energy consumption for each device type in a homogeneous node system are provided to you.
- **Docker support:** To further enhance the usability and portability of the energy measurement tool, it has been containerized using Docker.

## Requirements
- **RAPL (Running Average Power Limit):** it is a feature found in modern Intel processors that allows monitoring and controlling power consumption. RAPL provides a set of registers that can be used to read power-related information, such as power consumption, and to set power limits for the processor. If it is not installed, you can run the code below:
```bash
sudo apt install msr-tools   # For Ubuntu/Debian
```
- **ROCm-SMI :** ROCm-SMI (Radeon Open Compute System Management Interface) is a command-line interface developed by AMD as part of the ROCm (Radeon Open Compute) software stack. It provides a set of tools for managing and monitoring AMD GPUs kernels that are compatible with the ROCm platform. So you should install the ROCm stack for GPU profiling if it is not installed on your AMD GPU platform : [install ROCm](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/tutorial/install-overview.html)
- **Nvidia-SMI :** Nvidia-SMI(Nvidia System Management Interface) is the ROCm-SMI alternative if you are working with Nvidia GPU. Generally it comes with Nvidia drivers installation : [install Nividia Drivers](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#driver-installation)
- **Perf tools :** It is used to monitore energy for AMD CPU since we did not yet find a way to access the AMD RAPL files in Linux systems.
- **MPI library (for multi-node profiling) :** Ensure that you have an MPI implementation installed on your system. Common implementations include MPICH and OpenMPI. 
```bash
sudo apt-get install openmpi-bin openmpi-common libopenmpi-dev   # For Ubuntu/Debian as example of installation
```
And use the following to run the instrumented code :

```bash
mpiexec -n 4 python my_instrumented_mpi_app.py   # You can change mpiexec with mpirun depending of your MPI installation.
```


## Installation

To install EA2P, simply use pip:

```bash
pip install EA2P
```
## Usage

**Warning :** For any usage, you should authorize the access. Commands bellow could be used especially for perf (for AMD CPU), powercap(for Intel) and dmidecode (for DRAM):
```bash
sudo sh -c 'echo -1 >/proc/sys/kernel/perf_event_paranoid'
sudo chmod -R a+r /sys/firmware/dmi/tables
sudo chmod -R a+r /sys/class/powercap/intel-rapl
```

**Note :** Some examples might require to install specific libraries like TensorFlow or Pytorch as part of the application devellopement.

### Command-Line Interface (CLI)

Run the following command to start profiling: the file can be found in the **"examples"** folder of this repository. **my_application** can be any command line program that can run standalone like a compiled C/C++ program or python program with arguments.

```bash
python ea2p_cli.py my_application
```

### Code Instrumentation

Add annotations to your code to measure energy consumption. 
```python
from ea2p import PowerMeter
config_path = “config.csv” #set the configuration file for flexibility
power_meter = PowerMeter(config_path)

# Annotate the code section you want to measure. "package" and "algorithm" params are required. 
@power_meter.measure_power(package="time", algorithm="sleep",)
def test_sleep(interval):
   time.sleep(interval)
# runing
test_sleep(180) 		
```

### Using context manager

```python
from ea2p import PowerMeter

with PowerMeter() as meter:
   time.sleep(180)		
```

### Using start/stop

```python
from ea2p import PowerMeter
config_path = “config.csv” #set the configuration file for flexibility
power_meter = PowerMeter(config_path)

power_meter.start_measure()
time.sleep(180)
power_meter.stop_measure()		
```
## Configuration file

EA2P allows configuration for specific settings such as devices list, sampling frequency, and more. Configuration can be done via a json configuration file.
```json
{
    "devices_list": "cpu, gpu, ram",
    "sampling_freq": 1.0,
    "energy_unit": "J"
}
```

#### For more examples of how to use the profiler, clone the original repository from Github : [https://github.com/HPC-CRI/EA2P](https://github.com/HPC-CRI/EA2P) and run examples under `ea2p/examples` directory or visit the API reference and developper guide : [EA2P documentation](https://hpc-cri.github.io/EA2P/).


## Contributing

We welcome contributions to EA2P! Please check the [contribution guidelines]() for details on how to contribute to this project.

## License

EA2P is licensed under the [MIT License](https://chat.openai.com/c/link/to/license). See the LICENSE file for more details.

## Acknowledgments

-   **This research was supported by The Transition Institute 1.5 driven by École des Mines de Paris - PSL**
-   **CRI (Centre de recherche en Informatique) - Mines Paris - PSL**

## Contact

For any queries, support, or feedback, feel free to reach out via [email](roblex.nana_tchakoute@minesparis.psl.eu) or through our [website](https://hpc-cri.github.io/EA2P/).

