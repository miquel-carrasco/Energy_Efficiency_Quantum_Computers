from qcenergy.components import Component
from qcenergy.platforms import Computer, AtomBasedComputer

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

Nq = 400

trap_laser, N_trap_laser = Component('Trap Laser', 1500, 'Qubit Control'), 1
rydberg_laser, N_rydberg_laser = Component('Rydberg Laser', 1900, 'Qubit Control'), 1
other_lasers, N_other_lasers = Component('Other Lasers', 900*2+150*7, 'Qubit Control'), 1
magnetic_field, N_magnetic_field = Component('Magnetic Field Generation', 1050, 'Qubit Control'), 1
camera, N_camera = Component('Camera', 155, 'Qubit Control'), 1
vacuum_chamber, N_vacuum = Component('Vacuum Chamber', 100, 'Environmental Conditions'), 1
classical_comp, N_classical_comp = Component('Classical Computers', 150, 'Classical Processing'), 1
hvac, N_hvac = Component('HVAC', 7500, 'Environmental Conditions'), 1
other_electronics, N_other_electronics = Component('Other Electronics', 2000, 'Qubit Control'), 1
small_chiller, N_small_chiller = Component('Laser Chillers (small)', 600, 'Qubit Control'), 5
large_chiller, N_large_chiller = Component('Laser Chillers (large)', 1000, 'Qubit Control'), 2


components = [trap_laser, rydberg_laser, other_lasers, magnetic_field, camera, vacuum_chamber, classical_comp, hvac, other_electronics, small_chiller, large_chiller]

Ni = [N_trap_laser, N_rydberg_laser, N_other_lasers, N_magnetic_field, N_camera, N_vacuum, N_classical_comp, N_hvac, N_other_electronics, N_small_chiller, N_large_chiller]


T = 24*3600

t_reload = 500e-3
t_reload_freq = 2400
t_reset = 10e-3
t_2q= 150e-9
t_1q = 10e-6
t_reconfig = 500e-6
t_transport = 500e-6
t_meas = 10e-3

