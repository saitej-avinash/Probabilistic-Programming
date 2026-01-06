import ast
from itertools import product
from collections import defaultdict
import numpy as np

# ====================================================================
# AST PARSING CLASSES (ConditionNode and ConditionTreeBuilder)
# ====================================================================

class ConditionNode:
    """A class representing a node in the condition tree."""
    def __init__(self, condition=None):
        self.condition = condition
        self.true_statements = []  # Store statements inside the True branch
        self.false_statements = []  # Store statements inside the False branch
        self.true_branch = None
        self.false_branch = None
        self.next_condition = None  # For sequential conditions at the same level

    def __repr__(self):
        return (
            f"ConditionNode(condition={self.condition}, "
            f"true_statements={self.true_statements}, false_statements={self.false_statements}, "
            f"true_branch={self.true_branch}, false_branch={self.false_branch}, "
            f"next_condition={self.next_condition})"
        )


class ConditionTreeBuilder(ast.NodeVisitor):
    def __init__(self):
        self.root = None
        self.current = None
        self.last_top_level_if = None  # tracker for sequential IFs

    def visit_If(self, node):
        # 1. Create a new condition node
        condition = ast.unparse(node.test)
        condition_node = ConditionNode(condition=condition)

        # 2. Link the node: sequential vs nested IFs
        if self.current is None:
            # Top level
            if self.root is None:
                self.root = condition_node
                self.last_top_level_if = condition_node
            else:
                # Sequential top-level IF
                self.last_top_level_if.next_condition = condition_node
                self.last_top_level_if = condition_node
        else:
            # Inside a branch (nested)
            if not self.root:
                self.root = condition_node

        # Store the current node as the parent for the next level of nesting
        parent = self.current
        self.current = condition_node

        # 3. Process the True branch
        true_branch_builder = ConditionTreeBuilder()
        for stmt in node.body:
            if isinstance(stmt, ast.If):
                true_branch_builder.visit(stmt)
            else:
                condition_node.true_statements.append(ast.unparse(stmt))
        condition_node.true_branch = true_branch_builder.root

        # 4. Process the False branch (orelse)
        false_branch_builder = ConditionTreeBuilder()
        if node.orelse:
            for stmt in node.orelse:
                if isinstance(stmt, ast.If):
                    false_branch_builder.visit(stmt)
                else:
                    condition_node.false_statements.append(ast.unparse(stmt))
        else:
            # Implicit else (do nothing)
            condition_node.false_statements.append("pass")

        condition_node.false_branch = false_branch_builder.root

        # 5. Restore the current pointer to the parent
        self.current = parent

    def visit_FunctionDef(self, node):
        """Handle function definitions by visiting their body."""
        for stmt in node.body:
            self.visit(stmt)

    def build_tree(self, code):
        tree = ast.parse(code)
        self.visit(tree)
        return self.root


def check_for_return(statements):
    """Check if a list of statements contains a 'return'."""
    return any(stmt.strip().startswith('return') for stmt in statements)


def extract_paths(node, current_path=None, all_paths=None):
    """
    Recursively extract all paths from the condition tree.
    Continue through next_condition only if a 'return' was not hit.
    """
    if current_path is None:
        current_path = []
    if all_paths is None:
        all_paths = []

    if not node:
        return all_paths

    # --- TRUE Branch Traversal ---
    true_path = current_path + [(node.condition, "True")]
    true_has_return = False

    if node.true_statements:
        true_has_return = check_for_return(node.true_statements)
        true_path.append(("Statements", node.true_statements))

    if node.true_branch:
        extract_paths(node.true_branch, true_path, all_paths)
    elif node.next_condition and not true_has_return:
        extract_paths(node.next_condition, true_path, all_paths)
    else:
        all_paths.append(true_path)

    # --- FALSE Branch Traversal ---
    false_path = current_path + [(node.condition, "False")]
    false_has_return = False

    if node.false_statements:
        false_has_return = check_for_return(node.false_statements)
        false_path.append(("Statements", node.false_statements))

    if node.false_branch:
        extract_paths(node.false_branch, false_path, all_paths)
    elif node.next_condition and not false_has_return:
        extract_paths(node.next_condition, false_path, all_paths)
    else:
        all_paths.append(false_path)

    return all_paths


