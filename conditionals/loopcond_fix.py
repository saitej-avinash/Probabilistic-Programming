import ast, copy


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
        self.root = None  # Root of the condition tree
        self.current = None  # Tracks the current node

    def visit_If(self, node):
        # Create a new condition node
        condition = ast.unparse(node.test)
        condition_node = ConditionNode(condition=condition)

        if not self.root:
            # Set the root if it's the first condition
            self.root = condition_node
            self.current = condition_node
        else:
            # Handle sequential conditions (next independent condition)
            if self.current is not None:
                if self.current.next_condition is None:
                    self.current.next_condition = condition_node
                else:
                    current = self.current.next_condition
                    while current.next_condition:
                        current = current.next_condition
                    current.next_condition = condition_node

        # Update current pointer for nested conditions
        parent = self.current
        self.current = condition_node

        # Process the True branch
        true_branch_builder = ConditionTreeBuilder()
        for stmt in node.body:
            if isinstance(stmt, ast.If):
                true_branch_builder.visit(stmt)
            else:
                # Store non-conditional statements in the True branch
                condition_node.true_statements.append(ast.unparse(stmt))
        condition_node.true_branch = true_branch_builder.root

        # Process the False branch
        false_branch_builder = ConditionTreeBuilder()
        if node.orelse:
            
            for stmt in node.orelse:
                if isinstance(stmt, ast.If):
                    false_branch_builder.visit(stmt)
                else:
                    # Store non-conditional statements in the False branch
                    condition_node.false_statements.append(ast.unparse(stmt))
        elif not self.current.next_condition :

            # **Implicit Else Handling**: If no else, add an empty false branch
            condition_node.false_statements.append("pass")  # Represents implicit execution

        condition_node.false_branch = false_branch_builder.root

        # Restore the current pointer to the parent
        self.current = parent

    def build_tree(self, code):
        # Parse the code into an AST and visit it
        tree = ast.parse(code)
        self.visit(tree)
        return self.root


def extract_paths(node, current_path=None, all_paths=None):
    """
    Recursively extract all paths from the condition tree.
    Each path represents a sequence of (condition, truth value) pairs leading to a leaf.
    Also includes statements inside each branch.
    """
    if current_path is None:
        current_path = []
    if all_paths is None:
        all_paths = []

    if not node:
        return all_paths

    # True branch traversal
    if node.true_branch or node.true_statements:
        path = current_path + [(node.condition, "True")]
        if node.true_statements:
            path.append(("Statements", node.true_statements))
        if node.true_branch:
            extract_paths(node.true_branch, path, all_paths)
        else:
            all_paths.append(path)  # Ensure leaf paths are added

    # False branch traversal (handles missing branches)
    if node.false_branch or node.false_statements:
        path = current_path + [(node.condition, "False")]
        if node.false_statements:
            path.append(("Statements", node.false_statements))
        if node.false_branch:
            extract_paths(node.false_branch, path, all_paths)
        else:
            all_paths.append(path)  # Ensure leaf paths are added
        
        


    # Handle sequential (next_condition) **correctly** by keeping previous conditions
    if node.next_condition:
        extract_paths(node.next_condition, [], all_paths)  # Preserve `current_path`

    return all_paths



class WhileUnroller(ast.NodeTransformer):
    """
    Unrolls `while <cond>: <body>` into K sequential `if <cond>: <body>` blocks.
    This re-checks <cond> after each body, matching loop semantics.
    """
    def __init__(self, max_unroll=4, add_truncation_sentinel=False):
        super().__init__()
        self.max_unroll = max_unroll
        self.add_truncation_sentinel = add_truncation_sentinel

    def visit_While(self, node: ast.While):
        # Transform inside the loop first (in case there are nested loops/ifs)
        self.generic_visit(node)

        # Build K sequential IF blocks: if cond: body; if cond: body; ...
        blocks = []
        for _ in range(self.max_unroll):
            blocks.append(
                ast.If(
                    test=copy.deepcopy(node.test),
                    body=copy.deepcopy(node.body),
                    orelse=[]  # IMPORTANT: keep empty, or you'll get `elif`
                )
            )

        # Optional: add a truncation flag if the loop could continue
        if self.add_truncation_sentinel:
            blocks.append(
                ast.If(
                    test=copy.deepcopy(node.test),
                    body=[ast.parse("LOOP_TRUNCATED = True").body[0]],
                    orelse=[]
                )
            )

        # Return a list => these replace the While node in its parent's body
        return blocks

