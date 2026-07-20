from qcenergy.components import Component
from qcenergy.graphs import linear, circular, square, heavy_hex
import math


class Computer:
    """
    A class that represents a generic (qubit-agnostic) quantum computer.

    Attributes:
        Nq: Number of qubits in the computer.
        components: List of components in the computer.
        N_comp: List of number of components in the computer.
        list_components: List of components in the computer, assembled based on the number of components.
    """

    def __init__(self,
                 Nq: int = 100,
                 components: list[Component] = [],
                 N_comp: list[int] = []
                 ):
        
        self.Nq: int = Nq
        self.components: list[Component] = components
        self.N_comp: list[int] = N_comp
        self.list_components: list[Component] = self.assemble()

    
    @property
    def type_groups_components(self) -> dict[str, list[str]]:
        """
        Dictionary of types of components in the computer.
        """

        type_dict = {}
        for comp in self.list_components:
            if comp.comp_type in type_dict and comp.name not in type_dict[comp.comp_type]:
                type_dict[comp.comp_type].append(comp.name)
            elif comp.comp_type not in type_dict:
                type_dict[comp.comp_type] = [comp.name]
        return (type_dict)
    


    def assemble(self) -> list[Component]:
        """
        Assembles the hardware components of the computer, based on the list of components and
        number of components.

        Returns:
            list[Component]: list of components in the computer.
        """
        list_components = []
        for i, comp in enumerate(self.components):
            for  j in range(self.N_comp[i]):
                list_components.append(comp)
        return list_components
    

    def power_per_component(self) -> dict[str, float]:
        """
        Returns the power consumed by each component.

        Returns:
            dict[str, float]: power consumed by each component. Keys are component names.
        """
        power_dict = {}
        for comp in self.list_components:
            if comp.name in power_dict:
                power_dict[comp.name] += comp.P
            else:
                power_dict[comp.name] = comp.P
        return {k: v  for k,v in sorted(power_dict.items(), key=lambda item: item[1], reverse=True)}   
    

    @property
    def P(self) -> float:
        """
        Total power consumed by the computer, in watts.
        """
        return sum([comp.P for comp in self.list_components])
    


    def N_pi(self, t: float, D0: int, alpha: float, N_samples: float) -> float:
        """
        Returns the number of computations that can be performed in time T.

        Args:
            t: time in seconds.
            D0: initial depth of the circuit.
            alpha: overhead factor for routing.
            N_sampl: number of samples.

        Returns:
            float: number of computations.
        """

        return t / self.t_comp(D0, alpha, N_samples)
    
    