# ====================================================================
# PROBABILITY CALCULATION CLASS
# ====================================================================

class ProbabilityCalculator:
    def __init__(self, variables, domain):
        self.variables = variables
        self.domain = domain

    def evaluate_condition(self, condition, case):
        local_env = {var: val for var, val in zip(self.variables, case)}
        try:
            return bool(eval(condition, {}, local_env))
        except Exception:
            return False

    def count_valid_cases(self, condition, condition_filter=None):
        count = 0
        total = 0
        for case in product(*[self.domain[var] for var in self.variables]):
            if condition_filter and not self.evaluate_condition(condition_filter, case):
                continue
            total += 1
            if self.evaluate_condition(condition, case):
                count += 1
        return count, total

    def compute_probability(self, condition):
        total_domain_size = 1
        for var in self.variables:
            total_domain_size *= len(self.domain[var])
        count, _ = self.count_valid_cases(condition)
        return count / total_domain_size if total_domain_size else 0.0

    def compute_conditional_probability(self, condition, given_condition):
        count, total = self.count_valid_cases(condition, condition_filter=given_condition)
        return count / total if total else 0.0

    def calculate_path_probabilities(self, paths):
        path_probabilities = {}
        for path in paths:
            probability = 1.0
            previous_conditions = []

            for segment in path:
                if segment[0] == 'Statements':
                    # Do not alter probability on statement segments
                    continue

                condition, outcome = segment
                if outcome == 'True':
                    condition_str = condition
                elif outcome == 'False':
                    condition_str = f"not ({condition})"
                else:
                    continue

                if not previous_conditions:
                    branch_probability = self.compute_probability(condition_str)
                else:
                    given_condition_str = " and ".join(previous_conditions)
                    branch_probability = self.compute_conditional_probability(condition_str, given_condition_str)

                probability *= branch_probability
                # (optional) clamp tiny negatives due to float noise
                if probability < 0 and abs(probability) < 1e-15:
                    probability = 0.0

                previous_conditions.append(condition_str)

            key = tuple((cond, tuple(outcome) if isinstance(outcome, list) else outcome) for cond, outcome in path)
            path_probabilities[key] = probability

        return path_probabilities


# ====================================================================
# 3. FreivaldsAutomation Module (Generator and Calculator)
# ====================================================================

def generate_freivalds_code(A, B, C, N, MOD=2):
    """
    Generates the conditional code string for a SINGLE run (k=1) of 
    Freivald's algorithm using symbolic variables r_0, r_1, ..., r_{N-1},
    with arithmetic performed modulo MOD.
    """
    A_np = np.array(A, dtype=int)
    B_np = np.array(B, dtype=int)
    C_np = np.array(C, dtype=int)

    D_np = A_np @ B_np - C_np  # integer D = AB - C

    conditional_blocks = []

    # Iterate through the N components of the Dr vector
    for i in range(N):
        terms = []
        for j in range(N):
            coeff = int(D_np[i, j])
            if coeff != 0:
                r_var = f"r_{j}"
                if coeff == 1:
                    term = r_var
                elif coeff == -1:
                    term = f"-{r_var}"
                else:
                    term = f"{coeff}*{r_var}"
                terms.append(term)

        # Linear combo for row i
        if not terms:
            expression = "0"
        else:
            expression = " + ".join(terms).replace("+ -", "- ")

        # --- KEY: Test modulo MOD ---
        # Reject if ((row · r) % MOD) != 0; accept only if ALL rows == 0 mod MOD.
        condition = f"(({expression}) % {MOD}) != 0"
        conditional_blocks.append(condition)

    # Assemble the final code string (if-elif-else chain)
    code_lines = []
    if conditional_blocks:
        code_lines.append(f"if {conditional_blocks[0]}:")
        code_lines.append("    return False")
        for condition in conditional_blocks[1:]:
            code_lines.append(f"elif {condition}:")
            code_lines.append("    return False")

    code_lines.append("else:")
    code_lines.append("    return True")

    variables = [f"r_{j}" for j in range(N)]
    return "\n".join(code_lines), variables


