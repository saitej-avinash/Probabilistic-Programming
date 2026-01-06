#!/usr/bin/env python3
import re
from itertools import product
from functools import lru_cache

# -------------------- Utility: parse vars used in an expression --------------------
NAME_RE = re.compile(r'\b[a-zA-Z_]\w*\b')

def _vars_in(expr: str, allowed: set[str]) -> tuple[str, ...]:
    # Extract variable names used in expr and keep only those in 'allowed'
    return tuple(sorted(set(NAME_RE.findall(expr)) & allowed))

def _compile_expr(expr: str):
    return compile(expr, "<expr>", "eval")

# -------------------- Core Probability Calculator --------------------
class ProbabilityCalculator:
    def __init__(self, variables, domain):
        """
        variables: list of variable names (strings) used by the paths
        domain: dict var -> iterable of values (list/range/etc.)
        """
        self.variables = variables
        self.domain = domain
        self.varset = set(variables)

    # ---------- Core evaluation (compiled + small env) ----------
    @staticmethod
    def _eval_compiled(code_obj, env: dict):
        return bool(eval(code_obj, {}, env))

    # ---------- Counting with restriction to needed vars + caching ----------
    @lru_cache(maxsize=None)
    def _count_pair(self, cond: str, given: str):
        """
        Count (num_true, num_total) for 'cond' optionally under 'given'.
        Both 'cond' and 'given' are strings. Empty given ("") means unconditional.
        Caches results across repeated calls.
        """
        cond_vars = _vars_in(cond, self.varset)
        if given:
            given_vars = _vars_in(given, self.varset)
            # Keep order stable and avoid duplicates
            vars_needed = tuple(dict.fromkeys(cond_vars + tuple(v for v in given_vars if v not in cond_vars)))
        else:
            vars_needed = cond_vars

        var_lists = [self.domain[v] for v in vars_needed]
        cond_code = _compile_expr(cond)
        given_code = _compile_expr(given) if given else None

        num_true = 0
        num_total = 0
        for tup in product(*var_lists):
            env = {v: val for v, val in zip(vars_needed, tup)}
            if given_code and not self._eval_compiled(given_code, env):
                continue
            num_total += 1
            if self._eval_compiled(cond_code, env):
                num_true += 1
        return num_true, num_total

    # ---------- Public probability API ----------
    def compute_probability(self, condition: str) -> float:
        t, T = self._count_pair(condition, "")
        return t / T if T else 0.0

    def compute_conditional_probability(self, condition: str, given_condition: str) -> float:
        t, T = self._count_pair(condition, given_condition)
        return t / T if T else 0.0

    # ---------- Birthday closed-form detection (strict) ----------
    @staticmethod
    def _match_birthday_eq(cond: str):
        """Return (i, j) iff cond is exactly 'b<i> == b<j>' with i>j; else None."""
        m = re.fullmatch(r'\s*b(\d+)\s*==\s*b(\d+)\s*', cond)
        if not m:
            return None
        i, j = int(m.group(1)), int(m.group(2))
        return (i, j) if i > j else None

    @staticmethod
    def _is_birthday_return1_step(step):
        """Detect a birthday 'hit' step ('bI == bJ','True') with I>J."""
        cond, outcome = step
        if outcome != 'True':
            return None
        return ProbabilityCalculator._match_birthday_eq(cond)

    @staticmethod
    def _birthday_all_distinct_K(path):
        """
        If 'path' is the canonical all-distinct birthday path:
          - every predicate is ('bI == bJ','False') with I>J
          - final step is ('Statements',['return 0'])
        return K = 1 + max index among used b-variables; else None.
        """
        if not path:
            return None
        *preds, last = path
        if not (isinstance(last, tuple) and last[0] == 'Statements'
                and last[1] in (['return 0'], ('return 0',))):
            return None

        max_idx = -1
        for cond, outcome in preds:
            if outcome != 'False':
                return None
            hit = ProbabilityCalculator._match_birthday_eq(cond)
            if not hit:
                return None
            i, j = hit
            max_idx = max(max_idx, i, j)

        return (max_idx + 1) if max_idx >= 0 else None

    @staticmethod
    def _path_returns_1(path):
        return (isinstance(path[-1], tuple)
                and path[-1][0] == 'Statements'
                and ('return 1' in path[-1][1]))

    def _birthday_closed_form_prob(self, path, S: int) -> float | None:
        """
        If the path is a strict birthday unrolled path, return its exact probability.
        Otherwise return None.
        Rules:
          - 'return 1' paths with last positive equality 'b_i == b_j' get p_no(i) * (1/S)
          - The all-distinct 'return 0' path gets ∏_{t=0}^{K-1} (1 - t/S)
        """
        # 'return 1' (collision) case
        if self._path_returns_1(path):
            last_hit = None
            for step in path[::-1]:
                if step[0] == 'Statements':
                    continue
                hit = self._is_birthday_return1_step(step)
                if hit:
                    last_hit = hit
                    break
            if not last_hit:
                return None
            i, _ = last_hit
            p_no = 1.0
            for t in range(i):
                if S - t <= 0:
                    return 0.0
                p_no *= (S - t) / S
            return p_no * (1.0 / S)

        # 'return 0' (all distinct) case
        K = self._birthday_all_distinct_K(path)
        if K is not None:
            p_all = 1.0
            for t in range(K):
                if S - t <= 0:
                    return 0.0
                p_all *= (S - t) / S
            return p_all

        return None  # not a recognized birthday path

    # ---------- Main path probability routine ----------
    def calculate_path_probabilities(self, paths):
        """
        Compute probabilities for all extracted paths.
        Uses closed-form for strict birthday paths when possible,
        otherwise falls back to conditional counting with variable restriction + caching.
        """
        # Infer uniform S if all domains have the same size
        unique_sizes = {len(list(v)) for v in self.domain.values()}
        S_uniform = unique_sizes.pop() if len(unique_sizes) == 1 else None

        probs = {}
        for path in paths:
            # 1) Try birthday closed-form (only if uniform S)
            p_cf = None
            if S_uniform is not None:
                p_cf = self._birthday_closed_form_prob(path, S_uniform)

            if p_cf is not None:
                p = p_cf
            else:
                # 2) Fallback: conditional counting along the path
                p = 1.0
                givens = []
                for condition, outcome in path[:-1]:  # Exclude the final ('Statements', ...)
                    cond_str = condition if outcome == 'True' else f"not ({condition})"
                    if not givens:
                        p *= self.compute_probability(cond_str)
                    else:
                        p *= self.compute_conditional_probability(cond_str, " and ".join(givens))
                    givens.append(cond_str)

            # Clean FP noise and ensure non-negative
            if abs(p) < 1e-15:
                p = 0.0
            p = max(p, 0.0)

            key = tuple((c, tuple(o) if isinstance(o, list) else o) for c, o in path)
            probs[key] = p
        return probs

