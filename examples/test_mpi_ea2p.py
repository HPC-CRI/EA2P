# mpi_matrix_multiplication.py
from mpi4py import MPI
import numpy as np

import time
import sys


from ea2p import PowerMeterMPI # The MPI version for multi rank
power_meter = PowerMeterMPI(project_name="test", print_to_cli=False)

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def matrix_multiply(A, B):
    """Performs matrix multiplication on two 2D numpy arrays."""
    return np.dot(A, B)

@power_meter.measure_power(
    package="np",
    algorithm="dot",
    algorithm_description="simple multi-nodes matrix multiplication with mpi4py and numpy"
)
def main():
    # Define the dimensions of the matrices
    N = 4096 

    # Only the root process initializes the matrices
    if rank == 0:
        #A = np.random.rand(N, N)
        #B = np.random.rand(N, N)
        A = np.ones((N, N))
        B = np.ones((N, N))
        C = np.zeros((N, N))
    else:
        A = None
        B = None
        C = None

    # Broadcast matrix B to all processes
    B = comm.bcast(B, root=0)

    # Scatter rows of matrix A to all processes
    local_A = np.zeros((N // size, N))
    comm.Scatter(A, local_A, root=0)

    # Each process computes its portion of the result matrix C
    local_C = np.dot(local_A, B)

    # Gather the local results into the final matrix C
    comm.Gather(local_C, C, root=0)

    # The root process now has the full result matrix
    # if rank == 0:
    #     # print("Matrix A:")
    #     # print(A)
    #     # print("Matrix B:")
    #     # print(B)
    #     print("Matrix C = A * B:")
    #     print(C)

if __name__ == "__main__":
    main()