def plot_D_and_Nsamples():
    computer = AtomBasedComputer(Nq=Nq, components=components, N_comp=Ni, t_reset=t_reset, t_meas=t_meas, t_clock=t_reconfig, t_transport=t_transport,
                                 t_reload=t_reload, t_reload_freq=t_reload_freq, N_gatezones=20, independent_gates=False, periodic_reload=True)
    fig, axs = plt.subplots(1, 2, figsize=(11,4.5), sharey=True)
    alpha = 0
    beta = 0.25

    #FIG A)
    N_samples_values = [1, 10, 100, 1000, 10000]

    D_values = np.arange(0, 10010, 10)
    D_print = [10, 100, 1000, 10000]

    colors = colormaps['Reds'](np.linspace(0.3, 0.8, len(N_samples_values)))
    for i, N_samples in enumerate(N_samples_values):
        EE_list = []
        N_pi_list = []
        for D0 in D_values:
            EE_list.append(computer.energy_efficiency(D0, alpha, beta, N_gates_layer=1, N_samples=N_samples))
            N_pi_list.append(computer.N_pi(t=T, D0=D0, alpha=alpha, beta=beta, N_gates_layer=1, N_samples=N_samples))
            if N_samples == 1 and D0 in D_print:
                print(f"N_sampl={N_samples}, D={D0}, computing time={computer.t_comp(D0=D0, alpha=alpha, beta=beta, N_gates_layer=1, N_samples=N_samples)}")
        axs[0].plot(D_values, EE_list, color = colors[i])
        axs[0].text(4000, EE_list[-1]*2.3, rf"$N_{{samples}}={N_samples}$", rotation = -9, fontsize=10)

    axs[0].set_xlabel(r"Post-compilation Circuit Depth, $D$")
    axs[0].set_ylabel(r"Energy Efficiency (computations/J)")
    axs[0].set_xlim(0, max(D_values))
    axs[0].set_yscale('log')
    axs[0].set_ylim(1.5e-10, 3e-3)

    axs[0].text(1000, 3e-4, "(a)", fontsize = 14)

    ax2 = axs[0].twinx()
    ax2.plot(D_values, N_pi_list, alpha=0)
    ax2.set_yscale('log')
    ax2.set_ylim(1.5e-10*computer.P*T, 3e-3*computer.P*T)
    ax2.set_yticklabels([])


    #FIG B)
    N_samples_values = np.arange(0, 10010, 10)
    D_values = [10, 100, 1000, 10000]

    colors = colormaps['Purples'](np.linspace(0.3, 0.8, len(D_values)))

    for i, D0 in enumerate(D_values):
        EE_list = []
        N_pi_list = []
        for N_samples in N_samples_values:
            EE_list.append(computer.energy_efficiency(D0, alpha, beta, N_gates_layer=1, N_samples=N_samples))
            N_pi_list.append(computer.N_pi(t=T, D0=D0, alpha=alpha, beta=beta, N_gates_layer=1, N_samples=N_samples))
            # if N_samples == 2500 and D0 in D_values:
                # print(f"t_sample={T/(N_pi_list[-1]*N_samples)}, N_sampl={N_samples}, D={D0}, N_pi={N_pi_list[-1]}, EE={EE_list[-1]}")
        axs[1].plot(N_samples_values, EE_list, color = colors[i], label=f"$D={D0}$")
        axs[1].text(2100, EE_list[-1]*5, rf"$D={D0}$", rotation = -6, fontsize=10)

    axs[1].set_xlabel(r"Number of samples, $N_{\mathrm{samples}}$")
    # axs[1].set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    axs[1].set_xlim(0, 5010)
    axs[1].set_yscale('log')
    # axs[1].set_ylim(2.5e-5, 2.7e-2)

    axs[1].text(500, 3e-4, "(b)", fontsize = 14)


    ax2 = axs[1].twinx()
    ax2.plot(N_samples_values, N_pi_list, alpha=0)
    ax2.set_ylabel(r"Computations in 24 hours")
    ax2.set_yticks(np.linspace(0.2e6, 1.4e6, 7), labels=[r'$0.2\times10^{6}$', r'$0.4\times10^{6}$', r'$0.6\times10^{6}$', r'$0.8\times10^{6}$', r'$1.0\times10^{6}$', r'$1.2\times10^{6}$', r'$1.4\times10^{6}$'])
    ax2.set_yscale('log')
    ax2.set_ylim(1.5e-10*computer.P*T, 3e-3*computer.P*T)

    # axs[1].legend(fontsize=11, loc='upper right', fancybox=False, edgecolor='black')

    plt.subplots_adjust(wspace=0.1)

    plt.savefig("Figures/Neutral_atoms/neutral_atoms_D_and_Nsamples.pdf", bbox_inches='tight')
    plt.close()


def plot_power_breakdown():
    computer = AtomBasedComputer(Nq=Nq, components=components, N_comp=Ni, t_reset=t_reset, t_meas=t_meas, t_clock=t_reconfig, t_transport=t_transport,
                                 t_reload=t_reload, t_reload_freq=t_reload_freq, N_gatezones=1, independent_gates=False, periodic_reload=False)
    print("Power: ", computer.P, " W")
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

    plt.savefig("Figures/Neutral_atoms/neutral_atoms_power_breakdown.pdf")
    plt.close()


