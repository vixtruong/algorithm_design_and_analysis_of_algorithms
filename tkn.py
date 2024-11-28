import time
import tracemalloc

class TKN:
    def __init__(self, dataset, k):
        """
        Initialize the TKN algorithm with the dataset and value of k.
        
        Parameters:
        dataset: List of transactions, where each transaction is a dictionary containing items, quantities, and profits.
        k: Number of high utility itemsets to find.
        
        Initializes various data structures for storing intermediate results.
        """
        self.dataset = dataset
        self.k = k
        self.min_util = float('-inf')  # Set to negative infinity initially
        self.ptwu = {}  # Stores positive transaction-weighted utility for each item
        self.secondary_items = []
        self.li_structure = {}  # Stores Leaf Itemset Utility for each itemset
        self.priority_queue = []  # Stores the top-k high utility itemsets
        self.visited_itemsets = set()  # Keeps track of visited itemsets to avoid duplicates

    def calculate_ptwu(self):
        """
        Calculate the positive transaction-weighted utility (Ptwu) for each item in the dataset.
        
        PTWU is calculated by summing the utility of each transaction that contains a given item.
        This helps to identify items with potentially high utility.
        """
        for transaction in self.dataset:
            transaction_sum = sum(q * p for q, p in zip(transaction["quantities"], transaction["profit"]) if p > 0)
            for item, quantity, profit in zip(transaction["items"], transaction["quantities"], transaction["profit"]):
                if item not in self.ptwu:
                    self.ptwu[item] = 0
                self.ptwu[item] += transaction_sum

    def prune_secondary_items(self):
        """
        Determine which items should be pruned by comparing their Ptwu to the min_util value.
        
        Items with PTWU less than the current minimum utility are pruned. This helps reduce the search space.
        """
        self.secondary_items = [item for item in self.ptwu if self.ptwu[item] >= self.min_util]

    def build_li_structure(self):
        """
        Build the Leaf Itemset Utility (LIU) structure for threshold raising strategies.
        
        This structure stores the utility of each subset of items, which helps in raising the minimum utility threshold.
        """
        ordered_items = sorted(self.secondary_items, key=lambda x: self.ptwu[x])
        for i in range(len(ordered_items)):
            for j in range(i, len(ordered_items)):
                subset = tuple(ordered_items[i:j+1])
                liu_value = 0
                for t in self.dataset:
                    if all(item in t["items"] for item in subset):
                        liu_value += sum(quantity * profit for item, quantity, profit in zip(t["items"], t["quantities"], t["profit"]) if item in subset)
                self.li_structure[subset] = liu_value

    def raise_min_util(self):
        """
        Raise the minimum utility threshold using threshold raising strategies.
        
        The minimum utility threshold is raised based on the utilities stored in the LIU structure.
        This helps in pruning less promising itemsets early.
        """
        li_values = list(self.li_structure.values())
        li_values.sort(reverse=True)
        if len(li_values) >= self.k:
            self.min_util = max(self.min_util, li_values[self.k - 1])

    def explore_candidates(self, current_itemset, dataset_projection):
        """
        Explore candidate itemsets recursively using depth-first search.
        
        Parameters:
        current_itemset: The current itemset being explored.
        dataset_projection: A subset of transactions relevant to the current itemset.
        
        This method recursively extends the current itemset by adding new items and evaluates their utility.
        """
        sorted_itemset = tuple(sorted(current_itemset))
        if sorted_itemset in self.visited_itemsets:
            return
        self.visited_itemsets.add(sorted_itemset)

        utility = 0
        for transaction in dataset_projection:
            if all(item in transaction["items"] for item in sorted_itemset):
                utility += sum(quantity * profit for item, quantity, profit in zip(transaction["items"], transaction["quantities"], transaction["profit"]) if item in sorted_itemset)

        if utility >= self.min_util:
            self.priority_queue.append((sorted_itemset, utility))
            self.priority_queue.sort(key=lambda x: x[1], reverse=True)
            if len(self.priority_queue) > self.k:
                self.priority_queue.pop()
            if len(self.priority_queue) == self.k:
                self.min_util = self.priority_queue[-1][1]

        for item in self.secondary_items:
            if item not in current_itemset and (not current_itemset or item > current_itemset[-1]):
                new_itemset = current_itemset + (item,)
                new_dataset_projection = [t for t in dataset_projection if all(x in t["items"] for x in new_itemset)]
                self.explore_candidates(new_itemset, new_dataset_projection)

    def run(self):
        """
        Execute the TKN algorithm to find the top-k high utility itemsets.
        
        This method runs all the steps of the TKN algorithm in sequence:
        1. Calculate PTWU for each item.
        2. Prune secondary items based on PTWU.
        3. Build the LIU structure.
        4. Raise the minimum utility threshold.
        5. Explore candidate itemsets to find top-k high utility itemsets.
        
        Returns:
        A list of the top-k high utility itemsets along with their utilities.
        """
        start_time = time.time()
        tracemalloc.start()
        self.calculate_ptwu()
        self.prune_secondary_items()
        self.build_li_structure()
        self.raise_min_util()
        self.explore_candidates((), self.dataset)
        end_time = time.time()
        tracemalloc.stop()
        print("Execution Time: {:.4f} seconds".format(end_time - start_time))
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"Current memory usage: {current / 1024:.2f} KB")
        print(f"Peak memory usage: {peak / 1024:.2f} KB")
        return self.priority_queue

def read_data(file_name="data.txt"):
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

# Top-K mining
k = 4
tkn = TKN(dataset, k)
top_k_results = tkn.run()
for result in top_k_results:
    print(result)