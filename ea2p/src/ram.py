#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Python classes monitoring GPU's power usage
during a time delimited between a start and a stop methods
"""
__all__ = ["PowerRam"]

import os
import subprocess
import psutil

from .utils import SAMPLING_FREQUENCY


class PowerRam():

    def __init__(self):
        self.ram_power = self.get_memory_power()
        self.number_slots = self.get_number_slots()

    def append_energy_usage(self):
        ram_usage_percent = psutil.virtual_memory()[2]
        energy_usage = {"DRAM energy (Wh)":(self.ram_power * self.number_slots * (ram_usage_percent / 100.0)) * SAMPLING_FREQUENCY / 3600}
        #print(energy_usage)
        return energy_usage

    def get_number_slots(self):
        os.system("dmidecode -t 17 | grep 'DIMM' > tmp_ram_slots.txt")
        #os.system("sudo-g5k dmidecode -t 17 | grep 'DIMM' > tmp_ram_slots.txt")
        with open(r"tmp_ram_slots.txt", 'r') as fp:
            lines = len(fp.readlines())
        return lines

    def get_memory_power(self):
        #os.system("sudo-g5k dmidecode -t 17 | grep 'Type: ' > tmp_ram_type.txt")
        os.system("dmidecode -t 17 | grep 'Type: ' > tmp_ram_type.txt")
        with open(r"tmp_ram_type.txt", 'r') as fp:
            ram_type = fp.readlines()[0]

        os.system("dmidecode -t 17 | grep 'GB' > tmp_ram_size.txt")
        with open(r"tmp_ram_size.txt", 'r') as fp2:
            ram_size = fp2.readlines()[0]

        if ("DDR5" in ram_type) or ("DDR4" in ram_type) :
            if "16" in ram_size :
                return 3.0
            elif "32" in ram_size:
                return 3.5
            elif "64" in ram_size:
                return 6.0
            elif "128" in ram_size:
                return 8.0
            else :
                return 10.0
        elif "DDR3" in ram_type:
            return 4.5
        else :
            return 0.0
