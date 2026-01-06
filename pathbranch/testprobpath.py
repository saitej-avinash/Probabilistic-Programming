# optimized_probcalc.py
import re
from itertools import product
from functools import lru_cache

# -------------------- Helpers --------------------

NAME_RE = re.compile(r'\b[a-zA-Z_]\w*\b')

def _vars_in(expr: str, allowed: set[str]) -> tuple[str, ...]:
    """Extract variable names used in expr and keep only those in 'allowed'."""
    return tuple(sorted(set(NAME_RE.findall(expr)) & allowed))

def _compile_expr(expr: str):
    return compile(expr, "<expr>", "eval")


# -------------------- Core Class --------------------

class ProbabilityCalculator:
    """
    Computes path probabilities given "paths" of the form:
        [
          [('cond1', 'True'/'False'), ('cond2','True'/'False'), ..., ('Statements',['return 1'])],
          ...
        ]

    Optimizations:
      - Restrict enumeration to variables actually used in (cond | given)
      - Memoize (cond, given) counts
      - Pre-compile condition expressions
      - Safe, strict "birthday" closed-form that only triggers on b<i>==b<j> chains
    """

    def __init__(self, variables, domain):
        self.variables = list(variables)
        self.domain = dict(domain)
        self.varset = set(self.variables)

    # --------- Compiled eval (tiny env) ----------
    @staticmethod
    def _eval_compiled(code_obj, env: dict):
        return bool(eval(code_obj, {}, env))

    # --------- Counting with restriction + cache ----------
    @lru_cache(maxsize=None)
    def _count_pair(self, cond: str, given: str):
        """
        Return (num_true, num_total) for cond, optionally under 'given'.
        Uses only the variables that actually appear in cond/given.
        """
        cond_vars = _vars_in(cond, self.varset)
        if given:
            given_vars = _vars_in(given, self.varset)
            # preserve order and uniqueness
            seen = set()
            vars_needed = []
            for v in cond_vars + tuple(given_vars):
                if v not in seen:
                    seen.add(v)
                    vars_needed.append(v)
            vars_needed = tuple(vars_needed)
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

    # --------- Public probability API ----------
    def compute_probability(self, condition: str) -> float:
        t, T = self._count_pair(condition, "")
        return t / T if T else 0.0

    def compute_conditional_probability(self, condition: str, given_condition: str) -> float:
        t, T = self._count_pair(condition, given_condition)
        return t / T if T else 0.0

    # --------- Strict birthday chain detection (closed form) ----------
    @staticmethod
    def _is_b_eq_b(cond: str):
        """Return (i,j) if cond is exactly 'b<i> == b<j>' with i != j; else None."""
        m = re.fullmatch(r'\s*b(\d+)\s*==\s*b(\d+)\s*', cond)
        if not m:
            return None
        i, j = int(m.group(1)), int(m.group(2))
        if i == j:
            return None
        return (i, j)

    @staticmethod
    def _path_uses_bvars(path) -> bool:
        """True iff any predicate mentions a b<idx> variable."""
        for step in path:
            if step[0] == 'Statements':
                continue
            if re.search(r'\bb\d+\b', step[0]):
                return True
        return False

    @staticmethod
    def _is_birthday_all_distinct_path(path):
        """
        Detect the 'all comparisons False' terminal path of the unrolled birthday chain:
          - at least one predicate
          - every predicate is EXACTLY 'bX == bY' with outcome 'False'
          - final step is ('Statements', ['return 0'])
        """
        if not path:
            return False
        *preds, last = path
        if not (isinstance(last, tuple) and last[0] == 'Statements' and ('return 0' in last[1])):
            return False
        if not preds:
            return False
        for cond, outcome in preds:
            if outcome != 'False':
                return False
            if ProbabilityCalculator._is_b_eq_b(cond) is None:
                return False
        return True

    @staticmethod
    def _path_returns_1(path):
        return isinstance(path[-1], tuple) and path[-1][0] == 'Statements' and ('return 1' in path[-1][1])

    def _birthday_closed_form_prob(self, path, S: int) -> float | None:
        """
        If path is an unrolled birthday-equality chain, return its exact probability.
        Otherwise return None.
        """
        # Guard: must actually be a birthday equality path
        if not self._path_uses_bvars(path):
            return None

        # 'return 1' case: find the last True equality b_i == b_j with i>j (first collision index is i)
        if self._path_returns_1(path):
            last_hit = None
            for cond, outcome in reversed(path):
                if cond == 'Statements':
                    continue
                ij = self._is_b_eq_b(cond)
                if ij and outcome == 'True':
                    i, j = ij
                    if i > j:  # we expect i to be the later variable
                        last_hit = (i, j)
                        break
            if not last_hit:
                return None
            i, _ = last_hit

            # P(no collision among first i) * P(b_i matches a SPECIFIC previous value) = p_no(i) * (1/S)
            p_no = 1.0
            for t in range(i):
                if S - t <= 0:
                    return 0.0
                p_no *= (S - t) / S
            return p_no * (1 / S)

        # 'return 0' all-distinct case
        if self._is_birthday_all_distinct_path(path):
            max_idx = -1
            for cond, outcome in path:
                for g in re.findall(r'\bb(\d+)\b', cond):
                    max_idx = max(max_idx, int(g))
            K = max_idx + 1
            if K <= 0:
                return None
            p_all = 1.0
            for t in range(K):
                if S - t <= 0:
                    return 0.0
                p_all *= (S - t) / S
            return p_all

        return None

    # --------- Main: calculate path probabilities ----------
    def calculate_path_probabilities(self, paths):
        """
        Uses closed-form for birthday-shaped paths when safe; otherwise does
        conditional counting with restricted enumeration + caching.
        """
        # infer S if all domains have same size
        unique_sizes = {len(list(v)) for v in self.domain.values()}
        S_uniform = unique_sizes.pop() if len(unique_sizes) == 1 else None

        probs = {}
        for path in paths:
            # 1) try closed-form for birthday chains
            p_cf = None
            if S_uniform is not None:
                p_cf = self._birthday_closed_form_prob(path, S_uniform)

            if p_cf is not None:
                p = p_cf
            else:
                # 2) fallback to conditional counting
                p = 1.0
                givens = []
                for condition, outcome in path[:-1]:  # skip final Statements
                    cond_str = condition if outcome == 'True' else f"not ({condition})"
                    if not givens:
                        p *= self.compute_probability(cond_str)
                    else:
                        p *= self.compute_conditional_probability(cond_str, " and ".join(givens))
                    givens.append(cond_str)

            key = tuple((c, tuple(o) if isinstance(o, list) else o) for c, o in path)
            probs[key] = p
        return probs