class SolidStateComputer(Computer):
    """
    Class representing a solid-state quantum computer, such as superconducting qubits or spin qubits.

    Attributes:
        Nq: Number of qubits in the computer.
        components: List of components in the computer.
        N_comp: List of number of components in the computer.
        t_reset: time to reset a qubit in seconds.
        t_meas: time to measure a qubit in seconds.
        t_clock: time to perform a clock cycle in seconds.
        graph_type: type of connectivity graph of the computer.
        list_components: List of components in the computer, assembled based on the number of components.
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
        self.t_reset: float = t_reset
        self.t_meas: float = t_meas
        self.t_clock: float = t_clock
        self.graph_type: str = graph_type

        self.list_components: list[Component] = self.assemble()

    
    @property
    def avg_spl(self) -> float:
        """
        Average shortest path length of the connectivity graph of the computer.
        """
        if self.graph_type == "All-to-all":
            return 1.0
        elif self.graph_type == "Linear":
            return linear(self.Nq)
        elif self.graph_type == "Circular":
            return circular(self.Nq)
        elif self.graph_type == "Square":
            return square(self.Nq)
        elif self.graph_type == "Heavy-hex":
            return heavy_hex(self.Nq)
        else:
            raise ValueError(f"Unknown graph type: {self.graph_type}. Try: All-to-all, Linear, Circular, Square or Heavy-hex")
    
    @property
    def list_types_components(self) -> list[str]:
        """
        List of the components types in the computer.
        """
        types = set()
        for comp in self.list_components:
            types.add(comp.comp_type)
        types = list(types)
        types.insert(0, types.pop(types.index('Cooling')))
        types.append(types.pop(types.index('Classical Processing')))
        return types
    
    def power_per_types(self) -> dict[str, float]:
        """
        Returns the power consumed by each type of component, in watts.

        Returns:
            dict[str, float]: power consumed by each type of component.
        """
        energy_dict = {}
        for type in self.list_types_components:
            energy_dict[type] = sum([comp.P for comp in self.list_components if comp.comp_type == type])
        
        return {k:v for k,v in energy_dict.items()}     

    def final_circuit_depth(self, D0: int, alpha: float) -> int:
        """
        Return the final depth of the circuit after compilation.

        Args:
            D0 (int): initial depth of the circuit.
            alpha (float): overhead factor for routing.

        Returns:
            int: final depth of the circuit.
        """
        
        return D0*(1 + 3*alpha*math.ceil((self.avg_spl-1)/2))

    def t_comp(self, D0: int, alpha: float, N_samples: float) -> float:
        """
        Returns the computation time for a given algorithm.

        Args:
            D0: initial depth of the circuit.
            alpha: overhead factor for routing.
            N_samples: number of samples.

        Returns:
            float: computation time.
        """
        D = self.final_circuit_depth(D0, alpha)
        return (self.t_reset + D*self.t_clock + self.t_meas)*N_samples
        


    def energy_efficiency(self, D0: int, alpha: float, N_samples: float) -> float:
        """
        Returns the energy efficiency of the computer running a given algorithm.

        Args:
            D0: initial depth of the circuit.
            alpha: overhead factor for routing.
            N_samples: number of samples.

        Returns:
            float: energy efficiency.
        """

        return 1 / (self.t_comp(D0, alpha, N_samples) * self.P)



class AtomBasedComputer(Computer):
    """
    Class representing an atom-based quantum computer, such as neutral atoms or trapped ions.

    Attributes:
        Nq: Number of qubits in the computer.
        components: List of components in the computer.
        N_comp: List of number of components in the computer.
        t_reset: time to reset a qubit in seconds.
        t_meas: time to measure a qubit in seconds.
        t_clock: time to perform a clock cycle in seconds.
        t_transport: time to transportqubits from the storage to the interaction zones in seconds.
        t_reload: time to reload a qubit in seconds.
        t_reload_freq: frequency of the atom reload procedure in number of layers.
        N_gatezones: number of independent gate zones in the computer.
        independent_gates: whether the gates can be performed independently in the different gate zones.
        periodic_reload: whether the atom reload procedure is performed periodically or not.
        list_components: List of components in the computer, assembled based on the number of components.

    
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
        self.t_reset: float = t_reset
        self.t_meas: float = t_meas
        self.t_clock: float = t_clock
        self.t_reload: float = t_reload
        self.t_reload_freq: int = t_reload_freq
        self.t_transport: float = t_transport
        self.N_gatezones: int = N_gatezones
        self.independent_gates: bool = independent_gates
        self.periodic_reload: bool = periodic_reload

        self.list_components: list[Component] = self.assemble()
    
    @property
    def list_types_components(self) -> list[str]:
        """
        List of the components types in the computer.
        """
        types = set()
        for comp in self.list_components:
            types.add(comp.comp_type)
        types = list(types)
        types.insert(0, types.pop(types.index('Environmental Conditions')))
        types.append(types.pop(types.index('Classical Processing')))
        return types
    

    def power_per_types(self) -> dict[str, float]:
        """
        Returns the power consumed by each type of component, in watts.

        Returns:
            dict[str, float]: power consumed by each type of component.
        """
        energy_dict = {}
        for type in self.list_types_components:
            energy_dict[type] = sum([comp.P for comp in self.list_components if comp.comp_type == type])
        
        return {k:v for k,v in energy_dict.items()}     

    
    def no_indep_depth(self, D0: int, alpha: float) -> int:
        """
        Returns a modified depth of the circuit when the gates cannot be performed independently in the different gate zones.

        Returns:
            int: final depth of the circuit.
        """
        return D0 + math.ceil(D0*alpha) 


    def final_circuit_depth(self, D0: int, alpha: float, N_gates_layer: int) -> int:
        """
        Returns the final depth of the circuit after all compilation processes, including non-independent gate performance and limited gate zones.

        Args:
            D0: initial depth of the circuit.
            alpha: overhead factor for routing.
            N_gates_layer: number of gates in the layer.
        
        Returns:
            int: final depth of the circuit.
        """

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
    
    def t_comp(self, D0: int, alpha: float, beta: float, N_gates_layer: int, N_samples: int) -> float:
        """
        Returns the computation time for a given algorithm.

        Args:
            D0: initial depth of the circuit.
            alpha: overhead factor for routing.
            beta: ratio of layers that require transport.
            N_gates_layer: number of gates in the layer.

        Returns:
            float: computation time, in seconds.
        """

        if not self.independent_gates:
            beta = beta/(1 + alpha)
        if not self.periodic_reload:
            return (self.t_reset + self.final_circuit_depth(D0, alpha, N_gates_layer)*self.t_clock + self.t_meas + self.t_transport*self.final_circuit_depth(D0, alpha, N_gates_layer)*beta)*N_samples
        else:
            N_reload = self.final_circuit_depth(D0, alpha, N_gates_layer)/self.t_reload_freq
            extra_reload_time = N_reload*self.t_reload
            return (self.t_reset + self.final_circuit_depth(D0, alpha, N_gates_layer)*self.t_clock + self.t_meas + self.t_transport*self.final_circuit_depth(D0, alpha, N_gates_layer)*beta+extra_reload_time)*N_samples

    def N_pi(self, t: float, D0: int, alpha: float, beta: float, N_gates_layer: int, N_samples: int) -> float:
        """
        Returns the number of computations that can be performed in time T.

        Args:
            t: time, in seconds.
            D0: initial depth of the circuit.
            alpha: overhead factor for routing.
            beta: ratio of layers that require transport.
            N_gates_layer: number of gates in the layer.
            N_samples: number of samples.

        Returns:
            float: number of computations.
        """
        return t / self.t_comp(D0, alpha, beta, N_gates_layer, N_samples)

    def energy_efficiency(self, D0: int, alpha: float, beta: float, N_gates_layer: int, N_samples: int) -> float:
        """
        Returns the energy efficiency of the computer running a given algorithm.

        Args:
            D0: initial depth of the circuit.
            alpha: overhead factor for routing.
            beta: ratio of layers that require transport.
            N_gates_layer: number of gates in the layer.
            N_samples: number of samples.

        Returns:
            float: energy efficiency.
        """
        return 1 / (self.t_comp(D0, alpha, beta, N_gates_layer, N_samples) * self.P)


