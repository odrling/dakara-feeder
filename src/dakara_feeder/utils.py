def divide_chunks(target, n):
    """Yield successive n-sized chunks from target

    Args:
        target (list): list to extract chunks from.
        n (int): size of the chunk.

    Yields:
        list: chunk of size n.
    """
    # looping till length l
    for i in range(0, len(target), n):
        yield target[i : i + n]


def clean_dict(target, keys):
    """Rebuild a new dictionary from requested keys.

    Args:
        target (dict): dictionary to extract keys from.
        keys (list): list of keys to extract. If one key cannot be found in
            target, it will be ignored.

    Returns:
        dict: dictionary with requested keys.
    """
    return {key: target[key] for key in keys if key in target}
