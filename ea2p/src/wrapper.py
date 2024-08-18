#!/usr/bin/python
# -*- coding: utf-8 -*-

from .utils import *
from .nvidia import PowerNvidia
from .power import *
from .intel import PowerClientIntel, PowerServerIntel
from .amd import PowerAmdCpu, PowerAmdGpu
from .ram import PowerRam

import logging
import subprocess
import threading
import time

LOGGER = logging.getLogger(__name__)
WH_TO_JOULE = 3600
WH_TO_KW = 1/1000


class PowerWrapper(PowerProfiler):
    """
    A wrapper class for energy monitoring across various devices including CPU, GPU, and DRAM.

    This class facilitates aggregation, coordination of execution, and formatting of the output 
    for measured energy values from different devices.

    Attributes:
        energy_unit (str): The energy unit for the final result report (e.g., 'J' for joule, 'Wh' for Watt-hour, 'kWh' for kilowatt-hour).
        power_devices (str): A string containing the list of specified devices to profile.
        record (dict): A dictionary to contain the recorded measurements.
        thread (Thread): The main Python Thread instance that coordinates measurement from other subprocess threads.
        interval (float): A float value to specify the sampling frequency of measurements.
        power_objects (list): A list that stores different instances of measurements classes for various devices.
        intel (bool): A boolean value indicating the presence (True) or absence (False) of an Intel CPU.
        amd (bool): A boolean value indicating the presence (True) or absence (False) of an AMD CPU.

    Methods:
        start(): Begins monitoring energy usage from the specified list of devices.
        stop(): Stops the energy monitoring process and agregate results.
        get_power_consumption(list): Continuously get energy usage from all specified power monitoring instances.
        __set_power(str): Create instances of power monitoring classes based on the specified power devices ("e.g., "cpu, Ram, gpu").
        get_all_power(list): Get energy usage from all specified power monitoring instances at a specific sampling period.

    """

    def __init__(self, config_file="config_energy.json"):
        """
        Initialize the PowerWrapper instance.

        Parameters:
        	config_file (str): Path to the configuration file to use. If not provided, the default energy unit is Watt-hour with sampling frequency of one(1) second and measurements are across both CPU GPU and RAM
        """
        super().__init__()

        with open(config_file, 'r') as file:
            config = json.load(file)

        self.power_devices = config.get('devices_list').lower()
        self.energy_unit = config.get('energy_unit').lower()
        self.record = {}
        self.thread = None
        self.interval = config.get('sampling_freq')
        self.amd = False
        self.intel = False
        self.intel_ram = False
        self.power_objects = self.__set_power(self.power_devices)

    def __set_power(self, power_devices):
        """
        Create instances of power monitoring classes based on the specified power devices.

        Parameters:
        	power_devices (str): A comma-separated string specifying the power devices to monitor.

        Returns:
        	power_objects (list): A list of power monitoring instances, respectivelly for each device in the devices list.
        """
        cpu_brand = ""
        power_objects = list()
        if ("cpu" not in power_devices) and ("gpu" not in power_devices) and ("ram" not in power_devices):
            raise ValueError("Please specify at least one device type to monitor in [cpu, gpu, ram] ")

        if "cpu" in power_devices:
            cpu_brand = cpuinfo.get_cpu_info()['brand_raw']
            if "Core(TM)" in cpu_brand:
                self.intel = True
                self.intel_power = PowerClientIntel()
            elif "Xeon" in cpu_brand:
                self.intel = True
                self.intel_power = PowerServerIntel()
            elif "AMD" in cpu_brand:
                self.amd_power = PowerAmdCpu()
                self.amd = True
                LOGGER.info("AMD found")
            else:
                raise SystemError(
                    "Unable to detect the CPU informations of your system. "
                    "Try to remove CPU in your config_energy.json file "
                    "to monitor other components like RAM or GPU energies "
                )

        if "gpu" in power_devices:
            try:
                subprocess.check_output('nvidia-smi')
                power_objects.append(PowerNvidia())
            except Exception:
                pass

            try:
                subprocess.check_output('rocminfo')
                power_objects.append(PowerAmdGpu())
            except Exception:
                pass

        if "ram" in power_devices and not ("Xeon" in cpu_brand):
            power_objects.append(PowerRam())

        return power_objects

    def get_all_power(self, power_objects):
        """
        Get energy usage from all specified power monitoring instances at a specific sampling period.

        Parameters:
        	power_objects (list): List of power monitoring instances, respectivelly for each device in the devices list.
        """
        energy_usage = {}
        for obj in power_objects:
            energy_usage.update(obj.append_energy_usage())

        self.power_draws.append(energy_usage)

    def get_power_consumption(self, power_objects):
        """
        Continuously get energy usage from all specified power monitoring instances.

        Parameters:
        	power_objects (list): List of power monitoring instances, respectivelly for each device in the devices list.
        """
        if self.amd:
            self.amd_power.start()

        if power_objects and self.intel:
            self.get_all_power(power_objects)
            while getattr(self.thread, "do_run", True):
                self.get_all_power(power_objects)
                self.intel_record.append(self.intel_power.append_energy_usage())
                time.sleep(self.interval)
            self.get_all_power(power_objects)
        elif power_objects:
            self.get_all_power(power_objects)
            while getattr(self.thread, "do_run", True):
                self.get_all_power(power_objects)
                time.sleep(self.interval)
            self.get_all_power(power_objects)
        elif self.intel:
            while getattr(self.thread, "do_run", True):
                self.intel_record.append(self.intel_power.append_energy_usage())
                time.sleep(self.interval)

    def start(self):
        """
        Start the power monitoring process. This function creates the main threads to coordinate subprocesses
        that profile energy/power on different devices.

        This function initializes threads to profile power consumption on various devices concurrently. Each thread
        corresponds to a specific device and is responsible for initiating the power profiling process for that device.
        The devices are specified in a list of device names. Power profiling subprocesses for each device are
        coordinated through separate threads to ensure parallel execution.

        Example:
            PowerWrapper wrapper = PowerWrapper()
            wrapper.start()

        Note:
            This function assumes the existence of a class or function responsible for profiling power consumption
            on individual devices. The actual power profiling logic should be implemented within the respective
            threads or subprocesses.
        """
        LOGGER.info("Starting CPU power monitoring...")
        self.start_time = time.time()
        self.power_draws = []
        self.intel_record = []
        self.record = {}
        if self.thread and self.thread.is_alive():
            self.stop_thread()
            self.thread.join()
        self.thread = threading.Thread(target=self.get_power_consumption, args=(self.power_objects,))
        # self.thread.do_run = True
        self.thread.start()

    def stop(self):
        """
        Stop the power monitoring process and collect/aggregate the final power consumption data.

        This function stops the power monitoring process by terminating the main threads responsible for coordinating
        the profiling of energy/power consumption on various devices. It ensures the orderly shutdown of all
        power profiling subprocesses and releases any associated resources. Additionally, it collects and aggregates
        data from the different devices' profiling, allowing for further analysis or reporting.

        Example:
            PowerWrapper wrapper = PowerWrapper()
            wrapper.stop()

        """
        if self.thread and self.thread.is_alive():
            # self.stop_thread()
            self.thread.do_run = False
            self.thread.join()
        
        end_time = time.time()

        usages = pd.DataFrame(self.power_draws)
        cpu_energy = pd.DataFrame()
        usages = usages.sum().to_frame().T
        usages = usages * self.interval / 3600          # convert watt to watt-hour for RAM and GPU especially

        if self.amd:
            self.amd_power.stop()
            cpu_energy = self.amd_power.parse_log()
            usages = pd.concat([cpu_energy, usages], axis=1)

        if self.intel:
            self.intel_record.append(self.intel_power.append_energy_usage())

            cpu_energy = pd.DataFrame(self.intel_record)
            cpu_energy = cpu_energy.diff().fillna(cpu_energy)
            cpu_energy = cpu_energy.iloc[1:, :]
            cpu_energy = cpu_energy.mask(cpu_energy.lt(0)).ffill().fillna(0)
            cpu_energy = cpu_energy.sum().to_frame().T
            usages = pd.concat([cpu_energy, usages], axis=1)

        if self.energy_unit=="j":
            usages = usages * WH_TO_JOULE
        elif self.energy_unit=="wh":
            pass
        elif self.energy_unit=="kwh":
            usages = usages * WH_TO_KW
        else :
            LOGGER.info("WARRNING : The specified energy unit is not supported. "
                        "Please try to specify J or WH or KWH in the energy config file. "
                        "Otherwise, the default unit of WH is used")


        usages[TOTAL_CPU_TIME] = end_time - self.start_time
        self.record = usages.round(5)
