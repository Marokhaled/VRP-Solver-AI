# 🚚 Vehicle Routing Problem Solver

A Python-based **Vehicle Routing Problem (VRP) Solver** that uses two optimization techniques — **Genetic Algorithm (GA)** and **Differential Evolution (DE)** — to find efficient vehicle routes while considering vehicle capacity constraints.

The project includes an interactive **Tkinter GUI** that allows users to enter or randomly generate customers, configure vehicles and algorithm parameters, solve the routing problem, and visualize the resulting routes.

## 📌 Project Overview

The Vehicle Routing Problem (VRP) is a classic optimization problem where the objective is to determine efficient routes for a fleet of vehicles serving multiple customers from a central depot.

This project approaches the problem using two evolutionary optimization methods:

* 🧬 **Genetic Algorithm (GA)**
* 🔬 **Differential Evolution (DE)**

The solver evaluates candidate solutions based on the total travel distance and applies penalties when vehicle or customer constraints are violated.

## ✨ Features

* Interactive graphical user interface using **Tkinter**
* Genetic Algorithm-based VRP optimization
* Differential Evolution-based VRP optimization
* Vehicle capacity constraints
* Configurable number of vehicles
* Configurable population size and number of generations
* Adjustable Genetic Algorithm mutation rate
* Adjustable Differential Evolution parameters (`F` and `CR`)
* Random depot generation
* Random customer generation
* Customer demand handling
* Route distance calculation
* Route visualization on a 2D canvas
* Displays total distance and vehicles used
* Displays the generated routes and customer demands

## 🧠 Algorithms

### Genetic Algorithm

The Genetic Algorithm represents a solution as a permutation of customer indices.

The algorithm uses:

1. Initial population generation
2. Fitness evaluation
3. Tournament-style selection
4. Crossover
5. Mutation
6. Elitism
7. Iterative improvement over multiple generations

The objective is to minimize the total route distance while satisfying the vehicle constraints.

### Differential Evolution

The project also implements Differential Evolution for permutation-based routing.

The implementation converts permutations into numerical vectors, performs differential mutation and crossover, and converts the resulting vectors back into customer permutations for evaluation.

## 🖥️ User Interface

The application provides controls for:

* Depot coordinates
* Number of customers
* Customer coordinates and demands
* Number of vehicles
* Vehicle capacity
* Population size
* Number of generations
* Genetic Algorithm mutation rate
* Differential Evolution differential weight (`F`)
* Differential Evolution crossover rate (`CR`)
* Algorithm selection

After solving, the application displays the calculated routes and visualizes them on the canvas.

## ⚙️ Requirements

The project uses Python's standard library.

### Required

* Python 3.x
* Tkinter

The main libraries used are:

```text
tkinter
random
math
colorsys
```

No external Python packages are required by the current implementation.

## 🚀 How to Run

### 1. Clone the repository

```bash
git clone https://github.com/Marokhaled/VRP-Solver-AI.git
```

### 2. Navigate to the project directory

```bash
cd VRP-Solver-AI
```

### 3. Run the application

```bash
python "AI Project.py"
```

> On some Windows installations, you may need to use `python3` instead of `python`.

## 📝 Example Input

Customers can be entered using the following format:

```text
x,y,demand
```

For example:

```text
10,20,10
80,10,15
20,90,12
70,80,20
30,40,8
```

The application also provides a **Generate Random Customers** option for automatically creating customer coordinates and demands.

## 📊 Optimization Parameters

| Parameter          | Description                                        |
| ------------------ | -------------------------------------------------- |
| Number of Vehicles | Maximum number of vehicles available               |
| Vehicle Capacity   | Maximum demand that a vehicle can carry            |
| Population Size    | Number of candidate solutions in the population    |
| Generations        | Number of optimization iterations                  |
| Mutation Rate      | Mutation probability used by the Genetic Algorithm |
| F                  | Differential weight used by Differential Evolution |
| CR                 | Crossover rate used by Differential Evolution      |

## 🗺️ Route Visualization

After the optimization process completes, the application displays the resulting routes graphically.

* **Depot** is displayed as the central starting/ending location.
* **Customers** are displayed as individual points.
* **Routes** are drawn between the depot and customers.
* Different routes are assigned different colors for easier visualization.

Each vehicle starts at the depot, visits its assigned customers, and returns to the depot.

## 🎯 Objective

The primary objective is to minimize the total distance traveled by all vehicles while ensuring that customer demands and vehicle limitations are respected.

The fitness function combines route distance with a penalty for infeasible solutions.

## 🛠️ Technologies Used

* **Python**
* **Tkinter**
* **Genetic Algorithms**
* **Differential Evolution**
* **Combinatorial Optimization**
* **Vehicle Routing Problem (VRP)**

## 📂 Project Structure

```text
VRP-Solver-AI/
│
├── AI Project.py
└── README.md
```

## 🔮 Future Improvements

Possible future improvements include:

* Add support for larger datasets
* Improve the constraint-handling mechanism
* Add performance comparison between GA and DE
* Add convergence graphs
* Add export functionality for optimized routes
* Improve the graphical interface
* Add additional optimization algorithms
* Separate the application into multiple Python modules for better maintainability

## 👤 Author

**Marwan Khaled**

---

⭐ If you find this project useful or interesting, feel free to star the repository!

