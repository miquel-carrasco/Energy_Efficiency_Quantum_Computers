"""
Defines base classes for components.
"""


class Component:
    """
    A generic component.
    """

    def __init__(self,
                 name: str = "generic component",
                 P: float = 0.0,
                 comp_type: str = ""):
        self.name = name  #: Name of the component.
        self.P = P  #: Power consumed by the component when being used.
        self.comp_type = comp_type  #: Type of the component.

    def __repr__(self):
        return f"({self.name}: P= {self.P}W)"

    def computation_energy(self, time: float) -> float:
        """
        Return the total energy spent for a given time.

        Args:
            time (float): time in seconds.

        Returns:
            float: total energy fixed_energy + P*t.
        """
        return time * self.P
