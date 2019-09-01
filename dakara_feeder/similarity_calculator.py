from difflib import SequenceMatcher


def calculate_file_path_similarity(path1, path2):
    """Calculate file path similarity, according more value to file name

    Args:
        path1 (path.Path): path to compare.
        path2 (path.Path): path to compare.

    Returns:
        float: Similarity index beetween path1 and path2. Value is between 0
        and 1. 1 representing high similarity.
    """
    basename_similarity = SequenceMatcher(
        None, path1.basename(), path2.basename()
    ).ratio()
    dirname_similarity = SequenceMatcher(None, path1.dirname(), path2.dirname()).ratio()

    return (dirname_similarity + 8 * basename_similarity) / 9
