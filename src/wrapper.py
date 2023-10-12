#!/usr/bin/python
# -*- coding: utf-8 -*-

from .utils import*
from .nvidia import PowerNvidia
from .power import*
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


class PowerWrapper(Power):
    def __init__(self, power_devices = "cpu"):
        super().__init__()
        self.power_devices = power_devices
        self.record = {}
        self.thread = None
        self.interval = SAMPLING_FREQUENCY
        self.amd = False
        self.intel = False
        self.power_objects = self.__set_power(self.power_devices)


    def __set_power(self, power_devices):
        power_objects = list()
        if (not "cpu" in power_devices) and (not "gpu" in power_devices) and (not "ram" in power_devices):
            raise ValueError(
                    "Please specify at least one device type to monitorein [cpu, gpu, ram] "
                )

        if "cpu" in power_devices:
            if "Core(TM)" in cpuinfo.get_cpu_info()['brand_raw']:
                #power_objects.append(PowerClientIntel())
                self.intel = True
                self.intel_power = PowerClientIntel()
            elif "Xeon" in cpuinfo.get_cpu_info()['brand_raw']:
                power_objects.append(PowerServerIntel())
            elif "AMD" in cpuinfo.get_cpu_info()['brand_raw']:
                self.amd_power = PowerAmdCpu()
                self.amd = True
                print("AMD found")
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
        
        energy_usage = {}
        for obj in power_objects:
            energy_usage.update(obj.append_energy_usage())
        
        #print("energy usage : ", energy_usage)
        self.power_draws.append(energy_usage)

    def get_power_consumption(self, power_objects):
        if self.amd:
            self.amd_power.start()
        
        # if self.intel:
        #     self.intel_record.append(self.intel_power.append_energy_usage())
            
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
        #print(self.power_draws)

    def start(self):
        LOGGER.info("starting CPU power monitoring ...")
        self.start_time = time.time()
        self.power_draws = []
        self.intel_record = []
        self.record = {}
        if self.thread and self.thread.is_alive():
            self.stop_thread()
        self.thread = threading.Thread(target=self.get_power_consumption, args=(self.power_objects,)) 
        self.thread.start()

    def stop(self):
        if self.thread and self.thread.is_alive():
            self.stop_thread()
        #LOGGER.info("stoping CPU power monitoring ...")
    
        usages = pd.DataFrame(self.power_draws)
        #usages = usages.diff().fillna(usages)
        #print(self.power_draws)
        #print(usages)
        cpu_energy = pd.DataFrame()
        usages = usages.sum().to_frame().T
        
        if self.amd:
            self.amd_power.stop()
            cpu_energy = self.amd_power.parse_log()
            usages = pd.concat([cpu_energy.iloc[[-1]].reset_index(drop=True), usages], axis=1)
        
        if self.intel:
            self.intel_record.append(self.intel_power.append_energy_usage())
            
            cpu_energy = pd.DataFrame(self.intel_record)
            cpu_energy = cpu_energy.diff().fillna(cpu_energy)
            cpu_energy = cpu_energy.iloc[1:, :]
            #print(cpu_energy)
            cpu_energy = cpu_energy.mask(cpu_energy.lt(0)).ffill().fillna(0)
            cpu_energy = cpu_energy.sum().to_frame().T
            usages = pd.concat([cpu_energy, usages], axis=1)

        #print(cpu_energy.iloc[[-1]].reset_index(drop=True))
        #print(usages)
        
        end_time = time.time()
    
        usages[TOTAL_CPU_TIME] = end_time - self.start_time
        self.record = usages.round(5)
        #print(self.record)
        #self.record[TOTAL_ENERGY_ALL] = 0