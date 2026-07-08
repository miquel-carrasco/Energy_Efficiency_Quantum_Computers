from qcenergy.components import Component
from qcenergy.platforms import Computer, SolidStateComputer

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

Nq = 49
N_r = math.ceil(Nq/5)

pulse_tube , N_pt = Component('Pulse Tube', 9500, 'Cooling'), 1
dilution_unit, N_du = Component('Gas Handling System', 2000, 'Cooling'), 1
chiller, N_chill = Component('Chiller', 4600, 'Cooling'), 1
control_and_redout, N_readout = Component('Control and Readout Cluster', 1100, 'Qubit Control'), 1
rf_source, N_rf = Component('RF Source', 70, 'Qubit Control'), N_r
lna, N_lna = Component('LNA', 1.4, 'Qubit Control'), 2*N_r
pba, N_pba = Component('PBA', 100, 'Qubit Control'), N_r
server, N_server = Component('Server', 800, 'Classical Processing'), 1

components = [pulse_tube, dilution_unit, chiller, control_and_redout, rf_source, lna, pba, server]
Ni = [N_pt, N_du, N_chill, N_readout, N_rf, N_lna, N_pba, N_server]
P_per_component = [comp.P*Ni[i] for i, comp in enumerate(components)]

T = 24*3600

t_reset_passive = 200e-6
t_reset_active = 5e-6
t_1q = 25e-9
t_2q= 50e-9
t_meas = 1.6e-6


def plot_power_breakdown():
    computer = SolidStateComputer(Nq = Nq, components=components, N_comp=Ni, t_reset=t_reset_active, t_clock=t_2q, t_meas=t_meas, graph_type='Square')
    power_types = computer.power_per_types()
    power_components = computer.power_per_component()
    print("Total Power Consumption:", computer.P, "W")

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
    ax.set_ylabel(r"Power consumption (W)")

    ax2 = ax.twinx()
    ax2.set_ylim(0, max(power_types.values())/computer.P*100*1.2)
    ax2.set_ylabel(r"Relative consumption (\%)")

    fig.savefig("Figures/Superconducting/superconducting_power_breakdown.pdf")
    plt.close()

def plot_QMIO_power_breakdown():
    pulse_tube , N_pt = Component('Pulse Tube', 9000, 'Cooling'), 1
    dilution_unit, N_du = Component('Gas Handling System', 1800, 'Cooling'), 1
    chiller, N_chill = Component('Chiller', 4200, 'Cooling'), 1
    cryostat_aux, N_aux = Component('Other', 1320, 'Cooling'), 1
    fpga, N_fpga = Component('FPGA', 125, 'Qubit Control'), 32
    rf_electronics, N_rf = Component('RF Electronics', 70, 'Qubit Control'), N_r
    server, N_server = Component('Server', 440, 'Classical Processing'), 1

    components_qmio = [pulse_tube, dilution_unit, chiller, cryostat_aux, fpga, rf_electronics, server]
    Ni_qmio = [N_pt, N_du, N_chill, N_aux, N_fpga, N_rf, N_server]

    error_values = [500, 400, 200, 200, 19*32, 100, 80]
    total_error_values = [500+400+200+200, 19*32+100]


    computer_qmio = SolidStateComputer(Nq = Nq, components=components_qmio, N_comp=Ni_qmio, t_reset=t_reset_active, t_clock=t_2q, t_meas=t_meas, graph_type='Square')
    power_types = computer_qmio.power_per_types()
    power_components = computer_qmio.power_per_component()
    print("Total Power Consumption:", computer_qmio.P, "W")

    width = 1

    fig, ax = plt.subplots(figsize=(7,4))
    offset = 0
    ticks = []
    maps = ['Purples', 'Blues', 'Greens', 'Oranges', 'Reds']
    colors = [colormaps[maps[i]](np.linspace(0.3, 0.8, len(computer_qmio.type_groups_components[t])+1)[::-1]) for i, t in enumerate(power_types.keys())]
    for i, t in enumerate(power_types):
        if len(computer_qmio.type_groups_components[t]) == 1:
            x = np.array([offset])
            bars = ax.bar(x[0], power_components[computer_qmio.type_groups_components[t][0]], width=width, label = computer_qmio.type_groups_components[t][0], color=colors[i][0])
            ax.errorbar(x[0], power_components[computer_qmio.type_groups_components[t][0]], yerr = error_values[-1], fmt='none', ecolor='k', capsize=5)
            ax.bar_label(bars, padding=3+error_values[j]/max(power_types.values())*1.2, labels= [computer_qmio.type_groups_components[t][0]], rotation=90)
            print(t,power_components[computer_qmio.type_groups_components[t][0]], power_components[computer_qmio.type_groups_components[t][0]]/computer_qmio.P*100)
        else:
            x = np.arange(offset, offset + len(computer_qmio.type_groups_components[t]) + width)
            bars = ax.bar(x[0], power_types[t], width=width, color = colors[i][0])
            ax.errorbar(x[0], power_types[t], yerr = total_error_values[i], fmt='none', ecolor='k', capsize=5)
            ax.bar_label(bars, labels = ['Total'], padding=3+error_values[i]/25, rotation=90)
            print(t,power_types[t], power_types[t]/computer_qmio.P*100)
            j = 0
            for name in power_components.keys():
                if name in computer_qmio.type_groups_components[t]:
                    bars = ax.bar(x[j+1], power_components[name], width=width, color=colors[i][j+1], yerr = error_values[j])
                    ax.errorbar(x[j+1], power_components[name], yerr = error_values[j], fmt='none', ecolor='k', capsize=4)
                    ax.bar_label(bars, labels = [name], padding=3+error_values[j]/max(power_types.values())*1.2, rotation=90)
                    j += 1
        offset = x[-1] + width + 2
        ticks.append(x[0] + (x[-1]-x[0])/2)

    ax.set_xticks(ticks)
    ax.set_xticklabels(list(power_types.keys()))
    ax.set_ylim(0, max(power_types.values())*1.3)
    ax.set_ylabel(r"Power consumption (W)")

    ax2 = ax.twinx()
    ax2.set_ylim(0, max(power_types.values())/computer_qmio.P*100*1.3)
    ax2.set_ylabel(r"Relative consumption (\%)")

    fig.savefig("Figures/Superconducting/superconducting_qmio_power_breakdown.pdf")
    plt.close()


