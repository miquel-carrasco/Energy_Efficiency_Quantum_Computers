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

n = 10

Nq = n**2


pulse_tube , N_pt = Component('Pulse Tube', 8000, 'Cooling'), 1
dilution_unit, N_du = Component('Dilution Unit', 1000, 'Cooling'), 1
chiller, N_chill = Component('Chiller', 4000, 'Cooling'), 1
DC_control, N_DC_control = Component('DC Control', 0.5, 'Qubit Control'), 2*n**2
BB_control, N_BB_control = Component('BB Control', 7.5, 'Qubit Control'), 2*n**2
MW_control, N_MW_control = Component('MW Control', 24, 'Qubit Control'), n**2
redout_lockin, N_redout_lockin = Component('Lock-in Amplifier', 48, 'Qubit Control'), 2*n*(n-1)
lna, N_lna = Component('LNA', 0.11, 'Qubit Control'), 2*n*(n-1)
rt_amplifier, N_rt_amplifier = Component('RT Amplifier', 0.5, 'Qubit Control'), 2*n*(n-1)
classical_comp, N_classical_comp = Component('Classical Computers', 150, 'Classical Processing'), 2

components = [pulse_tube, dilution_unit, DC_control, BB_control, MW_control, redout_lockin, lna, rt_amplifier, classical_comp, chiller]
Ni = [N_pt, N_du, N_DC_control, N_BB_control, N_MW_control, N_redout_lockin, N_lna, N_rt_amplifier, N_classical_comp, N_chill]
Ni = [int(x) for x in Ni]
P_per_component = [comp.P*Ni[i] for i, comp in enumerate(components)]

T = 24*3600

t_init_best = 0.1e-3
t_init_worst = 1e-3
t_g_best = 10e-9
t_g_worst = 100e-9
t_meas = 10e-6

computer = Computer(Nq = 100,
                    components = components,
                    N_comp = Ni,
                    graph_type="2D",
                    t_init = t_init_best,
                    t_meas = t_meas,
                    T_gates=[t_g_best])

print(computer.P, computer.P*3600*24/1000000)

def plot_EE_vs_D(computer: Computer):

    N_samples_values = [1, 10, 100, 1000, 10000]

    D_values = np.arange(0, 10010, 10)
    D_print = [1, 10, 100, 1000, 10000]

    fig, ax1 = plt.subplots()
    colors = colormaps['Reds'](np.linspace(0.3, 0.8, len(N_samples_values)))

    for i, N_samples in enumerate(N_samples_values):
        EE_list = []
        N_pi_list = []
        for D0 in D_values:
            alg = Algorithm(D=D0, eta=0)
            EE_list.append(computer.energy_efficiency(T = T, algorithm=alg, N_sampl=N_samples))
            N_pi_list.append(computer.N(T = T, algorithm=alg, N_sampl=N_samples))
            if N_samples == 100 and D0 in D_print:
                print(f"t_sample={T/(N_pi_list[-1]*N_samples)}, N_sampl={N_samples}, D={D0}, N_pi={N_pi_list[-1]}, EE={EE_list[-1]}")
        ax1.plot(D_values, EE_list, color = colors[i])
        ax1.text(4000, EE_list[-1]*1.9, rf"$N_{{samples}}={N_samples}$", rotation = -3, fontsize=10)

    ax1.set_xlabel(r"Total Circuit Depth, $D$")
    ax1.set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    ax1.set_xlim(0, max(D_values))
    ax1.set_yscale('log')
    ax1.set_ylim(4e-6, 1.7e0)



    ax2 = ax1.twinx()
    ax2.plot(D_values, N_pi_list, alpha=0)
    ax2.set_ylabel(r"Number of Computations, $N_{\pi}$")
    ax2.set_yticks(np.linspace(0.2e6, 1.4e6, 7), labels=[r'$0.2\times10^{6}$', r'$0.4\times10^{6}$', r'$0.6\times10^{6}$', r'$0.8\times10^{6}$', r'$1.0\times10^{6}$', r'$1.2\times10^{6}$', r'$1.4\times10^{6}$'])
    ax2.set_yscale('log')
    ax2.set_ylim(4e-6*computer.P*T, 1.7e1*computer.P*T)

    plt.savefig("Figures/Spin_qubits/spin_qubits_EE_vs_D.pdf", bbox_inches='tight')
    plt.close()