class PhotonicComputer(Computer):
    """
    Class representing a photonic computer, chip-based with a Clements architecture.

    Attributes:
        Nq: Number of qubits in the computer.
        components: List of components in the computer.
        N_comp: List of number of components in the computer.
        r_source: rate of the single photon source in Hz.
        D_optical: optical depth of the chip.
        eta_source: efficiency of the single photon source.
        eta_det: efficiency of the single photon detector.
        eta_dmx: efficiency of the demultiplexer.
        eta_coup: efficiency of the coupling between the source and the chip.
        eta_mzi: efficiency of the Mach-Zehnder interferometer.
        graph_type: type of connectivity graph of the computer.
    """

    def __init__(self,
                Nq: int = 24,
                components: list[Component] = [],
                N_comp: list[int] = [], 
                r_source: int = 100e6,
                D_optical: int = 48,
                eta_source: float = 0.5,
                eta_det: float = 0.95,
                eta_dmx: float = 0.8,
                eta_coup: float = 0.8,
                eta_mzi: float = 0.9,
                graph_type: str = "All-to-all"
                ):
        
        self.Nq: int = Nq
        self.components: list[Component] = components
        self.N_comp: list[int] = N_comp
        self.list_components: list[Component] = self.assemble()
        self.r_source: int = r_source
        self.D_optical: int = D_optical
        self.eta_source: float = eta_source
        self.eta_det: float = eta_det
        self.eta_dmx: float = eta_dmx
        self.eta_coup: float = eta_coup
        self.eta_mzi: float = eta_mzi
        self.graph_type: str = graph_type

    @property
    def list_types_components(self) -> list[str]:
        """
        List of the components types in the computer.
        """
        types = set()
        for comp in self.list_components:
            types.add(comp.comp_type)
        types = list(types)
        types.insert(0, types.pop(types.index('Cooling')))
        types.append(types.pop(types.index('Classical Processing')))
        return types
    

    def power_per_types(self) -> dict[str, float]:
        """
        Return the power consumed by each type of component.

        Returns:
            dict[str, float]: power consumed by each type of component.
        """
        energy_dict = {}
        for type in self.list_types_components:
            energy_dict[type] = sum([comp.P for comp in self.list_components if comp.comp_type == type])
        
        return {k:v for k,v in energy_dict.items()}     

    def eta_total(self) -> float:
        """
        Returns the end-to-end transmissivity of the chip.

        Returns:
            float: end-to-end transmissivity of the chip.
        """
        return self.eta_det*self.eta_source*self.eta_dmx*10**(-2*self.eta_coup/10)*10**(-2*self.D_optical*self.eta_mzi/10)
    
    def CoincRate(self, N_photons: int) -> float:
            """
            Return the coincidence rate for detecting N_photons.

            Args:
                N_photons: number of photons

            Returns:
                float: coincidence rate
            """

            return (N_photons/self.r_source)*self.eta_total()**(N_photons)
    
    def t_algo(self,N_samples : int, N_photon: int, N_source : int ) -> float:
            """
            Returns the time to perform an algorithm, in seconds.

            Args:
                N_photons: number of photons involved
                N_samples: number of samples necessary to perform the algorithm
                N_source: Number of single photon sources in the computer

            Returns:
                float: time to perform the algorithm, in seconds
            """

            eta_total = self.eta_total() #total transmission of the chip
            t_detect = (N_photon/(N_source*self.r_source) )* 1/(eta_total**N_photon)
            return N_samples*t_detect
            


    def energy_efficiency(self,N_samples : int, N_photon: int, N_source : int ) -> float:
        """
        Return the energy efficiency of the computer running a given algorithm, in computations per joule.
        
        Args:
            N_photons: number of photons involved
            N_samples: number of samples necessary to perform the algorithm
            N_source: Number of single photon sources in the computer

        Returns:
            float: energy efficiency in computations per joule

            """
        t = self.t_algo(N_samples, N_photon, N_source)
        tot_power = self.P

        return 1/(t*tot_power)
    
