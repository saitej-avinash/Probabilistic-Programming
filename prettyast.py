import ast
import astpretty

code = """
if x > 1:
    if x > 2:
        return 1
    else:
        return 0
"""

tree = ast.parse(code)
astpretty.pprint(tree)
