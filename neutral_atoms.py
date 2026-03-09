from qcenergy.components import Component
from qcenergy.platforms import Computer, AtomBasedComputer
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

small_chiller, N_pt = Component('Small Chiller', 600, 'Cooling/Vacuum'), 4
dilution_unit, N_du = Component('Large Chiller', 1000, 'Cooling/Vacuum'), 4


hvac, N_hvac = Component('HVAC', 7500, 'Cooling/Vacuum'), 1
vacuum_chamber, N_vacuum = Component('Vacuum Chamber', 100, 'Cooling/Vacuum'), 1
trap_laser, N_trap_laser = Component('Trap Laser', 1500, 'Qubit Control'), 1
amp_rydberg_1013, N_amp_rydberg_1013 = Component('Rydberg 1013nm Amplifier', 1000, 'Qubit Control'), 1
pump_rydberg_420, N_pump_rydberg_420 = Component('Rydberg 420nm Pump Laser', 900, 'Qubit Control'), 1
extra_lasers, N_extra_lasers = Component('Extra Lasers', 2550, 'Qubit Control'), 1
camera, N_camera = Component('Camera', 155, 'Qubit Control'), 1
other_electronics, N_other_electronics = Component('Other Electronics', 2000, 'Qubit Control'), 1

classical_comp, N_classical_comp = Component('Classical Computers', 250, 'Classical Processing'), 8

components_cryo = [small_chiller, dilution_unit, hvac, vacuum_chamber, trap_laser, amp_rydberg_1013, 
              pump_rydberg_420, extra_lasers, camera, other_electronics, classical_comp]
components_no_cryo = [hvac, vacuum_chamber, trap_laser, amp_rydberg_1013, 
              pump_rydberg_420, extra_lasers, camera, other_electronics, classical_comp]
Ni = [N_pt, N_du, N_hvac, N_vacuum, N_trap_laser, N_amp_rydberg_1013, N_pump_rydberg_420, 
      N_extra_lasers, N_camera, N_other_electronics, N_classical_comp]
Ni_no_cryo = [N_hvac, N_vacuum, N_trap_laser, N_amp_rydberg_1013, N_pump_rydberg_420, 
      N_extra_lasers, N_camera, N_other_electronics, N_classical_comp]

T = 24*3600

t_reload = 500e-3
t_reload_freq = 20
t_reset = 10e-3
t_2q= 150e-9
t_1q = 10e-6
t_reconfig = 500e-6
t_transport = 500e-6
t_meas = 10e-3

def plot_D_and_Nsamples():
    computer = AtomBasedComputer(Nq=Nq, components=components_no_cryo, N_comp=Ni_no_cryo, t_reset=t_reset, t_meas=t_meas, t_clock=t_reconfig, t_transport=t_transport,
                                 t_reload=t_reload, t_reload_freq=t_reload_freq, N_gatezones=20, independent_gates=False, periodic_reload=False)

    fig, axs = plt.subplots(1, 2, figsize=(10,4), sharey=True)
    alpha = 0
    beta = 1

    #FIG A)
    N_samples_values = [1, 10, 100, 1000, 10000]

    D_values = np.arange(0, 10010, 10)
    D_print = [100, 1000, 10000]

    colors = colormaps['Reds'](np.linspace(0.3, 0.8, len(N_samples_values)))

    for i, N_samples in enumerate(N_samples_values):
        EE_list = []
        N_pi_list = []
        for D0 in D_values:
            EE_list.append(computer.energy_efficiency(D0, alpha, beta, N_gates=D0, N_samples=N_samples))
            N_pi_list.append(computer.N_pi(t=T, D0=D0, alpha=alpha, beta=beta, N_gates=D0, N_samples=N_samples))
            if N_samples == 1 and D0 in D_print:
                print(f"N_sampl={N_samples}, D={D0}, computing time={computer.t_comp(D0=D0, alpha=alpha, beta=beta, N_gates=D0, N_samples=N_samples)}")
        axs[0].plot(D_values, EE_list, color = colors[i])
        axs[0].text(4000, EE_list[-1]*2.5, rf"$N_{{samples}}={N_samples}$", rotation = -8, fontsize=10)

    axs[0].set_xlabel(r"Final Circuit Depth, $D$")
    axs[0].set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    axs[0].set_xlim(0, max(D_values))
    axs[0].set_yscale('log')
    axs[0].set_ylim(9e-11, 1.5e-3)

    axs[0].text(1000, 3e-4, "(a)", fontsize = 14)

    ax2 = axs[0].twinx()
    ax2.plot(D_values, N_pi_list, alpha=0)
    ax2.set_yscale('log')
    ax2.set_ylim(9e-11*computer.P*T, 1.5e-3*computer.P*T)
    ax2.set_yticklabels([])


    #FIG B)
    N_samples_values = np.arange(0, 10010, 10)
    D_values = [10, 100, 1000, 10000]

    colors = colormaps['Purples'](np.linspace(0.3, 0.8, len(D_values)))

    for i, D0 in enumerate(D_values):
        EE_list = []
        N_pi_list = []
        for N_samples in N_samples_values:
            EE_list.append(computer.energy_efficiency(D0, alpha, beta, N_gates=D0, N_samples=N_samples))
            N_pi_list.append(computer.N_pi(t=T, D0=D0, alpha=alpha, beta=beta, N_gates=D0, N_samples=N_samples))
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
    ax2.set_ylabel(r"Number of Computations, $N_{\pi}$")
    ax2.set_yticks(np.linspace(0.2e6, 1.4e6, 7), labels=[r'$0.2\times10^{6}$', r'$0.4\times10^{6}$', r'$0.6\times10^{6}$', r'$0.8\times10^{6}$', r'$1.0\times10^{6}$', r'$1.2\times10^{6}$', r'$1.4\times10^{6}$'])
    ax2.set_yscale('log')
    ax2.set_ylim(9e-11*computer.P*T, 1.5e-3*computer.P*T)

    # axs[1].legend(fontsize=11, loc='upper right', fancybox=False, edgecolor='black')

    plt.subplots_adjust(wspace=0.1)

    plt.savefig("Figures/Neutral_atoms/neutral_atoms_D_and_Nsamples.pdf", bbox_inches='tight')
    plt.close()


