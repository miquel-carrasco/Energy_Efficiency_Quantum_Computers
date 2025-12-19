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

Nq = 400

small_chiller, N_pt = Component('Small Chiller', 600, 'Cooling'), 4
dilution_unit, N_du = Component('Large Chiller', 1000, 'Cooling'), 4
hvac, N_hvac = Component('HVAC', 5000, 'Cooling'), 1
vacuum_chamber, N_vacuum = Component('Vacuum Chamber', 1000, 'Cooling'), 1

trap_laser, N_trap_laser = Component('Trap Laser', 1500, 'Qubit Control'), 1
amp_rydberg_1013, N_amp_rydberg_1013 = Component('Rydberg 1013nm Amplifier', 1000, 'Qubit Control'), 1
pump_rydberg_420, N_pump_rydberg_420 = Component('Rydberg 420nm Pump Laser', 900, 'Qubit Control'), 1
extra_lasers, N_extra_lasers = Component('Extra Lasers', 2550, 'Qubit Control'), 1
camera, N_camera = Component('Camera', 155, 'Qubit Control'), 1
other_electronics, N_other_electronics = Component('Other Electronics', 2000, 'Qubit Control'), 1

classical_comp, N_classical_comp = Component('Classical Computers', 250, 'Classical Processing'), 8

components = [small_chiller, dilution_unit, hvac, vacuum_chamber, trap_laser, amp_rydberg_1013, 
              pump_rydberg_420, extra_lasers, camera, other_electronics, classical_comp]
Ni = [N_pt, N_du, N_hvac, N_vacuum, N_trap_laser, N_amp_rydberg_1013, N_pump_rydberg_420, 
      N_extra_lasers, N_camera, N_other_electronics, N_classical_comp]
P_per_component = [comp.P*Ni[i] for i, comp in enumerate(components)]

T = 24*3600

t_init = 4e-3
t_2q= 2e-6
t_meas = 10e-3

computer = Computer(Nq = 100,
                    components = components,
                    N_comp = Ni,
                    graph_type="2D",
                    t_init = t_init,
                    t_meas = t_meas,
                    T_gates=[t_2q])



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
        ax1.text(4000, EE_list[-1]*1.9, rf"$N_{{samples}}={N_samples}$", rotation = -3, fontsize=10)

    ax1.set_xlabel(r"Total Circuit Depth, $D$")
    ax1.set_ylabel(r"Energy Efficiency, $EE$ (\#computations/J)")
    ax1.set_xlim(0, max(D_values))
    ax1.set_yscale('log')
    ax1.set_ylim(4e-8, 1.7e-2)



    ax2 = ax1.twinx()
    ax2.plot(D_values, N_pi_list, alpha=0)
    ax2.set_ylabel(r"Number of Computations, $N_{\pi}$")
    ax2.set_yticks(np.linspace(0.2e6, 1.4e6, 7), labels=[r'$0.2\times10^{6}$', r'$0.4\times10^{6}$', r'$0.6\times10^{6}$', r'$0.8\times10^{6}$', r'$1.0\times10^{6}$', r'$1.2\times10^{6}$', r'$1.4\times10^{6}$'])
    ax2.set_yscale('log')
    ax2.set_ylim(4e-8*computer.P*T, 1.7e-2*computer.P*T)

    plt.savefig("Figures/Neutral_atoms/neutral_atoms_EE_vs_D.pdf", bbox_inches='tight')
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

    plt.savefig("Figures/Neutral_atoms/neutral_atoms_power_breakdown.pdf")
    plt.close()


if __name__ == "__main__":
    plot_EE_vs_D(computer)
    # plot_D_D0(computer)
    # plot_power_breakdown(computer)
    print(computer.P, computer.P*3600*24/1000000)