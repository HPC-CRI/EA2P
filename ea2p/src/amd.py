#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Python classes monitoring AMD CPU's and GPU's power usage
during a timeframe delimited between a start and a stop methods
"""
__all__ = ["PowerAmdCpu", "PowerAmdGpu"]

import subprocess
import logging
import signal
import re
import pandas as pd
import os 
import numpy as np

from .utils import SAMPLING_FREQUENCY

LOGGER = logging.getLogger(__name__)

AMDPOWERLOG_FILENAME = "amdPowerLog.txt"


class PowerAmdCpu():
    
    def __init__(self):
        self.logging_process = None

    def start(self):
        """
        Start the measure process using Linux Perf Tools through perf stat system wide sampling
        """
        if self.logging_process is not None:
            self.stop()

        self.logging_process = subprocess.Popen(
            [
                "perf",
                "stat",
                "-e",
                "power/energy-pkg/",
                "-a",
                "--per-node",
                "-o",
                str(AMDPOWERLOG_FILENAME),
            ]
        )

    def stop(self):
        """
        Stop the measure process if started. A signal is send to the logging process to stop measurements
        """
        self.logging_process.send_signal(signal.SIGINT)
        self.logging_process = None

    def parse_log(self):
        """
        Parse the AMD CPU power log file to energy values per package and per nodes.

        Returns:
        	DataFrame containing energy data.
        """
        with open(r"%s" % AMDPOWERLOG_FILENAME, 'r') as fp:
            data = fp.read()
        data = data.replace(",", ".")
        p = re.compile(r'([\d]+.+[\d.]+)\s+Joules power/energy-pkg/')
        data = p.findall(data)
        data = [d.replace(" ", "") for d in data]
        for i in range(len(data)):
            # Count the total number of periods
            total_periods = data[i].count('.')
            # If there are more than one periods, replace all but the last one
            if total_periods > 1:
                # Remove all periods except the last one
                data[i] = data[i].replace('.', '', total_periods - 1)
        cols = ["package " + str(i) for i in range(len(data))]
        energy = pd.DataFrame(np.array([data]), columns=cols)
        energy = energy.astype("float32")
        energy = energy / 3600
        return energy


class PowerAmdGpu():
    def __init__(self):
        pass

    def append_energy_usage(self):
        """
        Append AMD GPU energy usage to dict containing sampling power measurements.

        Returns:
        	Dictionary containing GPU power usage per GPU devices.
        """
        cmd = "rocm-smi --showpower | grep 'GPU' > tmp_gpu_energy.txt"
        os.system(cmd)
        with open(r"tmp_gpu_energy.txt", 'r') as fp:
            data = fp.readlines()

        energy = {}
        for line in data:
            linesplit = line.split(":")
            energy.update({linesplit[0].replace(' ', ''): float(linesplit[2])})

        return energy


class PowerAmdCpu2():
    def __init__(self):
        self.logging_process = None
        self.interval = SAMPLING_FREQUENCY

    def start(self):
        """
        Start the AMD CPU power measurement process using Linux turbostat tools
        """
        if self.logging_process is not None:
            self.stop()

        self.logging_process = subprocess.Popen(
            [
                "sudo-g5k",
                "turbostat",
                "--show",
                "PkgWatt",
                "--quiet",
                "--interval",
                str(self.interval),
                "-o",
                str(AMDPOWERLOG_FILENAME),
            ]
        )

    def stop(self):
        """
        Stop the measure process if started
        """
        self.logging_process.send_signal(signal.SIGINT)
        self.logging_process = None

    def parse_log(self):
        """
        Parse the AMD CPU power log file.

        Returns:
        	DataFrame containing energy data.
        """
        with open(r"%s" % AMDPOWERLOG_FILENAME, 'r') as fp:
            data = fp.read()
        data = data.replace("\nPkgWatt", "PkgWatt")
        data = data.replace("\n", " ")
        data = data[:-1]
        energy_pakages = data.split("PkgWatt ")[1:]
        e_all = []
        for pakage in energy_pakages:
            e_all.append(pakage.split(" ")[:3])
        energy = pd.DataFrame(e_all, columns=['Total Pakages (Wh)'] + ['Pakage ' + str(i) + "(Wh)" for i in range(1, len(e_all[1]))])
        energy = energy.astype(float).sum().to_frame().T
        energy = energy * self.interval / 3600
        return energy
