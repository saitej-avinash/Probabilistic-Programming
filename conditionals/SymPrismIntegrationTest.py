#!/usr/bin/env python3
"""
Build a PRISM DTMC directly from an embedded symbolic-path dump.

- Parses blocks like:
  Path: (('x > 1', 'True'), ..., ('Statements', ('return 1',)))
  Probability: 0.727273

- Emits paths_embedded.prism + a quick summary on stdout.
"""

import re
from decimal import Decimal, getcontext

getcontext().prec = 50  # high precision for clean remainder arithmetic

# ============================
# 1) Paste your dump here
# ============================
DUMP = """
Path: (('x > 1', 'True'), ('x > 2', 'True'), ('Statements', ('return 1',)))
Probability: 0.727273

Path: (('x > 1', 'True'), ('x > 2', 'False'), ('Statements', ('return 0',)))
Probability: 0.090909

Path: (('x > 1', 'False'), ('x > 3', 'True'), ('Statements', ('return 0',)))
Probability: 0.000000

Path: (('x > 1', 'False'), ('x > 3', 'False'), ('Statements', ('pass',)))
Probability: 0.181818
""".strip()


BDYUMP = """ 
Path: (('b1 == b0', 'True'), ('Statements', ('return 1',)))
Probability: 0.142857

Path: (('b1 == b0', 'False'), ('b2 == b0', 'True'), ('Statements', ('return 1',)))
Probability: 0.122449

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'True'), ('Statements', ('return 1',)))
Probability: 0.122449

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'True'), ('Statements', ('return 1',)))
Probability: 0.087464

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'True'), ('Statements', ('return 1',)))
Probability: 0.087464

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'True'), ('Statements', ('return 1',)))
Probability: 0.087464

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'True'), ('Statements', ('return 1',)))
Probability: 0.049979

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'True'), ('Statements', ('return 1',)))
Probability: 0.049979

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'True'), ('Statements', ('return 1',)))
Probability: 0.049979

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'True'), ('Statements', ('return 1',)))
Probability: 0.049979

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'True'), ('Statements', ('return 1',)))
Probability: 0.021420

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'True'), ('Statements', ('return 1',)))
Probability: 0.021420

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'True'), ('Statements', ('return 1',)))
Probability: 0.021420

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'True'), ('Statements', ('return 1',)))
Probability: 0.021420

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'True'), ('Statements', ('return 1',)))
Probability: 0.021420

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'True'), ('Statements', ('return 1',)))
Probability: 0.006120

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'True'), ('Statements', ('return 1',)))
Probability: 0.006120

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'True'), ('Statements', ('return 1',)))
Probability: 0.006120

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'True'), ('Statements', ('return 1',)))
Probability: 0.006120

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'True'), ('Statements', ('return 1',)))
Probability: 0.006120

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'True'), ('Statements', ('return 1',)))
Probability: 0.006120

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'True'), ('Statements', ('return 1',)))
Probability: 0.000874

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'True'), ('Statements', ('return 1',)))
Probability: 0.000874

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'True'), ('Statements', ('return 1',)))
Probability: 0.000874

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'True'), ('Statements', ('return 1',)))
Probability: 0.000874

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'True'), ('Statements', ('return 1',)))
Probability: 0.000874

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'True'), ('Statements', ('return 1',)))
Probability: 0.000874

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'False'), ('b7 == b6', 'True'), ('Statements', ('return 1',)))
Probability: 0.000874

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'False'), ('b7 == b6', 'False'), ('b8 == b0', 'True'), ('Statements', ('return 1',)))
Probability: 0.000000

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'False'), ('b7 == b6', 'False'), ('b8 == b0', 'False'), ('b8 == b1', 'True'), ('Statements', ('return 1',)))
Probability: 0.000000

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'False'), ('b7 == b6', 'False'), ('b8 == b0', 'False'), ('b8 == b1', 'False'), ('b8 == b2', 'True'), ('Statements', ('return 1',)))
Probability: 0.000000

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'False'), ('b7 == b6', 'False'), ('b8 == b0', 'False'), ('b8 == b1', 'False'), ('b8 == b2', 'False'), ('b8 == b3', 'True'), ('Statements', ('return 1',)))
Probability: 0.000000

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'False'), ('b7 == b6', 'False'), ('b8 == b0', 'False'), ('b8 == b1', 'False'), ('b8 == b2', 'False'), ('b8 == b3', 'False'), ('b8 == b4', 'True'), ('Statements', ('return 1',)))
Probability: 0.000000

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'False'), ('b7 == b6', 'False'), ('b8 == b0', 'False'), ('b8 == b1', 'False'), ('b8 == b2', 'False'), ('b8 == b3', 'False'), ('b8 == b4', 'False'), ('b8 == b5', 'True'), ('Statements', ('return 1',)))
Probability: 0.000000

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'False'), ('b7 == b6', 'False'), ('b8 == b0', 'False'), ('b8 == b1', 'False'), ('b8 == b2', 'False'), ('b8 == b3', 'False'), ('b8 == b4', 'False'), ('b8 == b5', 'False'), ('b8 == b6', 'True'), ('Statements', ('return 1',)))
Probability: 0.000000

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'False'), ('b7 == b6', 'False'), ('b8 == b0', 'False'), ('b8 == b1', 'False'), ('b8 == b2', 'False'), ('b8 == b3', 'False'), ('b8 == b4', 'False'), ('b8 == b5', 'False'), ('b8 == b6', 'False'), ('b8 == b7', 'True'), ('Statements', ('return 1',)))
Probability: 0.000000

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'False'), ('b7 == b6', 'False'), ('b8 == b0', 'False'), ('b8 == b1', 'False'), ('b8 == b2', 'False'), ('b8 == b3', 'False'), ('b8 == b4', 'False'), ('b8 == b5', 'False'), ('b8 == b6', 'False'), ('b8 == b7', 'False'), ('b9 == b0', 'True'), ('Statements', ('return 1',)))
Probability: 0.000000

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'False'), ('b7 == b6', 'False'), ('b8 == b0', 'False'), ('b8 == b1', 'False'), ('b8 == b2', 'False'), ('b8 == b3', 'False'), ('b8 == b4', 'False'), ('b8 == b5', 'False'), ('b8 == b6', 'False'), ('b8 == b7', 'False'), ('b9 == b0', 'False'), ('b9 == b1', 'True'), ('Statements', ('return 1',)))
Probability: 0.000000

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'False'), ('b7 == b6', 'False'), ('b8 == b0', 'False'), ('b8 == b1', 'False'), ('b8 == b2', 'False'), ('b8 == b3', 'False'), ('b8 == b4', 'False'), ('b8 == b5', 'False'), ('b8 == b6', 'False'), ('b8 == b7', 'False'), ('b9 == b0', 'False'), ('b9 == b1', 'False'), ('b9 == b2', 'True'), ('Statements', ('return 1',)))
Probability: 0.000000

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'False'), ('b7 == b6', 'False'), ('b8 == b0', 'False'), ('b8 == b1', 'False'), ('b8 == b2', 'False'), ('b8 == b3', 'False'), ('b8 == b4', 'False'), ('b8 == b5', 'False'), ('b8 == b6', 'False'), ('b8 == b7', 'False'), ('b9 == b0', 'False'), ('b9 == b1', 'False'), ('b9 == b2', 'False'), ('b9 == b3', 'True'), ('Statements', ('return 1',)))
Probability: 0.000000

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'False'), ('b7 == b6', 'False'), ('b8 == b0', 'False'), ('b8 == b1', 'False'), ('b8 == b2', 'False'), ('b8 == b3', 'False'), ('b8 == b4', 'False'), ('b8 == b5', 'False'), ('b8 == b6', 'False'), ('b8 == b7', 'False'), ('b9 == b0', 'False'), ('b9 == b1', 'False'), ('b9 == b2', 'False'), ('b9 == b3', 'False'), ('b9 == b4', 'True'), ('Statements', ('return 1',)))
Probability: 0.000000

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'False'), ('b7 == b6', 'False'), ('b8 == b0', 'False'), ('b8 == b1', 'False'), ('b8 == b2', 'False'), ('b8 == b3', 'False'), ('b8 == b4', 'False'), ('b8 == b5', 'False'), ('b8 == b6', 'False'), ('b8 == b7', 'False'), ('b9 == b0', 'False'), ('b9 == b1', 'False'), ('b9 == b2', 'False'), ('b9 == b3', 'False'), ('b9 == b4', 'False'), ('b9 == b5', 'True'), ('Statements', ('return 1',)))
Probability: 0.000000

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'False'), ('b7 == b6', 'False'), ('b8 == b0', 'False'), ('b8 == b1', 'False'), ('b8 == b2', 'False'), ('b8 == b3', 'False'), ('b8 == b4', 'False'), ('b8 == b5', 'False'), ('b8 == b6', 'False'), ('b8 == b7', 'False'), ('b9 == b0', 'False'), ('b9 == b1', 'False'), ('b9 == b2', 'False'), ('b9 == b3', 'False'), ('b9 == b4', 'False'), ('b9 == b5', 'False'), ('b9 == b6', 'True'), ('Statements', ('return 1',)))
Probability: 0.000000

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'False'), ('b7 == b6', 'False'), ('b8 == b0', 'False'), ('b8 == b1', 'False'), ('b8 == b2', 'False'), ('b8 == b3', 'False'), ('b8 == b4', 'False'), ('b8 == b5', 'False'), ('b8 == b6', 'False'), ('b8 == b7', 'False'), ('b9 == b0', 'False'), ('b9 == b1', 'False'), ('b9 == b2', 'False'), ('b9 == b3', 'False'), ('b9 == b4', 'False'), ('b9 == b5', 'False'), ('b9 == b6', 'False'), ('b9 == b7', 'True'), ('Statements', ('return 1',)))
Probability: 0.000000

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'False'), ('b7 == b6', 'False'), ('b8 == b0', 'False'), ('b8 == b1', 'False'), ('b8 == b2', 'False'), ('b8 == b3', 'False'), ('b8 == b4', 'False'), ('b8 == b5', 'False'), ('b8 == b6', 'False'), ('b8 == b7', 'False'), ('b9 == b0', 'False'), ('b9 == b1', 'False'), ('b9 == b2', 'False'), ('b9 == b3', 'False'), ('b9 == b4', 'False'), ('b9 == b5', 'False'), ('b9 == b6', 'False'), ('b9 == b7', 'False'), ('b9 == b8', 'True'), ('Statements', ('return 1',)))
Probability: 0.000000

Path: (('b1 == b0', 'False'), ('b2 == b0', 'False'), ('b2 == b1', 'False'), ('b3 == b0', 'False'), ('b3 == b1', 'False'), ('b3 == b2', 'False'), ('b4 == b0', 'False'), ('b4 == b1', 'False'), ('b4 == b2', 'False'), ('b4 == b3', 'False'), ('b5 == b0', 'False'), ('b5 == b1', 'False'), ('b5 == b2', 'False'), ('b5 == b3', 'False'), ('b5 == b4', 'False'), ('b6 == b0', 'False'), ('b6 == b1', 'False'), ('b6 == b2', 'False'), ('b6 == b3', 'False'), ('b6 == b4', 'False'), ('b6 == b5', 'False'), ('b7 == b0', 'False'), ('b7 == b1', 'False'), ('b7 == b2', 'False'), ('b7 == b3', 'False'), ('b7 == b4', 'False'), ('b7 == b5', 'False'), ('b7 == b6', 'False'), ('b8 == b0', 'False'), ('b8 == b1', 'False'), ('b8 == b2', 'False'), ('b8 == b3', 'False'), ('b8 == b4', 'False'), ('b8 == b5', 'False'), ('b8 == b6', 'False'), ('b8 == b7', 'False'), ('b9 == b0', 'False'), ('b9 == b1', 'False'), ('b9 == b2', 'False'), ('b9 == b3', 'False'), ('b9 == b4', 'False'), ('b9 == b5', 'False'), ('b9 == b6', 'False'), ('b9 == b7', 'False'), ('b9 == b8', 'False'), ('Statements', ('return 0',)))
Probability: 0.000000
""".strip()


