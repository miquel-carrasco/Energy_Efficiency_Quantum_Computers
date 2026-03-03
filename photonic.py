from qcenergy.components import Component
from qcenergy.platforms import PhotonicComputer, Computer
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

r_source = 1*10e9
t_source = 1/r_source
eta_source =0.712
eta_det = 0.98
eta_dmx = 0.83
eta_coup = 0.0035
eta_mzi = 0.057

N_photon = 12
D_optical = 2*N_photon
T = 24*3600

pulse_tube , N_pt = Component('Pulse Tube', 1500, 'Cooling'), math.ceil(2*N_photon/25)
laser, N_laser = Component('Laser', 4, 'Qubit Control'), 1
chip, N_chip = Component('Peltier cooling of the chip', 250, 'Qubit Control'), 1
demultiplex, N_dplx = Component('Demultiplexer', 50, 'Qubit Control'), math.ceil(N_photon/12)
fpga, N_fpga = Component('Other electronics (FPGA)', 15, 'Qubit Control'), math.ceil((4*N_photon**2)/16)
server, N_server = Component('Server', 150, 'Classical Processing'), 1

components = [pulse_tube, laser, chip, demultiplex, fpga, server]
Ni = [N_pt, N_laser, N_chip, N_dplx, N_fpga, N_server]
P_per_component = [comp.P*Ni[i] for i, comp in enumerate(components)]




computer1 = PhotonicComputer(Nq = N_photon,
                    components = components,
                    N_comp = Ni,
                    graph_type="All-to-all",
                    r_source = r_source,
                    D_optical = D_optical,
                    eta_source = eta_source,
                    eta_det = eta_det,
                    eta_dmx = eta_dmx,
                    eta_coup = eta_coup,
                    eta_mzi = eta_mzi)

N_photon = 24
D_optical = 2*N_photon

pulse_tube , N_pt = Component('Pulse Tube', 1500, 'Cooling'), math.ceil(2*N_photon/25)
laser, N_laser = Component('Laser', 4, 'Qubit Control'), 1
chip, N_chip = Component('Peltier cooling of the chip', 250, 'Qubit Control'), 1
demultiplex, N_dplx = Component('Demultiplexer', 50, 'Qubit Control'), math.ceil(N_photon/12)
fpga, N_fpga = Component('Other electronics (FPGA)', 15, 'Qubit Control'), math.ceil((4*N_photon**2)/16)
server, N_server = Component('Server', 150, 'Classical Processing'), 1

components = [pulse_tube, laser, chip, demultiplex, fpga, server]
Ni = [N_pt, N_laser, N_chip, N_dplx, N_fpga, N_server]
P_per_component = [comp.P*Ni[i] for i, comp in enumerate(components)]


computer2 = PhotonicComputer(Nq = N_photon,
                    components = components,
                    N_comp = Ni,
                    graph_type="All-to-all",
                    r_source = r_source,
                    D_optical = D_optical,
                    eta_source = eta_source,
                    eta_det = eta_det,
                    eta_dmx = eta_dmx,
                    eta_coup = eta_coup,
                    eta_mzi = eta_mzi)

N_photon = 48
D_optical = 2*N_photon

pulse_tube , N_pt = Component('Pulse Tube', 1500, 'Cooling'), math.ceil(2*N_photon/25)
laser, N_laser = Component('Laser', 4, 'Qubit Control'), 1
chip, N_chip = Component('Peltier cooling of the chip', 250, 'Qubit Control'), 1
demultiplex, N_dplx = Component('Demultiplexer', 50, 'Qubit Control'), math.ceil(N_photon/12)
fpga, N_fpga = Component('Other electronics (FPGA)', 15, 'Qubit Control'), math.ceil((4*N_photon**2)/16)
server, N_server = Component('Server', 150, 'Classical Processing'), 1

components = [pulse_tube, laser, chip, demultiplex, fpga, server]
Ni = [N_pt, N_laser, N_chip, N_dplx, N_fpga, N_server]
P_per_component = [comp.P*Ni[i] for i, comp in enumerate(components)]

computer3 = PhotonicComputer(Nq = N_photon,
                    components = components,
                    N_comp = Ni,
                    graph_type="All-to-all",
                    r_source = r_source,
                    D_optical = D_optical,
                    eta_source = eta_source,
                    eta_det = eta_det,
                    eta_dmx = eta_dmx,
                    eta_coup = eta_coup,
                    eta_mzi = eta_mzi)

