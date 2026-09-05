import tkinter as tk
from tkinter import messagebox
import random
import math
import colorsys

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def generate_distinct_colors(n):
    colors = []
    h = 0.618033988749895
    s = 0.7
    v = 0.9
    for i in range(n):
        h += h
        h %= 1
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        colors.append('#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255)))
    return colors

def decode_chromosome(chromosome, depot, customers, num_vehicles, vehicle_capacity, customer_demands):
    routes = []
    current_route = []
    current_capacity_used = 0
    vehicle_count = 0
    customers_assigned_count = 0
    unassigned_customers = []

    if num_vehicles <= 0:
        return [], False

    for customer_index in chromosome:
        demand = customer_demands[customer_index]

        if current_capacity_used + demand <= vehicle_capacity:
            current_route.append(customer_index)
            current_capacity_used += demand
            customers_assigned_count += 1
        else:
            if current_route:
                routes.append(current_route)
                vehicle_count += 1

            if vehicle_count < num_vehicles:
                current_route = [customer_index]
                current_capacity_used = demand
                customers_assigned_count += 1
            else:
                unassigned_customers.append(customer_index)

    if current_route:
        routes.append(current_route)
        vehicle_count += 1

    all_customers_assigned = customers_assigned_count == len(customer_demands)
    vehicle_limit_respected = vehicle_count <= num_vehicles

    is_feasible = all_customers_assigned and vehicle_limit_respected

    return routes, is_feasible

def calculate_route_distance(route_indices, depot, customers):
    total = 0
    if not route_indices:
        return 0

    route_coords = [customers[i] for i in route_indices]

    total += distance(depot, route_coords[0])

    for i in range(len(route_coords) - 1):
        total += distance(route_coords[i], route_coords[i+1])

    total += distance(route_coords[-1], depot)

    return total

def vrp_fitness(chromosome, depot, customers, num_vehicles, vehicle_capacity, customer_demands, penalty_factor=10000):
    routes_indices, is_feasible = decode_chromosome(
        chromosome, depot, customers, num_vehicles, vehicle_capacity, customer_demands
    )

    total_distance = 0
    for route_indices in routes_indices:
        total_distance += calculate_route_distance(route_indices, depot, customers)

    penalty = 0
    if not is_feasible:
        assigned_count = sum(len(route) for route in routes_indices)
        unassigned_count = len(customer_demands) - assigned_count
        penalty += unassigned_count * penalty_factor

    return total_distance + penalty

def initial_population_vrp(num_customers, size):
    population = []
    if num_customers <= 0:
        return [[] for _ in range(size)]

    customer_indices = list(range(num_customers))
    for _ in range(size):
        individual = customer_indices.copy()
        random.shuffle(individual)
        population.append(individual)
    return population

def selection_vrp(population, fitness_func):
    if not population:
        return []
    k = 5
    k = min(k, len(population))
    selected = random.sample(population, k)
    selected.sort(key=fitness_func)
    return selected[0]

def crossover_vrp(parent1, parent2):
    size = len(parent1)
    if size == 0:
        return []

    start, end = sorted([random.randint(0, size-1) for _ in range(2)])
    if start == end:
        end = (end + 1) % size
        if start > end: start, end = end, start

    child = [None] * size
    child[start:end] = parent1[start:end]

    parent2_sequence = [item for item in parent2 if item not in child]

    current_parent2_idx = 0
    for i in range(size):
        if child[i] is None:
            child[i] = parent2_sequence[current_parent2_idx]
            current_parent2_idx += 1

    return child

def mutate_vrp(chromosome, rate=0.02):
    if not chromosome:
        return
    size = len(chromosome)
    for i in range(size):
        if random.random() < rate:
            j = random.randint(0, size-1)
            chromosome[i], chromosome[j] = chromosome[j], chromosome[i]

def genetic_algorithm_vrp(customers, depot, num_vehicles, vehicle_capacity, customer_demands,
                          pop_size=100, generations=1000, mutation_rate=0.02):
    num_customers = len(customers)
    if num_customers == 0:
        return [], 0, 0, []

    current_fitness_func = lambda chrom: vrp_fitness(
        chrom, depot, customers, num_vehicles, vehicle_capacity, customer_demands
    )

    pop = initial_population_vrp(num_customers, pop_size)

    best_chromosome = min(pop, key=current_fitness_func)
    best_fitness_val = current_fitness_func(best_chromosome)
    best_fitness_per_gen = [best_fitness_val]

    for gen in range(generations):
        new_pop = []
        new_pop.append(best_chromosome.copy())

        while len(new_pop) < pop_size:
            parent1 = selection_vrp(pop, current_fitness_func)
            parent2 = selection_vrp(pop, current_fitness_func)
            child = crossover_vrp(parent1, parent2)
            mutate_vrp(child, mutation_rate)
            new_pop.append(child)

        pop = new_pop

        current_best_chromosome = min(pop, key=current_fitness_func)
        current_fitness_val = current_fitness_func(current_best_chromosome)

        if current_fitness_val < best_fitness_val:
            best_chromosome = current_best_chromosome.copy()
            best_fitness_val = current_fitness_val

        best_fitness_per_gen.append(best_fitness_val)

    best_routes_indices, is_feasible = decode_chromosome(
        best_chromosome, depot, customers, num_vehicles, vehicle_capacity, customer_demands
    )

    actual_total_distance = 0
    for route_indices in best_routes_indices:
        actual_total_distance += calculate_route_distance(route_indices, depot, customers)

    return best_routes_indices, actual_total_distance, len(best_routes_indices), best_fitness_per_gen

# --- Differential Evolution Implementation ---

def permutation_to_vector(perm):
    n = len(perm)
    ranks = [0]*n
    for idx, val in enumerate(perm):
        ranks[val] = idx / (n-1 if n > 1 else 1)
    return ranks

def vector_to_permutation(vec):
    sorted_indices = sorted(range(len(vec)), key=lambda i: vec[i])
    return sorted_indices

def differential_evolution_vrp(customers, depot, num_vehicles, vehicle_capacity, customer_demands,
                              pop_size=100, generations=1000, F=0.8, CR=0.7):
    num_customers = len(customers)
    if num_customers == 0:
        return [], 0, 0, []

    fitness_func = lambda perm: vrp_fitness(
        perm, depot, customers, num_vehicles, vehicle_capacity, customer_demands
    )

    population = []
    for _ in range(pop_size):
        perm = list(range(num_customers))
        random.shuffle(perm)
        population.append(permutation_to_vector(perm))

    best_idx = 0
    best_fitness = fitness_func(vector_to_permutation(population[0]))
    best_fitness_per_gen = [best_fitness]

    for gen in range(generations):
        new_population = []
        for i in range(pop_size):
            idxs = list(range(pop_size))
            idxs.remove(i)
            a, b, c = random.sample(idxs, 3)
            x_a, x_b, x_c = population[a], population[b], population[c]

            mutant = [x_a[j] + F * (x_b[j] - x_c[j]) for j in range(num_customers)]
            mutant = [max(0, min(1, val)) for val in mutant]

            trial = []
            j_rand = random.randint(0, num_customers-1)
            for j in range(num_customers):
                if random.random() < CR or j == j_rand:
                    trial.append(mutant[j])
                else:
                    trial.append(population[i][j])

            trial_perm = vector_to_permutation(trial)
            target_perm = vector_to_permutation(population[i])

            trial_fitness = fitness_func(trial_perm)
            target_fitness = fitness_func(target_perm)

            if trial_fitness < target_fitness:
                new_population.append(trial)
                if trial_fitness < best_fitness:
                    best_fitness = trial_fitness
                    best_idx = i
            else:
                new_population.append(population[i])

        population = new_population
        best_fitness_per_gen.append(best_fitness)

    best_perm = vector_to_permutation(population[best_idx])

    best_routes_indices, is_feasible = decode_chromosome(
        best_perm, depot, customers, num_vehicles, vehicle_capacity, customer_demands
    )

    actual_total_distance = 0
    for route_indices in best_routes_indices:
        actual_total_distance += calculate_route_distance(route_indices, depot, customers)

    return best_routes_indices, actual_total_distance, len(best_routes_indices), best_fitness_per_gen

# --- GUI class without plotting ---

class VRPSolverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VRP Solver with Genetic Algorithm and Differential Evolution")

        self.input_frame = tk.Frame(root)
        self.input_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        tk.Label(self.input_frame, text="Depot (x,y):").grid(row=0, column=0, sticky="w")
        self.depot_x = tk.Entry(self.input_frame, width=10)
        self.depot_x.grid(row=0, column=1, sticky="ew", padx=2)
        self.depot_y = tk.Entry(self.input_frame, width=10)
        self.depot_y.grid(row=0, column=2, sticky="ew", padx=2)
        self.depot_x.insert(0, "50")
        self.depot_y.insert(0, "50")
        self.generate_depot_button = tk.Button(self.input_frame, text="Generate Random Depot", command=self.generate_random_depot)
        self.generate_depot_button.grid(row=0, column=3, padx=5)

        tk.Label(self.input_frame, text="Number of Customers:").grid(row=1, column=0, sticky="w")
        self.num_customers_entry = tk.Entry(self.input_frame, width=10)
        self.num_customers_entry.grid(row=1, column=1, sticky="ew", padx=2)
        self.num_customers_entry.insert(0, "10")
        self.generate_customers_button = tk.Button(self.input_frame, text="Generate Random Customers", command=self.generate_random_customers)
        self.generate_customers_button.grid(row=1, column=3, padx=5)

        tk.Label(self.input_frame, text="Customers (x,y,demand per line):").grid(row=2, column=0, columnspan=4, sticky="w")
        self.customers_text = tk.Text(self.input_frame, width=40, height=8)
        self.customers_text.grid(row=3, column=0, columnspan=4, sticky="nsew", padx=2, pady=2)
        self.customers_text.insert(tk.END, "10,20,10\n80,10,15\n20,90,12\n70,80,20\n30,40,8\n90,60,18\n40,10,11\n60,30,14\n5,70,9\n75,25,16\n")

        tk.Label(self.input_frame, text="Number of Vehicles:").grid(row=4, column=0, sticky="w")
        self.num_vehicles_entry = tk.Entry(self.input_frame, width=10)
        self.num_vehicles_entry.grid(row=4, column=1, sticky="ew", padx=2)
        self.num_vehicles_entry.insert(0, "3")

        tk.Label(self.input_frame, text="Vehicle Capacity:").grid(row=5, column=0, sticky="w")
        self.vehicle_capacity_entry = tk.Entry(self.input_frame, width=10)
        self.vehicle_capacity_entry.grid(row=5, column=1, sticky="ew", padx=2)
        self.vehicle_capacity_entry.insert(0, "50")

        tk.Label(self.input_frame, text="Population Size:").grid(row=6, column=0, sticky="w")
        self.pop_size_entry = tk.Entry(self.input_frame, width=10)
        self.pop_size_entry.grid(row=6, column=1, sticky="ew", padx=2)
        self.pop_size_entry.insert(0, "200")

        tk.Label(self.input_frame, text="Generations:").grid(row=7, column=0, sticky="w")
        self.generations_entry = tk.Entry(self.input_frame, width=10)
        self.generations_entry.grid(row=7, column=1, sticky="ew", padx=2)
        self.generations_entry.insert(0, "1000")

        tk.Label(self.input_frame, text="Mutation Rate (GA only):").grid(row=8, column=0, sticky="w")
        self.mutation_rate_entry = tk.Entry(self.input_frame, width=10)
        self.mutation_rate_entry.grid(row=8, column=1, sticky="ew", padx=2)
        self.mutation_rate_entry.insert(0, "0.02")

        tk.Label(self.input_frame, text="Differential Weight F (DE only):").grid(row=9, column=0, sticky="w")
        self.F_entry = tk.Entry(self.input_frame, width=10)
        self.F_entry.grid(row=9, column=1, sticky="ew", padx=2)
        self.F_entry.insert(0, "0.8")

        tk.Label(self.input_frame, text="Crossover Rate CR (DE only):").grid(row=10, column=0, sticky="w")
        self.CR_entry = tk.Entry(self.input_frame, width=10)
        self.CR_entry.grid(row=10, column=1, sticky="ew", padx=2)
        self.CR_entry.insert(0, "0.7")

        # Algorithm choice: GA or DE
        tk.Label(self.input_frame, text="Algorithm:").grid(row=11, column=0, sticky="w")
        self.algorithm_var = tk.StringVar(value="GA")
        tk.Radiobutton(self.input_frame, text="Genetic Algorithm", variable=self.algorithm_var, value="GA").grid(row=11, column=1, sticky="w")
        tk.Radiobutton(self.input_frame, text="Differential Evolution", variable=self.algorithm_var, value="DE").grid(row=11, column=2, sticky="w")

        self.solve_button = tk.Button(self.input_frame, text="Solve VRP", command=self.solve_vrp)
        self.solve_button.grid(row=12, column=0, columnspan=4, pady=10)

        self.output_frame = tk.Frame(root)
        self.output_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        tk.Label(self.output_frame, text="Results:").grid(row=0, column=0, sticky="w")
        self.output = tk.Text(self.output_frame, width=50, height=10)
        self.output.grid(row=1, column=0, sticky="nsew")

        self.canvas_frame = tk.Frame(root, bg="white", bd=2, relief="groove")
        self.canvas_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=5, pady=5)

        self.canvas_width = 600
        self.canvas_height = 600
        self.canvas = tk.Canvas(self.canvas_frame, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(expand=True, fill="both")

        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(1, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=1)
        self.input_frame.grid_columnconfigure(2, weight=1)
        self.input_frame.grid_columnconfigure(3, weight=1)
        self.input_frame.grid_rowconfigure(3, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_rowconfigure(1, weight=1)

        self.padding = 30
        self.point_size = 5
        self.route_colors = []

    def generate_random_depot(self):
        rand_x = random.randint(0, 100)
        rand_y = random.randint(0, 100)
        self.depot_x.delete(0, tk.END)
        self.depot_x.insert(0, str(rand_x))
        self.depot_y.delete(0, tk.END)
        self.depot_y.insert(0, str(rand_y))

    def generate_random_customers(self):
        try:
            num_customers = int(self.num_customers_entry.get())
            if num_customers <= 0:
                 messagebox.showwarning("Input Warning", "Number of customers must be positive.")
                 return

            self.customers_text.delete("1.0", tk.END)
            for _ in range(num_customers):
                rand_x = random.randint(0, 100)
                rand_y = random.randint(0, 100)
                rand_demand = random.randint(1, 20)
                self.customers_text.insert(tk.END, f"{rand_x},{rand_y},{rand_demand}\n")

        except ValueError:
            messagebox.showerror("Input Error", "Invalid number of customers. Please enter an integer.")

    def parse_input(self):
        depot = None
        customers = []
        customer_demands = []
        num_vehicles = 0
        vehicle_capacity = 0

        try:
            depot_x = float(self.depot_x.get())
            depot_y = float(self.depot_y.get())
            depot = (depot_x, depot_y)
        except ValueError:
            raise ValueError("Invalid Depot coordinates. Please enter numbers (e.g., 50, 50).")

        customers_raw = self.customers_text.get("1.0", tk.END).strip().split("\n")
        if not customers_raw or customers_raw == ['']:
             pass
        else:
            for i, line in enumerate(customers_raw):
                if line.strip() == "": continue
                try:
                    parts = line.split(",")
                    if len(parts) != 3:
                        raise ValueError(f"Invalid format on line {i+1}. Expected 'x,y,demand'.")
                    x, y = float(parts[0].strip()), float(parts[1].strip())
                    demand = float(parts[2].strip())
                    if demand < 0:
                         raise ValueError(f"Demand cannot be negative on line {i+1}.")
                    customers.append((x, y))
                    customer_demands.append(demand)
                except ValueError as e:
                    raise ValueError(f"Invalid Customer data on line {i+1}: '{line}'. {e}")

        try:
            num_vehicles = int(self.num_vehicles_entry.get())
            if num_vehicles <= 0:
                 raise ValueError("Number of vehicles must be a positive integer.")
        except ValueError:
            raise ValueError("Invalid Number of Vehicles. Please enter a positive integer.")

        try:
            vehicle_capacity = float(self.vehicle_capacity_entry.get())
            if vehicle_capacity <= 0:
                 raise ValueError("Vehicle capacity must be a positive number.")
        except ValueError:
            raise ValueError("Invalid Vehicle Capacity. Please enter a positive number.")

        return depot, customers, customer_demands, num_vehicles, vehicle_capacity

    def solve_vrp(self):
        try:
            depot, customers, customer_demands, num_vehicles, vehicle_capacity = self.parse_input()

            pop_size = int(self.pop_size_entry.get())
            generations = int(self.generations_entry.get())
            mutation_rate = float(self.mutation_rate_entry.get())
            F = float(self.F_entry.get())
            CR = float(self.CR_entry.get())

            if pop_size <= 0 or generations <= 0:
                 raise ValueError("Population size and Generations must be positive integers.")

            if len(customers) > 0 and num_vehicles == 0:
                 raise ValueError("Cannot solve VRP with customers and zero vehicles.")

            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, f"Solving VRP using {self.algorithm_var.get()}...\n")
            self.root.update_idletasks()

            if self.algorithm_var.get() == "GA":
                best_routes_indices, total_distance, vehicles_used, _ = genetic_algorithm_vrp(
                    customers, depot, num_vehicles, vehicle_capacity, customer_demands,
                    pop_size=pop_size, generations=generations, mutation_rate=mutation_rate
                )
            else:
                best_routes_indices, total_distance, vehicles_used, _ = differential_evolution_vrp(
                    customers, depot, num_vehicles, vehicle_capacity, customer_demands,
                    pop_size=pop_size, generations=generations, F=F, CR=CR
                )

            self.output.insert(tk.END, f"Algorithm finished.\n")
            self.output.insert(tk.END, f"Total Distance of Best Solution: {total_distance:.2f}\n")
            self.output.insert(tk.END, f"Vehicles Used: {vehicles_used}\n")
            self.output.insert(tk.END, "\nRoutes:\n")

            best_routes_coords = [[customers[i] for i in route_indices] for route_indices in best_routes_indices]

            if not best_routes_coords:
                 self.output.insert(tk.END, "No customers to visit.\n")
            else:
                for i, route_coords in enumerate(best_routes_coords):
                    route_str = f"Vehicle {i+1}: Depot"
                    current_capacity = 0
                    for j, customer_coord in enumerate(route_coords):
                        try:
                            original_index = customers.index(customer_coord)
                            demand = customer_demands[original_index]
                            route_str += f" -> C{original_index+1}{customer_coord} (Demand: {demand})"
                            current_capacity += demand
                        except ValueError:
                            route_str += f" -> {customer_coord} (Demand: N/A - Error)"

                    route_str += f" -> Depot (Distance: {calculate_route_distance([customers.index(c) for c in route_coords], depot, customers):.2f}, Capacity Used: {current_capacity})\n"
                    self.output.insert(tk.END, route_str)

            self.draw_routes(depot, customers, best_routes_coords)

        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
            self.output.insert(tk.END, f"Error: {ve}\n")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            self.output.insert(tk.END, f"Error: {e}\n")

    def map_coords_to_canvas(self, x, y, min_x, max_x, min_y, max_y):
        range_x = max_x - min_x
        range_y = max_y - min_y

        if range_x == 0: min_x -= 10; max_x += 10; range_x = 20.0
        if range_y == 0: min_y -= 10; max_y += 10; range_y = 20.0

        scale_x = (self.canvas_width - 2 * self.padding) / range_x
        scale_y = (self.canvas_height - 2 * self.padding) / range_y

        canvas_x = self.padding + (x - min_x) * scale_x
        canvas_y = self.canvas_height - self.padding - (y - min_y) * scale_y

        return canvas_x, canvas_y

    def draw_routes(self, depot, customers, routes_coords):
        self.canvas.delete("all")

        all_points = [depot] + customers

        if not all_points:
             return

        min_x = min(p[0] for p in all_points)
        max_x = max(p[0] for p in all_points)
        min_y = min(p[1] for p in all_points)
        max_y = max(p[1] for p in all_points)

        if min_x == max_x:
             min_x -= 10
             max_x += 10
        if min_y == max_y:
             min_y -= 10
             max_y += 10

        depot_canvas_x, depot_canvas_y = self.map_coords_to_canvas(depot[0], depot[1], min_x, max_x, min_y, max_y)
        self.canvas.create_rectangle(depot_canvas_x - self.point_size * 1.5, depot_canvas_y - self.point_size * 1.5,
                                     depot_canvas_x + self.point_size * 1.5, depot_canvas_y + self.point_size * 1.5,
                                     fill="red", outline="black", tags="depot")
        self.canvas.create_text(depot_canvas_x, depot_canvas_y - self.point_size * 2, text="Depot", tags="depot")

        customer_canvas_coords = {}
        for i, customer in enumerate(customers):
            cust_canvas_x, cust_canvas_y = self.map_coords_to_canvas(customer[0], customer[1], min_x, max_x, min_y, max_y)
            customer_canvas_coords[customer] = (cust_canvas_x, cust_canvas_y)
            self.canvas.create_oval(cust_canvas_x - self.point_size, cust_canvas_y - self.point_size,
                                    cust_canvas_x + self.point_size, cust_canvas_y + self.point_size,
                                    fill="blue", outline="black", tags="customer")
            self.canvas.create_text(cust_canvas_x, cust_canvas_y - self.point_size * 1.5, text=f"C{i+1}", tags="customer_label")

        if routes_coords:
            self.route_colors = generate_distinct_colors(len(routes_coords))

            for i, route_coords in enumerate(routes_coords):
                route_color = self.route_colors[i % len(self.route_colors)]

                prev_p_canvas = (depot_canvas_x, depot_canvas_y)

                for j, current_p_coords in enumerate(route_coords):
                    current_p_canvas = customer_canvas_coords.get(current_p_coords)

                    if prev_p_canvas and current_p_canvas:
                         self.canvas.create_line(prev_p_canvas[0], prev_p_canvas[1], current_p_canvas[0], current_p_canvas[1],
                                                 fill=route_color, width=2, arrow=tk.LAST, tags=f"route_{i}")
                    prev_p_canvas = current_p_canvas

                if prev_p_canvas and (depot_canvas_x, depot_canvas_y):
                     self.canvas.create_line(prev_p_canvas[0], prev_p_canvas[1], depot_canvas_x, depot_canvas_y,
                                             fill=route_color, width=2, arrow=tk.LAST, tags=f"route_{i}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VRPSolverGUI(root)
    root.mainloop()
