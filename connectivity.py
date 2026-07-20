import rustworkx as rx
import rustworkx.generators as rx_gen
from rustworkx.visualization import mpl_draw
import matplotlib.pyplot as plt
import math
import numpy as np
from matplotlib import colormaps

params = {'axes.labelsize': 14,
         'axes.titlesize': 15,
         'axes.linewidth': 1.2,
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

colors_1 = colormaps['summer'].reversed()(np.linspace(0.3, 0.7, 2))
colors_2 = colormaps['winter'].reversed()(np.linspace(0.3, 0.7, 2))

def final_depth(D0, alpha, avg_spl):
    return D0*(1 + alpha * 3*math.ceil((avg_spl-1)/2))

def plot_D_scalings():
    linear_graph = rx_gen.path_graph(50)
    linear_avg_spl = rx.graph_unweighted_average_shortest_path_length(linear_graph)

    circular_graph = rx_gen.cycle_graph(50)
    circular_avg_spl = rx.graph_unweighted_average_shortest_path_length(circular_graph)

    square_graph = rx_gen.grid_graph(7,7)
    square_avg_spl = rx.graph_unweighted_average_shortest_path_length(square_graph)

    d = 5
    heavy_hex_graph = rx_gen.heavy_hex_graph(d, multigraph=False)
    heavy_hex_avg_spl = rx.graph_unweighted_average_shortest_path_length(heavy_hex_graph)
    n_heavy_hex = int((5*d**2-2*d-1)/2)


    fig, axs = plt.subplots(1,3, figsize = (10, 4), sharey = True)

    D0_vals = np.arange(0, 1040, 10)
    alpha_vals = [0.1, 0.5, 0.9]

    for i,alpha in enumerate(alpha_vals):
        linear_D = []
        circular_D = []
        square_D = []
        heavy_hex_D = []
        for D0 in D0_vals:
            linear_D.append(final_depth(D0, alpha, linear_avg_spl))
            circular_D.append(final_depth(D0, alpha, circular_avg_spl))
            square_D.append(final_depth(D0, alpha, square_avg_spl))
            heavy_hex_D.append(final_depth(D0, alpha, heavy_hex_avg_spl))
        axs[i].plot(D0_vals, linear_D, label = f"Linear graph (50 qubits)", zorder = 0, color = colors_1[0])
        axs[i].plot(D0_vals, circular_D, label = f"Circular graph (50 qubits)", zorder = 5, color = colors_1[1], ls = "--")
        axs[i].plot(D0_vals, heavy_hex_D, label = f"Heavy-hex graph ({n_heavy_hex} qubits)", zorder = 9, color = colors_2[0])
        axs[i].plot(D0_vals, square_D, label = f"Square graph (49 qubits)", zorder = 10, color = colors_2[1], ls = "--")
        axs[i].plot(D0_vals, D0_vals, label = f"Fully connected graph", zorder = 12, color = "k")
        
        axs[i].set_title(rf"$\alpha_{{\rm{{2q}}}}={alpha}$", pad = 10)
        axs[i].set_xlim(0,max(D0_vals))

    axs[0].set_ylim(-10, 2.5e4)
    axs[0].legend(fontsize=10, loc='upper left', fancybox=False, edgecolor='black')
    fig.supxlabel(r'Pre-routing Circuit Depth, $D_{0}$', fontsize = 16, y = 0.04)
    axs[0].set_ylabel(r"Post-routing Circuit Depth, $D$", fontsize = 16)

    fig.savefig("Figures/connectivity_D_scaling.pdf", bbox_inches = "tight")


def plot_avg_spl():
    
    colors = colormaps['viridis'].reversed()(np.linspace(0.2, 0.8, 4))
    fig, axs = plt.subplots(1,1, figsize = (5, 4), sharey = True)

    Nq_1d_vals = np.arange(1, 211, 10)
    n_square_vals = np.arange(1,15, 1)
    d_heavy_hex_vals = [1, 3, 5, 7, 9]

    Nq_square_vals = [n**2 for n in n_square_vals]
    Nq_heavy_hex_vals = [int((5*d**2-2*d-1)/2) for d in d_heavy_hex_vals]

    linear = [rx.graph_unweighted_average_shortest_path_length(rx_gen.path_graph(Nq)) for Nq in Nq_1d_vals]
    linear[0] = 0
    circular = [rx.graph_unweighted_average_shortest_path_length(rx_gen.cycle_graph(Nq)) for Nq in Nq_1d_vals]
    circular [0] = 0
    square = [rx.graph_unweighted_average_shortest_path_length(rx_gen.grid_graph(n,n)) for n in n_square_vals]
    square[0] = 0
    heavy_hex = [rx.graph_unweighted_average_shortest_path_length(rx_gen.heavy_hex_graph(d, multigraph=False)) for d in d_heavy_hex_vals]
    heavy_hex[0] = 0

    axs.plot(Nq_1d_vals, linear, "o-", label = f"Linear graph", color = colors_1[0])
    axs.plot(Nq_1d_vals, circular, "o--", label=f"Circular graph", color = colors_1[1])
    axs.plot(Nq_heavy_hex_vals, heavy_hex, "o-", label=f"Heavy-hex graph", color = colors_2[0])
    axs.plot(Nq_square_vals, square, "o--", label=f"Square graph", color = colors_2[1])
    axs.legend(fontsize=11, loc='upper left', fancybox=False, edgecolor='black', handlelength = 3)

    axs.set_xlim(0, 204)
    axs.set_ylim(-1, 70)
    axs.set_xlabel(r"Number of qubits, $N_{\rm{q}}$")
    axs.set_ylabel(r"Avg. Shortest-path Length, $\overline{d(G)}$")

    fig.savefig("Figures/connectivity_avg_spl.pdf")

if __name__ == "__main__":
    plot_avg_spl()
    plot_D_scalings()