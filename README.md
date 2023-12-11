# EA2P (Energy-Aware Application Profiling Tool)
![PyPI Downloads](https://img.shields.io/pypi/dm/EA2P?color=brightgreen&label=PyPI%20downloads&logo=pypi&logoColor=yellow)

EA2P is an energy profiling tool designed to accurately measure the energy consumption of various computer devices, including RAM, CPU, and GPU. It supports multiple hardware vendors such as Nvidia, AMD, and Intel, allowing comprehensive energy measurements across different systems. The particularity of the tool is the flexibility over target device selection feature and the support for AMD devices energy measurement.  

## Features

- **Device Energy Measurement**: Profiling and measuring energy consumption of RAM, CPU, and GPU.
- **Vendor Support**: Compatible with hardware from Nvidia, AMD, and Intel for accurate energy readings.
- **Code Instrumentation**: Ability to annotate code for energy measurement purposes. Very important to drive energy optimization step or give a fine graned knownledge on the most importants parts of our code.
- **Command-Line Interface**: User-friendly CLI for convenient and straightforward usage. Usefull to measure the energy of any application in the whole runtime.
- **Device auto-detection**: The Tool is capable to auto detect devices vendors and set the corresponding low level command or energy sensors paths.

## Installation

To install EA2P, simply use pip:

```bash
pip install EA2P
```
## Usage

### Command-Line Interface (CLI)

Run the following command to start profiling:

```bash
python ea2p my_application.py
```

### Code Instrumentation

Add annotations to your code to measure energy consumption. 
```bash
from ea2p import Meter
config_path = “config.csv” #set the configuration file for flexibility
power_meter = Meter(config_path)

# Annotate the code section you want to measure.
@power_meter.measure_power(package="time", algorithm="sleep",)
def test_sleep(interval):
   time.sleep(interval)
# runing
test_sleep(180) 		
```

## Configuration

EA2P allows configuration for specific settings such as output format, verbosity, or vendor-specific settings. Configuration can be done via a configuration file.
```
devices=gpu,cpu,ram
interval=0.01
output_file=experiment.csv
RAPL_FILE=/sys/class/powercap/intel/
energy_unit=wh
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

