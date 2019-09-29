import itertools


def generate_diff(old_list, new_list):
    """Returns 2 lists of added, deleted and unchanged elements

    Added elements are elements presents in new_list but not in old_list.
    Deleted elements are elements presents in old_list but not in new_list.

    Args:
        old_list (list): Old list.
        new_list (list): New list.

    Returns:
        tuple: contains 2 elements:
            - A list of added elements;
            - A list of deleted elements.
            - A list of unchanged elements.
    """
    old_set = set(old_list)
    new_set = set(new_list)

    added = new_set - old_set
    deleted = old_set - new_set
    unchanged = old_set.intersection(new_set)

    return list(added), list(deleted), list(unchanged)


def match_similar(list1, list2, compute_similarity, threshold=0.8):
    """Match similar strings between list1 and list2 using the compute_similarity method

    Args:
        list1 (list): Elements to match.
        list2 (list): Elements to match.
        compute_similarity (function): Funtion taking as argument element from
            first list and element from second list. Should return a float
            between 0 and 1 indicating similarity (1 meaning high similarity,
            0 low similarity).
        threshold (float): Only consider pairs with similarity higher than this
            value. Default is 0.8.

    Returns:
        tuple of list: contains 3 values.
            first value: list of tuple with matching elements from list1 and
                list2.
            second value: list of unmatched elements from list1.
            third value: list of unmatched elements from list2.
    """
    items1 = list1.copy()
    items2 = list2.copy()

    # Generate list of similarity for each pair of items
    pairs = []
    for item1, item2 in itertools.product(items1, items2):
        similarity = compute_similarity(item1, item2)
        if similarity > threshold:
            pairs.append({"similarity": similarity, "item1": item1, "item2": item2})

    # Sort the pair of items with higher similarity first
    pairs.sort(key=lambda e: e["similarity"], reverse=True)

    # Loop over all pairs and create match if elements not already matched with
    # a higher similarity element
    matched_elements = []
    for pair in pairs:
        item1 = pair["item1"]
        item2 = pair["item2"]

        if item1 not in items1 or item2 not in items2:
            # Element already matched with a higher similarity item
            continue

        # Create match
        matched_elements.append((item1, item2))
        # Remove matched elements from source lists
        items1.remove(item1)
        items2.remove(item2)

    return matched_elements, items1, items2
