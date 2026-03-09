from qcenergy.components import Component
from qcenergy.graphs import expander_graph, ND_graph, linear
from qcenergy.algorithms import Algorithm, Circuit
import math
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
                 N_comp: list[int] = []
                 ):
        
        self.Nq = Nq
        self.components = components
        self.N_comp = N_comp
        self.list_components = self.assemble()
        

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
        types = list(types)
        types.insert(0, types.pop(types.index('Environmental Conditions')))
        types.append(types.pop(types.index('Classical Processing')))
        return types
    
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
        
        # return {k: v  for k,v in sorted(energy_dict.items(), key=lambda item: item[1], reverse=True)}
        return {k:v for k,v in energy_dict.items()}        
    

    @property
    def P(self) -> float:
        """
        Return the total power consumed by the computer.

        Returns:
            float: total power.
        """
        return sum([comp.P for comp in self.list_components])
    
    

class SolidStateComputer(Computer):
    """
    A solid-state computer.
    """
    def __init__(self,
                 Nq: int = 100,
                 components: list[Component] = [],
                 N_comp: list[int] = [], 
                 t_reset: float = 0.0, 
                 t_meas: float = 0.0, 
                 t_clock: float = 0.0,
                 graph_type: str = "All-to-all"
                 ):
    
        super().__init__(Nq=Nq, components=components, N_comp=N_comp)
        self.t_reset = t_reset
        self.t_meas = t_meas
        self.t_clock = t_clock
        self.graph_type = graph_type

        self.list_components = self.assemble()

    
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
    
    def final_circuit_depth(self, D0: int, eta: float) -> int:
        """
        Return the final depth of the circuit after compilation.

        Args:
            D0 (int): initial depth of the circuit.
            eta (float): overhead factor for routing.

        Returns:
            int: final depth of the circuit.
        """
        
        return D0*(1 + eta*math.ceil((self.avg_diameter-1)/2))

    def t_comp(self, D0: int, eta: float, N_samples: float) -> float:
        """
        Return the computation time for a given algorithm.

        Args:
            D0 (int): initial depth of the circuit.
            eta (float): overhead factor for routing.
            N_samples (float): number of samples.

        Returns:
            float: computation time.
        """
        D = self.final_circuit_depth(D0, eta)
        return (self.t_reset + D*self.t_clock + self.t_meas)*N_samples
        
    
    def N_pi(self, t: float, D0: int, eta: float, N_samples: float) -> float:
        """
        Return the number of computations that can be performed in time T.

        Args:
            t (float): time in seconds.
            D0 (int): initial depth of the circuit.
            eta (float): overhead factor for routing.
            N_sampl (float): number of samples.

        Returns:
            float: number of computations.
        """

        return t / self.t_comp(D0, eta, N_samples)

    def energy_efficiency(self, D0: int, eta: float, N_samples: float) -> float:
        """
        Return the energy efficiency of the computer.

        Args:
            D0 (int): initial depth of the circuit.
            eta (float): overhead factor for routing.
            N_sampl (float): number of samples.

            T_list (dict): list of computation times for each component.

        Returns:
            float: energy efficiency.
        """

        return 1 / (self.t_comp(D0, eta, N_samples) * self.P)



