from qcenergy.components import Component
from qcenergy.platforms import Computer
from qcenergy.algorithms import Algorithm, Circuit

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib import colormaps
import math

params = {'axes.labelsize': 14,
         'axes.titlesize': 15,
         'axes.linewidth': 1.5,
         'lines.markeredgecolor': "black",
     	'lines.linewidth': 1.5,
         'xtick.labelsize': 11,
         'ytick.labelsize': 11,
         "text.usetex": True,
         "font.family": "serif",
         "font.serif": ["Palatino"]
         }
plt.rcParams.update(params)

Nq = 100
N_lines = math.ceil(Nq/5)

pulse_tube , N_pt = Component('Pulse Tube', 8000, 'Cooling'), 1
dilution_unit, N_du = Component('Dilution Unit', 1200, 'Cooling'), 1
chiller, N_chill = Component('Chiller', 4000, 'Cooling'), 1
control_and_redout, N_readout = Component('Control and Readout', 110, 'Qubit Control'), N_lines
rf_source, N_rf = Component('RF Source', 70, 'Qubit Control'), N_lines
lna, N_lna = Component('LNA', 1, 'Qubit Control'), 2*N_lines
pba, N_pba = Component('PBA', 100, 'Qubit Control'), N_lines
server, N_server = Component('Server', 800, 'Classical Processing'), 1

components = [pulse_tube, dilution_unit, chiller, control_and_redout, rf_source, lna, pba, server]
Ni = [N_pt, N_du, N_chill, N_readout, N_rf, N_lna, N_pba, N_server]
P_per_component = [comp.P*Ni[i] for i, comp in enumerate(components)]

T = 24*3600

t_init_passive = 200e-6
t_init_active = 500e-9 + 5000e-9
t_1q = 1e-7
t_2q= 50e-9
t_meas = 1.6e-6

computer = Computer(Nq = 100,
                    components = components,
                    N_comp = Ni,
                    graph_type="2D",
                    t_init = t_init_passive,
                    t_meas = t_meas,
                    T_gates=[t_1q, t_2q])


def plot_multiple_graphs(computer):
    
    fig, ax = plt.subplots(1, 4, figsize=(15,5), sharey = True)

    D0_values = np.arange(10, 1070, 10)
    etas = [0, 0.25, 0.5, 0.75, 1.0]

    graphs = ["Linear", "2D", "3D", "Expander"]

    colors = colormaps['summer'].reversed()(np.linspace(0.2, 0.8, len(etas)))

    for i, graph in enumerate(graphs):
        computer.graph_type = graph
        for j, eta in enumerate(etas):
            Npi_list = []
            for D0 in D0_values:
                alg = Algorithm(D=D0, eta=eta)
                Npi_list.append(computer.N(T = T, algorithm=alg, N_sampl=1000))
            ax[i].plot(D0_values, Npi_list, label=rf'$\eta = {eta}$', color=colors[j])
        ax[i].set_title(f'{graph} Graph')
        # ax[i].set_xlabel(r'Precompiled circuit depth, $D_{0}$')
        ax[i].set_ylim(0, 4.7e5)
        ax[i].set_xlim(0, 1070)
    fig.supxlabel(r'Precompiled Circuit Depth, $D_{0}$',fontsize = 18)
    ax[0].set_ylabel(r'Number of computations in 24 hours, $N^{\pi}$',fontsize = 18)
    ax[3].legend(fontsize=11, loc='lower left', fancybox=False, edgecolor='black')
    fig.subplots_adjust(wspace=0.05)
    fig.savefig("Figures/connectivity_graphs.pdf", bbox_inches='tight')

def plot_D_vs_D0(computer):
    
    D0_values = np.arange(10, 1010, 10)
    etas = [0, 0.25, 0.5, 0.75, 1.0]

    graphs = ["Linear", "2D", "3D", "Expander"]
    colormaps_list = ["Purples", "Blues", "Greens", "Reds"]

    colors = [colormaps[colormaps_list[i]].reversed()(np.linspace(0.2, 0.8, len(etas))) for i in range(len(graphs))]

    fig, ax = plt.subplots()

    for i, graph in enumerate(graphs):
        computer.graph_type = graph
        avg_diameter = computer.avg_diameter
        for j, eta in enumerate(etas):
            D_list = []
            for D0 in D0_values:
                alg = Algorithm(D=D0, eta=eta)
                circ = Circuit(algorithm=alg, avg_diameter=avg_diameter)
                D_list.append(circ.D)
            ax.plot(D0_values, D_list, label=rf'$\eta = {eta}$, Graph: {graph}', color=colors[i][j])
    # ax.set_xlabel(r'Precompiled circuit depth, $D_{0}$')
    fig.supxlabel(r'Precompiled Circuit Depth, $D_{0}$')
    ax.set_ylabel(r'Final Circuit Depth, $D$')
    ax.set_xlim(0, 1010)
    plt.show()



plot_multiple_graphs(computer)