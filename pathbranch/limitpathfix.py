import re
from itertools import product
from functools import lru_cache

NAME_RE = re.compile(r'\b[a-zA-Z_]\w*\b')

def _vars_in(expr: str, allowed: set[str]) -> tuple[str, ...]:
    # Extract variable names used in expr and keep only those in 'allowed'
    return tuple(sorted(set(NAME_RE.findall(expr)) & allowed))

def _compile_expr(expr: str):
    return compile(expr, "<expr>", "eval")

class ProbabilityCalculator:
    def __init__(self, variables, domain, pmf=None):
        """
        variables: list[str] of variable names in conditions/paths
        domain: dict[str, Iterable] mapping var -> list/range of values
        pmf: optional dict[str, dict[value, prob]] for an independent product distribution.
             Example for biased coin with parameter p:
               pmf = {'a': {0:p, 1:1-p}, 'b': {0:p, 1:1-p}}
        """
        self.variables = variables
        self.domain = domain
        self.varset = set(variables)
        self.pmf = pmf  # optional

    # ---------- Core evaluation (compiled + small env) ----------
    @staticmethod
    def _eval_compiled(code_obj, env: dict):
        return bool(eval(code_obj, {}, env))

    # ---------- Counting / weighted-summing with restriction + caching ----------
    @lru_cache(maxsize=None)
    def _count_pair(self, cond: str, given: str):
        """
        Return (mass_true, mass_total) for 'cond' optionally under 'given'.
        If pmf is provided, we sum weights; otherwise we count uniformly.
        """
        # Which vars actually appear?
        cond_vars = _vars_in(cond, self.varset)
        if given:
            given_vars = _vars_in(given, self.varset)
            vars_needed = tuple(dict.fromkeys(
                cond_vars + tuple(v for v in given_vars if v not in cond_vars)
            ))
        else:
            vars_needed = cond_vars

        var_lists = [self.domain[v] for v in vars_needed]
        cond_code = _compile_expr(cond)
        given_code = _compile_expr(given) if given else None

        # CHANGED: use weighted masses if pmf provided
        mass_true = 0.0
        mass_total = 0.0

        for tup in product(*var_lists):
            env = {v: val for v, val in zip(vars_needed, tup)}

            # weight for this assignment (independent product pmf)
            if self.pmf:
                w = 1.0
                for v, val in env.items():
                    try:
                        w *= self.pmf[v][val]
                    except KeyError:
                        # value not specified in pmf: treat as zero mass
                        w = 0.0
                        break
                if w == 0.0:
                    continue
            else:
                # uniform case: each tuple contributes 1
                w = 1.0

            if given_code and not self._eval_compiled(given_code, env):
                continue

            mass_total += w
            if self._eval_compiled(cond_code, env):
                mass_true += w

        return mass_true, mass_total

    # ---------- Public probability API ----------
    def compute_probability(self, condition: str) -> float:
        t, T = self._count_pair(condition, "")
        return t / T if T else 0.0

    def compute_conditional_probability(self, condition: str, given_condition: str) -> float:
        t, T = self._count_pair(condition, given_condition)
        return t / T if T else 0.0

    # ---------- Closed-form birthday shortcut detection (unchanged) ----------
    @staticmethod
    def _is_birthday_return1_step(step):
        cond, outcome = step
        if outcome != 'True':
            return None
        m = re.fullmatch(r'\s*b(\d+)\s*==\s*b(\d+)\s*', cond)
        if not m:
            return None
        i, j = int(m.group(1)), int(m.group(2))
        if i <= j:
            return None
        return (i, j)

    @staticmethod
    def _is_birthday_all_distinct_path(path):
        if not path:
            return False
        *preds, last = path
        if not (isinstance(last, tuple) and last[0] == 'Statements' and last[1] in (['return 0'], ('return 0',))):
            return False
        for cond, outcome in preds:
            if outcome != 'False':
                return False
        return True

    @staticmethod
    def _path_returns_1(path):
        return isinstance(path[-1], tuple) and path[-1][0] == 'Statements' and ('return 1' in path[-1][1])

    def _birthday_closed_form_prob(self, path, S: int) -> float | None:
        # 'return 1' case?
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
                p_no *= (S - t) / S
            return p_no * (1 / S)

        # 'return 0' all-distinct
        if self._is_birthday_all_distinct_path(path):
            max_idx = -1
            for cond, outcome in path:
                m = re.findall(r'\bb(\d+)\b', cond) if cond != 'Statements' else []
                for g in m:
                    max_idx = max(max_idx, int(g))
            K = max_idx + 1 if max_idx >= 0 else 0
            p_all = 1.0
            for t in range(K):
                if S - t <= 0:
                    return 0.0
                p_all *= (S - t) / S
            return p_all

        return None

    # ---------- Batch path probabilities ----------
    def calculate_path_probabilities(self, paths):
        """
        Compute probabilities for all extracted paths.
        Uses closed-form (birthday) when possible; otherwise falls back to enumeration
        (weighted if pmf is provided).
        """
        unique_sizes = {len(list(v)) for v in self.domain.values()}
        S_uniform = unique_sizes.pop() if len(unique_sizes) == 1 else None

        probs = {}
        for path in paths:
            p_cf = None
            if S_uniform is not None:
                p_cf = self._birthday_closed_form_prob(path, S_uniform)

            if p_cf is not None:
                p = p_cf
            else:
                p = 1.0
                givens = []
                for condition, outcome in path[:-1]:  # skip final Statements
                    cond_str = condition if outcome == 'True' else f"not ({condition})"
                    if not givens:
                        p *= self.compute_probability(cond_str)
                    else:
                        p *= self.compute_conditional_probability(cond_str, " and ".join(givens))
                    givens.append(cond_str)

            if abs(p) < 1e-15:
                p = 0.0
            p = max(p, 0.0)

            key = tuple((c, tuple(o) if isinstance(o, list) else o) for c, o in path)
            probs[key] = p
        return probs


