import ast

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
        self.current = None  # Tracks the current node being nested *inside*
        self.last_top_level_if = None # CHANGE 1: New tracker for sequential IFs

    def visit_If(self, node):
        # 1. Create a new condition node
        condition = ast.unparse(node.test)
        condition_node = ConditionNode(condition=condition)

        # 2. Link the node - CHANGE 2: Correct logic for sequential vs. nested IFs
        if self.current is None:
            # We are at the *top level*
            if self.root is None:
                # First IF statement in the program
                self.root = condition_node
                self.last_top_level_if = condition_node
            else:
                # Sequential IF statement: Link it to the last top-level IF
                self.last_top_level_if.next_condition = condition_node
                self.last_top_level_if = condition_node
        else:
            # We are inside a branch (nested condition). 
            if not self.root:
                self.root = condition_node
            
        
        # Store the current node as the parent for the next level of nesting
        parent = self.current
        self.current = condition_node

        # 3. Process the True branch
        true_branch_builder = ConditionTreeBuilder()
        for stmt in node.body:
            if isinstance(stmt, ast.If):
                # Process nested 'if'
                true_branch_builder.visit(stmt)
            else:
                # Store non-conditional statements
                condition_node.true_statements.append(ast.unparse(stmt))
        
        # The true_branch_builder will only have a root if an 'if' was nested
        condition_node.true_branch = true_branch_builder.root

        # 4. Process the False branch (orelse)
        false_branch_builder = ConditionTreeBuilder()
        if node.orelse:
            for stmt in node.orelse:
                if isinstance(stmt, ast.If):
                    # Process elif/nested 'if'
                    false_branch_builder.visit(stmt)
                else:
                    # Store non-conditional statements
                    condition_node.false_statements.append(ast.unparse(stmt))
        
        # FIX 3: Implicit Else Handling
        elif not node.orelse: 
            condition_node.false_statements.append("pass")  # Represents implicit execution

        # The false_branch_builder will only have a root if an 'elif' or nested 'if' was present
        condition_node.false_branch = false_branch_builder.root

        # 5. Restore the current pointer to the parent
        self.current = parent

    def build_tree(self, code):
        # Parse the code into an AST and visit it
        tree = ast.parse(code)
        # Handle cases where the code is wrapped in a function definition
        if tree.body and isinstance(tree.body[0], ast.FunctionDef):
            # Only visit the body of the function
            for stmt in tree.body[0].body:
                self.visit(stmt)
        else:
            # Visit the whole tree if no function is found (for top-level scripts)
            for stmt in tree.body:
                self.visit(stmt)
        return self.root

def check_for_return(statements):
    """Simple check to see if a list of statements contains a 'return'."""
    return any(stmt.startswith('return') for stmt in statements)

# CHANGE 4: The fully corrected extract_paths function
def extract_paths(node, current_path=None, all_paths=None):
    """
    Recursively extract all paths from the condition tree.
    This corrected version ensures paths continue through next_condition 
    only if a 'return' statement was not hit.
    """
    if current_path is None:
        current_path = []
    if all_paths is None:
        all_paths = []

    if not node:
        return all_paths

    # --- TRUE Branch Traversal ---
    true_path = current_path + [(node.condition, "True")]
    true_statements_contain_return = False
    
    if node.true_statements:
        true_statements_contain_return = check_for_return(node.true_statements)
        true_path.append(("Statements", node.true_statements))
    
    if node.true_branch:
        # Continue recursion on the nested branch
        extract_paths(node.true_branch, true_path, all_paths)
    elif node.next_condition and not true_statements_contain_return:
        # End of true branch, continue to sequential condition if no return was hit
        extract_paths(node.next_condition, true_path, all_paths)
    else:
        # Path ends here (either leaf or return was hit)
        all_paths.append(true_path)

    # --- FALSE Branch Traversal ---
    false_path = current_path + [(node.condition, "False")]
    false_statements_contain_return = False
    
    if node.false_statements:
        false_statements_contain_return = check_for_return(node.false_statements)
        false_path.append(("Statements", node.false_statements))
        
    if node.false_branch:
        # Continue recursion on the nested branch
        extract_paths(node.false_branch, false_path, all_paths)
    elif node.next_condition and not false_statements_contain_return:
        # End of false branch, continue to sequential condition if no return was hit
        extract_paths(node.next_condition, false_path, all_paths)
    else:
        # Path ends here (either leaf or return was hit)
        all_paths.append(false_path)

    return all_paths