def plot_D_D0():
    computer = SolidStateComputer(Nq = Nq, components=components, N_comp=Ni, t_reset=t_reset_active, t_clock=t_2q, t_meas=t_meas, graph_type='Square')
    D0_values = np.arange(0, 2000, 10)
    alpha_values = [0, 0.25, 0.5, 0.75, 1]
    colors = colormaps['summer'](np.linspace(0.2, 0.8, len(alpha_values)))
    N_samples = 1000

    fig, main_ax = plt.subplots(figsize=(8,6))
    inset_ax = fig.add_axes([0.58, 0.62, 0.3, 0.25])

    for i, alpha in enumerate(alpha_values):
        D_values = []
        EE_values = []
        for D0 in D0_values:
            D_values.append(computer.final_circuit_depth(D0 = D0, alpha = alpha))
            EE_values.append(computer.energy_efficiency(D0 = D0, alpha = alpha, N_samples=N_samples))

        main_ax.plot(D0_values, EE_values, label=f"$\\alpha={alpha}$", color=colors[i])
        inset_ax.plot(D0_values, D_values, label=f"$\\alpha={alpha}$", color=colors[i])

    main_ax.set_xlabel(r"Initial Circuit Depth, $D_0$")
    main_ax.set_ylabel(r"Energy Efficiency (computations/J)")

    main_ax.set_yscale('log')
    main_ax.set_xlim(0, max(D0_values)*1.05)
    main_ax.set_ylim(1e-6, 1.2e-3)
    main_ax.text(700, 1.2e-4, r"$\alpha = 0$", fontsize=12)
    main_ax.text(700, 2.6e-5, r"$\alpha = 0.25$", fontsize=12)
    main_ax.text(700, 1.2e-5, r"$\alpha = 0.5$", fontsize=12)
    main_ax.text(700, 6e-6, r"$\alpha = 0.75$", fontsize=12)
    main_ax.text(700, 2e-6, r"$\alpha = 1$", fontsize=12)

    inset_ax.set_xlabel(r"$D_{0}$", fontsize=13)
    inset_ax.set_ylabel(r"$D$", fontsize=13)

    plt.savefig("Figures/Superconducting/superconducting_compilation.pdf", bbox_inches='tight')
    plt.close()


