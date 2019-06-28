import random

import numpy as np
from utils import *
from pyquil.gates import *
from pyquil import Program

#from pyquil.api import WavefunctionSimulator
from pyquil.api import QVMConnection
from pyquil import get_qc


seed = 1
random.seed(1)


d = 3
T = 1
p = 0.1
true_grid_size = 2*d-1
num_qubits = true_grid_size**2 
data_qubit_pairs = get_data_qubit_pairs(true_grid_size)
measure_qubit_pairs = list(set([(i, j) for i in range(true_grid_size) for 
                            j in range(true_grid_size)])
                            - set(data_qubit_pairs))
z_qubit_pairs = [(i,j) for i,j in measure_qubit_pairs if is_z(i,j)]
x_qubit_pairs = [(i,j) for i,j in measure_qubit_pairs if is_x(i,j)]

qc = get_qc('{}q-qvm'.format(num_qubits))

pq = Program()
mem_size = T*num_qubits + 1
ro = pq.declare('ro', 'BIT', mem_size)



#loop
for t in range(T):
    pq += get_noisy_step(p, true_grid_size)
    pq = pq + stabilize(z_qubit_pairs, x_qubit_pairs, true_grid_size, t)
    
    


qc.run(pq)
