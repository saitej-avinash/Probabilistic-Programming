def unroll_birthday_loop(K):
    """
    Given a K, generate the equivalent unrolled if/elif/else chain
    for the nested birthday collision check loop.
    """
    code_lines = ["def has_collision_canonical():"]

    indent = "    "
    first = True

    # generate each pair (i, j) check in same order
    for i in range(1, K):
        for j in range(i):
            if first:
                code_lines.append(f"{indent}if b{i} == b{j}:")
                first = False
            else:
                code_lines.append(f"{indent}elif b{i} == b{j}:")
            code_lines.append(f"{indent*2}return 1")

    # add final else branch
    code_lines.append(f"{indent}else:")
    code_lines.append(f"{indent*2}return 0")

    return "\n".join(code_lines)


print(unroll_birthday_loop(23))
