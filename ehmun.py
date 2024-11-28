import time
import tracemalloc

class EMHUNAlgorithm:
    def __init__(self, database, min_utility):
        self.database = database
        self.min_utility = min_utility
        self.high_utility_itemsets = []
        self.visited_itemsets = set()  # Keep track of visited itemsets to prevent deep recursion

    def run(self):
        start = time.time()
        tracemalloc.start()
        X = set()
        rho, delta, eta = self.classify_items()
        secondary_X = self.calculate_secondary(rho, delta, eta)
        self.sort_items(secondary_X, eta)
        primary_X = self.calculate_primary(secondary_X)
        self.search(eta, X, primary_X, secondary_X)
        # Sort high utility itemsets by utility in descending order
        self.high_utility_itemsets.sort(key=lambda x: x[1], reverse=True)
        end = time.time()
        print(f"Time taken: {end - start} seconds")
        
        
        tracemalloc.stop()
        current, peak = tracemalloc.get_traced_memory()

        tracemalloc.stop()
        print(f"Current memory usage: {current / 1024:.2f} KB")
        print(f"Peak memory usage: {peak / 1024:.2f} KB")
        return self.high_utility_itemsets

    def classify_items(self):
        rho, delta, eta = set(), set(), set()
        item_utilities = {}
        item_signs = {}  # Track if an item has both positive and negative utility
        for transaction in self.database:
            for i in range(len(transaction["items"])):
                item = transaction["items"][i]
                profit = transaction["profit"][i] * transaction["quantities"][i]
                if item not in item_utilities:
                    item_utilities[item] = 0
                    item_signs[item] = set()
                item_utilities[item] += profit
                item_signs[item].add(1 if profit > 0 else (-1 if profit < 0 else 0))

        for item in item_utilities:
            if item_signs[item] == {1}:
                rho.add(item)
            elif item_signs[item] == {1, -1}:
                delta.add(item)
            elif item_signs[item] == {-1}:
                eta.add(item)
        return rho, delta, eta

    def calculate_secondary(self, rho, delta, eta):
        secondary = set()
        for item in rho.union(delta).union(eta):
            if self.calculate_RTWU(item) >= self.min_utility:
                secondary.add(item)
        return secondary

    def calculate_RTWU(self, item):
        total_utility = 0
        for transaction in self.database:
            if item in transaction["items"]:
                total_utility += sum(transaction["profit"][i] * transaction["quantities"][i] for i in range(len(transaction["items"])) if transaction["profit"][i] > 0)
        return total_utility

    def calculate_RSU(self, X, z):
        rsu = 0
        for transaction in self.database:
            if set(X).union({z}).issubset(transaction["items"]):
                u_X = sum(transaction["profit"][i] * transaction["quantities"][i] for i in range(len(transaction["items"])) if transaction["items"][i] in X)
                u_z = transaction["profit"][transaction["items"].index(z)] * transaction["quantities"][transaction["items"].index(z)]
                rsu += u_X + u_z + self.calculate_rru(z, transaction)
        return rsu

    def calculate_rru(self, z, transaction):
        rru = 0
        for i in range(len(transaction["items"])):
            if transaction["items"][i] != z and transaction["profit"][i] > 0:
                rru += transaction["profit"][i] * transaction["quantities"][i]
        return rru

    def sort_items(self, secondary_X, eta):
        self.sorted_secondary = self.sort_by_RTWU(secondary_X)
        self.sorted_eta = self.sort_by_RTWU(eta)

    def sort_by_RTWU(self, items):
        items_list = list(items)
        for i in range(len(items_list)):
            for j in range(i + 1, len(items_list)):
                if self.calculate_RTWU(items_list[i]) < self.calculate_RTWU(items_list[j]):
                    items_list[i], items_list[j] = items_list[j], items_list[i]
        return items_list

    def calculate_primary(self, secondary_X):
        primary = set()
        for item in secondary_X:
            if self.calculate_RSU([], item) >= self.min_utility:
                primary.add(item)
        return primary

    def search(self, eta, X, primary_X, secondary_X):
        for item in primary_X:
            beta = X.union({item})
            if frozenset(beta) in self.visited_itemsets:
                continue
            self.visited_itemsets.add(frozenset(beta))

            db_beta = self.create_projected_database(beta)
            u_beta = self.calculate_utility(beta)

            if u_beta >= self.min_utility and u_beta > 0:
                self.high_utility_itemsets.append((beta, u_beta))
                self.searchN(eta, beta, db_beta)

            new_primary = self.calculate_primary(secondary_X - {item})
            if new_primary:
                self.search(eta, beta, new_primary, secondary_X - {item})

    def create_projected_database(self, itemset):
        projected_database = []
        for transaction in self.database:
            if all(item in transaction["items"] for item in itemset):
                projected_transaction = {
                    "TID": transaction["TID"],
                    "items": [],
                    "quantities": [],
                    "profit": []
                }
                for i in range(len(transaction["items"])):
                    if transaction["items"][i] not in itemset:
                        projected_transaction["items"].append(transaction["items"][i])
                        projected_transaction["quantities"].append(transaction["quantities"][i])
                        projected_transaction["profit"].append(transaction["profit"][i])
                projected_database.append(projected_transaction)
        return projected_database

    def calculate_utility(self, itemset):
        total_utility = 0
        for transaction in self.database:
            if all(item in transaction["items"] for item in itemset):
                utility = 0
                for i in range(len(transaction["items"])):
                    if transaction["items"][i] in itemset:
                        utility += transaction["profit"][i] * transaction["quantities"][i]
                total_utility += utility
        return total_utility

    def searchN(self, eta, beta, db_beta):
        for item in eta:
            new_itemset = beta.union({item})
            if frozenset(new_itemset) in self.visited_itemsets:
                continue
            self.visited_itemsets.add(frozenset(new_itemset))

            new_utility = self.calculate_utility(new_itemset)

            if new_utility >= self.min_utility and new_utility > 0:
                self.high_utility_itemsets.append((new_itemset, new_utility))
                new_db_beta = self.create_projected_database(new_itemset)
                self.searchN(eta - {item}, new_itemset, new_db_beta)

# Input Data
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

# Running the EMHUN algorithm
emhun = EMHUNAlgorithm(dataset, min_utility=14)
result = emhun.run()

# Outputting the results
for itemset, utility in result:
    print("_".join(itemset), "-", utility)