N_photon = 96
D_optical = 2*N_photon

pulse_tube , N_pt = Component('Pulse Tube', 1500, 'Cooling'), math.ceil(2*N_photon/25)
laser, N_laser = Component('Laser', 4, 'Qubit Control'), 1
chip, N_chip = Component('Peltier cooling of the chip', 250, 'Qubit Control'), 1
demultiplex, N_dplx = Component('Demultiplexer', 50, 'Qubit Control'), math.ceil(N_photon/12)
fpga, N_fpga = Component('Other electronics (FPGA)', 15, 'Qubit Control'), math.ceil((4*N_photon**2)/16)
server, N_server = Component('Server', 150, 'Classical Processing'), 1

components = [pulse_tube, laser, chip, demultiplex, fpga, server]
Ni = [N_pt, N_laser, N_chip, N_dplx, N_fpga, N_server]
P_per_component = [comp.P*Ni[i] for i, comp in enumerate(components)]


computer4 = PhotonicComputer(Nq = N_photon,
                    components = components,
                    N_comp = Ni,
                    graph_type="All-to-all",
                    r_source = r_source,
                    D_optical = D_optical,
                    eta_source = eta_source,
                    eta_det = eta_det,
                    eta_dmx = eta_dmx,
                    eta_coup = eta_coup,
                    eta_mzi = eta_mzi)


N_photon = 24
D_optical = 2*N_photon
eta_coup_EOLN = 3.4
eta_mzi_EOLN = 0.15

pulse_tube , N_pt = Component('Pulse Tube', 1500, 'Cooling'), math.ceil(2*N_photon/25)
laser, N_laser = Component('Laser', 4, 'Qubit Control'), 1
demultiplex, N_dplx = Component('Demultiplexer', 50, 'Qubit Control'), math.ceil(N_photon/12)
fpga, N_fpga = Component('Other electronics (FPGA)', 15, 'Qubit Control'), math.ceil((4*N_photon**2)/16)
server, N_server = Component('Server', 150, 'Classical Processing'), 1

components = [pulse_tube, laser, demultiplex, fpga, server]
Ni = [N_pt, N_laser, N_dplx, N_fpga, N_server]
P_per_component = [comp.P*Ni[i] for i, comp in enumerate(components)]


computerEOLN = PhotonicComputer(Nq = N_photon,
                    components = components,
                    N_comp = Ni,
                    graph_type="All-to-all",
                    r_source = r_source,
                    D_optical = D_optical,
                    eta_source = eta_source,
                    eta_det = eta_det,
                    eta_dmx = eta_dmx,
                    eta_coup = eta_coup_EOLN,
                    eta_mzi = eta_mzi_EOLN)

eta_coup_EOBTO = 0.127
eta_mzi_EOBTO = 0.3

pulse_tube , N_pt = Component('Pulse Tube', 1500, 'Cooling'), math.ceil(2*N_photon/25)
laser, N_laser = Component('Laser', 4, 'Qubit Control'), 1
demultiplex, N_dplx = Component('Demultiplexer', 50, 'Qubit Control'), math.ceil(N_photon/12)
fpga, N_fpga = Component('Other electronics (FPGA)', 15, 'Qubit Control'), math.ceil((4*N_photon**2)/16)
server, N_server = Component('Server', 150, 'Classical Processing'), 1

components = [pulse_tube, laser, demultiplex, fpga, server]
Ni = [N_pt, N_laser, N_dplx, N_fpga, N_server]
P_per_component = [comp.P*Ni[i] for i, comp in enumerate(components)]


computerEOBTO = PhotonicComputer(Nq = N_photon,
                    components = components,
                    N_comp = Ni,
                    graph_type="All-to-all",
                    r_source = r_source,
                    D_optical = D_optical,
                    eta_source = eta_source,
                    eta_det = eta_det,
                    eta_dmx = eta_dmx,
                    eta_coup = eta_coup_EOBTO,
                    eta_mzi = eta_mzi_EOBTO)


