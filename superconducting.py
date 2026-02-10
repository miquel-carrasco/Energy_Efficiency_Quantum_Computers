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
         "font.serif": ["Palatino"],
         "figure.autolayout": True
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
t_init_active = 5000e-9
t_1q = 25e-9
t_2q= 50e-9
t_meas = 1.6e-6

computer = Computer(Nq = 100,
                    components = components,
                    N_comp = Ni,
                    graph_type="2D",
                    t_init = t_init_active,
                    t_meas = t_meas,
                    T_gates=[t_1q, t_2q])



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
                print(f"N_sampl={N_samples}, D={D0}, N_pi={N_pi_list[-1]}, EE={EE_list[-1]}")
        ax1.plot(D_values, EE_list, color = colors[i])
        ax1.text(4000, EE_list[-1]*2.5, rf"$N_{{samples}}={N_samples}$", rotation = -6, fontsize=10)

    ax1.set_xlabel(r"Final Circuit Depth, $D$")
    ax1.set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    ax1.set_xlim(0, max(D_values))
    ax1.set_yscale('log')
    ax1.set_ylim(7e-6, 1.7e1)



    ax2 = ax1.twinx()
    ax2.plot(D_values, N_pi_list, alpha=0)
    ax2.set_ylabel(r"Number of Computations, $N_{\pi}$")
    ax2.set_yticks(np.linspace(0.2e6, 1.4e6, 7), labels=[r'$0.2\times10^{6}$', r'$0.4\times10^{6}$', r'$0.6\times10^{6}$', r'$0.8\times10^{6}$', r'$1.0\times10^{6}$', r'$1.2\times10^{6}$', r'$1.4\times10^{6}$'])
    ax2.set_yscale('log')
    ax2.set_ylim(7e-6*computer.P*T, 1.7e1*computer.P*T)

    plt.savefig("Figures/Superconducting/superconducting_EE_vs_D.pdf", bbox_inches='tight')
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
            # print(t,power_components[computer.type_groups_components[t][0]], power_components[computer.type_groups_components[t][0]]/computer.P*100)
        else:
            x = np.arange(offset, offset + len(computer.type_groups_components[t]) + width)
            bars = ax.bar(x[0], power_types[t], width=width, color = colors[i][0])
            ax.bar_label(bars, labels = ['Total'], padding=3, rotation=90)
            # print(t,power_types[t], power_types[t]/computer.P*100)
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

    plt.savefig("Figures/Superconducting/superconducting_power_breakdown.pdf")
    plt.close()


def plot_D_D0(computer: Computer):
    D0_values = np.arange(0, 2000, 10)
    eta_values = [0, 0.25, 0.5, 0.75, 1]
    colors = colormaps['summer'](np.linspace(0.2, 0.8, len(eta_values)))
    N_samples = 1000

    fig, main_ax = plt.subplots(figsize=(8,6))
    inset_ax = fig.add_axes([0.58, 0.62, 0.3, 0.25])

    for i, eta in enumerate(eta_values):
        D_values = []
        EE_values = []
        for D0 in D0_values:
            alg = Algorithm(D=D0, eta=eta)
            circuit = Circuit(algorithm=alg, avg_diameter=computer.avg_diameter)
            D_values.append(circuit.D)
            EE_values.append(computer.energy_efficiency(T = T, algorithm=alg, N_sampl=N_samples))

        main_ax.plot(D0_values, EE_values, label=f"$\\eta={eta}$", color=colors[i])
        inset_ax.plot(D0_values, D_values, label=f"$\\eta={eta}$", color=colors[i])

    main_ax.set_xlabel(r"Initial Circuit Depth, $D_0$")
    main_ax.set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")

    main_ax.set_yscale('log')
    main_ax.set_xlim(0, max(D0_values)*1.05)
    main_ax.set_ylim(1e-6, 1.2e-3)
    main_ax.text(700, 1.2e-4, r"$\eta = 0$", fontsize=12)
    main_ax.text(700, 2.6e-5, r"$\eta = 0.25$", fontsize=12)
    main_ax.text(700, 1.2e-5, r"$\eta = 0.5$", fontsize=12)
    main_ax.text(700, 6e-6, r"$\eta = 0.75$", fontsize=12)
    main_ax.text(700, 2e-6, r"$\eta = 1$", fontsize=12)

    inset_ax.set_xlabel(r"$D_{0}$", fontsize=13)
    inset_ax.set_ylabel(r"$D$", fontsize=13)

    plt.savefig("Figures/Superconducting/superconducting_compilation.pdf", bbox_inches='tight')
    plt.close()


