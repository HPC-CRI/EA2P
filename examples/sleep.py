import time
import sys

from ea2p import PowerMeter #Our package
power_meter = PowerMeter(project_name="test")

@power_meter.measure_power(
    package="time",
    algorithm="sleep"
)
def test_cpu(time_val):
    time.sleep(int(time_val))


if __name__ == '__main__':
    test_cpu(sys.argv[1])
