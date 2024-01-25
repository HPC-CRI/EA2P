# EA2P (Energy-Aware Application Profiling) Tool
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
from ea2p import Meter
config_path = “config.csv” #set the configuration file for flexibility
power_meter = Meter(config_path)

# Annotate the code section you want to measure. "package" and "algorithm" params are required. 
@power_meter.measure_power(package="time", algorithm="sleep",)
def test_sleep(interval):
   time.sleep(interval)
# runing
test_sleep(180) 		
```

## Configuration

EA2P allows configuration for specific settings such as devices list, sampling frequency, and more. Configuration can be done via a json configuration file.
```json
{
    "devices_list": "cpu, gpu, ram",
    "sampling_freq": 1.0,
    "energy_unit": "J"
}
```


## Contributing

We welcome contributions to EA2P! Please check the [contribution guidelines]() for details on how to contribute to this project.

## License

EA2P is licensed under the [MIT License](https://chat.openai.com/c/link/to/license). See the LICENSE file for more details.

## Acknowledgments

-   **This research was supported by The Transition Institute 1.5 driven by École des Mines de Paris - PSL**
-   **CRI (Centre de recherche en Informatique) - Mines Paris - PSL**

## Contact

For any queries, support, or feedback, feel free to reach out via [email](roblex.nana_tchakoute@minesparis.psl.eu) or through our [website](https://ea2p.com/).