def reset_time(computer):
    D_values = np.arange(0, 10100, 50)
    N_samples = 100

    computer.t_init = 0
    EE_zero = []
    for D in D_values:
        alg = Algorithm(D=D, eta=0)
        EE_zero.append(computer.energy_efficiency(T = T, algorithm=alg, N_sampl=N_samples))
    

    computer.t_init = t_init_passive
    EE_passive = []
    for D in D_values:
        alg = Algorithm(D=D, eta=0)
        EE_passive.append(computer.energy_efficiency(T = T, algorithm=alg, N_sampl=N_samples))
        if D == 100:
            print(computer.energy_efficiency(T = T, algorithm=alg, N_sampl=N_samples))

    
    computer.t_init = t_init_active
    EE_active = []
    for D in D_values:
        alg = Algorithm(D=D, eta=0)
        EE_active.append(computer.energy_efficiency(T = T, algorithm=alg, N_sampl=N_samples))
    
    fig, ax = plt.subplots()

    # ax.vlines(10*t_init_passive/(computer.T_clock), 0, 0.006, colors='k', linestyles='dashed')
    ax.text(6000, 0.0017, r'$D>> t_{\rm{reset}}^{\rm{act}} / t_{\rm{clock}}$', fontsize=12, rotation=-7, zorder = -1)

    ax.plot(D_values, EE_active, color='limegreen', label = r'$t_{\rm{reset}}^{\rm{act}}=5 \;\mu s$', zorder = 1)
    ax.plot(D_values, EE_passive, color='navy', label = r'$t_{\rm{reset}}^{\rm{pass}}=200 \;\mu s$', zorder = 3)
    ax.plot(D_values, EE_zero, color='k', linestyle=':', alpha = 0.8, label = r'$t_{\rm{reset}}=0$', zorder = 2)

    ax.legend(fontsize=12, fancybox = False, edgecolor='black', loc = "upper center")

    ax.set_ylim(0.0004, 0.7)
    ax.set_xlim(0, 10100)
    ax.set_yscale('log')
    ax.set_xlabel(r"Final Circuit Depth, $D$")
    ax.set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    plt.savefig("Figures/Superconducting/superconducting_reset_time.pdf", bbox_inches='tight')
    plt.close()

