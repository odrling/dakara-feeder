"""Compute similarities."""

from difflib import SequenceMatcher


def calculate_file_path_similarity(path1, path2, weight_dirname=1, weight_basename=8):
    """Calculate file path similarity, according more value to file name.

    Use a simple weighted sum formula.

    Args:
        path1 (path.Path): Path to compare.
        path2 (path.Path): Path to compare.
        weight_dirname (float): Importance of the directory name in similarity
            calculation. Result is divided by the sum of all weights.
        weight_basename (float): Importance of the base name in similarity
            calculation. Result is divided by the sum of all weights.

    Returns:
        float: Similarity value beetween the two paths. Value is between 0
        and 1. 1 representing high similarity.
    """
    basename_similarity = compute_symmetric_gestalt_pattern_matching(
        path1.basename(), path2.basename()
    )
    dirname_similarity = compute_symmetric_gestalt_pattern_matching(
        path1.dirname(), path2.dirname()
    )

    return (
        dirname_similarity * weight_dirname + basename_similarity * weight_basename
    ) / (weight_dirname + weight_basename)


def compute_symmetric_gestalt_pattern_matching(val1, val2):
    """Compute a symmetric ratio using `SequenceMatcher`.

    Use two `SequenceMatcher` instances with reversed arguments position.
    Compute the mean ratio of the two.

    Args:
        val1 (str): Value to compare.
        val2 (str): Value to compare.

    Returns:
        float: Symmetric ratio of similarity.
    """
    return 0.5 * (
        SequenceMatcher(None, val1, val2).ratio()
        + SequenceMatcher(None, val2, val1).ratio()
    )
