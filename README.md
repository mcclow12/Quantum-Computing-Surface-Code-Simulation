# Surface-Code-Simulation

The surface code is one of the leading ideas for quantum memory. This repository contains the author's final project on the surface code for CS269Q, a class on quantum computing at Stanford University. Received a near-perfect score from the instructor.

We implement a simulation of the surface code under perfect error syndrome extraction. The fault-tolerant threshold p=0.155 obtained by the simulations by Wang, Fowler et al. (https://arxiv.org/abs/0905.0531) is reproduced. 

#### Wang, Fowler et al. results:

![Alt text](.img/paper_surface_code_graph.png?raw=true "Title")

#### Our results:

![Alt text](.img/long_simulation.png?raw=true "Title")

## surface_code_ideal

The directory surface_code_ideal contains an implementation using NetworkX. The file main.py contains the code to obtain the simulation plots (for example the plot in sim.png), from which the threshold is obtained. The notebook visualize_surface_code is an instructive visualization of the surface code error correction.

#### Simulation Visualization

![Alt text](.img/jupyter_sim.png?raw=true "Title")


## pyquil_surface_code
The directory pyquil_surface_code contains an example implementation of the surface code error extraction in the quantum programming framework PyQuil. No threshold is obtained from this implementation, so it is less clear that the PyQuil code works -- it is provided moreso for illustrating the capabilities of the PyQuil programming language capabilities than for computation.

## Writeup
For full details, see writeup.pdf, which contains an in-depth explanation of the surface code as well as further discussion of the simulation.