# -------------------- Example Paths --------------------

def build_birthday_paths(K: int):
    """
    Build the "first-collision" unrolled birthday paths for people b0..bK
    plus the final all-distinct path.
    """
    paths = []
    # For each i=1..K: add i collision paths against earlier j<i
    for i in range(1, K + 1):
        prefix = []
        # all previous equalities must be False
        for ii in range(1, i):
            for jj in range(ii):
                prefix.append((f"b{ii} == b{jj}", 'False'))
        # now add each j<i as a True hit path
        for j in range(i):
            hit = prefix + [(f"b{i} == b{j}", 'True'), ('Statements', ['return 1'])]
            paths.append(hit)
    # all-distinct (everything False, then return 0)
    all_false = []
    for i in range(1, K + 1):
        for j in range(i):
            all_false.append((f"b{i} == b{j}", 'False'))
    paths.append(all_false + [('Statements', ['return 0'])])
    return paths

def demo_randminoftwo():
    print("\n=== Demo: randminoftwo_paths (x < y) with x,y in {1..9} ===")
    variables = ['x', 'y']
    domain = {'x': list(range(1, 10)), 'y': list(range(1, 10))}
    randminoftwo_paths = [
        [('x < y', 'True'),  ('Statements', ['return 1'])],
        [('x < y', 'False'), ('Statements', ['return 0'])]
    ]
    calc = ProbabilityCalculator(variables, domain)
    probs = calc.calculate_path_probabilities(randminoftwo_paths)
    for path, p in probs.items():
        print(f"Path: {path}\nProbability: {p:.6f}\n")

    # Sanity: 36/81 and 45/81
    #assert abs(probs[(('x < y','True'),('Statements',('return 1',)))] - 36/81) < 1e-12
    #assert abs(probs[(('x < y','False'),('Statements',('return 0',)))] - 45/81) < 1e-12
    #print("Assertions passed for randminoftwo.\n")