# --------------------- TEST: Von Neumann all paths at once ---------------------

variables = ['a', 'b']
domain = {'a': [0, 1], 'b': [0, 1]}

# (a==0 and b==1) -> return 0
# elif (a==1 and b==0) -> return 1
# else -> return -1   (repeat)
neumacoin = [
    [('a == 0 and b == 1', 'True'),  ('Statements', ['return 0'])],
    [('a == 0 and b == 1', 'False'), ('a == 1 and b == 0', 'True'),  ('Statements', ['return 1'])],
    [('a == 0 and b == 1', 'False'), ('a == 1 and b == 0', 'False'), ('Statements', ['return -1'])],
]

# ---- Case A: uniform (sanity check) ----
calc_uniform = ProbabilityCalculator(variables, domain)
uniform_probs = calc_uniform.calculate_path_probabilities(neumacoin)

print("=== Uniform (p=0.5) ===")
total = 0.0
for path, pr in uniform_probs.items():
    print(f"{path}  -> P={pr:.6f}")
    total += pr
print("Sum:", total, "\n")   # expect 1.0; masses should be 0.25, 0.25, 0.50

# ---- Case B: biased coin with parameter p (pmf) ----
p = 0.8
pmf = {'a': {0: p, 1: 1-p}, 'b': {0: p, 1: 1-p}}
calc_biased = ProbabilityCalculator(variables, domain, pmf=pmf)
biased_probs = calc_biased.calculate_path_probabilities(neumacoin)

print("=== Biased (P(0)=p, p=0.8) ===")
total = 0.0
agg = {"return 0": 0.0, "return 1": 0.0, "repeat": 0.0}
for path, pr in biased_probs.items():
    total += pr
    # detect label from last Statements
    last = path[-1]
    lab = "repeat"
    if last[0] == 'Statements':
        block = last[1] if isinstance(last[1], (list, tuple)) else [last[1]]
        for s in block:
            s = s.strip()
            if s.startswith("return 0"): lab = "return 0"
            elif s.startswith("return 1"): lab = "return 1"
            elif s.startswith("return -1"): lab = "repeat"
    agg[lab] += pr
    print(f"{path}  -> P={pr:.6f}")

print("Sum:", total)
print(f"P(HT → 0) = {agg['return 0']:.6f}   (expected p*(1-p))")
print(f"P(TH → 1) = {agg['return 1']:.6f}   (expected (1-p)*p)")
print(f"P(repeat) = {agg['repeat']:.6f}     (expected p*p + (1-p)*(1-p))")

accept = agg['return 0'] + agg['return 1']
if accept > 0:
    print(f"P(output=0 | accept) = {agg['return 0']/accept:.6f}")  # -> 0.5
    print(f"P(output=1 | accept) = {agg['return 1']/accept:.6f}")  # -> 0.5


#------randominoftwo function test-------

randminoftwo_paths = [
[('x < y', 'True'), ('Statements', ['return 1'])]
,[('x < y', 'False'), ('Statements', ['return 0'])]
]
calc_randmin = ProbabilityCalculator(['x','y'], {'x': list(range(1,10)),  'y': list(range(1,10)),})
randmin_probs = calc_randmin.calculate_path_probabilities(randminoftwo_paths)
print("\n=== randminoftwo paths ===")
total = 0.0
for path, pr in randmin_probs.items():
    print(f"{path}  -> P={pr:.6f}")
    total += pr
print("Sum:", total, "\n")   # expect 1.0; masses should be 0.55, 0.45  