def reset_time():
    computer = SolidStateComputer(Nq = Nq, components=components, N_comp=Ni, t_reset=t_reset_active, t_clock=t_2q, t_meas=t_meas, graph_type='Square')
    D_values = np.arange(0, 10100, 50)
    N_samples = 100

    computer.t_reset = 0
    EE_zero = []
    for D in D_values:
        EE_zero.append(computer.energy_efficiency(D0 = D, alpha = 0, N_samples=N_samples))
    

    computer.t_reset = t_reset_passive
    EE_passive = []
    for D in D_values:
        EE_passive.append(computer.energy_efficiency(D0 = D, alpha = 0, N_samples=N_samples))
        if D == 100:
            print(computer.energy_efficiency(D0 = D, alpha = 0, N_samples=N_samples))
    
    computer.t_reset = t_reset_active
    EE_active = []
    for D in D_values:
        EE_active.append(computer.energy_efficiency(D0 = D, alpha = 0, N_samples=N_samples))
    
    fig, ax = plt.subplots()

    # ax.vlines(10*t_reset_passive/(computer.T_clock), 0, 0.006, colors='k', linestyles='dashed')
    ax.text(6000, 0.0017, r'$D>> t_{\rm{reset}}^{\rm{act}} / t_{\rm{clock}}$', fontsize=12, rotation=-7, zorder = -1)

    ax.plot(D_values, EE_active, color='yellowgreen', label = r'$t_{\rm{reset}}^{\rm{act}}=5 \;\mu s$', zorder = 1, linewidth=1.7)
    ax.plot(D_values, EE_passive, color='royalblue', label = r'$t_{\rm{reset}}^{\rm{pass}}=200 \;\mu s$', zorder = 3, linewidth=1.7)
    ax.plot(D_values, EE_zero, color='k', linestyle=':', alpha = 0.8, label = r'$t_{\rm{reset}}=0$', zorder = 2, linewidth=1.7)

    ax.legend(fontsize=12, fancybox = False, edgecolor='black', loc = "upper center")

    ax.set_ylim(0.0004, 0.7)
    ax.set_xlim(0, 10100)
    ax.set_yscale('log')
    ax.set_xlabel(r"Post-compilation Depth, $D$")
    ax.set_ylabel(r"Energy Efficiency (computations/J)")
    plt.savefig("Figures/Superconducting/superconducting_reset_time.pdf", bbox_inches='tight')
    plt.close()

