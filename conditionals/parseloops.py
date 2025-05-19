import re

class ConditionNode:
    def __init__(self, condition=None, label=None):
        self.condition = condition
        self.label = label  # Label name for goto blocks
        self.true_statements = []
        self.false_statements = []
        self.true_branch = None
        self.false_branch = None
        self.next_condition = None
        self.goto_target = None  # Will later point to a ConditionNode

    def __repr__(self):
        return (
            f"ConditionNode(label={self.label}, condition={self.condition}, "
            f"true_statements={self.true_statements}, false_statements={self.false_statements}, "
            f"true_branch={self.true_branch}, false_branch={self.false_branch}, "
            f"goto_target={self.goto_target.label if isinstance(self.goto_target, ConditionNode) else self.goto_target}, "
            f"next_condition={self.next_condition.label if isinstance(self.next_condition, ConditionNode) else self.next_condition})"
        )


class GotoConditionTreeBuilder:
    def __init__(self):
        self.labels = {}   # label_name -> ConditionNode
        self.root = None
        self.current = None
        self.pending_gotos = []  # List of (node, label) to resolve later

    def build_tree(self, code):
        # Reset state
        self.labels = {}
        self.pending_gotos = []
        self.root = None
        self.current = None

        lines = [line.strip() for line in code.strip().splitlines() if line.strip()]
        i = 0

        while i < len(lines):
            line = lines[i]

            # Label (e.g. states:)
            label_match = re.match(r'^(\w+):$', line)
            if label_match:
                label = label_match.group(1)
                node = ConditionNode(label=label)
                self.labels[label] = node

                if not self.root:
                    self.root = node
                else:
                    if self.current:
                        self.current.next_condition = node

                self.current = node
                i += 1
                continue

            # If condition
            if line.startswith("if ") and ":" in line:
                cond_match = re.match(r'if (.+?)\s*:\s*$', line)
                if cond_match:
                    cond = cond_match.group(1)
                    condition_node = ConditionNode(condition=cond)

                    i += 1
                    body_lines = []

                    # Collect indented block (simplified)
                    while i < len(lines) and not re.match(r'^\w+:$', lines[i]) and not lines[i].startswith("if "):
                        goto_match = re.search(r'goto\s+(\w+)', lines[i])
                        if goto_match:
                            goto_label = goto_match.group(1)
                            condition_node.goto_target = goto_label
                            self.pending_gotos.append((condition_node, goto_label))
                        else:
                            body_lines.append(lines[i])
                        i += 1

                    condition_node.true_statements = body_lines

                    if self.current is None:
                        self.root = condition_node
                        self.current = condition_node
                    else:
                        self.current.next_condition = condition_node
                        self.current = condition_node
                    continue

            # Goto (standalone)
            if "goto" in line:
                goto_label = re.search(r'goto\s+(\w+)', line).group(1)
                if self.current is None:
                    self.current = ConditionNode(label="entry")
                    self.root = self.current
                self.current.goto_target = goto_label
                self.pending_gotos.append((self.current, goto_label))
                i += 1
                continue

            # Plain statement
            if self.current is None:
                self.current = ConditionNode(label="entry")
                self.root = self.current

            self.current.true_statements.append(line)
            i += 1

        # Resolve goto targets
        for node, label in self.pending_gotos:
            if label in self.labels:
                node.goto_target = self.labels[label]

        return self.root


def extract_paths(node, current_path=None, all_paths=None, visited=None):
    if current_path is None:
        current_path = []
    if all_paths is None:
        all_paths = []
    if visited is None:
        visited = set()

    if node in visited:
        return  # Prevent infinite loop
    visited.add(node)

    if node.condition:
        path_true = current_path + [(node.condition, "True")]
        if node.true_statements:
            path_true.append(("Statements", node.true_statements))
        if node.goto_target:
            extract_paths(node.goto_target, path_true, all_paths, visited.copy())
        elif node.true_branch:
            extract_paths(node.true_branch, path_true, all_paths, visited.copy())
        else:
            all_paths.append(path_true)

        path_false = current_path + [(node.condition, "False")]
        if node.false_statements:
            path_false.append(("Statements", node.false_statements))
        if node.false_branch:
            extract_paths(node.false_branch, path_false, all_paths, visited.copy())
        else:
            all_paths.append(path_false)
    else:
        path = current_path[:]
        if node.true_statements:
            path.append(("Statements", node.true_statements))
        if node.goto_target:
            extract_paths(node.goto_target, path, all_paths, visited.copy())
        elif node.next_condition:
            extract_paths(node.next_condition, path, all_paths, visited.copy())
        else:
            all_paths.append(path)

    return all_paths


pseudo_code = """
looper = 0
Is_In = 0

states:
x = random.randint(0,315)
y = random.randint(0,315)

if x**2 + y**2 <= 315*315:
    count += 1

looper += 1

if looper < 315*315:
    goto states
else:
    halt
"""

builder = GotoConditionTreeBuilder()
condition_tree = builder.build_tree(pseudo_code)

# Print the condition tree
print("Condition Tree Root:")
print(condition_tree)

# Extract paths
paths = extract_paths(condition_tree)
print("\nExtracted Paths:")
for i, path in enumerate(paths):
    print(f"\nPath {i + 1}:")
    for step in path:
        print(step)

