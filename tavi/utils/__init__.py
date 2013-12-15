# -*- coding: utf-8 -*-
"""Various utility functions."""


def flatten(target):
    """Flatten a list with nested lists into a single list.

    For example::
        flatten([1, [2, 3]) # => [1, 2, 3]

    """
    return [item for sublist in target for item in sublist]
