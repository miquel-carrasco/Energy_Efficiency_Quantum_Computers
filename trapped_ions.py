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
N_gatezones = 1


compressor , N_compressor = Component('Compressor', 7500, 'Environmental Conditions'), 1
chiller, N_chill = Component('Chiller', 2000, 'Environmental Conditions'), 1
image_system, N_image = Component('Image System', 100, 'Qubit Control'), 1
HVAC, N_HVAC = Component('HVAC', 7500, 'Environmental Conditions'), 1
magnetic_field_generation, N_magnetic_field = Component('Magnetic Field Generation', 1, 'Qubit Control'), 1
active_control, N_active_control = Component('Active Control System', 100, 'Qubit Control'), 1
gate_drive, N_gate_drive = Component('Gate Drive', 800, 'Qubit Control'), 1
passive_control, N_passive_control = Component('Passive Control System', 200, 'Qubit Control'), 1
control_desktop, N_control_desktop = Component('Control Desktop', 150, 'Classical Processing'), 1

components_cryo = [compressor, chiller, image_system, HVAC, magnetic_field_generation, active_control, gate_drive, passive_control, control_desktop]
N_comp_cryo = [N_compressor, N_chill, N_image, N_HVAC, N_magnetic_field, N_active_control, N_gate_drive, N_passive_control, N_control_desktop]

components_no_cryo = [image_system, HVAC, magnetic_field_generation, active_control, gate_drive, passive_control, control_desktop]
N_comp_no_cryo = [N_image, N_HVAC, N_magnetic_field, N_active_control, N_gate_drive, N_passive_control, N_control_desktop]

T = 24*3600


t_reset = 100e-3 #Doppler cooling
t_clock_1_gatezone = 70e-6
t_clock_mult_gatezones = 1e-3
t_transport = 50e-3
t_meas = 0.5e-3


def plot_power_breakdown():
    computer = AtomBasedComputer(Nq=Nq, components=components_no_cryo, N_comp=N_comp_no_cryo, t_reset=t_reset, t_meas=t_meas, t_clock=t_clock_1_gatezone, t_transport=t_transport, N_gatezones=N_gatezones)

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

def plot_D_and_Nsamples():
    computer = AtomBasedComputer(Nq=Nq, components=components_no_cryo, N_comp=N_comp_no_cryo, t_reset=t_reset, t_meas=t_meas, t_clock=t_clock_1_gatezone, t_transport=t_transport, N_gatezones=N_gatezones, independent_gates=False)
    alpha = 0 #No increase in depth due to non-indep gates
    beta = 1
    print(computer.P)
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
            EE_list.append(computer.energy_efficiency(D0, alpha, beta, N_gates=D0, N_samples=N_samples))
            N_pi_list.append(computer.N_pi(t=T, D0=D0, alpha=alpha, beta=beta, N_gates=D0, N_samples=N_samples))
            if N_samples == 1 and D0 in D_print:
                print(f"t_sample={T/(N_pi_list[-1]*N_samples)}, N_samples={N_samples}, D={D0}, N_pi={N_pi_list[-1]}, EE={EE_list[-1]}")
        axs[0].plot(D_values, EE_list, color = colors[i])
        axs[0].text(4000, EE_list[-1]*2.5, rf"$N_{{samples}}={N_samples}$", rotation = -6, fontsize=10)

    axs[0].set_xlabel(r"Final Circuit Depth, $D$")
    axs[0].set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    axs[0].set_xlim(0, max(D_values))
    axs[0].set_yscale('log')
    axs[0].set_ylim(8.5e-12, 2.5e-4)

    axs[0].text(1000, 5e-5, "(a)", fontsize = 14)

    ax2 = axs[0].twinx()
    ax2.plot(D_values, N_pi_list, alpha=0)
    ax2.set_yscale('log')
    ax2.set_ylim(8.5e-12*computer.P*T, 2.5e-4*computer.P*T)
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
            if N_samples == 1 and D0 in D_values:
                print(f"t_sample={T/(N_pi_list[-1]*N_samples)}, N_samples={N_samples}, D={D0}, N_pi={N_pi_list[-1]}, EE={EE_list[-1]}")
        axs[1].plot(N_samples_values, EE_list, color = colors[i], label=f"$D={D0}$")
        axs[1].text(2200, EE_list[-1]*5, rf"$D={D0}$", rotation = -6, fontsize=10)

    axs[1].set_xlabel(r"Number of samples, $N_{\mathrm{samples}}$")
    # axs[1].set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    axs[1].set_xlim(0, 5010)
    axs[1].set_yscale('log')
    # axs[1].set_ylim(8.5e-12, 2.7e-2)

    axs[1].text(500, 5e-5, "(b)", fontsize = 14)


    ax2 = axs[1].twinx()
    ax2.plot(N_samples_values, N_pi_list, alpha=0)
    ax2.set_ylabel(r"Number of Computations, $N_{\pi}$")
    ax2.set_yticks(np.linspace(0.2e6, 1.4e6, 7), labels=[r'$0.2\times10^{6}$', r'$0.4\times10^{6}$', r'$0.6\times10^{6}$', r'$0.8\times10^{6}$', r'$1.0\times10^{6}$', r'$1.2\times10^{6}$', r'$1.4\times10^{6}$'])
    ax2.set_yscale('log')
    ax2.set_ylim(8.5e-12*computer.P*T, 2.5e-4*computer.P*T)

    # axs[1].legend(fontsize=11, loc='upper right', fancybox=False, edgecolor='black')

    plt.subplots_adjust(wspace=0.1)

    plt.savefig("Figures/Trapped_ions/trapped_ions_D_and_Nsamples.pdf", bbox_inches='tight')
    plt.close()

