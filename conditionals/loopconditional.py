import ast
from copy import deepcopy

class ConditionNode:
    """Condition/loop node in the decision structure."""
    def __init__(self, condition=None, node_type="if"):
        self.condition = condition            # str (condition source)
        self.node_type = node_type            # "if" or "while"
        self.true_statements = []             # statements under True / loop body (non-if/while)
        self.false_statements = []            # statements under False (or while-orelse)
        self.true_branch = None               # nested subtree for True/body
        self.false_branch = None              # nested subtree for False/orelse
        self.next_condition = None            # sibling at same lexical level

    def __repr__(self):
        return (f"ConditionNode(type={self.node_type}, condition={self.condition}, "
                f"true_statements={self.true_statements}, false_statements={self.false_statements}, "
                f"true_branch={self.true_branch}, false_branch={self.false_branch}, "
                f"next_condition={self.next_condition})")

class ConditionTreeBuilder(ast.NodeVisitor):
    """
    Builds a chain of ConditionNodes from Python code.
    - Top-level sequential if/while nodes linked via .next_condition
    - Nested if/while become .true_branch / .false_branch
    """
    def __init__(self):
        self.root = None
        self.tail = None  # last top-level node

    def build_tree(self, code: str):
        tree = ast.parse(code)
        self.visit(tree)
        return self.root

    def visit_Module(self, node):
        prev = None
        for stmt in node.body:
            if isinstance(stmt, (ast.If, ast.While)):
                cn = self._build_subtree(stmt)
                if self.root is None:
                    self.root = cn
                    self.tail = cn
                else:
                    self.tail.next_condition = cn
                    self.tail = cn
            # ignore non-branching top-level stmts
        return self.root

    def _build_subtree(self, node):
        if isinstance(node, ast.If):
            cond = ast.unparse(node.test)
            cn = ConditionNode(condition=cond, node_type="if")
            # TRUE/body
            true_builder = ConditionTreeBuilder()
            for s in node.body:
                if isinstance(s, (ast.If, ast.While)):
                    true_builder.visit(ast.Module(body=[s], type_ignores=[]))
                else:
                    cn.true_statements.append(ast.unparse(s))
            cn.true_branch = true_builder.root
            # FALSE/orelse
            false_builder = ConditionTreeBuilder()
            if node.orelse:
                for s in node.orelse:
                    if isinstance(s, (ast.If, ast.While)):
                        false_builder.visit(ast.Module(body=[s], type_ignores=[]))
                    else:
                        cn.false_statements.append(ast.unparse(s))
            else:
                # implicit else: represent as pass so a leaf is emitted
                cn.false_statements.append("pass")
            cn.false_branch = false_builder.root
            return cn

        elif isinstance(node, ast.While):
            cond = ast.unparse(node.test)
            cn = ConditionNode(condition=cond, node_type="while")
            # LOOP BODY (True branch)
            true_builder = ConditionTreeBuilder()
            for s in node.body:
                if isinstance(s, (ast.If, ast.While)):
                    true_builder.visit(ast.Module(body=[s], type_ignores=[]))
                else:
                    cn.true_statements.append(ast.unparse(s))
            cn.true_branch = true_builder.root
            # WHILE-Orelse is executed if loop exits via condition False (rarely used)
            false_builder = ConditionTreeBuilder()
            if node.orelse:
                for s in node.orelse:
                    if isinstance(s, (ast.If, ast.While)):
                        false_builder.visit(ast.Module(body=[s], type_ignores=[]))
                    else:
                        cn.false_statements.append(ast.unparse(s))
            else:
                # exiting the loop without orelse: we still want a leaf
                cn.false_statements.append("pass")
            cn.false_branch = false_builder.root
            return cn

        else:
            return None

def _append_leaf(out, base_path, stmts):
    if stmts:
        out.append(base_path + [('Statements', stmts)])
    else:
        out.append(base_path + [('Statements', ['pass'])])

def _collect_leaf_paths(node, cur, out, loop_budget, node_budgets):
    """
    DFS that emits Monty-style paths.
    - For IF: like your original extractor.
    - For WHILE: explore False (exit) and True (enter body) up to 'loop_budget' times.
    """
    if node is None:
        return

    # IF node
    if node.node_type == "if":
        # TRUE side
        path_true = cur + [(node.condition, 'True')]
        emitted = False
        if node.true_statements:
            _append_leaf(out, path_true, node.true_statements)
            emitted = True
        if node.true_branch:
            _collect_leaf_paths(node.true_branch, path_true, out, loop_budget, node_budgets)
            emitted = True
        if not emitted:
            _append_leaf(out, path_true, [])

        # FALSE side
        path_false = cur + [(node.condition, 'False')]
        emitted = False
        if node.false_statements:
            _append_leaf(out, path_false, node.false_statements)
            emitted = True
        if node.false_branch:
            _collect_leaf_paths(node.false_branch, path_false, out, loop_budget, node_budgets)
            emitted = True
        if not emitted:
            _append_leaf(out, path_false, [])

        # Sibling chain
        if node.next_condition:
            _collect_leaf_paths(node.next_condition, [], out, loop_budget, node_budgets)
        return

    # WHILE node
    if node.node_type == "while":
        nid = id(node)
        remaining = node_budgets.get(nid, loop_budget)

        # Option 1: exit loop now (condition False)
        path_false = cur + [(node.condition, 'False')]
        emitted = False
        if node.false_statements:
            _append_leaf(out, path_false, node.false_statements)
            emitted = True
        if node.false_branch:
            _collect_leaf_paths(node.false_branch, path_false, out, loop_budget, node_budgets)
            emitted = True
        if not emitted:
            _append_leaf(out, path_false, [])

        # After exiting loop, go to sibling (start fresh like your Monty format)
        if node.next_condition:
            _collect_leaf_paths(node.next_condition, [], out, loop_budget, node_budgets)

        # Option 2: take True (enter body), if budget remains
        if remaining > 0:
            path_true = cur + [(node.condition, 'True')]
            # explore body; for each leaf produced in body, continue the loop again
            body_leaves = []
            _collect_leaf_paths(node.true_branch, path_true, body_leaves, loop_budget, deepcopy(node_budgets))
            # for each leaf from body, try another iteration by decrementing budget
            for lp in body_leaves:
                nb = deepcopy(node_budgets)
                nb[nid] = remaining - 1
                _collect_leaf_paths(node, lp[:-1], out, loop_budget, nb)  # lp has ('Statements',...), strip it before looping
            # If there were no statements/branches in body, still iterate
            if not body_leaves:
                nb = deepcopy(node_budgets)
                nb[nid] = remaining - 1
                _collect_leaf_paths(node, path_true + [('Statements', ['pass'])], out, loop_budget, nb)
        return

def extract_paths(root_node, loop_unroll=2):
    """
    Public API: extract Monty-style paths with bounded loop unrolling.
    - loop_unroll = max number of True-taken iterations per 'while' node.
    """
    out = []
    _collect_leaf_paths(root_node, [], out, loop_unroll, {})
    return out


# Put your pWhile-style code string here:
example_birthday_pwhile = """
days = 7
k = 4
seen = [0] * days
i = 0

while i < k:
    b = sample_uniform(0, days - 1)
    if seen[b] == 1:
        return 1
    else:
        seen[b] = 1
    i = i + 1

return 0
"""

builder = ConditionTreeBuilder()
root = builder.build_tree(example_birthday_pwhile)

# IMPORTANT: choose how deep to unroll the while (e.g., k iterations max)
paths = extract_paths(root, loop_unroll=4)

for p in paths:
    print(p)
