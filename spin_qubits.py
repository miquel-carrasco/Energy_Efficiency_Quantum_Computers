from qcenergy.components import Component
from qcenergy.platforms import Computer, SolidStateComputer
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

n = 7

Nq = n**2


pulse_tube , N_pt = Component('Pulse Tube', 9500, 'Cooling'), 1
dilution_unit, N_du = Component('Gas handling system', 2000, 'Cooling'), 1
chiller, N_chill = Component('Water cooler', 4600, 'Cooling'), 1
DC_control, N_DC_control = Component('DC Control', 0.5, 'Qubit Control'), 3*Nq - 2*math.ceil(math.sqrt(Nq))
BB_control, N_BB_control = Component('BB Control', 7.5, 'Qubit Control'), 3*Nq - 2*math.ceil(math.sqrt(Nq))
MW_control, N_MW_control = Component('MW Control', 24, 'Qubit Control'), Nq
redout_lockin, N_redout_lockin = Component('Lock-in Amplifier', 48, 'Qubit Control'), math.ceil(Nq/2)
lna, N_lna = Component('LNA', 0.11, 'Qubit Control'), math.ceil(Nq/2)
rt_amplifier, N_rt_amplifier = Component('RT Amplifier', 0.5, 'Qubit Control'), math.ceil(Nq/2)
classical_comp, N_classical_comp = Component('Classical Computers', 150, 'Classical Processing'), 2

components = [pulse_tube, dilution_unit, DC_control, BB_control, MW_control, redout_lockin, lna, rt_amplifier, classical_comp, chiller]
Ni = [N_pt, N_du, N_DC_control, N_BB_control, N_MW_control, N_redout_lockin, N_lna, N_rt_amplifier, N_classical_comp, N_chill]
Ni = [int(x) for x in Ni]

T = 24*3600

t_reset_best = 0.1e-3
t_reset_worst = 1e-3
t_g_best = 10e-9
t_g_worst = 100e-9
t_meas = 10e-6


def plot_power_breakdown():
    computer = SolidStateComputer(components=components, N_comp=Ni, graph_type="2D", t_reset=t_reset_best, t_meas=t_meas, t_clock=t_g_best)
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


