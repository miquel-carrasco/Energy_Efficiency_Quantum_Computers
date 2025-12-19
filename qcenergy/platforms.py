from qcenergy.components import Component
from qcenergy.graphs import expander_graph, ND_graph, linear
from qcenergy.algorithms import Algorithm, Circuit
"""
Defines the base classes for computation platforms.
"""

class Computer:
    """
    A generic computer.
    """

    def __init__(self,
                 Nq: int = 100,
                 components: list[Component] = [],
                 N_comp: list[int] = [], 
                 t_init: float = 0.0, 
                 t_meas: float = 0.0, 
                 T_gates: list[float] = [],
                 graph_type: str = "All-to-all"
                 ):
        
        self.Nq = Nq
        self.components = components
        self.N_comp = N_comp
        self.list_components = self.assemble()
        self.t_init = t_init
        self.t_meas = t_meas
        self.t_clock = max(T_gates)
        self.graph_type = graph_type


    @property
    def avg_diameter(self) -> float:
        """
        Return the average diameter of the computer's connectivity graph.

        Returns:
            float: average diameter.
        """
        if self.graph_type == "All-to-all":
            return 1.0
        elif self.graph_type == "Expander":
            return expander_graph(self.Nq)
        elif self.graph_type == "2D":
            return ND_graph(self.Nq, 2)
        elif self.graph_type == "3D":
            return ND_graph(self.Nq, 3)
        elif self.graph_type == "Linear":
            return linear(self.Nq)
        else:
            raise ValueError(f"Unknown graph type: {self.graph_type}")
        

    @property
    def list_types_components(self) -> list[str]:
        """
        Return the list of types of components in the computer.

        Returns:
            list[str]: list of types of components.
        """
        types = set()
        for comp in self.list_components:
            types.add(comp.comp_type)
        return list(types)
    
    @property
    def type_groups_components(self) -> dict[str, list[str]]:
        """
        Return the dictionary of types of components in the computer.

        Returns:
            dict[str, set[str]]: dictionary of types of components.
        """
        type_dict = {}
        for comp in self.list_components:
            if comp.comp_type in type_dict and comp.name not in type_dict[comp.comp_type]:
                type_dict[comp.comp_type].append(comp.name)
            elif comp.comp_type not in type_dict:
                type_dict[comp.comp_type] = [comp.name]
        return (type_dict)

    def assemble(self) -> None:
        """
        Assemble a list of components into the computer
        """
        list_components = []
        for i, comp in enumerate(self.components):
            for  j in range(self.N_comp[i]):
                list_components.append(comp)
        return list_components

    def power_per_component(self) -> dict[str, float]:
        """
        Return the power consumed by each component.

        Returns:
            dict[str, float]: power consumed by each component type.
        """
        power_dict = {}
        for comp in self.list_components:
            if comp.name in power_dict:
                power_dict[comp.name] += comp.P
            else:
                power_dict[comp.name] = comp.P
        return {k: v  for k,v in sorted(power_dict.items(), key=lambda item: item[1], reverse=True)}

    def power_per_types(self) -> dict[str, float]:
        """
        Return the power consumed by each type of component.

        Args:
            time (float): time in seconds.
        Returns:
            dict[str, float]: energy spent by each type of component.
        """
        energy_dict = {}
        for type in self.list_types_components:
            energy_dict[type] = sum([comp.P for comp in self.list_components if comp.comp_type == type])
        
        return {k: v  for k,v in sorted(energy_dict.items(), key=lambda item: item[1], reverse=True)}
    

    def total_energy(self, time: float) -> float:
        """
        Return the total energy spent for a given time.

        Args:
            time (float): time in seconds.

        Returns:
            float: total energy fixed_energy + power*t.
        """
        return sum([comp.computation_energy(time) for comp in self.list_components])
        
    

    @property
    def P(self) -> float:
        """
        Return the total power consumed by the computer.

        Returns:
            float: total power.
        """
        return sum([comp.P for comp in self.list_components])
    
    
    def N(self, T: float, algorithm: Algorithm, N_sampl: float) -> float:
        """
        Return the number of computations that can be performed in time T.

        Args:
            T (float): time in seconds.
            T_list (dict): list of computation times for each component.

        Returns:
            float: number of computations.
        """

        circuit = Circuit(algorithm=algorithm, avg_diameter=self.avg_diameter)
        return T / ((self.t_init + circuit.D*self.t_clock + self.t_meas)*N_sampl)

    def energy_efficiency(self, T: float, algorithm: Algorithm, N_sampl: float) -> float:
        """
        Return the energy efficiency of the computer.

        Args:
            T (float): time in seconds.
            T_list (dict): list of computation times for each component.

        Returns:
            float: energy efficiency.
        """

        circuit = Circuit(algorithm=algorithm, avg_diameter=self.avg_diameter)
        return self.N(T, circuit, N_sampl) / (T*self.P)