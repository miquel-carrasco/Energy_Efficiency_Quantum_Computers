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


compressor , N_compressor = Component('Compressor', 7500, 'Cooling/Vacuum'), 1
chiller, N_chill = Component('Chiller', 2000, 'Cooling/Vacuum'), 1
emccd, N_emccd = Component('EMCCD', 96, 'Qubit Control'), 1
nanopositioner, N_nanopositioner = Component('Nanopositioner Controller', 10, 'Qubit Control'), 1
magnet, N_magnet = Component('Superconducting Magnet', 180, 'Qubit Control'), 1
rf_amp, N_rrf_amp = Component('RF Amplifier',72, 'Qubit Control'), 1
laser_system, N_laser_system = Component('Laser System', 825.7, 'Qubit Control'), 1
microwave_drive, N_mw_drive = Component('Microwave Drive', 669, 'Qubit Control'), 1
artiq_control, N_artiq = Component('ARTIQ Control System', 130, 'Qubit Control'), 1
server, N_server = Component('Server', 100, 'Classical Processing'), 1
control_desktop, N_control_desktop = Component('Control Desktop', 50, 'Classical Processing'), 1
HVAC, N_HVAC = Component('HVAC', 2000, 'Cooling/Vacuum'), 1
# Server, N_server = Component('Server', 130, 'Classical Processing'), 1
# classical_comp, N_classical_comp = Component('Classical Computer', 180, 'Classical Processing'), 1

components = [compressor, chiller, emccd, nanopositioner, magnet, rf_amp, laser_system, microwave_drive, artiq_control, server, control_desktop, HVAC]
Ni = [N_compressor, N_chill, N_emccd, N_nanopositioner, N_magnet, N_rrf_amp, N_laser_system, N_mw_drive, N_artiq, N_server, N_control_desktop, N_HVAC]
Ni = [int(x) for x in Ni]
P_per_component = [comp.P*Ni[i] for i, comp in enumerate(components)]

T = 24*3600


t_init = 100e-3 #Doppler cooling
t_2q = 10e-6 
t_shuttle = 100e-6
t_meas = 0.5e-3

computer = Computer(Nq = 100,
                    components = components,
                    N_comp = Ni,
                    graph_type="All-to-all",
                    t_init = t_init,
                    t_meas = t_meas,
                    T_gates=[t_2q, t_shuttle])

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
        ax1.text(4000, EE_list[-1]*2.4, rf"$N_{{samples}}={N_samples}$", rotation = -6, fontsize=10)

    ax1.set_xlabel(r"Final Circuit Depth, $D$")
    ax1.set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    ax1.set_xlim(0, max(D_values))
    ax1.set_yscale('log')
    ax1.set_ylim(2.5e-3, 2.5e-3)



    ax2 = ax1.twinx()
    ax2.plot(D_values, N_pi_list, alpha=0)
    ax2.set_ylabel(r"Number of Computations, $N_{\pi}$")
    ax2.set_yticks(np.linspace(0.2e6, 1.4e6, 7), labels=[r'$0.2\times10^{6}$', r'$0.4\times10^{6}$', r'$0.6\times10^{6}$', r'$0.8\times10^{6}$', r'$1.0\times10^{6}$', r'$1.2\times10^{6}$', r'$1.4\times10^{6}$'])
    ax2.set_yscale('log')
    # ax2.set_ylim(2.5e-3*computer.P*T, 1.7e1*computer.P*T)

    plt.savefig("Figures/Trapped_ions/trapped_ions_EE_vs_D.pdf", bbox_inches='tight')
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
    # ax1.set_ylim(2.5e-5, 2.7e-2)


    ax2 = ax1.twinx()
    ax2.plot(N_samples_values, N_pi_list, alpha=0)
    ax2.set_ylabel(r"Number of Computations, $N_{\pi}$")
    ax2.set_yticks(np.linspace(0.2e6, 1.4e6, 7), labels=[r'$0.2\times10^{6}$', r'$0.4\times10^{6}$', r'$0.6\times10^{6}$', r'$0.8\times10^{6}$', r'$1.0\times10^{6}$', r'$1.2\times10^{6}$', r'$1.4\times10^{6}$'])
    ax2.set_yscale('log')
    # ax2.set_ylim(2.5e-5*computer.P*T, 2.7e-2*computer.P*T)

    ax1.legend(fontsize=11, loc='upper right', fancybox=False, edgecolor='black')

    plt.savefig("Figures/Trapped_ions/trapped_ions_EE_vs_Nsamples.pdf", bbox_inches='tight')
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

    plt.savefig("Figures/Trapped_ions/trapped_ions_power_breakdown.pdf")
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
        axs[0].text(4000, EE_list[-1]*2.5, rf"$N_{{samples}}={N_samples}$", rotation = -6, fontsize=10)

    axs[0].set_xlabel(r"Final Circuit Depth, $D$")
    axs[0].set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    axs[0].set_xlim(0, max(D_values))
    axs[0].set_yscale('log')
    axs[0].set_ylim(5e-9, 2.5e-3)

    axs[0].text(1000, 1e-3, "(a)", fontsize = 14)

    ax2 = axs[0].twinx()
    ax2.plot(D_values, N_pi_list, alpha=0)
    ax2.set_yscale('log')
    ax2.set_ylim(5e-9*computer.P*T, 2.5e-3*computer.P*T)
    ax2.set_yticklabels([])


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

    axs[1].set_xlabel(r"Number of samples, $N_{\mathrm{samples}}$")
    # axs[1].set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    axs[1].set_xlim(0, 5010)
    axs[1].set_yscale('log')
    # axs[1].set_ylim(5e-9, 2.7e-2)

    axs[1].text(500, 1e-3, "(b)", fontsize = 14)


    ax2 = axs[1].twinx()
    ax2.plot(N_samples_values, N_pi_list, alpha=0)
    ax2.set_ylabel(r"Number of Computations, $N_{\pi}$")
    ax2.set_yticks(np.linspace(0.2e6, 1.4e6, 7), labels=[r'$0.2\times10^{6}$', r'$0.4\times10^{6}$', r'$0.6\times10^{6}$', r'$0.8\times10^{6}$', r'$1.0\times10^{6}$', r'$1.2\times10^{6}$', r'$1.4\times10^{6}$'])
    ax2.set_yscale('log')
    ax2.set_ylim(5e-9*computer.P*T, 2.5e-3*computer.P*T)

    axs[1].legend(fontsize=11, loc='upper right', fancybox=False, edgecolor='black')

    plt.subplots_adjust(wspace=0.1)

    plt.savefig("Figures/Trapped_ions/trapped_ions_D_and_Nsamples.pdf", bbox_inches='tight')
    plt.close()



if __name__ == "__main__":
    plot_D_and_Nsamples(computer)
    print(computer.P, computer.P*3600*24/1000000)
    plot_power_breakdown(computer)