def crossbar_vs_planar_vs_linear_49_100():

    fig, ax = plt.subplots(1,1, figsize=(7,5), sharey=True)
    colors = colormaps['summer'].reversed()(np.linspace(0.4, 0.8, 2))
    D_values = np.arange(0, 2000, 5)
    EE_planar_49 = []
    EE_crossbar_og_49 = []
    EE_crossbar_red_49 = []
    EE_linear_49 = []

    n = 7
    Nq = n**2
    pulse_tube , N_pt = Component('Pulse Tube', 9500, 'Cooling'), 1
    dilution_unit, N_du = Component('Gas handling system', 2000, 'Cooling'), 1
    chiller, N_chill = Component('Water cooler', 4600, 'Cooling'), 1
    DC_control, N_DC_control = Component('DC Control', 0.5, 'Qubit Control'), 3*Nq - 2*math.ceil(math.sqrt(Nq))
    BB_control, N_BB_control = Component('BB Control', 7.5, 'Qubit Control'), 3*Nq - 2*math.ceil(math.sqrt(Nq))
    MW_control, N_MW_control = Component('MW Control', 24, 'Qubit Control'), Nq
    redout_lockin, N_redout_lockin = Component('Lock-in Amplifier', 48, 'Qubit Control'), math.ceil(Nq/2)
    lna, N_lna = Component('LNA', 0.11, 'Qubit Control'), math.ceil(Nq/2)
    rt_amplifier, N_rt_amplifier = Component('RT Amplifier', 0.5, 'Qubit Control'), math.ceil(Nq/2)
    classical_comp, N_classical_comp = Component('Classical Computers', 150, 'Classical Processing'), 2
    components = [pulse_tube, dilution_unit, DC_control, BB_control, MW_control, redout_lockin, lna, rt_amplifier, classical_comp, chiller]
    Ni = [N_pt, N_du, N_DC_control, N_BB_control, N_MW_control, N_redout_lockin, N_lna, N_rt_amplifier, N_classical_comp, N_chill]
    Ni = [int(x) for x in Ni]
    computer_49 = SolidStateComputer(components=components, N_comp=Ni, graph_type="2D", t_reset=t_reset_best, t_meas=t_meas, t_clock=t_g_best)


    eta = 0.9

    for D0 in D_values:
        # if D0 == 500:
        #     print("2D, 49 qubits", computer_49.energy_efficiency(D0, eta , N_samples=1))
        #     print("2D, 100 qubits", computer_100.energy_efficiency(D0, eta, N_samples=1))
        EE_planar_49.append(computer_49.energy_efficiency(D0, eta, N_samples=1))



    computer_49.graph_type = "Linear"
    Nq = 49
    Ni = [N_pt, N_du, 2*Nq-1, 2*Nq-1, Nq, math.ceil(math.sqrt(2*Nq)), math.ceil(math.sqrt(2*Nq)), math.ceil(math.sqrt(2*Nq)), N_classical_comp, N_chill]
    Ni = [int(x) for x in Ni]
    computer_49.N_comp = Ni
    computer_49.list_components = computer_49.assemble()
    for D0 in D_values:
        # if D0 == 500:
        #     print("Linear, 49 qubits", computer_49.energy_efficiency(D0, eta, N_samples=1))
        #     print("Linear, 100 qubits", computer_100.energy_efficiency(D0, eta, N_samples=1))
        EE_linear_49.append(computer_49.energy_efficiency(D0, eta, N_samples=1))

    computer_49.graph_type = "2D"
    Nq = 49
    Ni = [N_pt, N_du, math.ceil(4*math.sqrt(2*Nq)+1), math.ceil(4*math.sqrt(2*Nq)+1), 1, math.ceil(math.sqrt(2*Nq)), math.ceil(math.sqrt(2*Nq)), math.ceil(math.sqrt(2*Nq)), N_classical_comp, N_chill]
    Ni = [int(x) for x in Ni]
    computer_49.t_clock = 250e-9
    computer_49.t_meas = 10e-5
    computer_49.N_comp = Ni
    computer_49.list_components = computer_49.assemble()
    Nq = 100
    Ni = [N_pt, N_du, math.ceil(4*math.sqrt(2*Nq)+1), math.ceil(4*math.sqrt(2*Nq)+1), 1, math.ceil(math.sqrt(2*Nq)), math.ceil(math.sqrt(2*Nq)), math.ceil(math.sqrt(2*Nq)), N_classical_comp, N_chill]
    Ni = [int(x) for x in Ni]

    for D0 in D_values:
        # if D0 == 500:
        #     print("Crossbar, 49 qubits", computer_49.energy_efficiency(D0, eta, N_samples=1))
        #     print("Crossbar, 100 qubits", computer_100.energy_efficiency(D0, eta, N_samples=1))
        EE_crossbar_og_49.append(computer_49.energy_efficiency(D0, eta, N_samples=1))
    
    computer_49.t_clock = 10e-9
    computer_49.t_meas = 10e-6
    computer_49.N_comp = Ni
    for D0 in D_values:
        # if D0 == 500:
        #     print("Crossbar, 49 qubits", computer_49.energy_efficiency(D0, eta, N_samples=1))
        #     print("Crossbar, 100 qubits", computer_100.energy_efficiency(D0, eta, N_samples=1))
        EE_crossbar_red_49.append(computer_49.energy_efficiency(D0, eta, N_samples=1))

    ax.plot(D_values, EE_linear_49, label='Linear', color = "royalblue", zorder = 10)
    ax.plot(D_values, EE_planar_49, label='2D', color = "yellowgreen")
    ax.plot(D_values, EE_crossbar_og_49, label=r'Crossbar ($t_{\rm{clock}}=250~\mathrm{ns}$, $t_{\rm{meas}}=100\;\mu\mathrm{s}$)', color = "darkgreen")
    ax.plot(D_values, EE_crossbar_red_49, label=r'Crossbar ($t_{\rm{clock}}=10~\mathrm{ns}$, $t_{\rm{meas}}=10\;\mu\mathrm{s}$)', color = "darkgreen", linestyle='--')


    ax.fill_between(D_values, EE_planar_49, EE_crossbar_red_49, color=colors[1], alpha=0.2)
    ax.text(400, 0.363, r'$P^{\rm{2D}}-P^{\rm{crossbar}}\approx 1\mathrm{kW}$', fontsize=10, color='black', rotation=-9)
    ax.set_xlabel(r"Pre-routing Circuit Depth, $D_{0}$")
    ax.set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    ax.set_xlim(0, 1000)
    ax.set_ylim(1e-2, 0.68e0)
    # ax.set_yscale('log')
    ax.legend(fontsize=10, loc='upper right', fancybox=False, edgecolor='black', ncols=2)
    fig.savefig("Figures/Spin_qubits/spin_qubits_crossbar_vs_planar_vs_linear.pdf", bbox_inches='tight')
    plt.close()

