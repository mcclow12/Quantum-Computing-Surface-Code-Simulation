import random
from itertools import product, combinations

import networkx as nx
from networkx.algorithms import max_weight_matching
import numpy as np
import matplotlib.pyplot as plt

class surface_code_sim():
    """
    Simulator for the surface code.
    """

    def __init__(self, distance, p, error_mode, display_mode):
        """
        Initialization method for the surface code simulator
        :param distance: The distance of the surface code.
        :param p: The probability of a bit-flip in the simulation.
        :param error_mode: Which error mode to use. Either 'depolarizing' or 'uncorrelated'.
        :param display_mode: Whether to draw the graph after each step.
        """
        if error_mode == 'depolarizing':
            self.flip_prob = 2*p/3
        elif error_mode == 'uncorrelated':
            self.flip_prob = p
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

    def reset(self):
        """Resets the simulation to an empty graph with no logical error."""
        self.G = nx.create_empty_copy(self.G)
        self.logical_error = False

    def _generate_bit_flips(self):
        """Generates bit flips in the graph with probability self.flip_prob."""
        for edge in self.data_edges:
            r = random.random()
            if r < self.flip_prob:
                if not self.G.has_edge(*edge):
                    self.G.add_edge(*edge)
                else:
                    self.G.remove_edge(*edge)

    def _get_error_syndrome(self):
        return [n for n in self.z_nodes if self.G.degree[n]%2==1]

    def _build_syndrome_graph(self, error_syndrome):
        """
        Returns the complete graph H on all error syndrome nodes. The edges are weighted by the negative
        distance in the original graph self.G (where all edges have weight 1). The graph H also contains the edge
        from each error syndrome node to the nearest boundary node.
        """
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
            bds.append(nearest_bd)
            H.add_node(nearest_bd)
            H.add_edge(z, nearest_bd, weight=-min_dist)

        for bd1, bd2 in combinations(bds, 2):
            H.add_edge(bd1, bd2, weight=0)
        return H

    def _get_correction_matching(self, error_syndrome):
        """
        Returns a perfect matching of nodes in the syndrome graph. The matching is chosen to minimize the
        sum of the distances from x to y for each pair (x,y) in the matching.
        """
        H = self._build_syndrome_graph(error_syndrome)
        correction_matching = max_weight_matching(H, maxcardinality=True)
        return correction_matching
        
    def _in_correction_boundary(self, node):
        """Returns True if node is a boundary node in the syndrome graph."""
        return not type(node[1]) is int

    def _apply_correction_path(self, correction_path):
        """Flips all the edges in self.G contained in correction_path."""
        for edge in correction_path:
            if self.G.has_edge(*edge):
                self.G.remove_edge(*edge)
            else:
                self.G.add_edge(*edge)

    def _boundary_edge(self, edge):
        """Returns true if the edge contains two boundary nodes in the syndrome graph."""
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
        """
        Apply the corrections according to the matching correction_matching which is obtained
        from the error syndrome.
        """
        for edge in correction_matching:
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
                self._apply_correction_path(correction_path)

    def _prune(self, edges):
        """Removes each edge in edges from self.G"""
        for edge in edges:
            self.G.remove_edge(*edge)

    def _prune_cycles(self):
        """Removes all cycles from the graph self.G"""
        while(True):
            try:
                self._prune(nx.algorithms.find_cycle(self.G))
            except:
                break

    def display_graph(self):
        """Plots the graph self.G"""
        plt.figure()
        pos = {n:n for n in self.G.nodes}
        node_list = list(self.G.nodes)
        node_color = ['g' if 0 <= n[0] < self.grid_size else 'b' for n in node_list]
        nx.draw_networkx(self.G, pos=pos, with_labels = False, node_color=node_color)

    def _is_logical_x(self, connected_component):
        """Returns True if connected_component represents a logical bit flip error."""
        left, right = False, False
        for node in connected_component:
            if self.G.degree[node] == 2:
                continue
            elif node[0] == -1:
                left = True
            elif node[0] == self.grid_size:
                right = True
            else:
                return False
        return left and right

    def _check_logical_errors(self):
        """Returns True if the graph G contains a logical bit flip error."""
        components = nx.connected_components(self.G)
        logical_xs = 0
        for c in components:
            if len(c) > 1 and self._is_logical_x(c):
                logical_xs += 1
        return logical_xs % 2 == 1

    def simulate_step(self):
        """Simulates one step of errors and surface code error correction."""
        self.G = nx.create_empty_copy(self.G)
        self._generate_bit_flips()
        error_syndrome = self._get_error_syndrome()
        correction_matching = self._get_correction_matching(error_syndrome)
        if self.display_mode:
            print('(1) pre_corrections')
            self.display_graph()
        self._apply_corrections(correction_matching)
        if self.display_mode:
            print('(2) post_corrections')
            self.display_graph()
        self.logical_error = self._check_logical_errors() 

    def has_logical_error(self):
        """Returns true"""
        return self.logical_error

    def simulate(self):
        """Repeatedly runs simulate_step until a logical bit flip is created.

        :return (int) count: number of simulation steps until logical bit flip error."""
        count = 0
        while not self.has_logical_error():
            self.simulate_step()
            count += 1
        return count
