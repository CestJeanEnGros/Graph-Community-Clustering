import os
import colorsys

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import random as rd

from typing import Iterable
from collections import deque
from pathlib import Path

"""
    Global visualization variables.
    Modify to your own convinience
"""
figure_size = (18,14) 

def make_universal(filepath):
    """
        Create an exploitable path for every operating systems
    """
    return os.sep.join(filepath.split('/'))

class Node:
    def __init__(self,idx,neighbors):
        self.__idx = idx
        self.__neighbors = neighbors
        self.__group = None
    
    def group(self) -> int:
        return self.__group
    
    def neighbors(self) -> list[int]:
        return self.__neighbors 
    
    def degree(self) -> int:
        return len(self.__neighbors)

    def __hash__(self) -> int:
        return self.__idx
    
    def __eq__(self, other):
        return self.__idx == other.__idx

    def __repr__(self) -> str:
        return 'Node'+str(['idx:'+str(self.__idx),'neighbors:'+str(self.__neighbors)])
    
    def get_idx(self):
        return self.__idx
    
class Edge:
    def __init__(self,n1,n2,superGraphe=False):
        if not superGraphe:
            self.__idx = frozenset((n1,n2))
        else:
            self.__idx = tuple((n1,n2))
    def __hash__(self):
        return self.__idx.__hash__()

    def __repr__(self):
        return 'Edge'+str(tuple(self.__idx))
    
    def __eq__(self, other):
        return self.__idx == other.__idx
    
    def has_node(self,u) -> bool:
        return u in self.__idx
    
    def get_idx(self):
        return self.__idx

class Solution:
    def __init__(self,groups: list[Iterable[int]]):
        self.L = len(groups)
        self.groups_of_node_dict = {}
        self.groups_dict = {}
        for i, group in enumerate(groups):
            group_id = i+1
            self.groups_dict[group_id] = list(group)
            for node in group:
                if node not in self.groups_of_node_dict.keys():
                    self.groups_of_node_dict[node] = []
                self.groups_of_node_dict[node].append(group_id)

    def get_group(self, idx: int) -> list[int]:
        assert(idx > 0)
        assert(idx <= self.L)
        return self.groups_dict[idx-1]

    def __repr__(self):
        return 'Solution'+str([('idx:'+str(k),'neighbors:'+str(v)) for k,v in self.groups_dict.items()])

