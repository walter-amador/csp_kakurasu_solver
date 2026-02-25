import time

class KakurasuSolver:
    def __init__(self, n, row_targets, col_targets, algo, heuristic):
        self.n = n
        self.row_targets = row_targets
        self.col_targets = col_targets
        self.algo = algo
        self.heuristic = heuristic
        self.nodes_visited = 0
        self.start_time = 0
        self.timeout_limit = 60.0

    def solve(self):
        self.nodes_visited = 0
        self.start_time = time.time()
        
        if self.algo == "AC-3 Algorithm":
            yield from self.backtrack_ac3({})
        else:
            yield from self.backtrack({})
            
        # If we finish without yielding a terminal state
        yield ({}, self.nodes_visited, "no_solution")

    def is_consistent(self, assignment):
        # Check rows
        for r in range(1, self.n + 1):
            current_sum = sum(c for c in range(1, self.n + 1) if assignment.get((r, c)) == 1)
            if current_sum > self.row_targets[r - 1]:
                return False
            max_possible = current_sum + sum(c for c in range(1, self.n + 1) if (r, c) not in assignment)
            if max_possible < self.row_targets[r - 1]:
                return False
                
        # Check cols
        for c in range(1, self.n + 1):
            current_sum = sum(r for r in range(1, self.n + 1) if assignment.get((r, c)) == 1)
            if current_sum > self.col_targets[c - 1]:
                return False
            max_possible = current_sum + sum(r for r in range(1, self.n + 1) if (r, c) not in assignment)
            if max_possible < self.col_targets[c - 1]:
                return False
                
        return True

    def get_unassigned_vars(self, assignment):
        return [(r, c) for r in range(1, self.n + 1) for c in range(1, self.n + 1) if (r, c) not in assignment]

    def select_unassigned_variable(self, assignment):
        unassigned = self.get_unassigned_vars(assignment)
        if not unassigned:
            return None
            
        if self.heuristic == "MRV":
            def count_valid(var):
                valid = 0
                for val in [0, 1]:
                    assignment[var] = val
                    if self.is_consistent(assignment):
                        valid += 1
                    del assignment[var]
                return valid
            return min(unassigned, key=count_valid)
            
        elif self.heuristic == "MCV":
            def degree(var):
                r, c = var
                return sum(1 for c2 in range(1, self.n + 1) if (r, c2) not in assignment) + \
                       sum(1 for r2 in range(1, self.n + 1) if (r2, c) not in assignment)
            return max(unassigned, key=degree)
            
        return unassigned[0]

    def order_domain_values(self, var, assignment):
        if self.heuristic == "LCV":
            def count_future_valid(val):
                assignment[var] = val
                if not self.is_consistent(assignment):
                    del assignment[var]
                    return -1
                total_valid = 0
                for u_var in self.get_unassigned_vars(assignment):
                    for u_val in [0, 1]:
                        assignment[u_var] = u_val
                        if self.is_consistent(assignment):
                            total_valid += 1
                        del assignment[u_var]
                del assignment[var]
                return total_valid
            return sorted([0, 1], key=count_future_valid, reverse=True)
            
        return [1, 0]

    def backtrack(self, assignment):
        if time.time() - self.start_time > self.timeout_limit:
            yield (assignment.copy(), self.nodes_visited, "timeout")
            return

        if len(assignment) == self.n * self.n:
            if self.is_consistent(assignment):
                yield (assignment.copy(), self.nodes_visited, "solved")
            return

        var = self.select_unassigned_variable(assignment)
        if not var:
            return

        for val in self.order_domain_values(var, assignment):
            assignment[var] = val
            self.nodes_visited += 1
            
            yield (assignment.copy(), self.nodes_visited, "searching")
            
            if self.is_consistent(assignment):
                for result in self.backtrack(assignment):
                    yield result
                    if result[2] in ["solved", "timeout"]:
                        return
                        
            del assignment[var]
            yield (assignment.copy(), self.nodes_visited, "searching")

    def backtrack_ac3(self, assignment):
        domains = {}
        for r in range(1, self.n + 1):
            for c in range(1, self.n + 1):
                if (r, c) in assignment:
                    domains[(r, c)] = [assignment[(r, c)]]
                else:
                    domains[(r, c)] = [0, 1]
                    
        if not self.ac3(domains):
            return
            
        if time.time() - self.start_time > self.timeout_limit:
            yield (assignment.copy(), self.nodes_visited, "timeout")
            return

        unassigned = [v for v in domains if len(domains[v]) > 1]
        if not unassigned:
            final_assignment = {v: domains[v][0] for v in domains}
            yield (final_assignment, self.nodes_visited, "solved")
            return
            
        var = unassigned[0]
        for val in domains[var]:
            assignment[var] = val
            self.nodes_visited += 1
            yield (assignment.copy(), self.nodes_visited, "searching")
            
            for result in self.backtrack_ac3(assignment):
                yield result
                if result[2] in ["solved", "timeout"]:
                    return
                    
            del assignment[var]
            yield (assignment.copy(), self.nodes_visited, "searching")

    def ac3(self, domains):
        changed = True
        while changed:
            changed = False
            for r in range(1, self.n + 1):
                min_sum = sum(c for c in range(1, self.n + 1) if domains[(r, c)] == [1])
                max_sum = sum(c for c in range(1, self.n + 1) if 1 in domains[(r, c)])
                if min_sum > self.row_targets[r - 1] or max_sum < self.row_targets[r - 1]:
                    return False
                for c in range(1, self.n + 1):
                    if len(domains[(r, c)]) == 2:
                        if min_sum + c > self.row_targets[r - 1]:
                            domains[(r, c)] = [0]
                            changed = True
                        elif max_sum - c < self.row_targets[r - 1]:
                            domains[(r, c)] = [1]
                            changed = True
                            
            for c in range(1, self.n + 1):
                min_sum = sum(r for r in range(1, self.n + 1) if domains[(r, c)] == [1])
                max_sum = sum(r for r in range(1, self.n + 1) if 1 in domains[(r, c)])
                if min_sum > self.col_targets[c - 1] or max_sum < self.col_targets[c - 1]:
                    return False
                for r in range(1, self.n + 1):
                    if len(domains[(r, c)]) == 2:
                        if min_sum + r > self.col_targets[c - 1]:
                            domains[(r, c)] = [0]
                            changed = True
                        elif max_sum - r < self.col_targets[c - 1]:
                            domains[(r, c)] = [1]
                            changed = True
        return True