# Installation and Usage

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

meter.start_measure()
time.sleep(180)
meter.stop_measure()		
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

**For more examples of how to use the profiler, clone the original repository from Github : [https://github.com/HPC-CRI/EA2P](https://github.com/HPC-CRI/EA2P) and run examples under `ea2p/examples` directory or visit the API reference and developper guide : [EA2P documentation](https://hpc-cri.github.io/EA2P/).**