class Instance:
    def __init__(self,in_file: str, realM=None, superGraphe=False):
        self.filepath = Path(make_universal(in_file))
        assert(self.filepath.exists())
        with open(self.filepath) as f:
            if not superGraphe:
                self.superGraphe = superGraphe
                lines = list([[int(x.strip()) for x in x.split(' ') if x.strip() != ''] for x in f.readlines()])
                self.N, self.M = tuple(map(int,lines[0]))
                self.nodes = [Node(i+1,line) for i, line in enumerate(lines[1:self.N+1])]
                self.edges = {Edge(i+1,j) for i, line in enumerate(lines[1:self.N+1]) for j in line}
            else:
                self.superGraphe = superGraphe
                self.realM = realM
                lines = list([[int(x.strip()) for x in x.split(' ') if x.strip() != ''] for x in f.readlines()])
                self.N, self.M = tuple(map(int,lines[0]))
                self.nodes = [Node(i+1,line) for i, line in enumerate(lines[1:self.N+1])]
                self.edges = [Edge(i+1,j, superGraphe) for i, line in enumerate(lines[1:self.N+1]) for j in line if i+1<=j]
        assert(self.N == len(self.nodes))
        assert(self.M == len(self.edges))

    def get_node(self, idx: int) -> Node:
        assert(idx > 0)
        assert(idx <= self.N)
        return self.nodes[idx-1]

    def is_valid_solution(self,sol:Solution) -> bool:
        """ 
            Returns True when the solution is valid
        """
        return self.unique_nodes_in_solution(sol) and self.no_missing_or_added_nodes(sol) and self.no_disconnected_groups_in_solution(sol)
    
    def unique_nodes_in_solution(self,sol:Solution) -> bool:
        """
            Returns True when the solution has no overlapping pieces
        """
        return len(self.non_unique_nodes(sol))==0

    def non_unique_nodes(self,sol:Solution)-> dict[int,frozenset[int]]:
        """
            Returns all pairs of nodes and ids of groups that overlaps because of them
        """
        pairs = {}
        for node, group in sol.groups_of_node_dict.items():
            if len(group) > 1:
                pairs[node] = frozenset(group)
        
        return pairs

    def no_missing_or_added_nodes(self,sol:Solution) -> bool:
        """
            Returns True when the solution has no overlapping pieces
        """
        return len(self.missing_nodes(sol))==0 and len(self.added_nodes(sol))==0 

    def missing_nodes(self,sol:Solution)-> set[int]:
        """
            Returns all nodes missing from the group assignement
        """
        node_set = {node.get_idx() for node in self.nodes}
        return node_set.difference(sol.groups_of_node_dict.keys())

    def added_nodes(self,sol:Solution)-> set[int]:
        """
            Returns all nodes missing from the group assignement
        """
        node_set = {node.get_idx() for node in self.nodes}
        return set(sol.groups_of_node_dict.keys()).difference(node_set)

    def no_disconnected_groups_in_solution(self,sol:Solution) -> bool:
        """
            Returns True when the solution has no overlapping pieces
        """
        return len(self.disconnected_groups(sol))==0

    def disconnected_groups(self,sol:Solution)-> set[int]:
        """
            Returns all disconnected groups 
        """
        disconnected = set()
        groups = sol.groups_dict
        for group_id, nodes in groups.items():
            if len(nodes) > 1:
                visited = set()
                queue = deque()
                queue.append(nodes[0])
                while len(queue) > 0:
                    current = queue.pop()
                    if current in visited:
                        continue

                    visited.add(current)
                    for node in nodes:
                        if node in visited:
                            continue
                        if Edge(current, node) in self.edges:
                            queue.append(node)
                
                if len(visited.intersection(nodes)) != len(nodes):
                    disconnected.add(group_id)
        return disconnected

    def solution_value(self, sol: Solution) -> float:
        """
            Compute and return the cohesion value of a solution
        """
        if self.superGraphe:
            M = self.realM
            deg_sum = 2 * M
            norm = 1 / deg_sum ** 2
            L_c = np.zeros(sol.L)
            deg_c = np.zeros(sol.L)

            for e in self.edges:
                n1, n2 = e.get_idx()
                gid_n1 = sol.groups_of_node_dict[n1][0]
                gid_n2 = sol.groups_of_node_dict[n2][0]
                if gid_n1 == gid_n2:
                    if n1 == n2:
                        L_c[gid_n2-1] += 0.5
                    else:
                        L_c[gid_n2-1] += 1
                if n1 == n2:
                    deg_c[gid_n1-1] += 0.5
                    deg_c[gid_n2-1] += 0.5
                else:
                    deg_c[gid_n1-1] += 1
                    deg_c[gid_n2-1] += 1
            
            # print(L_c)
            # print(deg_c)
            # print(self.edges)
            # print(M)
            # print(sol)
            return np.sum(L_c / M - (deg_c ** 2) * norm)
        else:
            M = self.M
            deg_sum = 2 * M
            norm = 1 / deg_sum ** 2
            L_c = np.zeros(sol.L)
            deg_c = np.zeros(sol.L)

            for e in self.edges:
                n1, n2 = e.get_idx()
                gid_n1 = sol.groups_of_node_dict[n1][0]
                gid_n2 = sol.groups_of_node_dict[n2][0]
                if gid_n1 == gid_n2:
                    L_c[gid_n2-1] += 1
                
                deg_c[gid_n1-1] += 1
                deg_c[gid_n2-1] += 1
            
            # print(L_c)
            # print(deg_c)
            # print(norm)
            # print(M)
            return np.sum(L_c / M - (deg_c ** 2) * norm)

    def solution_value_and_validity(self, sol: Solution) -> tuple[float,bool]:
        """
            Return the cohesion and validity of a solution
        """
        return self.solution_value(sol), self.is_valid_solution(sol)

    def generate_distinct_colors(self, num_colors):
        """
            Generates an array of #num_colors colors such that
            the colors are the most distinct possible
        """
        # Generate equally spaced hues
        hues = np.linspace(0, 1, num_colors, endpoint=False)

        # Set constant saturation and value
        saturation = 0.9
        value = 0.9

        # Convert HSV to RGB
        rgb_colors = []
        for hue in hues:
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
            rgb_colors.append((r, g, b, .4))
            rgb_colors.append((r, g, b, 1))

        return rgb_colors

    def visualize_instance(self):
        """
            Show the instance graph
        """
        G = nx.Graph()
        G.add_nodes_from([n.get_idx() for n in self.nodes])
        G.add_edges_from([e.get_idx() for e in self.edges])
        pos = nx.spring_layout(G, seed=1430)
        # Nodes colored by cluster
        fig, ax = plt.subplots(figsize=figure_size)

        nx.draw(G, pos=pos, ax=ax)

        fig.suptitle("Visualisation de l'instance", fontsize=16)
        fig.tight_layout()
        plt.show()
        plt.close()

    def visualize_solution(self, sol: Solution):
        """
            Show and save the solution's visualization
        """
        G = nx.Graph()
        G.add_nodes_from([n.get_idx() for n in self.nodes])
        G.add_edges_from([e.get_idx() for e in self.edges])

        # Layout for base graph
        base_pos = nx.spring_layout(G, seed=1430)

        # Compute positions for the node clusters as if they were themselves nodes in a
        # supergraph using a larger scale factor
        supergraph: nx.Graph = nx.cycle_graph(sol.L)
        superpos = nx.circular_layout(supergraph, scale=supergraph.number_of_nodes() * 1.5)

        # Use the "supernode" positions as the center of each node cluster
        centers = list(superpos.values())
        pos = {}
        for center, comm in zip(centers, sol.groups_dict.values()):
            pos.update(nx.spring_layout(nx.subgraph(G, comm), center=center, seed=1430))

        colors = self.generate_distinct_colors(sol.L)
        
        color_map = []
        for node in G:
            for group, clr in zip(sol.groups_dict.values(), colors):
                if node in group:
                    color_map.append(clr)
        
        
        # Nodes colored by cluster
        fig, ax = plt.subplots(1,2, figsize=figure_size)

        ax[0].set_title("Coloration de l'instance")
        nx.draw(G, pos=base_pos, node_color=color_map, ax=ax[0])
        ax[0].set_axis_on()

        ax[1].set_title("Coloration du super-graphe de groupement")
        nx.draw(G, pos=pos, node_size=100, node_color=color_map, ax=ax[1])
        ax[1].set_axis_on()

        cohesion = self.solution_value(sol)
        fig.suptitle(f"Solution de {self.filepath.stem}\n Coefficient de cohésion = {cohesion}", fontsize=18)
        fig.tight_layout()
        plt.savefig("visualization_"+self.filepath.stem+".png")
        plt.show()
        plt.close()
    
    def save_solution(self, sol: Solution) -> None:
        """
            Saves the solution to a file
        """
        solution_dir = Path(os.path.join(os.path.dirname(__file__),"solutions"))
        if not solution_dir.exists():
            solution_dir.mkdir()

        with open(os.path.join(solution_dir, self.filepath.stem + ".txt"),'w+') as f:
            f.write(f"{sol.L}\n")
            for group in sol.groups_dict.values():
                f.write(f'{" ".join([str(w) for w in group])}\n')

    
    def read_solution(self, in_file: str) -> Solution:
        """
            Read a solution file
        """
        solution_file = Path(make_universal(in_file))

        with open(solution_file) as f:
            lines = list([[int(x.strip()) for x in x.split(' ') if x.strip() != ''] for x in f.readlines()])
            L = int(lines[0][0])
            
            groups = [line for line in lines[1:L+1]]

        assert(L == len(groups))
        return Solution(groups)
    
class Components:
    def __init__(self, graph: Instance):
        self.graph = graph
        self.components = {}
        self.num_components = 0

    def find_components(self):
        """
        Find and store the connected components of the graph.
        """
        visited = set()
        components = {}

        def dfs(node, component_id):
            """
            Perform DFS to visit all nodes in the connected component.
            """
            stack = [node]
            while stack:
                current_node = stack.pop()
                if current_node not in visited:
                    visited.add(current_node)
                    components[component_id].append(current_node)
                    for neighbor in self.graph.get_node(current_node).neighbors():
                        if neighbor not in visited:
                            stack.append(neighbor)

        # Iterate over all nodes to find all connected components
        for node in self.graph.nodes:
            if node.get_idx() not in visited:
                self.num_components += 1
                components[self.num_components] = []
                dfs(node.get_idx(), self.num_components)

        self.components = components

    def get_number_of_components(self):
        """
        Returns the number of connected components.
        """
        return self.num_components

    def get_components(self):
        """
        Returns the dictionary of connected components.
        """
        return self.components

    def __repr__(self):
        return f"ConnectedComponents(num_components={self.num_components}, components={self.components})"


