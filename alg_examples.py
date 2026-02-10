import qiskit
import matplotlib.pyplot as plt
import numpy as np
from qiskit.circuit.library import QFT, CDKMRippleCarryAdder
from qiskit import transpile
from qiskit.converters import circuit_to_dag

from qcenergy.algorithms import Algorithm, Circuit

circ = QFT(num_qubits = 100)
qc = transpile(circ, basis_gates=['cx', 'h', 'rx', 'z', 's'], optimization_level=0)

dag = circuit_to_dag(qc)

layers_w_2q = 0
for layer in dag.layers():
    for gate in layer['partition']:
        if len(gate)==2:
            layers_w_2q += 1
            break

print(f'QFT: D0={dag.depth()}, eta={layers_w_2q/dag.depth()}')


circ = CDKMRippleCarryAdder(int(100/2)-1)
qc = transpile(circ, basis_gates=['cx', 'h', 'rx', 'z', 's'], optimization_level=0)

dag = circuit_to_dag(qc)

layers_w_2q = 0
for layer in dag.layers():
    for gate in layer['partition']:
        if len(gate)==2:
            layers_w_2q += 1
            break

print(f'CDKM Adder: D0={dag.depth()}, eta={layers_w_2q/dag.depth()}')

