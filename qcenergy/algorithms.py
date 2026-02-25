import numpy as np
import math

class Algorithm:
    """
    A generic algorithm.
    """
    
    def __init__(self,
                 D0: int = 1000,
                 eta: float = 0.1,
                 ):
        
        self.D0 = D0
        self.eta = eta


class Circuit:
    """
    A generic circuit.
    """
    
    def __init__(self,
                 algorithm: Algorithm,
                 avg_diameter: float,
                 ):
        
        self.D0 = algorithm.D
        self.eta = algorithm.eta
        self.avg_diameter = avg_diameter

    @property
    def D(self) -> float:
        """
        Returns the final depth of the circuit, depending on the algorithm and the computer.

        Returns:
            float: depth.
        """
        return self.D0*(1 + self.eta*math.ceil((self.avg_diameter-1)/2))