# ============================
# 2) Parse the dump
# ============================
PATH_RE = re.compile(r"^Path:\s*\((.*)\)\s*$")
PROB_RE = re.compile(r"^Probability:\s*([0-9]*\.?[0-9]+)\s*$")

def parse_dump(text: str):
    """Return list of dicts: [{'id':k,'prob':Decimal,'outcome':'win|lose|pass','raw':...}, ...]"""
    lines = [ln.rstrip() for ln in text.splitlines()]
    i = 0
    k = 0
    paths = []
    while i < len(lines):
        m = PATH_RE.match(lines[i])
        if m:
            k += 1
            raw = m.group(1)
            # probability line (skip blank lines)
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j >= len(lines):
                raise ValueError(f"Missing Probability after Path {k}")
            pm = PROB_RE.match(lines[j])
            if not pm:
                raise ValueError(f"Expected 'Probability:' after Path {k}, got: {lines[j]}")
            prob = Decimal(pm.group(1))

            # detect outcome from the 'Statements' part
            raw_lower = raw.lower()
            if "return 1" in raw_lower or "return1" in raw_lower:
                outcome = "win"
            elif "return 0" in raw_lower or "return0" in raw_lower:
                outcome = "lose"
            elif "pass" in raw_lower:
                outcome = "pass"
            else:
                # default to pass if unspecified
                outcome = "pass"

            paths.append({"id": k, "prob": prob, "outcome": outcome, "raw": raw})
            i = j + 1
        else:
            i += 1
    return paths


