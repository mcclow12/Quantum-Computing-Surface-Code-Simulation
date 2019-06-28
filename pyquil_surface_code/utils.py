from pyquil import Program
from pyquil.gates import *

import random


def get_data_qubit_pairs(true_grid_size):
    pairs = []
    for i in range(true_grid_size):
        if i%2 == 0:
            row_pairs = [(i, j) for j in range(0, 
                        true_grid_size, 2)]            
        else:
            row_pairs = [(i, j) for j in range(1, 
                        true_grid_size, 2)]            
        pairs += row_pairs
    return pairs

def pair_to_single(i, j, true_grid_size):
    return i*(true_grid_size)+j

def triple_to_single(i,j,t, true_grid_size):
    num_qubits = true_grid_size**2
    return t*num_qubits + pair_to_single(i,j, true_grid_size)

def get_noisy_step(p, true_grid_size):
    q = Program()
    for i in range(true_grid_size):
        for j in range(true_grid_size):
            qubit = pair_to_single(i,j, true_grid_size)
            r = random.random()
            if 0 <= r <p/3:
                q += X(qubit)
            elif p/3 <= r < 2*p/3:
                q += Y(qubit)
            elif 2*p/3 <= r < p:
                q += Z(qubit)
            elif p < r <= 1:
                q += I(qubit)
            else:
                print ('step bug')
    return q

def is_z(i, j):
    return i%2 == 0

def is_x(i, j):
    return i%2 == 1

def inbounds(pair, true_grid_size):
    i, j = pair
    return 0 <= i < true_grid_size and 0 <= j < true_grid_size

#handle ground later
def step_1(z_qubit_pairs, x_qubit_pairs, true_grid_size, t):    
    r = Program()
    for i,j in z_qubit_pairs:
        qubit = pair_to_single(i, j, true_grid_size)
        r += I(qubit)

    for i,j in x_qubit_pairs:
        reg = triple_to_single(i, j, t, true_grid_size)
        qubit = pair_to_single(i, j, true_grid_size)

        r += RESET(qubit)
    return r

def step_2(z_qubit_pairs, x_qubit_pairs, true_grid_size, t):    
    r = Program()
    for i,j in z_qubit_pairs:
        qubit = pair_to_single(i, j, true_grid_size)
        r += RESET(qubit)

    for i,j in x_qubit_pairs:
        reg = triple_to_single(i, j, t, true_grid_size)
        qubit = pair_to_single(i, j, true_grid_size)

        r += H(qubit)
    return r

def step_3(z_qubit_pairs, x_qubit_pairs, true_grid_size, t):    
    r = Program()
    for i,j in z_qubit_pairs:
        qubit = pair_to_single(i, j, true_grid_size)
        a = (i, j-1)
        if inbounds(a, true_grid_size):
            r += CNOT(pair_to_single(*a, true_grid_size), qubit)

    for i,j in x_qubit_pairs:
        qubit = pair_to_single(i, j, true_grid_size)
        a = (i, j-1)
        if inbounds(a, true_grid_size):
            r += CNOT(qubit, pair_to_single(*a, true_grid_size))
    return r

def step_4(z_qubit_pairs, x_qubit_pairs, true_grid_size, t):    
    r = Program()
    for i,j in z_qubit_pairs:
        qubit = pair_to_single(i, j, true_grid_size)
        b = (i-1, j)
        if inbounds(b, true_grid_size):
            r += CNOT(pair_to_single(*b, true_grid_size), qubit)

    for i,j in x_qubit_pairs:
        qubit = pair_to_single(i, j, true_grid_size)
        b = (i-1, j)
        if inbounds(b, true_grid_size):
            r += CNOT(qubit, pair_to_single(*b, true_grid_size))
    return r

def step_5(z_qubit_pairs, x_qubit_pairs, true_grid_size, t):    
    r = Program()
    for i,j in z_qubit_pairs:
        qubit = pair_to_single(i, j, true_grid_size)
        c = (i, j+1)
        if inbounds(c, true_grid_size):
            r += CNOT(pair_to_single(*c, true_grid_size), qubit)

    for i,j in x_qubit_pairs:
        qubit = pair_to_single(i, j, true_grid_size)
        c = (i, j+1)
        if inbounds(c, true_grid_size):
            r += CNOT(qubit, pair_to_single(*c, true_grid_size))
    return r

def step_6(z_qubit_pairs, x_qubit_pairs, true_grid_size, t):    
    r = Program()
    for i,j in z_qubit_pairs:
        qubit = pair_to_single(i, j, true_grid_size)
        d = (i+1, j)
        if inbounds(d, true_grid_size):
            r += CNOT(pair_to_single(*d, true_grid_size), qubit)

    for i,j in x_qubit_pairs:
        qubit = pair_to_single(i, j, true_grid_size)
        d = (i+1, j)

        if inbounds(d, true_grid_size):
            r += CNOT(qubit, pair_to_single(*d, true_grid_size))
    return r

def step_7(z_qubit_pairs, x_qubit_pairs, true_grid_size, t):    
    r = Program()
    #r += Program('PRAGMA COMMUTING_BLOCKS')
    for i,j in x_qubit_pairs:
        reg = triple_to_single(i, j, t, true_grid_size)
        qubit = pair_to_single(i, j, true_grid_size)
        r += MEASURE(qubit, reg)

    for i,j in x_qubit_pairs:
        reg = triple_to_single(i, j, t, true_grid_size)
        qubit = pair_to_single(i, j, true_grid_size)
        r += H(qubit)
    return r

def step_8(z_qubit_pairs, x_qubit_pairs, true_grid_size, t):    
    r = Program()
    for i,j in z_qubit_pairs:
        qubit = pair_to_single(i, j, true_grid_size)
        r += I(qubit)

    for i,j in x_qubit_pairs:
        reg = triple_to_single(i, j, t, true_grid_size)
        qubit = pair_to_single(i, j, true_grid_size)
        r += MEASURE(qubit, reg)
    return r

def stabilize(z_qubit_pairs, x_qubit_pairs, true_grid_size, t):
    p = Program()
    p += step_1(z_qubit_pairs, x_qubit_pairs, true_grid_size, t)
    p += step_2(z_qubit_pairs, x_qubit_pairs, true_grid_size, t)
    p += step_3(z_qubit_pairs, x_qubit_pairs, true_grid_size, t)
    p += step_4(z_qubit_pairs, x_qubit_pairs, true_grid_size, t)
    p += step_5(z_qubit_pairs, x_qubit_pairs, true_grid_size, t)
    p += step_6(z_qubit_pairs, x_qubit_pairs, true_grid_size, t)
    p += step_7(z_qubit_pairs, x_qubit_pairs, true_grid_size, t)
    p += step_8(z_qubit_pairs, x_qubit_pairs, true_grid_size, t)
    return p 
