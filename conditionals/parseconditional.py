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
        if node.orelse:
            false_branch_builder = ConditionTreeBuilder()
            for stmt in node.orelse:
                if isinstance(stmt, ast.If):
                    false_branch_builder.visit(stmt)
                else:
                    # Store non-conditional statements in the False branch
                    condition_node.false_statements.append(ast.unparse(stmt))
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

    # Traverse the true branch
    if node.true_branch or node.true_statements:
        path = current_path + [(node.condition, "True")]
        if node.true_statements:
            path.append(("Statements", node.true_statements))
        if node.true_branch:
            extract_paths(node.true_branch, path, all_paths)
        else:
            all_paths.append(path)

    # Traverse the false branch
    if node.false_branch or node.false_statements:
        path = current_path + [(node.condition, "False")]
        if node.false_statements:
            path.append(("Statements", node.false_statements))
        if node.false_branch:
            extract_paths(node.false_branch, path, all_paths)
        else:
            all_paths.append(path)

    # Handle next independent condition (next_condition) **correctly**
    if node.next_condition:
        extract_paths(node.next_condition, [], all_paths)

    return all_paths


# Example Python code to parse
example_code1 = """
def probabilistic_function(x, y):
    if x > 1:
        z = x + y
        return True
    else:
        w = x - y
        print(w)

        if x < 1:
            x = x + 1
        else : 
            x = x +5 
    return False

    if x > 5:
        return True
    
    else : 
        if  x < 5 :
            z = 1 
            return
        z = 3

    if x > 8: 
        return True 
    else:
        if x == 0:
            return 0
        elif x== -1 :
            return -1
        else :
            return -9
        return False
"""


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
                choice = 10

    
    return choice == car_door

"""

example_code2 = """
def prob(x,y):
    if x > 1:
        if x > y:
            return True
        else:
            return False
    else:
        
        if x < 1 :
            x= x + 1 
        
        else  : 
            

            if x==0 :
                
                return 0
            else :
                return 1
        
            return False"""

example_code3 = """
if x>1  : 
    if x > y :
        return True
    else :
        return False
return False
    """


example_code5 = """
if x>1:
    if y>x:
        if z>1:
            return 1"""

example_code4= """
if x > 1:
    if x > y:
        return 1
    else:
        return 0
else:
        
    if x==0 :
                
        return 0
    else :
        return 0
        
    return False"""

example_code6 = """
if x>1:
    if x>2:
        return 1
    else: 
    
        return 0
if x>3:
    return 0"""
# Build the condition tree
builder = ConditionTreeBuilder()
condition_tree = builder.build_tree(example_code6)

# Print the condition tree
#print("Condition Tree:")
#print(condition_tree)

# Extract all paths from the condition tree
paths = extract_paths(condition_tree)

# Print the extracted paths
print("\nExtracted Paths:")
for path in paths:
    print(path)

'''Now I need you to find the probability for each path 
you neeed to find the branch probabilities
for example : 
[('x > 1', 'True'), ('x < y', 'True'), ('Statements', ['return True'])]

first branch is  x>1 is true 
if we consider x, y ~U(1,3) 
then probability of first branch getting true is 2/3 
and then we need to check the probability of  second branch 
here we need to check the 2 things 
whether the second branch is dependent on the first branch or not 
if it is independent then we find the probability else the branch dependent on the first branch then you need to find the conditional probability based on the first branch 

In the example we have x<y it is conditional since y need to check with x 
so the probability will be 1/6'''