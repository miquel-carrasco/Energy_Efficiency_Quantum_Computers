import numpy as np

def expander_graph(Nq):
    return np.log(Nq)

def ND_graph(Nq, D):
    return Nq**(1/D)

def linear(Nq):
    return Nq