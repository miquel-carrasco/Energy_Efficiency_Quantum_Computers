# Energy Efficiency of Quantum computers

This repository contains the python scripts and data used to estimate the energy efficiencies of different quantum computing platforms, based on the method presented in our paper of the same name: [text](https://arxiv.org/abs/2605.15090).


The **qcenergy** folder includes the modules with the **components** and quantum computing **platforms** classes, as well as functions that return the shortest-path length of the considered **connectivity graphs**. The platforms included in our study are grouped in three main families that have Computer class of their own:

### Solid-state computers:
- Superconducting
- Spin qubits

### Atom-based computers:
- Trapped ions
- Neutral atoms

### Photonic computers:
- Linear optics on-chip photonic computers


In this repository, there are all the scripts that we used to produce the results shown in our work. Mainly, there are five files corresponding to each of the platforms, as well as two extra scripts that plot the effect of the **basis gate set** and **connectivity constraints** on the final depth of quantum circuits.

In 