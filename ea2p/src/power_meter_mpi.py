#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ["PowerMeterMPI"]

from mpi4py import MPI
import datetime
import pandas as pd
import logging
import sys
import traceback
from .wrapper import * 

LOGGER = logging.getLogger(__name__)

class PowerMeterMPI:
    """
    PowerMeter
    ---------
    Multi-node capable class for monitoring power consumption.
    """

    DATETIME_FORMAT = "%m/%d/%Y %H:%M:%S"
    DEFAULT_CONFIG_FILE = "config_energy.json"
    DEFAULT__OUTPUT_FILEPATH = "energy_report.csv"
    LOGGING_FILE = "logging_file.txt"

    def __init__(self, project_name="test_project", output_filepath=None, config_file=None, output_format="csv", print_to_cli=True):
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

        # Initialize MPI
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()

    def measure_power(self, package, algorithm, algorithm_description=""):
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
        self.used_package = package
        self.used_algorithm = algorithm
        self.used_algorithm_description = algorithm_description

    def __call__(self, package, algorithm, algorithm_description=""):
        self.__set_used_arguments(package, algorithm, algorithm_description=algorithm_description)
        return self

    def __enter__(self):
        self.start_measure(
            self.used_package,
            self.used_algorithm,
            algorithm_description=self.used_algorithm_description,
        )

    def __exit__(self, exit_type, value, traceback):
        self.stop_measure()

    def start_measure(self, package, algorithm, algorithm_description=""):
        self.power.start()
        self.__set_used_arguments(
            package,
            algorithm,
            algorithm_description=algorithm_description,
        )
    
    
    def stop_measure(self):
        """
        Stop measuring power consumption and gather results from all processes.
        """
        self.power.stop()
        local_record = self.power.record

        # Add rank number to local record
        if local_record is not None:
            local_record['Rank'] = self.rank

        # Gathering data from all processes
        global_record = self.comm.gather(local_record, root=0)

        if self.rank == 0:
            # Filter out None values in case some processes had no data
            global_record = [record for record in global_record if record is not None]

            if global_record:
                # Concatenate data from all processes, preserving the original ranks
                global_record = pd.concat(global_record, ignore_index=True)

                # Compute total energy and add the 'Rank' column for the total row
                total_energy = global_record.sum(numeric_only=True)
                total_energy['Rank'] = 'Total'
                total_energy_row = pd.DataFrame([total_energy], columns=global_record.columns)
                total_energy_row = total_energy_row.round(5)

                # Append the total row to the global record
                global_record = pd.concat([global_record, total_energy_row], ignore_index=True)

                # Print the result if required
                if self.print_to_cli:
                    print("Energy report for the experiment:\n")
                    print(global_record)

                # Log the results
                self.__log_records(
                    global_record,
                    algorithm=self.used_algorithm,
                    package=self.used_package,
                    algorithm_description=self.used_algorithm_description,
                )
            else:
                print("No data was collected from the processes.")




    def __record_data_to_file(self, data):
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
        payload_prefix = {
            "Project Name": self.project_name,
            "Datetime": datetime.datetime.now().strftime(self.DATETIME_FORMAT)
        }
        payload_suffix = {
            "Package": package,
            "Algorithm": algorithm,
            "Algorithm's parameters": algorithm_description,
        }
        written = self.__record_data_to_file(
            pd.concat(
                [pd.DataFrame(payload_prefix, index=[0]), recorded_power, pd.DataFrame(payload_suffix, index=[0])],
                axis=1,
            )
        )
        LOGGER.info("Recorded into a file? %s", written)