def plot_EE_vs_Nsamp(list_comp):

    N_values = np.arange(1, 10010, 10)
    D_print = [1, 10, 100, 1000, 10000]

    fig, ax1 = plt.subplots()
    colors = colormaps['Reds'](np.linspace(0.3, 0.8, len(list_comp)))
    i=0
    for comp in list_comp:
        print(comp.Nq)
        EE_list=[]
        for N in N_values:
            EE_list.append(comp.energy_efficiency(N_samples =N, N_photon= comp.Nq, N_source =1))

        ax1.plot(N_values, EE_list, color = colors[i])
        i=i+1
        ax1.text(4000, EE_list[-1]*2.5, rf"$N_{{photon}}={comp.Nq}$", rotation = -6, fontsize=10)

    ax1.set_xlabel(r"$N_{{sample}}$")
    ax1.set_ylabel(r"Energy efficiency")
    ax1.set_xlim(0, max(N_values))
    ax1.set_yscale('log')

    plt.savefig("Figures/Photonic/Photonic_EE_vs_sample.pdf", bbox_inches='tight')
    plt.show()
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

    plt.savefig("Figures/Photonic/photonic_power_breakdown.pdf")
    plt.show()
    plt.close()


def plot_EE_vs_comp(list_comp):

    N_values = np.arange(1, 10010, 10)
    comp_names = ["Glass mesh", "EO-LN", "EO-BTO"]

    fig, ax1 = plt.subplots()
    colors = colormaps['Reds'](np.linspace(0.3, 0.8, len(list_comp)))
    i=0
    for comp in list_comp:
        print(comp.Nq)
        EE_list=[]
        for N in N_values:
            EE_list.append(comp.energy_efficiency(N_samples =N, N_photon= comp.Nq, N_source =1))

        ax1.plot(N_values, EE_list, color = colors[i])
        ax1.text(4000, EE_list[-1]*2.5, comp_names[i], rotation = -6, fontsize=10)
        i=i+1

    ax1.set_xlabel(r"$N_{{sample}}$")
    ax1.set_ylabel(r"Energy efficiency")
    ax1.set_xlim(0, max(N_values))
    ax1.set_yscale('log')

    plt.savefig("Figures/Photonic/Photonic_EE_vs_comp2.pdf", bbox_inches='tight')
    plt.show()
    plt.close()



def plot_EE_vs_Nphoton(N_samples):
    photon = [i for i in range(1,96)]
    fig, ax1 = plt.subplots()
    colors = colormaps['Reds'](np.linspace(0.3, 0.8, len(N_samples)))
    
    for j, N in enumerate(N_samples):
        EE_list = []
        for i in photon:

            N_photon = i
            D_optical = 2*N_photon
            pulse_tube , N_pt = Component('Pulse Tube', 1500, 'Cooling'), math.ceil(2*N_photon/25)
            laser, N_laser = Component('Laser', 4, 'Qubit Control'), 1
            chip, N_chip = Component('Peltier cooling of the chip', 250, 'Qubit Control'), 1
            demultiplex, N_dplx = Component('Demultiplexer', 50, 'Qubit Control'), math.ceil(N_photon/12)
            fpga, N_fpga = Component('Other electronics (FPGA)', 15, 'Qubit Control'), math.ceil((4*N_photon**2)/16)
            server, N_server = Component('Server', 150, 'Classical Processing'), 1

            components = [pulse_tube, laser, chip, demultiplex, fpga, server]
            Ni = [N_pt, N_laser, N_chip, N_dplx, N_fpga, N_server]
            P_per_component = [comp.P*Ni[i] for i, comp in enumerate(components)]




            computer = PhotonicComputer(Nq = N_photon,
                                components = components,
                                N_comp = Ni,
                                graph_type="All-to-all",
                                r_source = r_source,
                                D_optical = D_optical,
                                eta_source = eta_source,
                                eta_det = eta_det,
                                eta_dmx = eta_dmx,
                                eta_coup = eta_coup,
                                eta_mzi = eta_mzi)
            
            EE_list.append(computer.energy_efficiency(N_samples =N, N_photon= computer.Nq, N_source =1))

        ax1.plot(photon, EE_list, color = colors[j])
        ax1.text(4000, EE_list[-1]*2.5, rf"$N_{{samples}}={N}$", rotation = -6, fontsize=10)

    ax1.set_xlabel(r"$N_{{photon}}$")
    ax1.set_ylabel(r"Energy efficiency")
    ax1.set_xlim(0, max(photon))
    ax1.set_yscale('log')

    plt.savefig("Figures/Photonic/Photonic_EE_vs_photon.pdf", bbox_inches='tight')
    plt.show()
    plt.close()


if __name__ == "__main__":
    #plot_EE_vs_Nsamp([computer1,computer2,computer3,computer4])
    #plot_EE_vs_comp([computer2,computerEOLN,computerEOBTO])
    #plot_power_breakdown(computer2)
    plot_EE_vs_Nphoton([100,10000,100000000000])