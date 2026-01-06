import random
from types import FunctionType

def gen_birthday_chain_source(K: int, N: int = 365, func_name: str = "birthday_paradox_chain") -> str:
    """
    Generate Python source for a function that:
      - samples b0..b{K-1} ~ Uniform(0..N-1)
      - checks equality in the exact nested if/elif order
      - returns 1 on the first match, else 0 at the final else.
    The generated function signature is: def <func_name>(N=<N>):
    """
    if K <= 0:
        raise ValueError("K must be >= 1")

    lines = []
    lines.append("import random")
    lines.append(f"def {func_name}(N={N}):")
    IND = "    "

    # sample b0..b{K-1}
    for i in range(K):
        lines.append(f"{IND}b{i} = random.randrange(N)")
        if i == 0:
            continue

        # start a fresh if/elif chain for bi
        for j in range(i):
            kw = "if" if j == 0 else "elif"
            lines.append(f"{IND}{kw} b{i} == b{j}:")
            lines.append(f"{IND*2}return 1")

        # only for the *last* person we close the chain with an else:return 0
        if i == K - 1:
            lines.append(f"{IND}else:")
            lines.append(f"{IND*2}return 0")

    # Edge case: if K == 1, no comparisons were emitted; ensure we return 0
    if K == 1:
        lines.append(f"{IND}return 0")

    return "\n".join(lines)


def build_birthday_chain_fn(K: int, N: int = 365, func_name: str = "birthday_paradox_chain") -> FunctionType:
    """
    Generate, exec, and return the function object.
    Usage:
        f = build_birthday_chain_fn(4)
        f() -> 0/1
    """
    src = gen_birthday_chain_source(K, N, func_name)
    ns = {}
    exec(src, ns)           # define the function in ns
    return ns[func_name]


# -------------------- Demo --------------------
if __name__ == "__main__":
    K = 4
    N = 365

    # 1) See the exact source that was generated (matches your if/elif pattern)
    print(gen_birthday_chain_source(K, N, "birthday_paradox_chain"))
    print("-" * 60)

    # 2) Build the function object and run a quick Monte Carlo
    f = build_birthday_chain_fn(K, N, "birthday_paradox_chain")
    trials = 200_000
    hits = sum(f() for _ in range(trials))
    print(f"Estimated P(match) for K={K}: {hits / trials:.6f}")