def plot_power_breakdown():
    computer = AtomBasedComputer(Nq=Nq, components=components_no_cryo, N_comp=Ni_no_cryo, t_reset=t_reset, t_meas=t_meas, t_clock=t_reconfig, t_transport=t_transport,
                                 t_reload=t_reload, t_reload_freq=t_reload_freq, N_gatezones=1, independent_gates=False, periodic_reload=False)
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
    computer_periodic = AtomBasedComputer(Nq=Nq, components=components_no_cryo, N_comp=Ni_no_cryo, t_reset=t_reset, t_meas=t_meas, t_clock=t_reconfig, t_transport=t_transport, 
                                            t_reload=t_reload, t_reload_freq=t_reload_freq, N_gatezones=2, independent_gates=True, periodic_reload=True)
    

    components_cont_reload = [hvac, vacuum_chamber, trap_laser, amp_rydberg_1013, 
                          pump_rydberg_420, extra_lasers, camera, other_electronics, classical_comp]
    Ni_cont_reload = [N_hvac, N_vacuum, N_trap_laser, N_amp_rydberg_1013, N_pump_rydberg_420, 
                  N_extra_lasers, N_camera, N_other_electronics, N_classical_comp]

    computer_continuous = AtomBasedComputer(Nq=Nq, components=components_cont_reload, N_comp=Ni_cont_reload, t_reset=0, t_meas=t_meas, t_clock=t_reconfig, 
                                            t_transport=t_transport, N_gatezones=2, independent_gates=True, periodic_reload=False)

    print((t_reload_freq + t_reload) / t_reload_freq)

    D0 = np.arange(0, 510, 5)
    alpha = 0
    beta = 1
    N_gates_per_slice = 1
    N_samples = 1000

    fig, ax = plt.subplots(figsize=(7,5))

    EE_periodic = []
    EE_continuous = []
    for D in D0:
        N_gates = D * N_gates_per_slice
        EE_periodic.append(computer_periodic.energy_efficiency(D, alpha, beta, N_gates, N_samples))
        EE_continuous.append(computer_continuous.energy_efficiency(D, alpha, beta, N_gates, N_samples))
    ax.plot(D0, EE_periodic, label='Periodic Reload', color = 'royalblue')
    ax.plot(D0, EE_continuous, label='Continuous Reload', color = 'yellowgreen')

    ax.set_xlabel(r"Final Circuit Depth, $D$")
    ax.set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    ax.set_yscale('log')
    ax.set_xlim(0, max(D0))
    ax.set_ylim(9.5e-8, 8.5e-6)
    ax.legend(fontsize=11, loc='upper right', fancybox=False, edgecolor='black')
    fig.savefig("Figures/Neutral_atoms/neutral_atoms_periodic_vs_continuous_reload.pdf", bbox_inches='tight')




if __name__ == "__main__":
    plot_periodic_vs_continuous_reload()