#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
PowerMeter
---------
Main Python class or entrypoint to monitor the power consumption of
an algorithm.
"""

__all__ = ["PowerMeter"]

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

from .wrapper import*

POWER_DEVICES = "cpu,ram,gpu"

LOGGER = logging.getLogger(__name__)


class PowerMeter:

    DATETIME_FORMAT = "%m/%d/%Y %H:%M:%S"  # "%c"

    # ----------------------------------------------------------------------
    # Constructors
    def __init__(self, project_name="test_project", user_name="toto", cpu_power_log_path="", powerlog_save_path="", filepath=None, output_format="csv" ):
        self.pue = 1.3

        self.power = PowerWrapper(POWER_DEVICES)

        self.user = user_name

        self.used_package = ""
        self.used_algorithm = ""
        self.used_data_type = ""
        self.used_data_shape = ""
        self.used_algorithm_params = ""

        if not filepath:
            LOGGER.info("No current filepath, will use the default")
            self.filepath = Path.cwd() / "CPU_validation_emissions.csv"
        else:
            LOGGER.info("Filepath given, will save there")
            self.filepath = Path(filepath)

        self.output_format = output_format

        self.logging_filename = PACKAGE_PATH / LOGGING_FILE

    @classmethod
    def from_config(cls, path):
        with open(path) as file:
            args = json.load(file)
        return cls(**args)

    def measure_power(self, package, algorithm, data_type="", data_shape="", algorithm_params=""):
        if not algorithm or not package:
            raise SyntaxError(
                "Please input a description for the function you are trying "
                "to monitor. Pass in the algorithm and the package you are "
                "trying to monitor"
            )

        def decorator(func):
            def wrapper(*args, **kwargs):
                self.start_measure(package, algorithm, data_type=data_type, data_shape=data_shape, algorithm_params=algorithm_params)
                try:
                    results = func(*args, **kwargs)
                finally:
                    self.stop_measure()
                return results

            return wrapper

        return decorator

    def __set_used_arguments(self, package, algorithm, data_type="", data_shape="", algorithm_params=""):
        self.used_package = package
        self.used_algorithm = algorithm
        self.used_data_type = data_type
        self.used_data_shape = data_shape
        self.used_algorithm_params = algorithm_params

    def __call__(self, package, algorithm, data_type="", data_shape="", algorithm_params=""):
        
        self.__set_used_arguments(package, algorithm, data_type=data_type, data_shape=data_shape, algorithm_params=algorithm_params)
        return self

    def __enter__(self, ):
        self.start_measure(self.used_package, self.used_algorithm, data_type=self.used_data_type, data_shape=self.used_data_shape, algorithm_params=self.used_algorithm_params)

    def __exit__(self, exit_type, value, traceback):
        self.stop_measure()

    def start_measure(self, package, algorithm, data_type="", data_shape="", algorithm_params=""):
        self.power.start()
        self.__set_used_arguments(package, algorithm, data_type=data_type, data_shape=data_shape, algorithm_params=algorithm_params)

    def stop_measure(self):
        self.power.stop()
        self.__log_records(
            self.power.record, 
            algorithm=self.used_algorithm,
            package=self.used_package,
            data_type=self.used_data_type,
            data_shape=self.used_data_shape,
            algorithm_params=self.used_algorithm_params,
        )

    def __record_data_to_file(self, data):
        try:
            #data = pd.DataFrame(info, index=[0])
            if Path(self.filepath).exists():
                data.to_csv(self.filepath, mode="a", index=False, header=False)
            else:
                data.to_csv(self.filepath, index=False)
            return True
        except Exception:
            LOGGER.error("* error during the csv writing process *")
            LOGGER.error(traceback.format_exc())
            return False

    def __log_records(self, recorded_power, algorithm="", package="", data_type="", data_shape="", algorithm_params=""):
        payload_prefix = {
            "Datetime": datetime.datetime.now().strftime(self.DATETIME_FORMAT),
            "User ID": self.user,
        }
        payload_sufix = {
            #"PUE": self.pue,
            "Package": package,
            "Algorithm": algorithm,
            "Algorithm's parameters": algorithm_params,
            "Data type": data_type,
            "Data shape": data_shape,
        }
        #data_final = {}
        #data_final.update(payload_prefix).update(recorded_power).update(payload_sufix)
        written = self.__record_data_to_file(pd.concat([pd.DataFrame(payload_prefix, index=[0]), recorded_power, pd.DataFrame(payload_sufix, index=[0])], axis = 1))
        LOGGER.info("* recorded into a file? %s*", written)

