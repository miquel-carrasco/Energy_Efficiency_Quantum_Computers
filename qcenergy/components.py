"""
Defines base classes for components.
"""


class Component:
    """
    A generic component class that can be used to represent any component in a quantum computing system.

    Attributes:
        name (str): Name of the component.
        P (float): Power consumed by the component when being used.
        comp_type (str): Type of the component (e.g., 'cooling', 'qubit control', etc.).
    """

    def __init__(self,
                 name: str = "generic component",
                 P: float = 0.0,
                 comp_type: str = ""):
        self.name = name  #: Name of the component.
        self.P = P  #: Power consumed by the component when being used.
        self.comp_type = comp_type  #: Type of the component.


    def computation_energy(self, time: float) -> float:
        """
        Return the total energy spent for a given time.

        Args:
            time (float): time in seconds.

        Returns:
            float: energy consumed in time t (P*t).
        """
        return time * self.P
