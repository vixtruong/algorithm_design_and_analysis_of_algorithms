import time

class EHMIN:
    def __init__(self, database, min_util):
        self.database = database
        self.min_util = min_util
        self.global_lists = {}
        self.results = []
        self.patterns = {}

    def load_external_utility(self):
        for transaction in self.database:
            for item, profit in zip(transaction['items'], transaction['profit']):
                if item not in self.global_lists:
                    self.global_lists[item] = {'profit': profit, 'transactions': []}

    def first_scan(self):
        for transaction in self.database:
            for item, quantity, profit in zip(transaction['items'], transaction['quantities'], transaction['profit']):
                if item in self.global_lists:
                    self.global_lists[item]['transactions'].append({
                        'tid': transaction['TID'],
                        'quantity': quantity,
                        'utility': quantity * profit
                    })

    def prune_low_utility_items(self):
        for transaction in self.database:
            for item in transaction['items']:
                if item not in self.global_lists:
                    self.global_lists[item] = {'profit': 0, 'transactions': []}
                    for i, t_item in enumerate(transaction['items']):
                        if t_item == item:
                            self.global_lists[item]['transactions'].append({
                                'tid': transaction['TID'],
                                'quantity': transaction['quantities'][i],
                                'utility': transaction['quantities'][i] * transaction['profit'][i]
                            })

    def calculate_pattern_utility(self, pattern):
        utility = 0
        for transaction in self.database:
            if all(item in transaction['items'] for item in pattern):
                indices = [transaction['items'].index(item) for item in pattern]
                transaction_utility = sum(transaction['quantities'][i] * transaction['profit'][i] for i in indices)
                utility += transaction_utility
        return utility

    def generate_combinations(self, items, length):
        if length == 0:
            return [[]]
        if not items:
            return []
        with_first = [[items[0]] + rest for rest in self.generate_combinations(items[1:], length - 1)]
        without_first = self.generate_combinations(items[1:], length)
        return with_first + without_first

    def mine_high_utility_patterns(self):
        items = list(self.global_lists.keys())
        processed_patterns = set()
        for length in range(1, len(items) + 1):
            for combination in self.generate_combinations(items, length):
                combination = tuple(combination)
                if combination not in processed_patterns:
                    utility = self.calculate_pattern_utility(combination)
                    if utility >= self.min_util:
                        self.results.append((combination, utility))
                    processed_patterns.add(combination)

    def run(self):
        start_time = time.time()
        self.load_external_utility()
        self.first_scan()
        self.prune_low_utility_items()
        self.mine_high_utility_patterns()
        self.results.sort(key=lambda x: (-x[1], x[0]))
        end_time = time.time()
        execution_time = end_time - start_time
        print(f'Time taken: {execution_time} seconds')
        return self.results


database = [
    {
        "TID": "T1",
        "items": ["a", "b", "d", "h"],
        "quantities": [2, 3, 1, 1],
        "profit": [2, 1, 3, -1],
    },
    {"TID": "T2", "items": ["a", "c", "e", "h"], "quantities": [2, 4, 2, 3], "profit": [2, 1, -1, -1]},
    {
        "TID": "T3",
        "items": ["b", "c", "d", "e", "f"],
        "quantities": [6, 3, 1, 3, 2],
        "profit": [1, 1, 3, -1, 5],
    },
    {
        "TID": "T4",
        "items": ["a", "b", "c", "g"],
        "quantities": [4, 3, 3, 2],
        "profit": [2, 1, 1, -1],
    },
    {"TID": "T5", "items": ["b", "d", "e", "g" ,"h"], "quantities": [4, 4, 1, 2, 1], "profit": [1, 3, -1, -1, -1]},
]

min_util = 14
ehmin = EHMIN(database, min_util)
results = ehmin.run()
for pattern, utility in results:
    print("_".join(pattern), "-", utility)