def demo_randmaxoftwo():
    print("\n=== Demo: randmaxoftwo_paths (x > y) with x,y in {1..9} ===")
    variables = ['x', 'y']
    domain = {'x': list(range(1, 10)), 'y': list(range(1, 10))}
    randminoftwo_paths = [
        [('x > y', 'True'),  ('Statements', ['return 1'])],
        [('x > y', 'False'), ('Statements', ['return 0'])]
    ]
    calc = ProbabilityCalculator(variables, domain)
    probs = calc.calculate_path_probabilities(randminoftwo_paths)
    for path, p in probs.items():
        print(f"Path: {path}\nProbability: {p:.6f}\n")

    # Sanity: 36/81 and 45/81
    ##assert abs(probs[(('x > y','True'),('Statements',('return 1',)))] - 36/81) < 1e-12
    #assert abs(probs[(('x > y','False'),('Statements',('return 0',)))] - 45/81) < 1e-12
    #print("Assertions passed for randminoftwo.\n")

def demo_randeqoftwo():
    print("\n=== Demo: randeqoftwo_paths (x == y) with x,y in {1..9} ===")
    variables = ['x', 'y']
    domain = {'x': list(range(1, 10)), 'y': list(range(1, 10))}
    randminoftwo_paths = [
        [('x == y', 'True'),  ('Statements', ['return 1'])],
        [('x == y', 'False'), ('Statements', ['return 0'])]
    ]
    calc = ProbabilityCalculator(variables, domain)
    probs = calc.calculate_path_probabilities(randminoftwo_paths)
    for path, p in probs.items():
        print(f"Path: {path}\nProbability: {p:.6f}\n")

    # Sanity: 36/81 and 45/81
    #assert abs(probs[(('x == y','True'),('Statements',('return 1',)))] - 36/81) < 1e-12
    #assert abs(probs[(('x == y','False'),('Statements',('return 0',)))] - 45/81) < 1e-12
    #print("Assertions passed for randeqoftwo.\n")

def demo_birthday(K=5, S=365):
    #print(f"\n=== Demo: Birthday Paradox paths for K={K} (people b0..b{K}) with S={S} days ===")
    # Build variables b0..bK and uniform domain 0..S-1
    variables = [f"b{i}" for i in range(K + 1)]
    domain = {v: list(range(S)) for v in variables}

    paths = build_birthday_paths(K)
    calc = ProbabilityCalculator(variables, domain)
    probs = calc.calculate_path_probabilities(paths)

    # Print a few sample paths and totals
    total_prob = 0.0
    printed = 0
    for path, p in probs.items():
        if printed < 6:  # show a handful
            print(f"Path: {path}\nProbability: {p:.12f}\n")
            printed += 1
        total_prob += p
    #print(f"Total probability over all birthday paths (should be 1): {total_prob:.12f}")
    #assert abs(total_prob - 1.0) < 1e-9
    #print("Assertions passed for birthday paradox paths.\n")

# -------------------- Main --------------------
if __name__ == "__main__":
    #demo_randminoftwo()
    #demo_randmaxoftwo()
    #demo_randeqoftwo()
    demo_birthday(K=23, S=365)
