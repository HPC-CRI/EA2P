#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ["PowerMeter"]

import datetime
import logging
import traceback

import pandas as pd  # type: ignore

from .wrapper import *

LOGGER = logging.getLogger(__name__)


class PowerMeter:

    """
    PowerMeter
    ---------
    
    The Main Python class for monitoring power consumption during the execution of an algorithm.

    Attributes:
        DATETIME_FORMAT (str): The format for datetime objects.
        DEFAULT_CONFIG_FILE (str): The default configuration file name to use for wrapper.
        DEFAULT_OUTPUT_FILEPATH (str): The default output file path to save results.
        LOGGING_FILE (str): The filename for the experimentation logging file.
        project_name (str): Name of the experimentation project.
        config_file (str): Path to the configuration file for the wrapper initialisation.
        output_filepath (str): Path to the output file for results of profiling.
        output_format (str): Format for the output file (e.g. csv).
        print_to_cli (bool): Flag to print the result of measurement in Terminal at the end (default True).
        power (PowerWrapper): Instance of PowerWrapper class for power measurement.
        used_package (str): Name of the package of algorithm to profile during power measurement.
        used_algorithm (str): Name of the profiled algorithm for power measurement.
        used_algorithm_description (str): Description of the algorithm used during power measurement.
        logging_filename (str): Path to the logging file of experiment.

    Methods:
        __init__: Initialize the PowerMeter instance.
        measure_power: Decorator to measure power consumption during the execution of a function.
        __set_used_arguments: Set the arguments used during power measurement.
        __call__: Set the arguments used during power measurement using a decorator syntax.
        __enter__: Enter method for context manager. Starts power measurement.
        __exit__: Exit method for context manager. Stops power measurement.
        start_measure: Start measuring power consumption.
        stop_measure: Stop measuring power consumption.
        __record_data_to_file: Record power data to a file.
        __log_records: Log recorded power data.
    """

    DATETIME_FORMAT = "%m/%d/%Y %H:%M:%S"  # "%c"
    DEFAULT_CONFIG_FILE = "config_energy.json"
    DEFAULT__OUTPUT_FILEPATH = "energy_report.csv"
    LOGGING_FILE = "logging_file.txt"

    # Constructors
    def __init__(self, project_name="test_project", output_filepath=None, config_file=None, output_format="csv", print_to_cli=True):
        """
        Initialize the PowerMeter instance.

        Parameters:
            config_file (str): Path to the configuration file.
            project_name (str): Name of the project.
            output_filepath (str): Path to the output file.
            output_format (str): Format for the output file.
            print_to_cli (bool): To print the result of measurement in Terminal at the end
        """

        self.project_name = project_name
        self.config_file = Path(config_file) if config_file else Path.cwd() / self.DEFAULT_CONFIG_FILE
        self.output_filepath = Path(output_filepath) if output_filepath else Path.cwd() / self.DEFAULT__OUTPUT_FILEPATH
        self.output_format = output_format
        self.print_to_cli = print_to_cli

        self.power = PowerWrapper(self.config_file)

        self.used_package = ""
        self.used_algorithm = ""
        self.used_algorithm_description = ""

        self.logging_filename = PACKAGE_PATH / self.LOGGING_FILE


    def measure_power(self, package, algorithm, algorithm_description=""):
        """
        Decorator to measure power consumption during the execution of a function.

        Parameters:
            package (str): Package name of the algorithm to profile.
            algorithm (str): Name of the algorithm to profile in the list of instruction of the decorated function.
            algorithm_description (str): Description of the profiled algorithm acording to the experimental setup or tesbet details (eg, dataset used, epochs for training, batch size, etc...).
        Returns:
            Decorator function.
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
                    algorithm_description=algorithm_description,
                )
                try:
                    results = func(*args, **kwargs)
                finally:
                    self.stop_measure()
                return results

            return wrapper

        return decorator

    def __set_used_arguments(self, package, algorithm, algorithm_description=""):
        """
        Set the arguments used during power measurement.

        Parameters:
            package (str): Package name of the algorithm to profile.
            algorithm (str): Name of the algorithm to profile in the list of instruction of the decorated function.
            algorithm_description (str): Description of the profiled algorithm acording to the experimental setup or tesbet details (eg, dataset used, epochs for training, batch size, etc...).

        """
        self.used_package = package
        self.used_algorithm = algorithm
        self.used_algorithm_description = algorithm_description

    def __call__(self, package, algorithm, algorithm_description=""):
        """
        Set the arguments used during power measurement using a decorator syntax.

        Parameters:
            package (str): Package name of the algorithm to profile.
            algorithm (str): Name of the algorithm to profile in the list of instruction of the decorated function.
            algorithm_description (str): Description of the profiled algorithm acording to the experimental setup or tesbet details (eg, dataset used, epochs for training, batch size, etc...).

        """
        self.__set_used_arguments(package, algorithm, algorithm_description=algorithm_description)
        return self

    def __enter__(self):
        """
        Enter method for context manager. Starts power measurement.
        """
        self.start_measure(
            self.used_package,
            self.used_algorithm,
            algorithm_description=self.used_algorithm_description,
        )

    def __exit__(self, exit_type, value, traceback):
        """
        Exit method for context manager. Stops power measurement.
        """
        self.stop_measure()

    def start_measure(self, package, algorithm, algorithm_description=""):
        """
        Start measuring power consumption.

        Parameters:
            package (str): Package name of the algorithm to profile.
            algorithm (str): Name of the algorithm to profile in the list of instruction of the decorated function.
            algorithm_description (str): Description of the profiled algorithm acording to the experimental setup or tesbet details (eg, dataset used, epochs for training, batch size, etc...).

        """
        self.power.start()
        self.__set_used_arguments(
            package,
            algorithm,
            algorithm_description=algorithm_description,
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
            algorithm_description=self.used_algorithm_description,
        )

    def __record_data_to_file(self, data):
        """
        Record power data to a file.

        Parameters:
            data (DataFrame): Power data to be recorded.
        Returns:
            True if recording is successful, False otherwise.
        """
        try:
            if self.output_filepath.exists():
                data.to_csv(self.output_filepath, mode="a", index=False, header=False)
            else:
                data.to_csv(self.output_filepath, index=False)
            return True
        except Exception as e:
            LOGGER.error("Error during the CSV writing process: %s", str(e))
            LOGGER.error(traceback.format_exc())
            return False

    def __log_records(self, recorded_power, algorithm="", package="", algorithm_description=""):
        """
        Log recorded power data.

        Parameters:
            recorded_power (DataFrame): Recorded power data.
            package (str): Package name of the algorithm to profile.
            algorithm (str): Name of the algorithm to profile in the list of instruction of the decorated function.
            algorithm_description (str): Description of the profiled algorithm acording to the experimental setup or tesbet details (eg, dataset used, epochs for training, batch size, etc...).

        """
        payload_prefix = {
            "Project Name": self.project_name,
            "Datetime": datetime.datetime.now().strftime(self.DATETIME_FORMAT)
        }
        payload_sufix = {
            "Package": package,
            "Algorithm": algorithm,
            "Algorithm's parameters": algorithm_description,
        }
        written = self.__record_data_to_file(
            pd.concat(
                [pd.DataFrame(payload_prefix, index=[0]), recorded_power, pd.DataFrame(payload_sufix, index=[0])],
                axis=1,
            )
        )
        LOGGER.info("Recorded into a file? %s", written)
