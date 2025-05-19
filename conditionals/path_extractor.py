def extract_paths(node, current_path=None, all_paths=None):
    if current_path is None:
        current_path = []
    if all_paths is None:
        all_paths = []

    if not node:
        return all_paths

    if node.true_branch or node.true_statements:
        path = current_path + [(node.condition, "True")]
        if node.true_statements:
            path.append(("Statements", node.true_statements))
        if node.true_branch:
            extract_paths(node.true_branch, path, all_paths)
        else:
            all_paths.append(path)

    if node.false_branch or node.false_statements:
        path = current_path + [(node.condition, "False")]
        if node.false_statements:
            path.append(("Statements", node.false_statements))
        if node.false_branch:
            extract_paths(node.false_branch, path, all_paths)
        else:
            all_paths.append(path)

    if node.next_condition:
        extract_paths(node.next_condition, [], all_paths)

    return all_paths