class AtomBasedComputer(Computer):
    """
    A trapped ions computer.
    """
    def __init__(self,
                 Nq: int = 100,
                 components: list[Component] = [],
                 N_comp: list[int] = [], 
                 t_reset: float = 0.0, 
                 t_meas: float = 0.0, 
                 t_clock: float = 0.0,
                 t_transport: float = 0.0,
                 t_reload: float = 0.0,
                 t_reload_freq: int = 0,
                 N_gatezones: int = 1,
                 independent_gates: bool = False,
                 periodic_reload: bool = False
                 ):
    
        super().__init__(Nq=Nq, components=components, N_comp=N_comp)
        self.t_reset = t_reset
        self.t_meas = t_meas
        self.t_clock = t_clock
        self.t_reload = t_reload
        self.t_reload_freq = t_reload_freq
        self.t_transport = t_transport
        self.N_gatezones = N_gatezones
        self.independent_gates = independent_gates
        self.periodic_reload = periodic_reload

        self.list_components = self.assemble()

    
    def no_indep_depth(self, D0: int, alpha: float) -> int:

        return D0 + math.ceil(D0*alpha) 


    def final_circuit_depth(self, D0: int, alpha: float, N_gates: int) -> int:
        
        if D0 == 0:
            return 0
        else:
            if not self.independent_gates and N_gates > 1:
                D_prima = self.no_indep_depth(D0, alpha)
            else:
                D_prima = D0
            
            return N_gates / min(N_gates/D_prima, self.N_gatezones)
    
    def t_comp(self, D0: int, alpha: float, beta: float, N_gates: int, N_samples: int) -> float:

        if not self.periodic_reload:
            return (self.t_reset + self.final_circuit_depth(D0, alpha, N_gates)*self.t_clock + self.t_meas + self.t_transport*self.final_circuit_depth(D0, alpha, N_gates)*beta)*N_samples
        else:
            extra_reload_time = math.floor(N_samples/self.t_reload_freq)*self.t_reload
            return (self.t_reset + self.final_circuit_depth(D0, alpha, N_gates)*self.t_clock + self.t_meas + self.t_transport*self.final_circuit_depth(D0, alpha, N_gates)*beta)*N_samples + extra_reload_time

    def N_pi(self, t: float, D0: int, alpha: float, beta: float, N_gates: int, N_samples: int) -> float:
        
        return t / self.t_comp(D0, alpha, beta, N_gates, N_samples)

    def energy_efficiency(self, D0: int, alpha: float, beta: float, N_gates: int, N_samples: int) -> float:
        
        return 1 / (self.t_comp(D0, alpha, beta, N_gates, N_samples) * self.P)


class PhotonicComputer(Computer):
    """
    A photonic computer, chip-based with a Clement architecture.
    """

    def __init__(self,
                Nq: int = 24,
                components: list[Component] = [],
                N_comp: list[int] = [], 
                r_source: int = 100*10^6,
                D_optical: int = 48,
                eta_source =0.5,
                eta_det = 0.95,
                eta_dmx = 0.8,
                eta_coup = 0.8,
                eta_mzi = 0.9,
                 graph_type: str = "All-to-all"
                 ):
        
        self.Nq = Nq
        self.components = components
        self.N_comp = N_comp
        self.list_components = self.assemble()
        self.r_source = r_source
        self.D_optical = D_optical
        self.eta_source = eta_source
        self.eta_det = eta_det
        self.eta_dmx = eta_dmx
        self.eta_coup = eta_coup
        self.eta_mzi = eta_mzi
        self.graph_type = graph_type

    def eta_total(self) -> float:
        """
        Return the end-to-end transmissivity of the chip 
        """
        return self.eta_det*self.eta_source*self.eta_dmx*10**(-2*self.eta_coup/10)*10**(-self.D_optical*self.eta_mzi/10)
    
    def CoincRate(self, N_photons: int) -> float:
            """
            Return the coincidence rate for detecting n photons

            Args:
                N_photons (int): number of photons

            Returns:
                float: coincidence rate
            """

            return (N_photons/self.r_source)*self.eta_total()**(N_photons)
    
    def t_aglo(self,N_samples : int, N_photon: int, N_source : int ) -> float:
            """
            Return the time to perform an algorithm in seconds
            Args:
                N_photons (int): number of photons involved
                N_samples (int): number of shots necessary to perform the algorithm
                N_source (int): Number of single photon sources in the computer
            """
            eta_total = self.eta_total() #total transmission of the chip
            t_detect = (N_photon/(N_source*self.r_source) )* 1/(eta_total**N_photon)
            return N_samples*t_detect
            


    def energy_efficiency(self,N_samples : int, N_photon: int, N_source : int ) -> float:
        """
        Return the energy efficiency 
        
        Args:
                N_photons (int): number of photons involved
                N_samples (int): number of shots necessary to perform the algorithm
                N_source (int): Number of single photon sources in the computer
            """
        t_algo = self.t_aglo(N_samples, N_photon, N_source)
        tot_power = self.P

        return 1/(t_algo*tot_power)
    
