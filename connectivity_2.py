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


    colors = colormaps['viridis'].reversed()(np.linspace(0.2, 0.8, 4))

    # print(f"Avg. linear graph shortest path length (50 qubits): {linear_avg_spl}")
    # print(f"Avg. circular graph shortest path length (50 qubits): {circular_avg_spl}")
    # print(f"Avg. square graph shortest path length (49 qubits): {square_avg_spl}")
    # print(f"Avg. heavy-hex graph shortest path length (57 qubits): {heavy_hex_avg_spl}")


    fig, axs = plt.subplots(1,3, figsize = (14, 4.5), sharey = True)

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
        axs[i].plot(D0_vals, linear_D, label = f"Linear graph (50 qubits)", zorder = 0 )
        axs[i].plot(D0_vals, circular_D, label = f"Circular graph (50 qubits)", zorder = 5)
        axs[i].plot(D0_vals, square_D, label = f"Square graph (49 qubits)", zorder = 10)
        axs[i].plot(D0_vals, heavy_hex_D, label = f"Heavy-hex graph ({n_heavy_hex} qubits)", zorder = 9)
        axs[i].plot(D0_vals, D0_vals, label = f"Fully connected graph", zorder = 12, color = "k")
        
        axs[i].set_title(rf"$\alpha_{{\rm{{2q}}}}={alpha}$", pad = 10)
        axs[i].set_xlim(0,max(D0_vals))

    # axs[0].set_yscale("log")
    axs[0].set_ylim(-10, 2.5e4)
    axs[0].legend(fontsize=11, loc='upper left', fancybox=False, edgecolor='black')
    fig.supxlabel(r'Pre-routing Circuit Depth, $D_{0}$', fontsize = 16, y = 0.04)
    axs[0].set_ylabel(r"Post-routing Circuit Depth, $D$", fontsize = 16)

    fig.savefig("Figures/connectivity_D_scaling.pdf", bbox_inches = "tight")


def plot_avg_spl():
    
    colors = colormaps['viridis'].reversed()(np.linspace(0.2, 0.8, 4))

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

    plt.plot(Nq_1d_vals, linear, "o-", label = f"Linear graph")
    plt.plot(Nq_1d_vals, circular, "o-", label=f"Circular graph")
    plt.plot(Nq_square_vals, square, "o-", label=f"Square graph")
    plt.plot(Nq_heavy_hex_vals, heavy_hex, "o-", label=f"Heavy-hex graph")
    plt.legend(fontsize=11, loc='upper left', fancybox=False, edgecolor='black', handlelength = 3)

    plt.xlim(0, 204)
    plt.xlabel(r"Number of qubits, $N_{\rm{q}}$")
    plt.ylabel(r"Avg. Shortest-path Length, $\overline{d(G)}$")


    plt.savefig("Figures/connectivity_avg_spl.pdf")

if __name__ == "__main__":
    plot_avg_spl()
    plot_D_scalings()