import rustworkx as rx
import rustworkx.generators as rx_gen
import math

"""
Average shortest path length (ASPL) functions for different graph topologies. These functions take the number of qubits (Nq) as input and return the (ASPL) for the corresponding graph topology.
"""


def linear(Nq):
    graph = rx_gen.path_graph(Nq)
    return rx.graph_unweighted_average_shortest_path_length(graph)

def circular(Nq):
    graph = rx_gen.cycle_graph(Nq)
    return rx.graph_unweighted_average_shortest_path_length(graph)

def square(Nq):
    n = math.sqrt(Nq)
    if n%1 == 0:
        n = int(n)
        graph = rx_gen.grid_graph(n, n)
        return rx.graph_unweighted_average_shortest_path_length(graph)
    else:
        raise Exception(f"Nq = {Nq} is not a valid number of qubits for a n x n square lattice")

def heavy_hex(Nq):
    valid_Nq = [1, 19, 57, 115, 193]
    d_vals = [1,3,5,7,9]
    if Nq in valid_Nq:
        d = d_vals[valid_Nq.index(Nq)]
        graph = rx_gen.heavy_hex_graph(d)
        return rx.graph_unweighted_average_shortest_path_length(graph)
    else:
        raise Exception(f"Nq = {Nq} is not a valid number of qubits for a heavy-hex lattice. Try: 1, 19, 57, 115, 193")