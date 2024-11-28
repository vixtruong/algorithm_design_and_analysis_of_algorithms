import random
import tracemalloc
import time

start = time.time()
tracemalloc.start()

# Calculate Transaction Utility (TU)
def calculate_tu(transaction):
    """
    Calculate the transaction utility for a given transaction.
    
    Parameters:
    - transaction (dict): A dictionary representing a transaction, including quantities and profit for each item.
    
    Returns:
    - int: The transaction utility, calculated as the sum of quantity * profit for each item in the transaction.
    """
    return sum(q * p for q, p in zip(transaction["quantities"], transaction["profit"]))

# Initial Population based on TU
def initialize_population(transactions, population_size):
    """
    Initialize the population by selecting transactions with the highest utility.
    
    Parameters:
    - transactions (list): A list of transactions.
    - population_size (int): The size of the population to initialize.
    
    Returns:
    - list: A list of sets representing the initial population of solutions.
    """
    # Sort transactions by their TU values in descending order
    sorted_transactions = sorted(transactions, key=calculate_tu, reverse=True)
    # Select top transactions as initial population
    initial_population = [set(txn["items"]) for txn in sorted_transactions[:population_size]]
    return initial_population

# Fitness Evaluation
def evaluate_fitness(solution, transactions):
    """
    Evaluate the fitness of a solution by calculating its utility across all transactions.
    
    Parameters:
    - solution (set): A set of items representing a solution.
    - transactions (list): A list of transactions.
    
    Returns:
    - int: The total utility of the solution across all transactions.
    """
    utility = 0
    for txn in transactions:
        if solution.issubset(set(txn["items"])):
            utility += sum([txn["quantities"][i] * txn["profit"][i] for i in range(len(txn["items"])) if txn["items"][i] in solution])
    return utility

# Crossover Operator
def crossover(parent1, parent2):
    """
    Perform crossover between two parent solutions to create offspring.
    
    Parameters:
    - parent1 (set): The first parent solution.
    - parent2 (set): The second parent solution.
    
    Returns:
    - tuple: Two child solutions resulting from the crossover.
    """
    child1 = parent1.copy()
    child2 = parent2.copy()
    # Swap a random item from parent1 with a random item from parent2
    if len(parent1) > 0 and len(parent2) > 0:
        item_from_parent1 = random.choice(list(parent1))
        item_from_parent2 = random.choice(list(parent2))
        child1.discard(item_from_parent1)
        child1.add(item_from_parent2)
        child2.discard(item_from_parent2)
        child2.add(item_from_parent1)
    return child1, child2

# Mutation Operator
def mutate(solution, all_items, mutation_rate=0.1):
    """
    Apply mutation to a solution by randomly adding or removing items.
    
    Parameters:
    - solution (set): The solution to mutate.
    - all_items (set): A set of all possible items.
    - mutation_rate (float): The probability of applying a mutation.
    
    Returns:
    - set: The mutated solution.
    """
    if random.random() < mutation_rate:
        if len(solution) > 0:
            solution.remove(random.choice(list(solution)))  # Remove a random item
        if random.random() < mutation_rate:
            solution.add(random.choice(list(all_items)))  # Add a random item from all available items
    return solution

# Genetic Algorithm
def tkhuim_ga(transactions, population_size=None, generations=None, mutation_rate=None):
    """
    Run the Top-K High Utility Itemset Mining Genetic Algorithm.
    
    Parameters:
    - transactions (list): A list of transactions.
    - population_size (int, optional): The number of solutions in the population. Default is 4.
    - generations (int, optional): The number of generations to evolve. Default is 5.
    - mutation_rate (float, optional): The probability of mutation. Default is 0.1.
    
    Returns:
    - tuple: A list of top solutions and their corresponding fitness values.
    """
    # Set default values if parameters are not provided
    if population_size is None:
        population_size = 4
    if generations is None:
        generations = 5
    if mutation_rate is None:
        mutation_rate = 0.1

    # Initialize population
    population = initialize_population(transactions, population_size)
    all_items = set(item for txn in transactions for item in txn["items"])

    # Track unique solutions
    unique_solutions = set()

    # Iterate through generations
    for generation in range(generations):
        # Evaluate fitness of each solution
        fitness_values = [evaluate_fitness(solution, transactions) for solution in population]
        # Select the top two solutions based on fitness
        sorted_population = [solution for _, solution in sorted(zip(fitness_values, population), reverse=True)]
        parent1, parent2 = sorted_population[0], sorted_population[1]

        # Crossover
        child1, child2 = crossover(parent1, parent2)

        # Mutation
        child1 = mutate(child1, all_items, mutation_rate)
        child2 = mutate(child2, all_items, mutation_rate)

        # Update population
        population = [parent1, parent2, child1, child2]

        # Add solutions to unique set
        for sol in population:
            unique_solutions.add(frozenset(sol))

    # Extract unique solutions and sort by fitness
    unique_population = [set(sol) for sol in unique_solutions]
    top_solutions = sorted(unique_population, key=lambda sol: evaluate_fitness(sol, transactions), reverse=True)[:population_size]
    top_fitness = [evaluate_fitness(sol, transactions) for sol in top_solutions]
    return top_solutions, top_fitness

# Allow user input for parameters
population_size = 100
generations = 30
mutation_rate = 0.1

# Dataset
def read_data(file_name="chessdata.txt"):
    """
    Read and parse the dataset from the given file.

    Parameters:
    file_name (str): The name of the file containing the dataset. The default is "ehmintable.txt".

    Returns:
    list: A list of dictionaries representing the transactions. Each dictionary contains:
        - 'TID': Transaction ID.
        - 'items': List of item names in the transaction.
        - 'profit': List of profit per item in the transaction.
        - 'quantities': List of quantities of each item in the transaction.

    Example:
    >>> dataset = read_data()
    >>> print(dataset)
    [
        {'TID': 'T1', 'items': ['apple', 'banana'], 'profit': [5, 3], 'quantities': [2, 3]},
        {'TID': 'T2', 'items': ['apple', 'date'], 'profit': [8, 7], 'quantities': [1, 5]},
        ...
    ]
    """
    with open(file_name, "r") as file:
        data = file.read()

    dataset = eval(data)
    return dataset

# Dataset
dataset = read_data()

# Run the Genetic Algorithm
top_solutions, top_fitness = tkhuim_ga(dataset, population_size, generations, mutation_rate)
for i in range(len(top_solutions)):
    print(f"Solution {i + 1}: {top_solutions[i]}, U: {top_fitness[i]}")

end = time.time()

print("Execution Time: {:.4f} seconds".format(end - start))

tracemalloc.stop()

current, peak = tracemalloc.get_traced_memory()

tracemalloc.stop()
print(f"Current memory usage: {current / 1024:.2f} KB")
print(f"Peak memory usage: {peak / 1024:.2f} KB")
