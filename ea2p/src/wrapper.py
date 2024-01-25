#!/usr/bin/python
# -*- coding: utf-8 -*-

from .utils import *
from .nvidia import PowerNvidia
from .power import *
from .intel import PowerClientIntel, PowerServerIntel
from .amd import PowerAmdCpu, PowerAmdGpu
from .ram import PowerRam

import datetime
import glob
import logging
import subprocess
import threading
import time

LOGGER = logging.getLogger(__name__)
WH_TO_JOULE = 3600
WH_TO_KW = 1/1000


class PowerWrapper(Power):
    """
    A wrapper class to manage and coordinate the power monitoring of different devices.
    """

    def __init__(self, config_file="config_energy.json"):
        """
        Initialize the PowerWrapper instance.

        Parameters:
        - config_file: Path to the configuration file.
        """
        super().__init__()

        with open(config_file, 'r') as file:
            config = json.load(file)

        self.power_devices = config.get('devices_list')
        self.energy_unit = config.get('energy_unit')
        self.record = {}
        self.thread = None
        self.interval = config.get('sampling_freq')
        self.amd = False
        self.intel = False
        self.power_objects = self.__set_power(self.power_devices)

    def __set_power(self, power_devices):
        """
        Create instances of power monitoring classes based on the specified power devices.

        Parameters:
        - power_devices (str): A comma-separated string specifying the power devices to monitor.

        Returns:
        - power_objects (list): A list of power monitoring instances.
        """
        power_objects = list()
        if ("cpu" not in power_devices) and ("gpu" not in power_devices) and ("ram" not in power_devices):
            raise ValueError("Please specify at least one device type to monitor in [cpu, gpu, ram] ")

        if "cpu" in power_devices:
            cpu_brand = cpuinfo.get_cpu_info()['brand_raw']
            if "Core(TM)" in cpu_brand or "Xeon" in cpu_brand:
                self.intel_power = PowerClientIntel()
                self.intel = True
            elif "AMD" in cpu_brand:
                self.amd_power = PowerAmdCpu()
                self.amd = True
                LOGGER.info("AMD found")
            else:
                power_objects.append(NoCpuPower())

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

        if "ram" in power_devices:
            power_objects.append(PowerRam())

        return power_objects

    def get_all_power(self, power_objects):
        """
        Get energy usage from all specified power monitoring instances.

        Parameters:
        - power_objects (list): List of power monitoring instances.
        """
        energy_usage = {}
        for obj in power_objects:
            energy_usage.update(obj.append_energy_usage())

        self.power_draws.append(energy_usage)

    def get_power_consumption(self, power_objects):
        """
        Continuously get energy usage from all specified power monitoring instances.

        Parameters:
        - power_objects (list): List of power monitoring instances.
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
        Start the power monitoring process.
        """
        LOGGER.info("Starting CPU power monitoring...")
        self.start_time = time.time()
        self.power_draws = []
        self.intel_record = []
        self.record = {}
        if self.thread and self.thread.is_alive():
            self.stop_thread()
        self.thread = threading.Thread(target=self.get_power_consumption, args=(self.power_objects,))
        self.thread.start()

    def stop(self):
        """
        Stop the power monitoring process and collect the final power consumption data.
        """
        if self.thread and self.thread.is_alive():
            self.stop_thread()

        usages = pd.DataFrame(self.power_draws)
        cpu_energy = pd.DataFrame()
        usages = usages.sum().to_frame().T
        usages = usages * self.interval / 3600          # convert watt to watt-hour

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

        end_time = time.time()

        if self.energy_unit=="J":
            usages = usages * WH_TO_JOULE
        elif self.energy_unit=="WH":
            pass
        elif self.energy_unit=="KWH":
            usages = usages * WH_TO_KW
        else :
            LOGGER.info("WARRNING : The specified energy unit is not supported. "
                        "Please try to specify J or WH or KWH in the energy config file. "
                        "Otherwise, the default unit of WH is used")


        usages[TOTAL_CPU_TIME] = end_time - self.start_time
        self.record = usages.round(5)
