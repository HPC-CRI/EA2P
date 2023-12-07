import os
from pathlib import Path
import datetime
import json
import logging
import shutil
import sys
import traceback
import warnings
import cpuinfo

import pandas as pd  # type: ignore
import requests

JOULE_TO_WATT = 3600000000          # micro joules to watt
SAMPLING_FREQUENCY = 1/1000

PACKAGE_PATH = Path(os.path.dirname(os.path.abspath(__file__)))
HOME_DIR = Path.home()

# sudo chmod 400 /sys/class/powercap/intel-rapl*/*/energy_uj
POWERLOG_PATH_LINUX = Path("/sys/class/powercap/intel-rapl")
#TURBO_STAT_PATH = "/usr/sbin/turbostat"

LOGGING_FILE = "power_logs.csv"

TOTAL_CPU_TIME = "Total Elapsed CPU Time (sec)"
TOTAL_GPU_TIME = "Total Elapsed GPU Time (sec)"


CPU_IDS_DIR = "/sys/devices/system/cpu/cpu*/topology/physical_package_id"
READ_RAPL_PATH = (
    "/sys/class/powercap/intel-rapl/intel-rapl:{}/"  # rapl_socket_id
)
RAPL_DEVICENAME_FILE = "name"
RAPL_ENERGY_FILE = "energy_uj"
RAPL_DRAM_PATH = "intel-rapl:{}:{}/"  # rapl_socket_id, rapl_device_id
RAPL_PATH_SUB_DOMS = "intel-rapl:{}:{}/"  # rapl_socket_id, rapl_device_id