def plot_D_and_Nsamples():
    computer = SolidStateComputer(components=components, N_comp=Ni, graph_type="2D", t_reset=t_reset_best, t_meas=t_meas, t_clock=t_g_best)

    fig, axs = plt.subplots(1, 2, figsize=(10,4), sharey=True)

    #FIG A)
    N_samples_values = [1, 10, 100, 1000, 10000]

    eta = 0
    D_values = np.arange(0, 10010, 10)
    D_print = [1, 10, 100, 1000, 10000]

    colors = colormaps['Reds'](np.linspace(0.3, 0.8, len(N_samples_values)))

    for i, N_samples in enumerate(N_samples_values):
        EE_list = []
        N_pi_list = []
        for D0 in D_values:
            EE_list.append(computer.energy_efficiency(D0, eta, N_samples=N_samples))
            N_pi_list.append(computer.N_pi(D0 = D0, eta = eta, t = 24*3600, N_samples=N_samples))
            if N_samples == 100 and D0 in D_print:
                print(f"N_samples={N_samples}, D={D0}, N_pi={N_pi_list[-1]}, EE={EE_list[-1]}")
        axs[0].plot(D_values, EE_list, color = colors[i])
        axs[0].text(4000, EE_list[-1]*1.7, rf"$N_{{samples}}={N_samples}$", rotation = -3, fontsize=10)

    axs[0].set_xlabel(r"Final Circuit Depth, $D$")
    axs[0].set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    axs[0].set_xlim(0, max(D_values))
    axs[0].set_yscale('log')
    axs[0].set_ylim(8.5e-6, 1.5e0)

    axs[0].text(1000, 7.0e-1, "(a)", fontsize = 14)

    ax2 = axs[0].twinx()
    ax2.plot(D_values, N_pi_list, alpha=0)
    ax2.set_yscale('log')
    ax2.set_ylim(8.5e-6*computer.P*T, 8.5e0*computer.P*T)
    ax2.set_yticklabels([])


    #FIG B)
    N_samples_values = np.arange(0, 10010, 10)
    D_values = [100, 1000, 10000]

    colors = colormaps['Purples'](np.linspace(0.3, 0.8, len(D_values)))

    for i, D0 in enumerate(D_values):
        EE_list = []
        N_pi_list = []
        for N_samples in N_samples_values:
            EE_list.append(computer.energy_efficiency(D0, eta, N_samples=N_samples))
            N_pi_list.append(computer.N_pi(D0 = D0, eta = eta, t = 24*3600, N_samples=N_samples))
            if N_samples == 2500 and D0 in D_values:
                print(f"t_sample={T/(N_pi_list[-1]*N_samples)}, N_samples={N_samples}, D={D0}, N_pi={N_pi_list[-1]}, EE={EE_list[-1]}")
        axs[1].plot(N_samples_values, EE_list, color = colors[i], label=f"$D={D0}$")
    axs[1].annotate(r"$D=100$", xy=(2300, 1.8e-4), xytext=(1800, 9e-4), arrowprops=dict(arrowstyle="->"), fontsize=10, rotation=-6)
    axs[1].annotate(r"$D=1000$", xy=(3000, 1.3e-4), xytext=(2400, 3e-4), arrowprops=dict(arrowstyle="->"), fontsize=10, rotation=-6.5)
    axs[1].text(2000, 4e-5, r"$D=10000$", fontsize=10, rotation=-6.5)

    axs[1].set_xlabel(r"Number of samples, $N_{\mathrm{samples}}$")
    # axs[1].set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    axs[1].set_xlim(0, 5010)
    axs[1].set_yscale('log')
    # axs[1].set_ylim(8.5e-6, 2.7e-2)

    axs[1].text(500, 7.0e-1, "(b)", fontsize = 14)


    ax2 = axs[1].twinx()
    ax2.plot(N_samples_values, N_pi_list, alpha=0)
    ax2.set_ylabel(r"Number of Computations in 24h, $N^{\pi}(24h)$")
    ax2.set_yticks(np.linspace(0.2e6, 1.4e6, 7), labels=[r'$0.2\times10^{6}$', r'$0.4\times10^{6}$', r'$0.6\times10^{6}$', r'$0.8\times10^{6}$', r'$1.0\times10^{6}$', r'$1.2\times10^{6}$', r'$1.4\times10^{6}$'])
    ax2.set_yscale('log')
    ax2.set_ylim(8.5e-6*computer.P*T, 8.5e0*computer.P*T)

    # axs[1].legend(fontsize=11, loc='upper right', fancybox=False, edgecolor='black')

    plt.subplots_adjust(wspace=0.1)

    plt.savefig("Figures/Spin_qubits/spin_qubits_D_and_Nsamples.pdf", bbox_inches='tight')
    plt.close()



if __name__ == "__main__":
    crossbar_vs_planar_vs_linear_49_100()