example_code = """def monty_hall(choice, door_switch):
    
    
    car_door = random.randint(1, 3)
    host_door = None

    
    if choice == car_door:
        return not door_switch

    
    if choice != 1 and car_door != 1:
        host_door = 1
    elif choice != 2 and car_door != 2:
        host_door = 2
    else:
        host_door = 3

   
    if door_switch:
        if host_door == 1:
            if choice == 2:
                choice=3
            else :
                choice =2 
        elif host_door == 2:
            if choice == 1 :
                choice = 3
            else: 
                choice= 1
        else:
            if choice == 1 :
                choice = 2
            else : 
                choice = 1

    
    if choice == car_door :
        return 1

"""

example_code7 = """
if x>1:
    if x>2:
        return 1
    else:
        return 0
if x>3:
    return 0"""


example_code9 = """
 
def randminoftwo():
    x = ran.randint(1,10)
    y= ran.randint(1,10)

    if x<y :
        return 1
    else :
        return 0
"""
example_code8 = """

x = sample_uniform(1, 6)

if x > 3:
    y = 1
else:
    y = 0
"""

example_code6 = """
if x>1:
    if x>2:
        return 1
    else:
        return 0


if x>3:
    return 1
else : 
    return 2
"""


example_code10 = """

def freivalds():
    r0 = sample_uniform(0, 1)
    r1 = sample_uniform(0, 1)

    # Hardcoded incorrect matrices: A @ B ≠ C
    A = [[2, 3], [3, 4]]
    B = [[1, 0], [1, 2]]
    C = [[6, 5], [8, 8]]  # C is incorrect

    # Compute B @ r
    Br0 = 1 * r0 + 0 * r1
    Br1 = 1 * r0 + 2 * r1

    # A @ (B @ r)
    ABr0 = 2 * Br0 + 3 * Br1
    ABr1 = 3 * Br0 + 4 * Br1

    # C @ r
    Cr0 = 6 * r0 + 5 * r1
    Cr1 = 8 * r0 + 8 * r1

    # Check if Freivalds returns True
    if ABr0 == Cr0 and ABr1 == Cr1:
        return True
    else:
        return False


"""


example_montyhall = """

if choice != 1 and car_door != 1:
        
    if choice == 2:
                
        if car_door == 3 : 
            return 1
    else :
                 
        if car_door == 2 : 
            return 1

elif choice != 2 and car_door != 2:
        
    if choice == 1 :
                
        if car_door == 3 : 
            return 1
    else: 
                
        if car_door == 1 : 
            return 1

elif choice != 3 and car_door !=3:
        
    if choice == 1 :
                
        if car_door == 2 : 
            return 1
    else : 
                
        if car_door == 1 : 
            return 1
"""

example_montypi = """
if x**2 + y**2 <= 315*315:
    return 1
else:
    return 0
"""


# Build the condition tree


randomsample = """
def check4(): 
    x =ran.randint(1,3)
    y= ran.randint(1,3)

    if  x>1 :
        if y>x:
            x=y
        else : 
            x = x+1
    if x>2:
        return 1
    return 0
"""

neumann = """
def von_neumann_fair_coin(p=0.8):

    while True:
        # two biased flips
        if random.random() < p :
            a = 0
        else:
            a = 1

        if random.random() < p :
            b= 0 
        else :
            b =1

        
        if a == 0 and b == 1:
            return 0   # (H,T) → 0
        elif a == 1 and b == 0:
            return 1   # (T,H) → 1
        else :
            return -1
        
"""

Randmintwo = """
def randminoftwo():
    x = ran.randint(1,10)
    y= ran.randint(1,10)

    if x<y :
        return 1
    else :
        return 0

"""

Randmaxtwo = """
def randmaxoftwo():
    x = ran.randint(1, 10)
    y= ran.randint(1, 10)

    if x>y :
        return 1
    else :
        return 0

"""

Randeqltwo = """
def randeqloftwo():
    x = ran.randint(1, 10)
    y= ran.randint(1, 10)

    if x==y :
        return 1
    else :
        return 0

"""


print("--- Testing example_code7 (Sequential 'if' statements) ---")
builder = ConditionTreeBuilder()
condition_tree = builder.build_tree(example_code7)
paths = extract_paths(condition_tree)
print("Extracted Paths:")
for path in paths:
    print(path)