def plot_periodic_vs_continuous_reload():
    computer_periodic = AtomBasedComputer(Nq=Nq, components=components, N_comp=Ni, t_reset=t_reset, t_meas=t_meas, t_clock=t_reconfig, t_transport=t_transport,
                                            t_reload=t_reload, t_reload_freq=t_reload_freq, N_gatezones=20, independent_gates=True, periodic_reload=True)

    transport_laser, N_transport_laser = Component('Transport Laser', 350, 'Qubit Control'), 1
    chiller_pump, N_chiller = Component('Chiller Pump', 1500, 'Environmental Conditions'), 1
    ion_vacuum_pump, N_ion_vacuum_pump = Component('Ion Vacuum Pump', 600, 'Environmental Conditions'), 1
    getter_vacuum_pump, N_getter_vacuum_pump = Component('Getter Vacuum Pump', 50, 'Environmental Conditions'), 2


    components_cont_reload = [trap_laser, rydberg_laser, other_lasers, magnetic_field, camera, vacuum_chamber, classical_comp, hvac, other_electronics, small_chiller, large_chiller, transport_laser, chiller_pump, ion_vacuum_pump, getter_vacuum_pump]

    Ni_cont_reload = [N_trap_laser, N_rydberg_laser, N_other_lasers, N_magnetic_field, N_camera, N_vacuum, N_classical_comp, N_hvac, N_other_electronics, N_small_chiller, N_large_chiller, N_transport_laser, N_chiller, N_ion_vacuum_pump, N_getter_vacuum_pump]

    computer_continuous = AtomBasedComputer(Nq=Nq, components=components_cont_reload, N_comp=Ni_cont_reload, t_reset=0, t_meas=t_meas, t_clock=t_reconfig,
                                            t_transport=t_transport, N_gatezones=20, independent_gates=True, periodic_reload=False)

    print("Power periodic reload: ", computer_periodic.P, " W")
    print("Power continuous reload: ", computer_continuous.P, " W")
    print("P_periodic/P_continuous: ", computer_periodic.P/computer_continuous.P)
    N_samples_values = [1,10]
    print_values = [0, 10, 100, 1000, 10000]
    alpha = 0
    beta = 0.25
    N_gates_per_slice = 1
    D0_values = np.arange(0, 10011, 1)
    D0_values_1 = D0_values[D0_values<=t_reload_freq]
    D0_values_2 = D0_values[D0_values>t_reload_freq]

    fig, ax = plt.subplots(figsize=(7,5))

    for i, N_samples in enumerate(N_samples_values):
        EE_periodic_1 = []
        EE_periodic_2 = []
        EE_continuous = []
        for D in D0_values:
            if D in print_values:
                print("t_continuous/t_periodic for D =",D, " is ", computer_continuous.t_comp(D0=D, alpha=alpha, beta=beta, N_gates_layer=N_gates_per_slice, N_samples=N_samples)/
                      computer_periodic.t_comp(D0=D, alpha=alpha, beta=beta, N_gates_layer=N_gates_per_slice, N_samples=N_samples))
                print("EE_periodic/EE_continuous for D =",D, " is ", computer_periodic.energy_efficiency(D, alpha, beta, N_gates_layer=N_gates_per_slice, N_samples=N_samples)/
                        computer_continuous.energy_efficiency(D, alpha, beta, N_gates_layer=N_gates_per_slice, N_samples=N_samples))
            if D<=t_reload_freq:
                EE_periodic_1.append(computer_periodic.energy_efficiency(D, alpha, beta, N_gates_layer=N_gates_per_slice, N_samples=N_samples))
            else: 
                EE_periodic_2.append(computer_periodic.energy_efficiency(D, alpha, beta, N_gates_layer=N_gates_per_slice, N_samples=N_samples))
            EE_continuous.append(computer_continuous.energy_efficiency(D, alpha, beta, N_gates_layer=N_gates_per_slice, N_samples=N_samples))
        if i == 0:
            ax.plot(D0_values_1, EE_periodic_1, label='Periodic Reload ($D \leq 2400$)', color = 'royalblue')
            ax.plot(D0_values_2, EE_periodic_2, label='Periodic Reload ($D > 2400$)', color = 'royalblue', linestyle='dashed')
            ax.plot(D0_values, EE_continuous, label='Continuous Reload', color = 'yellowgreen')
        else:
            ax.plot(D0_values_1, EE_periodic_1, label=None, color = 'royalblue')
            ax.plot(D0_values_2, EE_periodic_2, label=None, color = 'royalblue', linestyle='dashed')
            ax.plot(D0_values, EE_continuous, label=None, color = 'yellowgreen')
        ax.text(5550/2, EE_continuous[-1]*4, rf"$N_{{\rm{{samples}}}}={N_samples}$", rotation = -11, fontsize=10, horizontalalignment='center')


    ax.set_xlabel(r"Post-compilation Circuit Depth, $D$")
    ax.set_ylabel(r"Energy Efficiency (computations/J)")
    ax.set_yscale('log')
    # ax.set_xscale('log')
    ax.set_xlim(1, 5550)
    # ax.set_ylim(5.5e-6, 3.5e-3)
    # ax.set_title(r"Extra laser trap (1.5 kW)", fontsize=14)
    ax.legend(fontsize=11, fancybox=False, edgecolor='black')
    fig.savefig("Figures/Neutral_atoms/neutral_atoms_periodic_vs_continuous_reload.pdf", bbox_inches='tight')




if __name__ == "__main__":
    # plot_power_breakdown()
    plot_D_and_Nsamples()
    # plot_periodic_vs_continuous_reload()