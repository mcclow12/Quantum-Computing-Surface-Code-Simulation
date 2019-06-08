from itertools import product, combinations
import random

import networkx as nx
from networkx.algorithms import max_weight_matching
import numpy as np
import matplotlib.pyplot as plt

#random.seed(4)

class surface_code_sim():
    def __init__(self, distance, p, error_mode, display_mode):

        
        if error_mode == 'depolarizing':
            self.flip_prob = 2*p/3
        else:
            raise Exception('error_mode {} not supported'.format(mode))
        self.display_mode = display_mode
        
        self.grid_size = 2*distance-1
        self.logical_error = False

        self.G = nx.Graph()
        #measurement nodes
        self.z_nodes = [(i, j) for i, j in product(range(self.grid_size),
                        range(self.grid_size)) if i%2 == 1 and j%2 == 0]

        #implicit boundary nodes
        self.bd_nodes = [(i, j) for i, j in product([-1, self.grid_size], 
                        range(self.grid_size)) if j%2 == 0]

        self.G.add_nodes_from(self.z_nodes)
        self.G.add_nodes_from(self.bd_nodes)

        self.data_edges = [((i, j), (i, j+2)) for i,j in self.G.nodes
                            if 0<=i<self.grid_size and j+2<self.grid_size] 
        self.data_edges += [((i,j), (i+2,j)) for i,j in self.G.nodes
                                if i+2 <= self.grid_size]
        #print(self.data_edges)
        #print(self.G.nodes)
    
    
    def _generate_bit_flips(self):
        for edge in self.data_edges:
            r = random.random()
            if r < self.flip_prob:
                if not self.G.has_edge(*edge):
                    self.G.add_edge(*edge)
                else:
                    self.G.remove_edge(*edge)
        #print (self.G.edges)

    def _get_error_syndrome(self):
        return [n for n in self.z_nodes if self.G.degree[n]%2==1]

    def _build_syndrome_graph(self, error_syndrome):
        #print(error_syndrome)
        H = nx.Graph()
        H.add_nodes_from(error_syndrome)
        for z1, z2 in combinations(error_syndrome, 2):
            #negative l1 distance
            weight = -(abs(z1[0] - z2[0]) + abs(z1[1] - z2[1]))
            H.add_edge(z1, z2, weight=weight)
        bds = []
        for z in error_syndrome:
            t1 = (z[0]+1, -1)
            t2 = (self.grid_size - z[0], self.grid_size)
            min_dist, x_min = min([t1, t2]) 
            nearest_bd = (z, (x_min, z[1])) #needs to be unique for each node, of the form (z, bdz)
            #print(nearest_bd)
            bds.append(nearest_bd)
            H.add_node(nearest_bd)
            H.add_edge(z, nearest_bd, weight=-min_dist)

        for bd1, bd2 in combinations(bds, 2):
            H.add_edge(bd1, bd2, weight=0)
        #print(H.nodes)
        #print('edges', H.edges)
        return H

    def _get_correction_matching(self, error_syndrome):
        H = self._build_syndrome_graph(error_syndrome)
        correction_matching = max_weight_matching(H, maxcardinality=True)
        return correction_matching
        
    def _in_correction_boundary(self, node): #boundary edge in the syndrome graph
        return not type(node[1]) is int

    def _apply_correction_path(self, correction_path):
        for edge in correction_path:
            #print(edge)
            if self.G.has_edge(*edge):
                #print('remove')
                self.G.remove_edge(*edge)
            else:
                self.G.add_edge(*edge)

    def _boundary_edge(self, edge):
        return self._in_correction_boundary(edge[0]) and self._in_correction_boundary(edge[1])

    def _extract_coords(self, edge):
        node1, node2 = edge
        if type(node1[1]) is int:
            i1, j1 = node1
        else:
            i1, j1 = node1[1]
        if type(node2[1]) is int:
            i2, j2 = node2
        else:
            i2, j2 = node2[1]
        return (i1, j1), (i2, j2)

    def _apply_corrections(self, correction_matching):
        for edge in correction_matching:
            #print((i1, j1), (i2, j2))
            if not self._boundary_edge(edge):
                ((i1, j1), (i2, j2)) = self._extract_coords(edge)

                correction_path = []
                if j1 != j2:
                    jsign = np.sign(j2-j1)
                    correction_path += [((i1, u), (i1, u+jsign*2)) for u in
                                        range(j1, j2, jsign*2)]
                if i1 != i2:
                    isign = np.sign(i2-i1)
                    correction_path += [((u, j2), (u+isign*2, j2)) for u in
                                        range(i1, i2, isign*2)]
                #print('path', correction_path)
                self._apply_correction_path(correction_path)

    def _prune(self, edges):
        for edge in edges:
            self.G.remove_edge(*edge)

    def _prune_cycles(self):
        while(True):
            try:
                self._prune(nx.algorithms.find_cycle(self.G))
            except:
                break

    def display_graph(self):
        for e in self.G.edges:
            #print(e[0], e[1])
            plt.plot([e[0][0], e[1][0]], [e[0][1], e[1][1]])
            plt.xlim(-2, self.grid_size + 1)
            plt.ylim(-1, self.grid_size)
        #if len(self.G.edges) == 0:
            #print ('empty graph')
        plt.show()

    def _is_logical_x(self, connected_component):
        left, right = False, False
        #print('con_comp')
        for node in connected_component:
            #print(node)
            if self.G.degree[node] == 2:
                continue
            elif node[0] == -1:
                left = True
            elif node[0] == self.grid_size:
                right = True
            else:
                #print('false')
                return False
        #print('lr', left, right)
        return left and right

    def _check_logical_errors(self):
        components = nx.connected_components(self.G)
        logical_xs = 0
        #print('G', self.G)
        for c in components:
            if len(c) > 1 and self._is_logical_x(c):
                logical_xs += 1
        return logical_xs % 2 == 1

    def simulate_step(self):
        self.G = nx.create_empty_copy(self.G)
        self._generate_bit_flips()
        error_syndrome = self._get_error_syndrome()
        correction_matching = self._get_correction_matching(error_syndrome)
        #print('n', self.G.nodes)
        #print('e', self.G.edges)
        #print('err', error_syndrome)
        #print('cm', correction_matching)
        if self.display_mode:
            print('pre_corrections')
            self.display_graph()
        self._apply_corrections(correction_matching)
        if self.display_mode:
            print('post_corrections')
            self.display_graph()
        #print('n', self.G.nodes)
        #print('e', self.G.edges)
        #self._prune_cycles()
        #print('n', self.G.nodes)
        #print('e', self.G.edges)
        #if self.display_mode:
            #self.display_graph()
        self.logical_error = self._check_logical_errors() 

    def has_logical_error(self):
        return self.logical_error


        