def plot_EE_vs_Nsamples(computer: Computer):

    N_samples_values = np.arange(0, 10010, 10)
    D_values = [100, 1000, 10000]

    fig, ax1 = plt.subplots()
    colors = colormaps['Reds'](np.linspace(0.3, 0.8, len(D_values)))

    for i, D0 in enumerate(D_values):
        EE_list = []
        N_pi_list = []
        for N_samples in N_samples_values:
            alg = Algorithm(D=D0, eta=0)
            EE_list.append(computer.energy_efficiency(T = T, algorithm=alg, N_sampl=N_samples))
            N_pi_list.append(computer.N(T = T, algorithm=alg, N_sampl=N_samples))
            if N_samples == 2500 and D0 in D_values:
                print(f"t_sample={T/(N_pi_list[-1]*N_samples)}, N_sampl={N_samples}, D={D0}, N_pi={N_pi_list[-1]}, EE={EE_list[-1]}")
        ax1.plot(N_samples_values, EE_list, color = colors[i], label=f"$D={D0}$")

    ax1.set_xlabel(r"Number of samples, $N_{\mathrm{samples}}$")
    ax1.set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    ax1.set_xlim(0, 5010)
    ax1.set_yscale('log')
    ax1.set_ylim(2.5e-5, 2.7e-2)


    ax2 = ax1.twinx()
    ax2.plot(N_samples_values, N_pi_list, alpha=0)
    ax2.set_ylabel(r"Number of Computations, $N_{\pi}$")
    ax2.set_yticks(np.linspace(0.2e6, 1.4e6, 7), labels=[r'$0.2\times10^{6}$', r'$0.4\times10^{6}$', r'$0.6\times10^{6}$', r'$0.8\times10^{6}$', r'$1.0\times10^{6}$', r'$1.2\times10^{6}$', r'$1.4\times10^{6}$'])
    ax2.set_yscale('log')
    ax2.set_ylim(2.5e-5*computer.P*T, 2.7e-2*computer.P*T)

    ax1.legend(fontsize=11, loc='upper right', fancybox=False, edgecolor='black')

    plt.savefig("Figures/Spin_qubits/spin_qubits_EE_vs_Nsamples.pdf", bbox_inches='tight')
    plt.close()

def plot_power_breakdown(computer: Computer):
    power_types = computer.power_per_types()
    power_components = computer.power_per_component()

    width = 1

    fig, ax = plt.subplots()
    offset = 0
    ticks = []
    maps = ['Purples', 'Blues', 'Greens', 'Oranges', 'Reds']
    colors = [colormaps[maps[i]](np.linspace(0.3, 0.8, len(computer.type_groups_components[t])+1)[::-1]) for i, t in enumerate(power_types.keys())]
    for i, t in enumerate(power_types):
        if len(computer.type_groups_components[t]) == 1:
            x = np.array([offset])
            bars = ax.bar(x[0], power_components[computer.type_groups_components[t][0]], width=width, label = computer.type_groups_components[t][0], color=colors[i][0])
            ax.bar_label(bars, padding=3, labels= [computer.type_groups_components[t][0]], rotation=90)
            print(t,power_components[computer.type_groups_components[t][0]], power_components[computer.type_groups_components[t][0]]/computer.P*100)
        else:
            x = np.arange(offset, offset + len(computer.type_groups_components[t]) + width)
            bars = ax.bar(x[0], power_types[t], width=width, color = colors[i][0])
            ax.bar_label(bars, labels = ['Total'], padding=3, rotation=90)
            print(t,power_types[t], power_types[t]/computer.P*100)
            j = 0
            for name in power_components.keys():
                if name in computer.type_groups_components[t]:
                    bars = ax.bar(x[j+1], power_components[name], width=width, color=colors[i][j+1])
                    ax.bar_label(bars, labels = [name], padding=3, rotation=90)
                    j += 1
        offset = x[-1] + width + 2
        ticks.append(x[0] + (x[-1]-x[0])/2)

    ax.set_xticks(ticks)
    ax.set_xticklabels(list(power_types.keys()))
    ax.set_ylim(0, max(power_types.values())*1.2)
    ax.set_ylabel(r"Power consumption ($W$)")

    ax2 = ax.twinx()
    ax2.set_ylim(0, max(power_types.values())/computer.P*100*1.2)
    ax2.set_ylabel(r"Relative consumption (\%)")

    plt.savefig("Figures/Spin_qubits/spin_qubits_power_breakdown.pdf")
    plt.close()