def unroll_while_source(src: str, max_unroll=3, add_truncation_sentinel=True) -> str:
    tree = ast.parse(src)
    new_tree = WhileUnroller(max_unroll=max_unroll,
                             add_truncation_sentinel=add_truncation_sentinel).visit(tree)
    ast.fix_missing_locations(new_tree)
    return ast.unparse(new_tree)

# --- Use with your existing builder ---
# Example: your birthday-paradox loop (≤ n iterations), pick max_unroll = n
birthday_code = """
def has_collision(n, S=365):
    seen = [0]*S
    i = 0
    collide = 0
    while i < n and collide == 0:
        b = sample_uniform(0, S-1)
        if seen[b] == 1:
            collide = 1
        else:
            seen[b] = 1
            i = i + 1
    if collide == 1:
        return 1
    else:
        return 0
"""

K = 4  # for example; since loop ≤ n iterations, set K = n you’re analyzing
unrolled = unroll_while_source(birthday_code, max_unroll=K, add_truncation_sentinel=False)


import ast, copy

def _is_sample_uniform(call: ast.AST) -> bool:
    return isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == "sample_uniform"

def _is_seen_b_equals_one(node: ast.AST) -> bool:
    # matches: seen[b] == 1
    if not isinstance(node, ast.Compare):
        return False
    if not (isinstance(node.left, ast.Subscript)
            and isinstance(node.left.value, ast.Name)
            and node.left.value.id == "seen"):
        return False
    # slice should be Name('b')
    idx = node.left.slice
    if isinstance(idx, ast.Name):
        ok_idx = (idx.id == "b")
    elif isinstance(idx, ast.Index) and isinstance(idx.value, ast.Name):  # py<3.9
        ok_idx = (idx.value.id == "b")
    else:
        ok_idx = False
    if not ok_idx:
        return False
    # comparator == 1
    if len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq):
        comp = node.comparators[0]
        return isinstance(comp, ast.Constant) and comp.value == 1
    return False

def _is_assign_seen_b_to_one(node: ast.AST) -> bool:
    # matches: seen[b] = 1
    if not isinstance(node, ast.Assign) or len(node.targets) != 1:
        return False
    tgt = node.targets[0]
    if not (isinstance(tgt, ast.Subscript)
            and isinstance(tgt.value, ast.Name)
            and tgt.value.id == "seen"):
        return False
    # index is b
    idx = tgt.slice
    if isinstance(idx, ast.Name):
        ok_idx = (idx.id == "b")
    elif isinstance(idx, ast.Index) and isinstance(idx.value, ast.Name):
        ok_idx = (idx.value.id == "b")
    else:
        ok_idx = False
    if not ok_idx:
        return False
    return isinstance(node.value, ast.Constant) and node.value.value == 1

def _is_assign_collide_one(node: ast.AST) -> bool:
    # matches: collide = 1
    if not isinstance(node, ast.Assign) or len(node.targets) != 1:
        return False
    tgt = node.targets[0]
    return isinstance(tgt, ast.Name) and tgt.id == "collide" and isinstance(node.value, ast.Constant) and node.value.value == 1

def _is_inc_i(node: ast.AST) -> bool:
    # matches: i = i + 1
    if not isinstance(node, ast.Assign) or len(node.targets) != 1:
        return False
    tgt = node.targets[0]
    if not (isinstance(tgt, ast.Name) and tgt.id == "i"):
        return False
    val = node.value
    return (isinstance(val, ast.BinOp)
            and isinstance(val.left, ast.Name) and val.left.id == "i"
            and isinstance(val.op, ast.Add)
            and isinstance(val.right, ast.Constant) and val.right.value == 1)