def plot_D_and_Nsamples():
    computer = SolidStateComputer(Nq = Nq, components=components, N_comp=Ni, t_reset=t_reset_active, t_clock=t_2q, t_meas=t_meas, graph_type='Square')
    fig, axs = plt.subplots(1, 2, figsize=(11,4.5), sharey=True)

    #FIG A)
    N_samples_values = [1, 10, 100, 1000, 10000]

    D_values = np.arange(0, 10010, 10)
    D_print = [1, 10, 100, 1000, 10000]

    colors = colormaps['Reds'](np.linspace(0.3, 0.8, len(N_samples_values)))

    for i, N_samples in enumerate(N_samples_values):
        EE_list = []
        N_pi_list = []
        for D0 in D_values:
            EE_list.append(computer.energy_efficiency(D0 = D0, alpha = 0, N_samples=N_samples))
            N_pi_list.append(computer.N_pi(t = 24*3600, D0 = D0, alpha = 0, N_samples=N_samples))
            if N_samples == 100 and D0 in D_print:
                print(f"N_samples={N_samples}, D={D0}, N_pi={N_pi_list[-1]}, EE={EE_list[-1]}")
        axs[0].plot(D_values, EE_list, color = colors[i])
        axs[0].text(4000, EE_list[-1]*2.5, rf"$N_{{samples}}={N_samples}$", rotation = -6.5, fontsize=10)

    axs[0].set_xlabel(r"Post-compilation Depth, $D$")
    axs[0].set_ylabel(r"Energy Efficiency (computations/J)")
    axs[0].set_xlim(0, max(D_values))
    axs[0].set_yscale('log')
    axs[0].set_ylim(3e-6, 2.5e1)

    axs[0].text(1000, 6e0, "(a)", fontsize = 14)

    ax2 = axs[0].twinx()
    ax2.plot(D_values, N_pi_list, alpha=0)
    ax2.set_yscale('log')
    ax2.set_ylim(3e-6*computer.P*T, 2.5e1*computer.P*T)
    ax2.set_yticklabels([])

    # #QFT
    # D0=784
    # alpha = 0.3431
    # EE_qft = computer.energy_efficiency(D0=D0, alpha=alpha, N_samples=1000)
    # axs[0].scatter(computer.final_circuit_depth(D0=D0, alpha=alpha), EE_qft, marker='d', color = 'saddlebrown', edgecolors = 'k',linewidth =1, zorder = 10, label = r"QFT ($D=4304, N_{\rm{samples}}=1000$)")


    # #Adder
    # EE_adder = computer.energy_efficiency(D0=962, alpha=0.3514, N_samples=1000)
    # axs[0].scatter(computer.final_circuit_depth(D0=962, alpha=0.3514), EE_adder, marker='d', color = 'darkorchid', edgecolors = 'k',linewidth =1, zorder = 10, label = r"Adder ($D=5403, N_{\rm{samples}}=100$)")


    # #ISING
    # D_ising = 3 + (2+Nq-1)
    # EE_ising = computer.energy_efficiency(D0=D_ising, alpha=0, N_samples=1e7)
    # axs[0].scatter(computer.final_circuit_depth(D0=D_ising, alpha=0), EE_ising, marker='d', color = 'teal', edgecolors = 'k',linewidth =1, zorder = 10, label = r"ISING ($D=104, N_{\rm{samples}}=10^{7}$)")


    #FIG B)
    N_samples_values = np.arange(0, 10010, 10)
    D_values = [10, 100, 1000, 10000]

    colors = colormaps['Purples'](np.linspace(0.3, 0.8, len(D_values)))

    for i, D0 in enumerate(D_values):
        EE_list = []
        N_pi_list = []
        for N_samples in N_samples_values:
            EE_list.append(computer.energy_efficiency(D0 = D0, alpha = 0, N_samples=N_samples))
            N_pi_list.append(computer.N_pi(t = 24*3600, D0 = D0, alpha = 0, N_samples=N_samples))
            if N_samples == 2500 and D0 in D_values:
                print(f"t_sample={computer.t_comp(D0 = D0, alpha = 0, N_samples = 1)}")
        axs[1].plot(N_samples_values, EE_list, color = colors[i])
  
    # axs[1].text(1750, 3e-2, r"$D=10$", fontsize=10, rotation=-6)
    # axs[1].text(2200, 7e-3, r"$D=100$", fontsize=10, rotation=-6)
    axs[1].annotate(r"$D=10$", xy=(2300, 3.3e-3), xytext=(1800, 3e-2), arrowprops=dict(arrowstyle="->"), fontsize=10, rotation=-6)
    axs[1].annotate(r"$D=100$", xy=(3000, 1.4e-3), xytext=(2400, 7e-3), arrowprops=dict(arrowstyle="->"), fontsize=10, rotation=-6)
    axs[1].text(2000, 4.5e-4, r"$D=1000$", fontsize=10, rotation=-6)
    axs[1].text(2000, 5e-5, r"$D=10000$", fontsize=10, rotation=-6)

    axs[1].set_xlabel(r"Number of samples, $N_{\mathrm{samples}}$")
    # axs[1].set_ylabel(r"Energy Efficiency, $EE_{\mathcal{A}}^{\pi}$ [computations/J]")
    axs[1].set_xlim(0, 5010)
    axs[1].set_yscale('log')
    # axs[1].set_ylim(2.5e-5, 2.7e-2)

    axs[1].text(500, 6e0, "(b)", fontsize = 14)


    # #QFT
    # EE_qft = computer.energy_efficiency(D0=784, alpha=0.3431, N_samples=1000)
    # axs[1].scatter(1000, EE_qft, marker='d', color = 'saddlebrown', edgecolors = 'k',linewidth =1, zorder = 10, label = r"QFT ($D=4304, N_{\rm{samples}}=1000$)")


    # #Adder
    # EE_adder = computer.energy_efficiency(D0=962, alpha=0.3514, N_samples=1000)
    # axs[1].scatter(1000, EE_adder, marker='d', color = 'darkorchid', edgecolors = 'k',linewidth =1, zorder = 10, label = r"Adder ($D=5403, N_{\rm{samples}}=1000$)")


    # #ISING
    # EE_ising = computer.energy_efficiency(D0=D_ising, alpha=0, N_samples=1e7)
    # axs[1].scatter(1e7, EE_ising, marker='d', color = 'teal', edgecolors = 'k',linewidth =1, zorder = 10, label = r"ISING ($D=104, N_{\rm{samples}}=10^{7}$)")

    # axs[1].legend(fontsize=10, loc='upper right', fancybox=False, edgecolor='black')


    ax2 = axs[1].twinx()
    ax2.plot(N_samples_values, N_pi_list, alpha=0)
    ax2.set_ylabel(r"Computations in 24 hours")
    ax2.set_yticks(np.linspace(0.2e6, 1.4e6, 7), labels=[r'$0.2\times10^{6}$', r'$0.4\times10^{6}$', r'$0.6\times10^{6}$', r'$0.8\times10^{6}$', r'$1.0\times10^{6}$', r'$1.2\times10^{6}$', r'$1.4\times10^{6}$'])
    ax2.set_yscale('log')
    ax2.set_ylim(3e-6*computer.P*T, 2.5e1*computer.P*T)


    plt.subplots_adjust(wspace=0.1)

    plt.savefig("Figures/Superconducting/superconducting_D_and_Nsamples.pdf", bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    plot_QMIO_power_breakdown()
    # plot_D_and_Nsamples()
    # plot_power_breakdown()
    # reset_time()