#!/usr/bin/python
# -*- coding: utf-8 -*-
"""

"""
# __all__ = [
#     "PowerLinux",
#     "NoPower",
# ]

import abc
import datetime
import glob
import logging
import re
import struct
import subprocess
import threading
import time

import pandas as pd  # type: ignore
import psutil  # type: ignore

from .utils import*

LOGGER = logging.getLogger(__name__)


class Power(abc.ABC):
    def __init__(self):
        self.record = {}
        self.thread = None

    def __get_powerlog_file(self):
        """
        Retrieve the log file where PowerLog logs are written.
        """

    def start(self):
        """
        Starts the recording process.
        """

    def stop_thread(self):
        """
        Stops the recording thread.
        """
        self.thread.do_run = False
        self.thread.join()

    def stop(self):
        """
        Stops the recording process.
        """


class NoPower(Power):
    def __init__(self):
        super().__init__()
        self.start_time = 0

    def start(self):
        """
        Start the recording process.
        This method records the start time for later calculation.
        """
        self.start_time = time.time()

    def stop(self):
        """
        Stops the recording process.
        This method calculates the total energy consumption based on the recorded start time.
        """
        end_time = time.time()
        self.record[TOTAL_ENERGY_CPU] = 0
        self.record[TOTAL_ENERGY_MEMORY] = 0
        self.record[TOTAL_CPU_TIME] = end_time - self.start_time
        self.record[TOTAL_ENERGY_ALL] = 0


class PowerLinux(Power):
    @staticmethod
    def __get_cpu_ids():
        """
        Get CPU identifiers from files in CPU_IDS_DIR.
        
        Returns:
        - List of CPU identifiers.
        """
        cpu_ids = []
        for filename in glob.glob(CPU_IDS_DIR):
            with open(filename, "r") as f:
                package_id = int(f.read())
            if package_id not in cpu_ids:
                cpu_ids.append(package_id)
        return cpu_ids

    @staticmethod
    def __get_cpu_domains():
        """
        Get CPU domains from entries in POWERLOG_PATH_LINUX.
        
        Returns:
        - List of tuples containing CPU domain information.
        """
        cpu_doms = []
        for entry in os.scandir(POWERLOG_PATH_LINUX):
            if (entry.is_dir() and ("intel-rapl:" in entry.name)):
                dom = (entry.name.split(":"))[1]
                file = Path(READ_RAPL_PATH.format(int(dom))) / RAPL_DEVICENAME_FILE
                cpu_doms.append((int(dom), file.read_text().replace('\n','')))
        return cpu_doms

    def __init__(self):
        super().__init__()
        self.cpu_ids = self.__get_cpu_ids()
        self.cpu_doms = self.__get_cpu_domains()