# -------------------- TESTS --------------------

def test_freivalds():
    print("\n=== Freivalds test ===")
    # r0, r1 ~ Uniform{0,1}
    variables = ['r0', 'r1']
    domain = {'r0': [0, 1], 'r1': [0, 1]}
    # Condition: (0*r0 + 0*r1 == 0) and (2*r0 + 0*r1 == 0)  <=>  True and (r0 == 0)
    paths = [
        [('(0*r0 + 0*r1 == 0) and (2*r0 + 0*r1 == 0)', 'True'),
         ('Statements', ['return 1'])],
        [('(0*r0 + 0*r1 == 0) and (2*r0 + 0*r1 == 0)', 'False'),
         ('Statements', ['return 0'])]
    ]
    calc = ProbabilityCalculator(variables, domain)
    probs = calc.calculate_path_probabilities(paths)
    for path, p in probs.items():
        print(f"Path: {path}\nProbability: {p:.6f}\n")

def test_pi_estimate():
    print("\n=== π-estimation (quarter circle) test ===")
    # px, py ~ Uniform{0,...,314}
    variables = ['px', 'py']
    S = 315
    domain = {'px': list(range(S)), 'py': list(range(S))}
    paths = [
        [('px**2 + py**2 <= 315*315', 'True'),  ('Statements', ['return 1'])],
        [('px**2 + py**2 <= 315*315', 'False'), ('Statements', ['return 0'])]
    ]
    calc = ProbabilityCalculator(variables, domain)
    probs = calc.calculate_path_probabilities(paths)
    for path, p in probs.items():
        print(f"Path: {path}\nProbability: {p:.6f}\n")

if __name__ == "__main__":
    test_freivalds()
    test_pi_estimate()
