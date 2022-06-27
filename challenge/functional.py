# -*- coding: utf-8 -*-
"""Functional utilities"""
#pylint: disable=invalid-name

def fmap(f, xs):
    """
    Map a function f over the values in an iterable xs and return a list
    This in effect is the same function as `map`, only returning a list for
    convenience
    """
    return list(map(f, xs))

def compose(f, g):
    """
    Return a function that applies g to its argument and then f
    """
    return lambda x: f(g(x))

def length(xs):
    """Return the number of elements in the list"""
    return len(xs)

def first(xs):
    """
    Get the first item in a sequence
    Example:
        assert first([1,2,3]) == 1
    """
    return next(iter(xs))

def last(xs):
    """
    Get the last element in a sequence
    Example:
        assert last([1,2,3]) == 3
    """
    return xs[-1]

def tail(xs):
    """
    Return the sequence without the first item
    Example:
        assert tail([1, 2, 3]) == [2, 3]
    """
    return xs[1:]

def zip_with(f, xs, ys):
    """
    Generalization of zip where the function f is applied
    instead of making a tuple.
    """
    return [f(a, b) for (a, b) in zip(xs, ys)]
