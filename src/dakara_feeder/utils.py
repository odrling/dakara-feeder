def divide_chunks(listing, size):
    """Yield successive chunks from given listing

    Args:
        listing (list): List of objects to slice.
        size (int): Maximum size of each chunk.

    Yield:
        list: List of objects of limited size.
    """
    # looping till length listing
    for i in range(0, len(listing), size):
        yield listing[i : i + size]