class IterBlockRewriter(ast.NodeTransformer):
    """
    Rewrites a *single* unrolled iteration block (one `if` block):
      - Replaces `b = sample_uniform(...)` with `b{k} = sample_uniform(...)`
      - Replaces all loads of `b` in this block with `b{k}`
      - Replaces `seen[b] == 1` with (b{k}==b0 or ... or b{k}==b{k-1})
      - Replaces `collide = 1` with `return 1`
      - Drops `seen[b] = 1` and `i = i + 1`
    """
    def __init__(self, k: int, previous_b_names):
        super().__init__()
        self.k = k
        self.current_b = f"b{k}"
        self.previous = list(previous_b_names)
        self._inside = 0
        self._bound_current = False

    def visit_Assign(self, node: ast.Assign):
        # b = sample_uniform(...)  →  b{k} = sample_uniform(...)
        if (len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "b" and _is_sample_uniform(node.value)):
            self._bound_current = True
            new_node = copy.deepcopy(node)
            new_node.targets[0] = ast.Name(id=self.current_b, ctx=ast.Store())
            return new_node

        # seen[b] = 1 -> drop
        if _is_assign_seen_b_to_one(node):
            return None

        # i = i + 1 -> drop
        if _is_inc_i(node):
            return None

        # collide = 1 -> return 1
        if _is_assign_collide_one(node):
            return ast.Return(value=ast.Constant(value=1))

        return self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        # replace b (load) -> b{k}
        if isinstance(node.ctx, ast.Load) and node.id == "b" and self._bound_current:
            return ast.copy_location(ast.Name(id=self.current_b, ctx=ast.Load()), node)
        return node

    def visit_Compare(self, node: ast.Compare):
        # seen[b] == 1  →  big OR of (b{k}==b0 or ... b{k}==b{k-1})
        if _is_seen_b_equals_one(node):
            # k==0 => cannot collide yet: make it False
            if self.k == 0 or len(self.previous) == 0:
                return ast.copy_location(ast.Constant(value=False), node)
            # Build OR chain: (b{k}==b0) or (b{k}==b1) or ...
            left = ast.Compare(
                left=ast.Name(id=self.current_b, ctx=ast.Load()),
                ops=[ast.Eq()],
                comparators=[ast.Name(id=self.previous[0], ctx=ast.Load())],
            )
            expr = left
            for prev in self.previous[1:]:
                expr = ast.BoolOp(
                    op=ast.Or(),
                    values=[
                        expr,
                        ast.Compare(
                            left=ast.Name(id=self.current_b, ctx=ast.Load()),
                            ops=[ast.Eq()],
                            comparators=[ast.Name(id=prev, ctx=ast.Load())],
                        ),
                    ],
                )
            return ast.copy_location(expr, node)

        return self.generic_visit(node)

def rewrite_unrolled_birthday(source_unrolled: str) -> str:
    """
    Assumes source_unrolled is already While-unrolled into sequential `if` blocks.
    Walks the function body, and for each top-level `if` that contains
    `b = sample_uniform(...)`, assigns a fresh b{k} and rewrites checks.
    Also removes the final `if collide == 1: return 1 else: return 0`
    and just ensures a trailing `return 0`.
    """
    mod = ast.parse(source_unrolled)
    func = next((n for n in mod.body if isinstance(n, ast.FunctionDef)), None)
    if func is None:
        return source_unrolled

    new_body = []
    previous_b_names = []
    k = 0

    for stmt in func.body:
        if isinstance(stmt, ast.If):
            # Does this block draw b?
            draws_b = any(
                isinstance(s, ast.Assign)
                and len(s.targets) == 1
                and isinstance(s.targets[0], ast.Name)
                and s.targets[0].id == "b"
                and _is_sample_uniform(s.value)
                for s in ast.walk(stmt)
                if isinstance(s, ast.Assign)
            )
            if draws_b:
                rewriter = IterBlockRewriter(k, previous_b_names)
                stmt = rewriter.visit(copy.deepcopy(stmt))
                ast.fix_missing_locations(stmt)
                previous_b_names.append(f"b{k}")
                k += 1

        # Drop an end-of-function `if collide == 1: return 1 else: return 0`
        drop_final_collide_if = (
            isinstance(stmt, ast.If)
            and isinstance(stmt.test, ast.Compare)
            and isinstance(stmt.test.left, ast.Name)
            and stmt.test.left.id == "collide"
        )
        if drop_final_collide_if:
            # skip this 'if' entirely; we'll append a final 'return 0' later.
            continue

        new_body.append(stmt)

    # Ensure trailing return 0
    if not new_body or not isinstance(new_body[-1], ast.Return):
        new_body.append(ast.parse("return 0").body[0])

    func.body = new_body
    ast.fix_missing_locations(mod)
    return ast.unparse(mod)

rewritten = rewrite_unrolled_birthday(unrolled)
#print(rewritten)


example = """
def has_collision_canonical():
    if b1 == b0:
        return 1
    if b2 == b0:
        return 1
    if b2 == b1:
        return 1
    if b3 == b0:
        return 1
    if b3 == b1:
        return 1
    if b3 == b2:
        return 1
    return 0
"""

builder = ConditionTreeBuilder()
condition_tree = builder.build_tree(example)
paths = extract_paths(condition_tree)   

for p in paths:
    print(p)