# Energy-Aware Profiling Tool Developer Guide

Welcome to the Developer Guide for our Energy-Aware Profiling Tool! This guide will walk you through the process of cloning the repository, customizing it for your needs, and adding new file modules to support additional device measurements.

## Cloning the Repository

To get started, follow these steps to clone the repository:

1. Open a terminal or command prompt.
2. Navigate to the directory where you want to clone the repository.
3. Run the following command:
```bash
git clone https://github.com/HPC-CRI/EA2P
```

## Customizing the Tool

After cloning the repository, you may want to customize it according to your specific requirements. Here are some common customization tasks:

### Configuration

1. Modify the default configuration file `config_energy.json` located in the `ea2p/src` directory to adjust settings such as sampling interval, measurement thresholds, etc.

### Visualization output

2. Customize the output components named `__record_data_to_file` in the `ea2p/src/power_meter.py` file to tailor the output representation of energy profiling data as CSV, excel, json saving.

### RAPL path for Intel Users

3. Customize the intel RAPL directory to suit your energy profiling needs depending of your architecture using `ea2p/src/utils.py` files and set some others system configurations.

## Adding a New File Module

If you need to support new device measurements, you can add a new file module to handle the data. Follow these steps:

1. Create a new Python file in the `ea2p/src/` directory for your new module. For example, `FPGA_module.py`.

2. Implement the necessary functions to parse and process the data from the new device.

3. Update the `__init__.py` file in the `ea2p/src` directory to include your new module. For example:

```python
from .FPGA_module import XilinxPower
```

4. Configure the `ea2p/src/wrapper.py` module to support your energy module. Especially the `get_power_consumption` function. Also, adapt the `__set_power` method in the same file to support auto-detection of your devices and make some initializations eventually.

5. Finally, use the `PowerMeter` instance to profile your application by specifying your device in the list of devices in configuration the file. 





