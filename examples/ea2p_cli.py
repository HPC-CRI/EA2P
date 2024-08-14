import time
import sys
import subprocess

from ea2p import PowerMeter #Our package
power_meter = PowerMeter(project_name="omp_parallel")

@power_meter.measure_power(
    package="subprocess",
    algorithm="run"
)
def call_c_program(program):
    subprocess.run(program, shell=True)


if __name__ == '__main__':
    call_c_program(sys.argv[1])
