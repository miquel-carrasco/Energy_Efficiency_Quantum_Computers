import qiskit
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colormaps



params = {'axes.labelsize': 14,
         'axes.titlesize': 15,
         'axes.linewidth': 1.5,
         'lines.markeredgecolor': "black",
     	'lines.linewidth': 1.5,
         'xtick.labelsize': 10,
         'ytick.labelsize': 11,
         "text.usetex": True,
         "font.family": "serif",
         "font.serif": ["Palatino"]
         }
plt.rcParams.update(params)




def ghz_circuit(num_qubits):
    circuit = qiskit.QuantumCircuit(num_qubits, num_qubits)
    circuit.h(0)
    for i in range(num_qubits - 1):
        circuit.cx(i, i + 1)
    circuit.measure(range(num_qubits), range(num_qubits))
    return circuit


num_qubits = 100
# TODO: Need to check all the available gates in Qiskit, this list is from some months ago
all_gates = ['x', 'y', 'z', 'rx', 'ry', 'rz', 'cx', 'cp', 'cz', 'h', 's', 'sdg', 't', 'tdg', 'u1', 'u2', 'u3', 'swap', 'iswap', 'measure']

# TODO: Need to define which basis gate sets to use (one or two per platforms?)
basis_gates = [
    ['cx', 'h', 'rx', 'z', 's'],
    ['ecr', 'h', 'rx', 'z', 's'],
    ['rx', 'rz', 'h', 'cz']
]


qft_circ = qiskit.circuit.library.QFT(num_qubits)
lb_qft_circ = qiskit.transpile(qft_circ, basis_gates=all_gates)
lb_qft_depth = lb_qft_circ.depth()

adder_circ = qiskit.circuit.library.CDKMRippleCarryAdder(int(num_qubits/2)-1)
lb_adder_circ = qiskit.transpile(adder_circ, basis_gates=all_gates)
lb_adder_depth = lb_adder_circ.depth()

ghz_circuit = ghz_circuit(num_qubits)
lb_ghz_circ = qiskit.transpile(ghz_circuit, basis_gates=all_gates)
lb_ghz_depth = lb_ghz_circ.depth()

qft_transp_depths = []
adder_transp_depths = []
ghz_transp_depths = []
for bg in basis_gates:
    transpiled_circ = qiskit.transpile(qft_circ, basis_gates=bg)
    depth = transpiled_circ.depth()
    qft_transp_depths.append(depth)

    transpiled_adder_circ = qiskit.transpile(adder_circ, basis_gates=bg)
    depth = transpiled_adder_circ.depth()
    adder_transp_depths.append(depth)

    transpiled_ghz_circ = qiskit.transpile(ghz_circuit, basis_gates=bg)
    depth = transpiled_ghz_circ.depth()
    ghz_transp_depths.append(depth)


    # plot grouped bars for QFT, Adder and GHZ overhead ratios per basis gate set
qft_ratios = [d / lb_qft_depth for d in qft_transp_depths]
adder_ratios = [d / lb_adder_depth for d in adder_transp_depths]
ghz_ratios = [d / lb_ghz_depth for d in ghz_transp_depths]

x = np.arange(len(basis_gates))
width = 0.25

fig, ax = plt.subplots(figsize=(9, 4.5))

colors = colormaps['gist_earth'](np.linspace(0.25, 0.9, 3))

rects_qft = ax.bar(x - width, qft_ratios, width, label='QFT', color=colors[0])
rects_adder = ax.bar(x, adder_ratios, width, label='CDKM adder', color=colors[1])
rects_ghz = ax.bar(x + width, ghz_ratios, width, label='GHZ', color=colors[2])

ax.set_xticks(x)
basis_gates = [[s.upper() for s in basis] for basis in basis_gates]
ax.set_xticklabels([', '.join(bg) for bg in basis_gates], rotation=45, ha='right')
ax.set_ylabel('Depth Overhead Ratio')
# ax.set_title(f'Depth Overhead Ratios for Different Basis Gate Sets ({num_qubits} Qubits)')
ax.axhline(1, color='k', linestyle='--', label='Lower Bound Depth')
ax.legend()

# annotate bar values
for rect in list(rects_qft) + list(rects_adder) + list(rects_ghz):
    h = rect.get_height()
    ax.annotate(f'{h:.2f}',
                xy=(rect.get_x() + rect.get_width() / 2, h),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontsize=8)

# adjust y-limits a bit to make annotations visible
all_ratios = qft_ratios + adder_ratios + ghz_ratios
ax.set_ylim(0, max(1.05, max(all_ratios) * 1.15))

plt.tight_layout()
plt.savefig("Figures/basis_gate_set_comparison.pdf", bbox_inches='tight')
plt.close()