def plot_D_and_Nsamples(computer: Computer):

    fig, axs = plt.subplots(1, 2, figsize=(10,4), sharey=True)

    #FIG A)
    N_samples_values = [1, 10, 100, 1000, 10000]

    D_values = np.arange(0, 10010, 10)
    D_print = [1, 10, 100, 1000, 10000]

    colors = colormaps['Reds'](np.linspace(0.3, 0.8, len(N_samples_values)))

    for i, N_samples in enumerate(N_samples_values):
        EE_list = []
        N_pi_list = []
        for D0 in D_values:
            alg = Algorithm(D=D0, eta=0)
            EE_list.append(computer.energy_efficiency(T = T, algorithm=alg, N_sampl=N_samples))
            N_pi_list.append(computer.N(T = T, algorithm=alg, N_sampl=N_samples))
            if N_samples == 100 and D0 in D_print:
                print(f"N_sampl={N_samples}, D={D0}, N_pi={N_pi_list[-1]}, EE={EE_list[-1]}")
        axs[0].plot(D_values, EE_list, color = colors[i])
        axs[0].text(4000, EE_list[-1]*2.5, rf"$N_{{samples}}={N_samples}$", rotation = -6.5, fontsize=10)

    axs[0].set_xlabel(r"Final Circuit Depth, $D$")
    axs[0].set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    axs[0].set_xlim(0, max(D_values))
    axs[0].set_yscale('log')
    axs[0].set_ylim(3.5e-6, 2.5e1)

    axs[0].text(1000, 6e0, "(a)", fontsize = 14)

    ax2 = axs[0].twinx()
    ax2.plot(D_values, N_pi_list, alpha=0)
    ax2.set_yscale('log')
    ax2.set_ylim(3.5e-6*computer.P*T, 2.5e1*computer.P*T)
    ax2.set_yticklabels([])

    #QFT
    alg = Algorithm(D=1584, eta = 0.3434)
    circ = Circuit(algorithm=alg, avg_diameter = computer.avg_diameter)
    EE_qft = computer.energy_efficiency(T=T, algorithm=alg, N_sampl=100)
    axs[0].scatter(circ.D, EE_qft, marker='d', color = 'saddlebrown', edgecolors = 'k',linewidth =1, zorder = 10)


    #Adder
    alg = Algorithm(D=1962, eta = 0.3507)
    circ = Circuit(algorithm=alg, avg_diameter = computer.avg_diameter)
    EE_qft = computer.energy_efficiency(T=T, algorithm=alg, N_sampl=100)
    axs[0].scatter(circ.D, EE_qft, marker='d', color = 'darkorchid', edgecolors = 'k',linewidth =1, zorder = 10)

    #FIG B)
    N_samples_values = np.arange(0, 10010, 10)
    D_values = [10, 100, 1000, 10000]

    colors = colormaps['Purples'](np.linspace(0.3, 0.8, len(D_values)))

    for i, D0 in enumerate(D_values):
        EE_list = []
        N_pi_list = []
        for N_samples in N_samples_values:
            alg = Algorithm(D=D0, eta=0)
            EE_list.append(computer.energy_efficiency(T = T, algorithm=alg, N_sampl=N_samples))
            N_pi_list.append(computer.N(T = T, algorithm=alg, N_sampl=N_samples))
            if N_samples == 2500 and D0 in D_values:
                print(f"t_sample={T/(N_pi_list[-1]*N_samples)}, N_sampl={N_samples}, D={D0}, N_pi={N_pi_list[-1]}, EE={EE_list[-1]}")
        axs[1].plot(N_samples_values, EE_list, color = colors[i], label=f"$D={D0}$")
  
    # axs[1].text(1750, 3e-2, r"$D=10$", fontsize=10, rotation=-6)
    # axs[1].text(2200, 7e-3, r"$D=100$", fontsize=10, rotation=-6)
    axs[1].annotate(r"$D=10$", xy=(2300, 3.3e-3), xytext=(1800, 3e-2), arrowprops=dict(arrowstyle="->"), fontsize=10, rotation=-6)
    axs[1].annotate(r"$D=100$", xy=(3000, 1.4e-3), xytext=(2400, 7e-3), arrowprops=dict(arrowstyle="->"), fontsize=10, rotation=-6)
    axs[1].text(2000, 4.5e-4, r"$D=1000$", fontsize=10, rotation=-6)
    axs[1].text(2000, 5e-5, r"$D=10000$", fontsize=10, rotation=-6)

    axs[1].set_xlabel(r"Number of samples, $N_{\mathrm{samples}}$")
    # axs[1].set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    axs[1].set_xlim(0, 5010)
    axs[1].set_yscale('log')
    # axs[1].set_ylim(2.5e-5, 2.7e-2)

    axs[1].text(500, 6e0, "(b)", fontsize = 14)


    ax2 = axs[1].twinx()
    ax2.plot(N_samples_values, N_pi_list, alpha=0)
    ax2.set_ylabel(r"Number of Computations, $N_{\pi}$")
    ax2.set_yticks(np.linspace(0.2e6, 1.4e6, 7), labels=[r'$0.2\times10^{6}$', r'$0.4\times10^{6}$', r'$0.6\times10^{6}$', r'$0.8\times10^{6}$', r'$1.0\times10^{6}$', r'$1.2\times10^{6}$', r'$1.4\times10^{6}$'])
    ax2.set_yscale('log')
    ax2.set_ylim(3.5e-6*computer.P*T, 2.5e1*computer.P*T)

    # axs[1].legend(fontsize=11, loc='upper right', fancybox=False, edgecolor='black')

    plt.subplots_adjust(wspace=0.1)

    plt.savefig("Figures/Superconducting/superconducting_D_and_Nsamples.pdf", bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    # plot_EE_vs_D(computer)
    # plot_D_D0(computer)
    # reset_time(computer)
    # plot_power_breakdown(computer)
    # print(computer.P, computer.P*3600*24/1000000)
    plot_D_and_Nsamples(computer)