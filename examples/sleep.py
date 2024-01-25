import time
import sys
sys.path.append("/home/nana/Documents/EA2P")

from ea2p import PowerMeter #Our package
power_meter = PowerMeter(project_name="test")

@power_meter.measure_power(
    package="time",
    algorithm="sleep",
    data_type="",
    data_shape="",
    algorithm_params=""
)
def test_cpu(time_val):
    time.sleep(int(time_val))


if __name__ == '__main__':
    test_cpu(sys.argv[1])
