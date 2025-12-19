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


# class PassiveComponent(Component):
#     """
#     Generic passive component.
#     """

#     def __init__(self, power: float = 0.0, t_init: float = 0.0):
#         super().__init__(power)
#         self.t_init = t_init
#     name = "passive component"

#     def initial_energy(self) -> float:
#         """
#         Return the initial energy spent for a given time.

#         Returns:
#             float: total energy fixed_energy + power*t.
#         """
#         return self.t_init * self.power


# class ActiveComponent(Component):
#     """
#     Generic active component.
#     """

#     name = "active component"

#     def __init__(self, t_active: float = 0.0, power: float = 0.0):
#         super().__init__(power)
#         self.t_active = t_active  #: time in seconds the component is active.