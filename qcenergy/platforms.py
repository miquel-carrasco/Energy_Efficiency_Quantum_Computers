from qcenergy.components import Component
from qcenergy.graphs import linear, circular, square, heavy_hex
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
        elif self.graph_type == "Linear":
            return linear(self.Nq)
        elif self.graph_type == "Circular":
            return circular(self.Nq, 2)
        elif self.graph_type == "Square":
            return square(self.Nq, 3)
        elif self.graph_type == "Heavy-hex":
            return heavy_hex(self.Nq)
        else:
            raise ValueError(f"Unknown graph type: {self.graph_type}. Try: All-to-all, Linear, Circular, Square or Heavy-hex")
    
    def final_circuit_depth(self, D0: int, alpha: float) -> int:
        """
        Return the final depth of the circuit after compilation.

        Args:
            D0 (int): initial depth of the circuit.
            alpha (float): overhead factor for routing.

        Returns:
            int: final depth of the circuit.
        """
        
        return D0*(1 + 3*alpha*math.ceil((self.avg_diameter-1)/2))

    def t_comp(self, D0: int, alpha: float, N_samples: float) -> float:
        """
        Return the computation time for a given algorithm.

        Args:
            D0 (int): initial depth of the circuit.
            alpha (float): overhead factor for routing.
            N_samples (float): number of samples.

        Returns:
            float: computation time.
        """
        D = self.final_circuit_depth(D0, alpha)
        return (self.t_reset + D*self.t_clock + self.t_meas)*N_samples
        
    
    def N_pi(self, t: float, D0: int, alpha: float, N_samples: float) -> float:
        """
        Return the number of computations that can be performed in time T.

        Args:
            t (float): time in seconds.
            D0 (int): initial depth of the circuit.
            alpha (float): overhead factor for routing.
            N_sampl (float): number of samples.

        Returns:
            float: number of computations.
        """

        return t / self.t_comp(D0, alpha, N_samples)

    def energy_efficiency(self, D0: int, alpha: float, N_samples: float) -> float:
        """
        Return the energy efficiency of the computer.

        Args:
            D0 (int): initial depth of the circuit.
            alpha (float): overhead factor for routing.
            N_sampl (float): number of samples.

            T_list (dict): list of computation times for each component.

        Returns:
            float: energy efficiency.
        """

        return 1 / (self.t_comp(D0, alpha, N_samples) * self.P)



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


    def final_circuit_depth(self, D0: int, alpha: float, N_gates_layer: int) -> int:
        

        if D0 == 0:
            return 0
        else:
            if N_gates_layer <= self.N_gatezones: 
                D = D0
            else:
                D = math.ceil(N_gates_layer/self.N_gatezones)*D0
            if not self.independent_gates and N_gates_layer > 1 and self.N_gatezones > 1:
                return self.no_indep_depth(D, alpha)
            else:
                return  D
    
    def t_comp(self, D0: int, alpha: float, balpha: float, N_gates_layer: int, N_samples: int) -> float:
        if not self.independent_gates:
            balpha = balpha/(1 + alpha)
        if not self.periodic_reload:
            return (self.t_reset + self.final_circuit_depth(D0, alpha, N_gates_layer)*self.t_clock + self.t_meas + self.t_transport*self.final_circuit_depth(D0, alpha, N_gates_layer)*balpha)*N_samples
        else:
            N_reload = math.ceil(N_samples/self.t_reload_freq)
            extra_reload_time = N_reload*self.t_reload
            return (self.t_reset + self.final_circuit_depth(D0, alpha, N_gates_layer)*self.t_clock + self.t_meas + self.t_transport*self.final_circuit_depth(D0, alpha, N_gates_layer)*balpha)*N_samples + extra_reload_time

    def N_pi(self, t: float, D0: int, alpha: float, balpha: float, N_gates_layer: int, N_samples: int) -> float:
        
        return t / self.t_comp(D0, alpha, balpha, N_gates_layer, N_samples)

    def energy_efficiency(self, D0: int, alpha: float, balpha: float, N_gates_layer: int, N_samples: int) -> float:
        
        return 1 / (self.t_comp(D0, alpha, balpha, N_gates_layer, N_samples) * self.P)


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
                alpha_source =0.5,
                alpha_det = 0.95,
                alpha_dmx = 0.8,
                alpha_coup = 0.8,
                alpha_mzi = 0.9,
                 graph_type: str = "All-to-all"
                 ):
        
        self.Nq = Nq
        self.components = components
        self.N_comp = N_comp
        self.list_components = self.assemble()
        self.r_source = r_source
        self.D_optical = D_optical
        self.alpha_source = alpha_source
        self.alpha_det = alpha_det
        self.alpha_dmx = alpha_dmx
        self.alpha_coup = alpha_coup
        self.alpha_mzi = alpha_mzi
        self.graph_type = graph_type

    def alpha_total(self) -> float:
        """
        Return the end-to-end transmissivity of the chip 
        """
        return self.alpha_det*self.alpha_source*self.alpha_dmx*10**(-2*self.alpha_coup/10)*10**(-2*self.D_optical*self.alpha_mzi/10)
    
    def CoincRate(self, N_photons: int) -> float:
            """
            Return the coincidence rate for detecting n photons

            Args:
                N_photons (int): number of photons

            Returns:
                float: coincidence rate
            """

            return (N_photons/self.r_source)*self.alpha_total()**(N_photons)
    
    def t_aglo(self,N_samples : int, N_photon: int, N_source : int ) -> float:
            """
            Return the time to perform an algorithm in seconds
            Args:
                N_photons (int): number of photons involved
                N_samples (int): number of shots necessary to perform the algorithm
                N_source (int): Number of single photon sources in the computer
            """
            alpha_total = self.alpha_total() #total transmission of the chip
            t_detect = (N_photon/(N_source*self.r_source) )* 1/(alpha_total**N_photon)
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
    
