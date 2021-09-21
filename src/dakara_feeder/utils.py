"""Various utilities."""


def divide_chunks(listing, size):
    """Yield successive chunks from given listing.

    Args:
        listing (list): List of objects to slice.
        size (int): Maximum size of each chunk.

    Yield:
        list: List of objects of limited size.
    """
    # looping till length listing
    for i in range(0, len(listing), size):
        yield listing[i : i + size]


def clean_dict(target, keys):
    """Rebuild a new dictionary from requested keys.

    Args:
        target (dict): Dictionary to extract keys from.
        keys (list): List of keys to extract. If one key cannot be found in
            target, it will be ignored.

    Returns:
        dict: Dictionary with requested keys.
    """
    return {key: target[key] for key in keys if key in target}
