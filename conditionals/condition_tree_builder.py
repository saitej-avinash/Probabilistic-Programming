import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import ast
from conditionals.condition_node import ConditionNode

class ConditionTreeBuilder(ast.NodeVisitor):
    def __init__(self):
        self.root = None
        self.current = None

    def visit_If(self, node):
        condition = ast.unparse(node.test)
        condition_node = ConditionNode(condition=condition)

        if not self.root:
            self.root = condition_node
            self.current = condition_node
        else:
            if self.current is not None:
                if self.current.next_condition is None:
                    self.current.next_condition = condition_node
                else:
                    current = self.current.next_condition
                    while current.next_condition:
                        current = current.next_condition
                    current.next_condition = condition_node

        parent = self.current
        self.current = condition_node

        true_branch_builder = ConditionTreeBuilder()
        for stmt in node.body:
            if isinstance(stmt, ast.If):
                true_branch_builder.visit(stmt)
            else:
                condition_node.true_statements.append(ast.unparse(stmt))
        condition_node.true_branch = true_branch_builder.root

        false_branch_builder = ConditionTreeBuilder()
        if node.orelse:
            for stmt in node.orelse:
                if isinstance(stmt, ast.If):
                    false_branch_builder.visit(stmt)
                else:
                    condition_node.false_statements.append(ast.unparse(stmt))
        elif not self.current.next_condition:
            condition_node.false_statements.append("pass")

        condition_node.false_branch = false_branch_builder.root
        self.current = parent

    def build_tree(self, code):
        tree = ast.parse(code)
        self.visit(tree)
        return self.root
