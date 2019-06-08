import random

import numpy as np
from utils import *
from pyquil.gates import *
from pyquil import Program

#from pyquil.api import WavefunctionSimulator
from pyquil.api import QVMConnection
from pyquil import get_qc

#wf_sim = WavefunctionSimulator()

seed = 1
random.seed(1)


d = 3
T = 50 
p = 0.01
true_grid_size = 2*d-1
num_qubits = true_grid_size**2 
data_qubit_pairs = get_data_qubit_pairs(true_grid_size)
measure_qubit_pairs = list(set([(i, j) for i in range(true_grid_size) for 
                            j in range(true_grid_size)])
                            - set(data_qubit_pairs))
z_qubit_pairs = [(i,j) for i,j in measure_qubit_pairs if is_z(i,j)]
x_qubit_pairs = [(i,j) for i,j in measure_qubit_pairs if is_x(i,j)]

print(data_qubit_pairs, z_qubit_pairs, x_qubit_pairs)

#qc = QVMConnection()
qc = get_qc('{}q-qvm'.format(num_qubits))

pq = Program()
mem_size = T*num_qubits + 1
print(mem_size)
ro = pq.declare('ro', 'BIT', mem_size)


#init

#loop
for t in range(T):
    #pq += get_noisy_step(p, true_grid_size)
    #pq += WAIT
    pq = pq + stabilize(z_qubit_pairs, x_qubit_pairs, true_grid_size, t)
    
    
    #pq += measure

print(pq)
#run
#wf_sim.run_and_measure(pq, trials=1)

#qvm.compile(pq)
#qvm.run(pq, trials=1)

qc.run(pq)
compiled = qc.compile(pq)
#print('lol')
#qc.run(compiled)
qc.qam.load(compiled)
qc.qam.run()
#qc.qam.run(compiled)
#qc.qam.wait()
#qc.qam.run(pq, trials=1)
qc.qam.wait()
print(qc.qam.read_memory(region_name='ro'))
#qc.run(compiled)
#qc.qam.run(pq, trials=1)
#qc.qam.wait()
qc.qam.run()
qc.qam.wait()
print(qc.qam.read_memory(region_name='ro'))
#compute bit flip errors
#compute true errors



print('done')


