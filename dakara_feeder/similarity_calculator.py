from difflib import SequenceMatcher


def calculate_file_path_similarity(path1, path2):
    """Calculate file path similarity, according more value to file name

    Use a simple weighted sum formula.

    Args:
        path1 (path.Path): path to compare.
        path2 (path.Path): path to compare.

    Returns:
        float: Similarity index beetween path1 and path2. Value is between 0
        and 1. 1 representing high similarity.
    """
    basename_similarity = compute_symmetric_gestalt_pattern_matching(
        path1.basename(), path2.basename()
    )
    dirname_similarity = compute_symmetric_gestalt_pattern_matching(
        path1.dirname(), path2.dirname()
    )

    return (dirname_similarity + 8 * basename_similarity) / 9


def compute_symmetric_gestalt_pattern_matching(val1, val2):
    """Compute a symmetric ratio using SequenceMatcher

    Use two SequenceMatcher instances with reversed arguments position. Compute
    the mean ratio of the two.

    Args:
        val1 (str): value to compare.
        val2 (str): value to compare.

    Returns:
        float: symmetric ratio of similarity.
    """
    return 0.5 * (
        SequenceMatcher(None, val1, val2).ratio()
        + SequenceMatcher(None, val2, val1).ratio()
    )
