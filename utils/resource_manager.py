from gc import collect

"""This module provides utility functions for managing resources in the system. The memory on the PyBadge can be 
affected easily by fragmentation; it seems that once you go below around 7KB of free memory, the system becomes 
unstable. We want to keep the free RAM above this point therefore to keep the system stable."""


def cleanup():
    """
    Perform garbage collection.
    :return:
    """
    collect()