if False:
    d=5
    p=0.15
    count = 0
    error_mode = 'depolarizing'
    #display_mode = True
    display_mode = True
    s = surface_code_sim(d, p, error_mode, display_mode)
    while not s.has_logical_error():
        s.simulate_step()
        count += 1
        
if False:
    d=7
    p=0.155
    count = 0
    error_mode = 'depolarizing'
    #display_mode = True
    num_trials = 1000
    display_mode = False
    for __ in range(num_trials):
        s = surface_code_sim(d, p, error_mode, display_mode)
        while not s.has_logical_error():
            s.simulate_step()
            count += 1
    print(count/num_trials) 

if True:
    distances = [3, 5,7]
    error_mode = 'depolarizing'
    #display_mode = True
    display_mode = False
    num_trials = 1000
    #num_trials = 1
    plt.figure()
    for d in distances:
        ps = []
        ys = []
        for p in np.linspace(.13, 0.17, 4):
            count = 0
            for trial in range(num_trials):
                s = surface_code_sim(d, p, error_mode, display_mode)
                while not s.has_logical_error():
                    s.simulate_step()
                    count += 1
            ps.append(p)
            y = count/num_trials
            ys.append(y)
            print(p, y)
        print(ps, ys)
        plt.plot(ps, ys, label='{}'.format(d))
    plt.legend()
    plt.show()
