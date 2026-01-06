#!/usr/bin/env python3
import ast
from itertools import product
import argparse

# ---------- Condition tree ----------

class ConditionNode:
    def __init__(self, condition=None):
        self.condition = condition
        self.true_statements = []
        self.false_statements = []
        self.true_branch = None
        self.false_branch = None
        self.next_condition = None

class ConditionTreeBuilder(ast.NodeVisitor):
    def __init__(self):
        self.root = None
        self.current = None

    def visit_If(self, node):
        cond = ast.unparse(node.test)
        cn = ConditionNode(cond)

        if not self.root:
            self.root = cn
            self.current = cn
        else:
            # append as sequential condition at this level
            if self.current is not None:
                if self.current.next_condition is None:
                    self.current.next_condition = cn
                else:
                    cur = self.current.next_condition
                    while cur.next_condition:
                        cur = cur.next_condition
                    cur.next_condition = cn

        parent = self.current
        self.current = cn

        # true branch
        tb = ConditionTreeBuilder()
        for stmt in node.body:
            if isinstance(stmt, ast.If):
                tb.visit(stmt)
            else:
                cn.true_statements.append(ast.unparse(stmt))
        cn.true_branch = tb.root

        # false branch
        fb = ConditionTreeBuilder()
        if node.orelse:
            for stmt in node.orelse:
                if isinstance(stmt, ast.If):
                    fb.visit(stmt)
                else:
                    cn.false_statements.append(ast.unparse(stmt))
        elif not self.current.next_condition:
            # implicit else at leaf-level
            cn.false_statements.append("pass")
        cn.false_branch = fb.root

        self.current = parent

    def build_tree(self, code: str):
        self.root = None
        self.current = None
        self.visit(ast.parse(code))
        return self.root

# ---------- Path extraction (fixed sequential ifs) ----------

def extract_paths(root):
    if not root:
        return []

    def has_return(stmts):
        return any(s.strip().startswith("return") for s in stmts)

    def walk(node, prefix):
        if not node:
            return [prefix], [prefix]

        terminals, continuations = [], []

        # TRUE
        tpath = prefix + [(node.condition, "True")]
        if node.true_statements:
            tpath = tpath + [("Statements", node.true_statements)]
        if node.true_branch and not (node.true_statements and has_return(node.true_statements)):
            t_terms, t_conts = walk(node.true_branch, tpath[:-1] if (tpath and tpath[-1][0]=="Statements") else tpath)
            terminals += t_terms; continuations += t_conts
        else:
            if node.true_statements:
                if has_return(node.true_statements):
                    terminals.append(tpath)
                else:
                    terminals.append(tpath); continuations.append(tpath)
            else:
                leaf = tpath + [("Statements", ["pass"])]
                terminals.append(leaf); continuations.append(leaf)

        # FALSE
        fpath = prefix + [(node.condition, "False")]
        if node.false_statements:
            fpath = fpath + [("Statements", node.false_statements)]
        if node.false_branch and not (node.false_statements and has_return(node.false_statements)):
            f_terms, f_conts = walk(node.false_branch, fpath[:-1] if (fpath and fpath[-1][0]=="Statements") else fpath)
            terminals += f_terms; continuations += f_conts
        else:
            if node.false_statements:
                if has_return(node.false_statements):
                    terminals.append(fpath)
                else:
                    terminals.append(fpath); continuations.append(fpath)
            else:
                leaf = fpath + [("Statements", ["pass"])]
                terminals.append(leaf); continuations.append(leaf)

        # sequential if at same level
        if node.next_condition:
            forwarded = []
            for cont in continuations:
                stmts = cont[-1][1] if cont and cont[-1][0]=="Statements" else []
                if any(s.strip().startswith("return") for s in stmts):
                    forwarded.append(cont)  # already terminated
                else:
                    prefix2 = cont[:-1] if cont and cont[-1][0]=="Statements" else cont
                    sub_terms, _ = walk(node.next_condition, prefix2)
                    forwarded += sub_terms
            terminals = [p for p in terminals if p not in continuations] + forwarded

        return terminals, []

    terms, _ = walk(root, [])
    return terms

# ---------- Probability engine (enumeration) ----------

