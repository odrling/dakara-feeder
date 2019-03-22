
def generate_diff(old_list, new_list):
    """Returns 2 lists of added and removed elements

    Added elements are elements presents in new_list but not in old_list
    Removed elements are elements presents in old_list but not in new_list
    
    Args:
        old_list (list): Old list
        new_list (list): New list

    Returns:
        tuple: contains 2 elements:
            list: added elements
            list: removed elements
    """
    old_set = set(old_list)
    new_set = set(new_list)

    added = new_set - old_set
    removed = old_set - new_set

    return list(added), list(removed)
