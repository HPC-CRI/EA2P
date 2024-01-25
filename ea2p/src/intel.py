#!/usr/bin/python
# -*- coding: utf-8 -*-
"""

"""
# __all__ = [
#     "PowerClient",
# ]

import glob
from .utils import *
from .power import PowerLinux

from .utils import JOULE_TO_WATT

class PowerClientIntel(PowerLinux):
    def __init__(self):
        super().__init__()
        self.cpu_sub_doms = self.get_cpu_sub_domains()
        self.power_draws = []
        self.record = {}
        self.start_time = None

    def get_cpu_sub_domains(self):
        """
        Get the list of CPU sub-domains.

        Returns:
        - List of tuples containing CPU domain information.
        """
        cpu_sub_doms = []
        for dom, name in self.cpu_doms:
            dom_paths = glob.glob(
                READ_RAPL_PATH.format(dom)
                + RAPL_PATH_SUB_DOMS.format(dom, "*")
                + RAPL_DEVICENAME_FILE
            )
            for i, file in enumerate(dom_paths):
                file = Path(file)
                subdom_name = file.read_text().replace('\n','')
                cpu_sub_doms.append((dom, i, subdom_name))
        return cpu_sub_doms

    def append_energy_usage(self):
        """
        Append CPU energy usage.

        Returns:
        - Dictionary containing CPU energy usage.
        """
        energy_usage = {}
        energies = [self.get_cpu_energy_package(cpu_domain, cpu_sub_domain)
                for cpu_domain, cpu_sub_domain, subdom_name in self.cpu_sub_doms]

        energies_2 = [self.get_cpu_energy(dom) for dom, name in self.cpu_doms]
        i = 0
        for cpu_domain, cpu_sub_domain, subdom_name in self.cpu_sub_doms:
            energy_usage[subdom_name] = energies[i] / JOULE_TO_WATT
            i += 1
        i = 0
        for dom, name in self.cpu_doms:
            energy_usage[name] = energies_2[i] / JOULE_TO_WATT
            i += 1

        return energy_usage

    def get_cpu_energy_package(self, domain, sub_domain):
        """
        Get CPU energy usage for a specific sub-domain.

        Parameters:
        - domain: CPU domain.
        - sub_domain: CPU sub-domain.

        Returns:
        - Energy usage for the specified CPU sub-domain.
        """
        energy_file = (
            Path(READ_RAPL_PATH.format(domain))
            / (RAPL_PATH_SUB_DOMS.format(domain, sub_domain))
            / RAPL_ENERGY_FILE
        )
        energy = int(energy_file.read_text())
        return energy

    def get_cpu_energy(self, cpu):
        """
        Get CPU energy usage for a specific CPU.

        Parameters:
        - cpu: CPU identifier.

        Returns:
        - Energy usage for the specified CPU.
        """
        cpu_energy_file = Path(READ_RAPL_PATH.format(cpu)) / RAPL_ENERGY_FILE
        energy = int(cpu_energy_file.read_text())
        return energy


class PowerServerIntel(PowerLinux):
    def __init__(self):
        super().__init__()
        self.dram_ids = self.__get_drams_ids()
        self.power_draws = []
        self.record = {}
        self.start_time = None

    def __get_drams_ids(self):
        """
        Get the list of DRAM IDs.

        Returns:
        - List of tuples containing CPU and DRAM IDs.
        """
        dram_id_list = []
        for cpu in self.cpu_ids:
            dram_paths = glob.glob(
                READ_RAPL_PATH.format(cpu)
                + RAPL_DRAM_PATH.format(cpu, "*")
                + RAPL_DEVICENAME_FILE
            )
            for i, dram_file in enumerate(dram_paths):
                dram_file = Path(dram_file)
                if "dram" in dram_file.read_text():
                    dram_id_list.append((cpu, i))
                    break
        return dram_id_list

    def append_energy_usage(self):
        """
        Append CPU and memory energy usage.

        Returns:
        - Dictionary containing CPU and memory energy usage.
        """
        energy_usage = {}
        energy_usage["energy_cpu"] = sum([self.__get_cpu_energy(cpu_id) for cpu_id in self.cpu_ids]) / JOULE_TO_WATT
        energy_usage["energy_memory"] = sum([self.__get_dram_energy(cpu_id, dram_id) for cpu_id, dram_id in self.dram_ids ]) / JOULE_TO_WATT
        return energy_usage

    def __get_cpu_energy(self, cpu):
        """
        Get CPU energy usage for a specific CPU.

        Parameters:
        - cpu: CPU identifier.

        Returns:
        - Energy usage for the specified CPU.
        """
        cpu_energy_file = Path(READ_RAPL_PATH.format(cpu)) / RAPL_ENERGY_FILE
        energy = int(cpu_energy_file.read_text())
        return energy

    def __get_dram_energy(self, cpu, dram):
        """
        Get DRAM energy usage for a specific CPU and DRAM.

        Parameters:
        - cpu: CPU identifier.
        - dram: DRAM identifier.

        Returns:
        - Energy usage for the specified DRAM.
        """
        dram_energy_file = (
            Path(READ_RAPL_PATH.format(cpu))
            / (RAPL_DRAM_PATH.format(cpu, dram))
            / RAPL_ENERGY_FILE
        )
        energy = int(dram_energy_file.read_text())
        return energy