def calculate_freivalds_k_prob(A, B, C, N, K, MOD=2):
    """
    Calculates the final False Positive probability for K independent runs 
    by analyzing the single-run (k=1) code (modular arithmetic with MOD).
    """
    # 1. Generate the K=1 code string
    freivald_k1_code, variables = generate_freivalds_code(A, B, C, N, MOD=MOD)

    # 2. Domain for r_j (0/1)
    domain = {var: [0, 1] for var in variables}

    # 3. Build Tree and Extract Paths for K=1
    builder = ConditionTreeBuilder()
    condition_tree = builder.build_tree(freivald_k1_code)
    extracted_paths = extract_paths(condition_tree)

    # 4. Calculate Path Probabilities for K=1
    calculator = ProbabilityCalculator(variables, domain)
    path_probabilities = calculator.calculate_path_probabilities(extracted_paths)

    # 5. Sum ALL paths that contain 'return True' in any Statements segment
    p_fp_1 = 0.0
    for path, prob in path_probabilities.items():
        for node, payload in path:
            if node == 'Statements':
                payload_tuple = payload if isinstance(payload, (list, tuple)) else [payload]
                if any(stmt.strip() == 'return True' for stmt in payload_tuple):
                    p_fp_1 += prob
                    break  # avoid double-counting this path

    # 6. K runs (independent)
    p_fp_k = p_fp_1 ** K
    results = {
        "k1_code": freivald_k1_code,
        "p_fp_1": p_fp_1,
        "k_runs": K,
        "p_fp_k": p_fp_k,
        "p_cr_k": 1.0 - p_fp_k,
        "modulus": MOD,
    }
    return results


# ====================================================================
# DRIVER CODE (Test with User's Matrices)
# ====================================================================

if __name__ == "__main__":
    # Input Parameters
    A = [[1, 2], [3, 4]]
    B = [[1, 1], [1, 1]]
    C = [[1, 2], [1, 4]]  # Incorrect product
    N = 2                 # Matrix Dimension
    K = 3                 # Number of Freivalds runs to simulate
    MOD = 2               # arithmetic over F_2 for classic Freivalds

    # Calculate and print results
    results = calculate_freivalds_k_prob(A, B, C, N, K, MOD=MOD)

    print("--- Freivald's Algorithm Automated Analysis ---")
    print(f"Input Matrices: A({N}x{N}) * B({N}x{N}) vs C({N}x{N})")
    print(f"Modulus (field): {results['modulus']}")
    print(f"Number of Independent Runs (K): {results['k_runs']}")
    print("-" * 40)

    print("\n[STEP 1: K=1 Conditional Code Generated]")
    print(results['k1_code'])

    print("\n[STEP 2: Single Run Probability Analysis]")
    print(f"P(False Positive | k=1): {results['p_fp_1']:.6f}")
    print(f"P(Correct Rejection | k=1): {1.0 - results['p_fp_1']:.6f}")

    print("\n[STEP 3: Final K-Run Probability Calculation]")
    print(f"P(Total False Positive | K={K}): P(FP|k=1)^K = ({results['p_fp_1']:.3f})^{K} = {results['p_fp_k']:.6f}")
    print(f"P(Total Correct Rejection | K={K}): 1 - P(FP|K) = {results['p_cr_k']:.6f}")
