def expander_graph(Nq):
    import numpy as np
    return np.log(Nq)

def ND_graph(Nq, D):
    return Nq**(1/D)

def linear(Nq):
    return Nq