# ============================
# 3) Build PRISM text
# ============================
def build_prism(paths, model_name="paths_embedded"):
    # drop zero-probability paths
    nz = [p for p in paths if p["prob"] > 0]
    if not nz:
        raise ValueError("All paths have zero probability.")

    # normalize
    total = sum(p["prob"] for p in nz)
    norm_probs = [p["prob"] / total for p in nz]

    # initial branching with exact remainder on the last branch
    branches = []
    running = Decimal("0")
    for idx, p in enumerate(nz):
        pid = p["id"]          # terminal state id
        desc = p["outcome"]
        if idx < len(nz) - 1:
            prob = norm_probs[idx]
            branches.append(f"      {prob:.12f} : (s'={pid})  // path {pid}: {desc}")
            running += prob
        else:
            remainder = Decimal("1") - running
            branches.append(f"      {remainder:.30f} : (s'={pid})  // path {pid}: {desc}")

    max_state = max(p["id"] for p in nz)
    loops = "\n".join([f"  [] s={p['id']} -> (s'={p['id']});" for p in nz])

    win_states  = [str(p["id"]) for p in nz if p["outcome"] == "win"]
    lose_states = [str(p["id"]) for p in nz if p["outcome"] == "lose"]
    win_label  = " | ".join([f"s={w}" for w in win_states]) if win_states else "false"
    lose_label = " | ".join([f"s={l}" for l in lose_states]) if lose_states else "false"

    prism = f"""dtmc

module {model_name}
  // s=0 is start. Terminals are the path indices that had non-zero probability.
  s : [0..{max_state}] init 0;

  [] s=0 ->
{(" \n").join(branches)};
{loops}
endmodule

label "win"  = {win_label};
label "lose" = {lose_label};
"""
    return prism


# ============================
# 4) Run
# ============================
if __name__ == "__main__":
    parsed = parse_dump(BDYUMP)
    prism_text = build_prism(parsed, model_name="paths_embedded")
    with open("paths_embedded.prism", "w") as f:
        f.write(prism_text)

    p_win  = sum(p["prob"] for p in parsed if p["outcome"] == "win")
    p_lose = sum(p["prob"] for p in parsed if p["outcome"] == "lose")
    #p_pass = sum(p["prob"] for p in parsed if p["outcome"] == "pass")

    print("Wrote paths_embedded.prism")
    print(f"P(win)  = {p_win} ({p_win.normalize()})")
    print(f"P(lose) = {p_lose} ({p_lose.normalize()})")
    #print(f"P(pass) = {p_pass} ({p_pass.normalize()})")
