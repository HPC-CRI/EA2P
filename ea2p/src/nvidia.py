#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Python classes monitoring GPU's power usage
during a time delimited between a start and a stop methods
"""
__all__ = ["NoGpuPower", "PowerNvidia"]

import subprocess

from .utils import SAMPLING_FREQUENCY

class NoGpuPower():
    """
    Class used when no GPU is available
    """

    def __init__(self):
        pass


class PowerNvidia():

    def __init__(self):
        # Query drivers for the first time to avoid "Unknow" in result
        subprocess.check_output("nvidia-smi --query-gpu=power.draw --format=csv", shell=True)
    
    def append_energy_usage(self):
        cmd = "nvidia-smi --query-gpu=power.draw --format=csv"
        energy_usage = subprocess.check_output(cmd, shell=True)
        energy_usage = energy_usage.decode("utf-8").replace(" W", "")
        energy_usage = energy_usage.split("\n")[1:-1]
        #print(energy_usage)
        energy = {"GPU " + str(i): (float(energy_usage[i]) * SAMPLING_FREQUENCY / 3600) for i in range(len(energy_usage))}
        
        return energy
