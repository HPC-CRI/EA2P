#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Python classes monitoring Nvidia GPU's power usage by querying system management interface.
"""
__all__ = ["PowerNvidia"]

import subprocess

class PowerNvidia():
    """
    Class for monitoring Nvidia GPU power usage
    """

    def __init__(self):
        # Query drivers for the first time to avoid "Unknown" in the result. This also test the availability and working for Nvidia's drivers
        try:
            subprocess.check_output("nvidia-smi --query-gpu=power.draw --format=csv", shell=True)
        except subprocess.CalledProcessError:
            print("Error querying GPU power. Check if 'nvidia-smi' is installed and available.")

    def append_energy_usage(self):
        """
        Append Nvidia GPU energy usage to dict containing sampling power measurements.

        Returns:
        - Dictionary containing GPU power usage per GPU devices.
        """

        cmd = "nvidia-smi --query-gpu=power.draw --format=csv"
        energy_usage = subprocess.check_output(cmd, shell=True)
        energy_usage = energy_usage.decode("utf-8").replace(" W", "")
        energy_usage = energy_usage.split("\n")[1:-1]
        #print(energy_usage)
        energy = {"GPU " + str(i): (float(energy_usage[i])) for i in range(len(energy_usage))}
        
        return energy