def plot_comparison_traps():
    computer_1trap = AtomBasedComputer(Nq=Nq, components=components_no_cryo, N_comp=N_comp_no_cryo, t_reset=t_reset, t_meas=t_meas, t_clock=t_clock_1_gatezone, t_transport=t_transport, N_gatezones=1, independent_gates=False)

    N_components_indep = [N_image, N_HVAC, N_magnetic_field, 2, N_gate_drive, N_passive_control, N_control_desktop]
    computer_10traps_no_indep = AtomBasedComputer(Nq=Nq, components=components_no_cryo, N_comp=N_comp_no_cryo, t_reset=t_reset, t_meas=t_meas, t_clock=t_clock_mult_gatezones, t_transport=t_transport, N_gatezones=10, independent_gates=False)
    computer_10traps_indep = AtomBasedComputer(Nq=Nq, components=components_no_cryo, N_comp=N_components_indep, t_reset=t_reset, t_meas=t_meas, t_clock=t_clock_mult_gatezones, t_transport=t_transport, N_gatezones=10, independent_gates=True)

    fig, axs = plt.subplots(1,3, figsize=(13,4), sharey=True)

    Ng_per_layer_vals = [1, 10, 50]

    beta_1 = 0.5
    beta_10 = beta_1/10

    for i, Ng_per_layer in enumerate(Ng_per_layer_vals):
        #Worst case
        alpha = 1

        D_values = np.arange(1, 1010, 5)
        EE_1trap_worst = []
        EE_10traps_no_indep_alpha0= []
        EE_10traps_no_indep_alpha1= []
        EE_10traps_indep = []
        for D0 in D_values:
            Ng = D0*Ng_per_layer
            EE_1trap_worst.append(computer_1trap.energy_efficiency(D0, alpha, beta_1, N_gates=Ng, N_samples=100))
            EE_10traps_no_indep_alpha0.append(computer_10traps_no_indep.energy_efficiency(D0, 0, beta_10, N_gates=Ng, N_samples=100))
            EE_10traps_no_indep_alpha1.append(computer_10traps_no_indep.energy_efficiency(D0, 1, beta_10, N_gates=Ng, N_samples=100))
            EE_10traps_indep.append(computer_10traps_indep.energy_efficiency(D0, alpha, beta_10, N_gates=Ng, N_samples=100))


        axs[i].plot(D_values, EE_1trap_worst, label=r"1 trap", color='royalblue')
        axs[i].plot(D_values, EE_10traps_no_indep_alpha0, color='yellowgreen')
        axs[i].plot(D_values, EE_10traps_no_indep_alpha1, color='yellowgreen')
        axs[i].plot(D_values, EE_10traps_indep, label=r"10 traps, independent gates", color='darkgreen', linestyle='--')
        axs[i].fill_between(D_values, EE_10traps_no_indep_alpha0, EE_10traps_no_indep_alpha1, color='yellowgreen', alpha=0.5, label=r"10 traps, no independent gates ($\alpha=[0,1]$)")

        axs[i].set_xlabel(r"Pre-routing circuit depth, $D_{0}$")
        axs[i].set_xlim(0, max(D_values))
        axs[i].set_yscale('log')

    axs[0].text(320, 3.5e-6, r"a) $<N_{\rm{g}}^{\rm{layer}}>=1$", fontsize=14)
    axs[1].text(320, 3.5e-6, r"b) $<N_{\rm{g}}^{\rm{layer}}>=10$", fontsize=14)
    axs[2].text(320, 3.5e-6, r"c) $<N_{\rm{g}}^{\rm{layer}}>=50$", fontsize=14)
    axs[0].set_ylim(3.5e-10, 1.5e-5)
    axs[0].set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    axs[0].legend(fontsize=11, loc='lower left', fancybox=False, edgecolor='black')

    fig.subplots_adjust(wspace=0.05)

    fig.savefig(f"Figures/Trapped_ions/trapped_ions_comparison_traps_beta1={beta_1}.pdf", bbox_inches='tight')