def plot_power_breakdown_multiplexing(computer: Computer):
    Ni = [N_pt, N_du, n, n, n, n-1, n-1, n-1, N_classical_comp, N_chill]
    Ni = [int(x) for x in Ni]
    computer.N_comp = Ni
    computer.list_components = computer.assemble()

    power_types = computer.power_per_types()
    power_components = computer.power_per_component()

    width = 1

    fig, ax = plt.subplots()
    offset = 0
    ticks = []
    maps = ['Purples', 'Blues', 'Greens', 'Oranges', 'Reds']
    colors = [colormaps[maps[i]](np.linspace(0.3, 0.8, len(computer.type_groups_components[t])+1)[::-1]) for i, t in enumerate(power_types.keys())]
    for i, t in enumerate(power_types):
        if len(computer.type_groups_components[t]) == 1:
            x = np.array([offset])
            bars = ax.bar(x[0], power_components[computer.type_groups_components[t][0]], width=width, label = computer.type_groups_components[t][0], color=colors[i][0])
            ax.bar_label(bars, padding=3, labels= [computer.type_groups_components[t][0]], rotation=90)
            print(t,power_components[computer.type_groups_components[t][0]], power_components[computer.type_groups_components[t][0]]/computer.P*100)
        else:
            x = np.arange(offset, offset + len(computer.type_groups_components[t]) + width)
            bars = ax.bar(x[0], power_types[t], width=width, color = colors[i][0])
            ax.bar_label(bars, labels = ['Total'], padding=3, rotation=90)
            print(t,power_types[t], power_types[t]/computer.P*100)
            j = 0
            for name in power_components.keys():
                if name in computer.type_groups_components[t]:
                    bars = ax.bar(x[j+1], power_components[name], width=width, color=colors[i][j+1])
                    ax.bar_label(bars, labels = [name], padding=3, rotation=90)
                    j += 1
        offset = x[-1] + width + 2
        ticks.append(x[0] + (x[-1]-x[0])/2)

    ax.set_xticks(ticks)
    ax.set_xticklabels(list(power_types.keys()))
    ax.set_ylim(0, max(power_types.values())*1.2)
    ax.set_ylabel(r"Power consumption ($W$)")

    ax2 = ax.twinx()
    ax2.set_ylim(0, max(power_types.values())/computer.P*100*1.2)
    ax2.set_ylabel(r"Relative consumption (\%)")

    plt.savefig("Figures/Spin_qubits/spin_qubits_power_breakdown_multiplexing.pdf")
    plt.close()
    print(computer.P, computer.P*3600*24/1000000)


def planar_vs_linear(computer):
    D_values = np.arange(0, 2000, 5)
    EE_planar = []
    EE_planar_multiplex = []
    EE_linear = []

    fig, ax = plt.subplots()
    colors = colormaps['summer'].reversed()(np.linspace(0.4, 0.8, 2))

    computer.graph_type = "2D"

    for D0 in D_values:
        alg = Algorithm(D=D0, eta=0.9)
        EE_planar.append(computer.energy_efficiency(T = T, algorithm=alg, N_sampl=100))


    Ni = [N_pt, N_du, n, n, n, n-1, n-1, n-1, N_classical_comp, N_chill]
    Ni = [int(x) for x in Ni]
    computer.N_comp = Ni
    computer.list_components = computer.assemble()
    for D0 in D_values:
        alg = Algorithm(D=D0, eta=0.9)
        EE_planar_multiplex.append(computer.energy_efficiency(T = T, algorithm=alg, N_sampl=100))

    computer.graph_type = "Linear"
    Ni = [N_pt, N_du, N_DC_control, N_BB_control, N_MW_control, n-1, n-1, n-1, N_classical_comp, N_chill]
    Ni = [int(x) for x in Ni]
    computer.N_comp = Ni
    computer.list_components = computer.assemble()
    for D0 in D_values:
        alg = Algorithm(D=D0, eta=0.9)
        EE_linear.append(computer.energy_efficiency(T = T, algorithm=alg, N_sampl=100))

    print(computer.P, computer.P*3600*24/1000000)

    ax.plot(D_values, EE_planar, label='2D', color = colors[1])
    ax.plot(D_values, EE_planar_multiplex, label='2D Multiplexed', color = colors[1], linestyle='--')
    ax.plot(D_values, EE_linear, label='Linear', color = colors[0])
    ax.set_xlabel(r"Algorithm Depth, $D_{0}$")
    ax.set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    ax.set_xlim(0, 1000)
    ax.set_ylim(8e-6, 1.7e-2)
    ax.set_yscale('log')
    ax.legend(fontsize=11, loc='upper right', fancybox=False, edgecolor='black')
    fig.savefig("Figures/Spin_qubits/spin_qubits_planar_vs_linear.pdf", bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    print(computer.P, computer.P*3600*24/1000000)
    # plot_EE_vs_D(computer)
    # plot_power_breakdown(computer)
    # plot_EE_vs_Nsamples(computer)
    planar_vs_linear(computer)
    # plot_power_breakdown_multiplexing(computer)