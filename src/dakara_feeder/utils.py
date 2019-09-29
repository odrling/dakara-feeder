def divide_chunks(l, n):
    """Yield successive n-sized
    chunks from l."""
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i : i + n]
