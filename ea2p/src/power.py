#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ["PowerLinux","PowerProfiler"]

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


class PowerProfiler(abc.ABC):
    """
    This abstract class PowerProfiler defines two abstract methods "start" and "stop" which need to be implemented by any subclass inheriting from it. 
    These methods will handle the actual start and stop operations for profiling power consumption, respectively depending on device drivers or registries access. 
    """

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


class PowerLinux(PowerProfiler):
    """
    A class "PowerLinux" which inherits from "PowerProfiler" for energy/power profiling under Linux systems.
    We have two statics methods to get the RAPL domains and subsdomains on the Linux system for Intel CPUs.
    """

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