def plot_beta_tradeoff():
    computer_1trap = AtomBasedComputer(Nq=Nq, components=components_no_cryo, N_comp=N_comp_no_cryo, t_reset=t_reset, t_meas=t_meas, t_clock=t_clock_1_gatezone, t_transport=t_transport, N_gatezones=1, independent_gates=False)

    N_components_indep = [N_image, N_HVAC, N_magnetic_field, 2, N_gate_drive, N_passive_control, N_control_desktop]
    computer_10traps_no_indep = AtomBasedComputer(Nq=Nq, components=components_no_cryo, N_comp=N_comp_no_cryo, t_reset=t_reset, t_meas=t_meas, t_clock=t_clock_mult_gatezones, t_transport=t_transport, N_gatezones=10, independent_gates=False)
    computer_10traps_indep = AtomBasedComputer(Nq=Nq, components=components_no_cryo, N_comp=N_components_indep, t_reset=t_reset, t_meas=t_meas, t_clock=t_clock_mult_gatezones, t_transport=t_transport, N_gatezones=10, independent_gates=True)

    fig, axs = plt.subplots(1,3, figsize=(15,4), sharey=True)

    Ng_per_layer_vals = [1, 10, 50]

    beta_vals = np.logspace(-3, 0, 20)
    D0 = 500
    Ng_per_layer = 1
    alpha = 1
    for i, Ng_per_layer in enumerate(Ng_per_layer_vals):
        EE_1trap = []
        EE_10traps_no_indep_alpha0= []
        EE_10traps_no_indep_alpha1=[]
        EE_10traps_indep = []
        for beta in beta_vals:
            beta_1 = beta
            beta_10 = beta_1/10
            Ng = D0*Ng_per_layer
            EE_1trap.append(computer_1trap.energy_efficiency(D0, alpha, beta_1, N_gates=Ng, N_samples=100))
            EE_10traps_no_indep_alpha0.append(computer_10traps_no_indep.energy_efficiency(D0, 0, beta_10, N_gates=Ng, N_samples=100))
            EE_10traps_no_indep_alpha1.append(computer_10traps_no_indep.energy_efficiency(D0, 1, beta_10, N_gates=Ng, N_samples=100))
            EE_10traps_indep.append(computer_10traps_indep.energy_efficiency(D0, alpha, beta_10, N_gates=Ng, N_samples=100))
        axs[i].plot(beta_vals, EE_1trap, label=r"1 trap", color='royalblue')
        axs[i].plot(beta_vals, EE_10traps_no_indep_alpha0, color='yellowgreen')
        axs[i].plot(beta_vals, EE_10traps_no_indep_alpha1, color='yellowgreen')
        axs[i].plot(beta_vals, EE_10traps_indep, label=r"10 traps, independent gates", color='darkgreen', linestyle='--')
        axs[i].fill_between(beta_vals, EE_10traps_no_indep_alpha0, EE_10traps_no_indep_alpha1, color='yellowgreen', alpha=0.5, label=r"10 traps, no independent gates ($\alpha=[0,1]$)")
        axs[i].set_xlabel(r"Transport per layer ratio, $\beta$")

    axs[0].set_xscale('log')
    axs[0].set_xlim(1e-3, 1)
    axs[0].set_yscale('log')
    axs[1].set_xscale('log')
    axs[1].set_xlim(1e-3, 1)
    axs[2].set_xscale('log')
    axs[2].set_xlim(1e-3, 1)
    axs[0].set_ylim(5.1e-10, 8.5e-6)


    axs[0].text(1e-2, 3e-6, r"a) $<N_{\rm{g}}^{\rm{layer}}>=1$", fontsize=14)
    axs[1].text(1e-2, 3e-6, r"b) $<N_{\rm{g}}^{\rm{layer}}>=10$", fontsize=14)
    axs[2].text(1e-2, 3e-6, r"c) $<N_{\rm{g}}^{\rm{layer}}>=50$", fontsize=14)
    axs[0].set_ylabel(r"Energy Efficiency, $EE$ (computations/J)")
    axs[0].legend(fontsize=11, loc='lower left', fancybox=False, edgecolor='black')

    fig.savefig(f"Figures/Trapped_ions/trapped_ions_beta_tradeoff.pdf", bbox_inches='tight')


if __name__ == "__main__":
    plot_comparison_traps()