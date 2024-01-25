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
import sys
import traceback

import pandas as pd  # type: ignore

from .wrapper import *

LOGGER = logging.getLogger(__name__)


class PowerMeter:

    DATETIME_FORMAT = "%m/%d/%Y %H:%M:%S"  # "%c"
    DEFAULT_CONFIG_FILE = "config_energy.json"
    DEFAULT_FILEPATH = "energy_report.csv"
    LOGGING_FILE = "logging_file.txt"

    # Constructors
    def __init__(
        self,
        project_name="test_project",
        filepath=None,
        config_file=None,
        output_format="csv",
        print_to_cli=True
    ):
        """
        Initialize the PowerMeter instance.

        Parameters:
        - config_file: Path to the configuration file.
        - project_name: Name of the project.
        - filepath: Path to the output file.
        - output_format: Format for the output file.
        - print_to_cli: To print the result of measurement in Terminal at the end
        """

        self.project_name = project_name
        self.config_file = Path(config_file) if config_file else Path.cwd() / self.DEFAULT_CONFIG_FILE
        self.filepath = Path(filepath) if filepath else Path.cwd() / self.DEFAULT_FILEPATH
        self.output_format = output_format
        self.print_to_cli = print_to_cli

        self.power = PowerWrapper(self.config_file)

        self.used_package = ""
        self.used_algorithm = ""
        self.used_data_type = ""
        self.used_data_shape = ""
        self.used_algorithm_params = ""

        self.logging_filename = PACKAGE_PATH / self.LOGGING_FILE


    def measure_power(self, package, algorithm, data_type="", data_shape="", algorithm_params=""):
        """
        Decorator to measure power consumption during the execution of a function.

        Parameters:
        - package: Package name.
        - algorithm: Algorithm name.
        - data_type: Type of data.
        - data_shape: Shape of data.
        - algorithm_params: Parameters of the algorithm.

        Returns:
        - Decorator function.
        """
        if not algorithm or not package:
            raise SyntaxError(
                "Please input a description for the function you are trying "
                "to monitor. Pass in the algorithm and the package you are "
                "trying to monitor"
            )

        def decorator(func):
            def wrapper(*args, **kwargs):
                self.start_measure(
                    package,
                    algorithm,
                    data_type=data_type,
                    data_shape=data_shape,
                    algorithm_params=algorithm_params,
                )
                try:
                    results = func(*args, **kwargs)
                finally:
                    self.stop_measure()
                return results

            return wrapper

        return decorator

    def __set_used_arguments(self, package, algorithm, data_type="", data_shape="", algorithm_params=""):
        """
        Set the arguments used during power measurement.

        Parameters:
        - package: Package name.
        - algorithm: Algorithm name.
        - data_type: Type of data.
        - data_shape: Shape of data.
        - algorithm_params: Parameters of the algorithm.
        """
        self.used_package = package
        self.used_algorithm = algorithm
        self.used_data_type = data_type
        self.used_data_shape = data_shape
        self.used_algorithm_params = algorithm_params

    def __call__(self, package, algorithm, data_type="", data_shape="", algorithm_params=""):
        """
        Set the arguments used during power measurement using a decorator syntax.

        Parameters:
        - package: Package name.
        - algorithm: Algorithm name.
        - data_type: Type of data.
        - data_shape: Shape of data.
        - algorithm_params: Parameters of the algorithm.
        """
        self.__set_used_arguments(package, algorithm, data_type=data_type, data_shape=data_shape, algorithm_params=algorithm_params)
        return self

    def __enter__(self):
        """
        Enter method for context manager. Starts power measurement.
        """
        self.start_measure(
            self.used_package,
            self.used_algorithm,
            data_type=self.used_data_type,
            data_shape=self.used_data_shape,
            algorithm_params=self.used_algorithm_params,
        )

    def __exit__(self, exit_type, value, traceback):
        """
        Exit method for context manager. Stops power measurement.
        """
        self.stop_measure()

    def start_measure(self, package, algorithm, data_type="", data_shape="", algorithm_params=""):
        """
        Start measuring power consumption.

        Parameters:
        - package: Package name.
        - algorithm: Algorithm name.
        - data_type: Type of data.
        - data_shape: Shape of data.
        - algorithm_params: Parameters of the algorithm.
        """
        self.power.start()
        self.__set_used_arguments(
            package,
            algorithm,
            data_type=data_type,
            data_shape=data_shape,
            algorithm_params=algorithm_params,
        )

    def stop_measure(self):
        """
        Stop measuring power consumption.
        """
        self.power.stop()

        if self.print_to_cli :
            print("Energy report for the experiment : \n\n")
            print(self.power.record)

        self.__log_records(
            self.power.record,
            algorithm=self.used_algorithm,
            package=self.used_package,
            data_type=self.used_data_type,
            data_shape=self.used_data_shape,
            algorithm_params=self.used_algorithm_params,
        )

    def __record_data_to_file(self, data):
        """
        Record power data to a file.

        Parameters:
        - data: Power data to be recorded.

        Returns:
        - True if recording is successful, False otherwise.
        """
        try:
            if self.filepath.exists():
                data.to_csv(self.filepath, mode="a", index=False, header=False)
            else:
                data.to_csv(self.filepath, index=False)
            return True
        except Exception as e:
            LOGGER.error("Error during the CSV writing process: %s", str(e))
            LOGGER.error(traceback.format_exc())
            return False

    def __log_records(self, recorded_power, algorithm="", package="", data_type="", data_shape="", algorithm_params=""):
        """
        Log recorded power data.

        Parameters:
        - recorded_power: Recorded power data.
        - algorithm: Algorithm name.
        - package: Package name.
        - data_type: Type of data.
        - data_shape: Shape of data.
        - algorithm_params: Parameters of the algorithm.
        """
        payload_prefix = {
            "Project Name": self.project_name,
            "Datetime": datetime.datetime.now().strftime(self.DATETIME_FORMAT)
        }
        payload_sufix = {
            "Package": package,
            "Algorithm": algorithm,
            "Algorithm's parameters": algorithm_params,
            "Data type": data_type,
            "Data shape": data_shape,
        }
        written = self.__record_data_to_file(
            pd.concat(
                [pd.DataFrame(payload_prefix, index=[0]), recorded_power, pd.DataFrame(payload_sufix, index=[0])],
                axis=1,
            )
        )
        LOGGER.info("Recorded into a file? %s", written)