class ProbabilityCalculator:
    def __init__(self, variables, domain):
        self.variables = list(variables)
        self.domain = dict(domain)

    def _eval_case(self, expr, case):
        env = {v: val for v, val in zip(self.variables, case)}
        return eval(expr, {}, env)

    def _prob(self, cond, given=None):
        cnt = tot = 0
        for case in product(*[self.domain[v] for v in self.variables]):
            if given and not self._eval_case(given, case):
                continue
            tot += 1
            if self._eval_case(cond, case):
                cnt += 1
        return (cnt / tot) if tot else 0.0

    def path_probabilities(self, paths):
        out = {}
        for path in paths:
            prob = 1.0
            givens = []
            for cond, outcome in path:
                if cond == "Statements":
                    continue
                cond_str = cond if outcome == "True" else f"not ({cond})"
                prob *= self._prob(cond_str, " and ".join(givens) if givens else None)
                givens.append(cond_str)
            key = tuple((c, tuple(v) if isinstance(v, list) else v) for c, v in path)
            out[key] = prob
        return out

def print_probs(probs):
    for path, p in probs.items():
        print(f"Path: {path}")
        print(f"Probability: {p:.6f}\n")

# ---------- Example snippets ----------

# 1) Simple example (matches your screenshot format)
EX_SIMPLE = """
if x>1:
    if x>2:
        return 1
    else:
        return 0
if x>3:
    return 0
"""

SIMPLE_VARS = ['x']
SIMPLE_DOMAIN = {'x': list(range(0,11))}

# 2) Monty Hall switching, branch-only encoding (your example_code11)
EX_MONTY = """
if choice != 1 and car_door != 1:
    if choice == 2:
        if car_door == 3:
            return 1
    else:
        if car_door == 2:
            return 1
elif choice != 2 and car_door != 2:
    if choice == 1:
        if car_door == 3:
            return 1
    else:
        if car_door == 1:
            return 1
elif choice != 3 and car_door != 3:
    if choice == 1:
        if car_door == 2:
            return 1
    else:
        if car_door == 1:
            return 1
"""
MONTY_VARS = ['choice','car_door']
MONTY_DOMAIN = {'choice':[1,2,3],'car_door':[1,2,3]}

# 3) Quarter-circle test (π’s building block)
EX_PI = """
if x*x + y*y <= R2:
    return 1
else:
    return 0
"""

# 4) Freivalds for your specific 2x2 matrices with r=(r0,r1) in {0,1}^2
# A=[[2,3],[3,4]], B=[[1,0],[1,2]], C=[[6,5],[8,8]]
# Br = [1*r0 + 0*r1, 1*r0 + 2*r1]
# ABr = [2*Br0 + 3*Br1, 3*Br0 + 4*Br1]
# Cr = [6*r0 + 5*r1, 8*r0 + 8*r1]
EX_FREIVALDS = """
if (2*(1*r0 + 0*r1) + 3*(1*r0 + 2*r1) == 6*r0 + 5*r1) and (3*(1*r0 + 0*r1) + 4*(1*r0 + 2*r1) == 8*r0 + 8*r1):
    return 1
else:
    return 0
"""
FREV_VARS = ['r0','r1']
FREV_DOMAIN = {'r0':[0,1],'r1':[0,1]}

# ---------- CLI ----------

def main():
    ap = argparse.ArgumentParser(description="Extract paths and compute probabilities")
    ap.add_argument("--example", choices=["simple","monty","pi","freivalds"], required=True)
    ap.add_argument("--R", type=int, default=400, help="Grid radius for pi example")
    args = ap.parse_args()

    if args.example == "simple":
        code, vars_, dom = EX_SIMPLE, SIMPLE_VARS, SIMPLE_DOMAIN
    elif args.example == "monty":
        code, vars_, dom = EX_MONTY, MONTY_VARS, MONTY_DOMAIN
    elif args.example == "pi":
        code = EX_PI.replace("R2", str(args.R*args.R))
        vars_, dom = ['x','y'], {'x': list(range(0,args.R+1)), 'y': list(range(0,args.R+1))}
    else:  # freivalds
        code, vars_, dom = EX_FREIVALDS, FREV_VARS, FREV_DOMAIN

    builder = ConditionTreeBuilder()
    root = builder.build_tree(code)
    paths = extract_paths(root)

    calc = ProbabilityCalculator(vars_, dom)
    probs = calc.path_probabilities(paths)
    print_probs(probs)

if __name__ == "__main__":
    main()
