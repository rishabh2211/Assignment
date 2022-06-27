# -*- coding: utf-8 -*-

"""Defines graph path-finding algorithms used in this challenge"""

from collections import deque
from sys import (maxsize)
from heapq import (heappop, heappush)

from .functional import (first, last)

def dijkstras_shortest_path(graph, start, finish):
    """
    Implementation of dijkstra's famous shortest path algorithm.
    @param  graph: networkx.Graph
    @param  start: The starting node in the graph
    @param finish: The destination node in the graph
    """
    # The bumf suggested we don't use a library to do everything for us, and
    # so using networkx `shortest_path` is a little bit cheaky.

    class Item(tuple):
        """Used to define < (less than) for use with heapq"""
        def __new__(cls, priority, node, previous):
            return tuple.__new__(Item, (priority, node, previous))

        def __lt__(self, rhs):
            return first(self) < first(rhs)

        def __repr__(self):
            priority, node, previous = self
            return 'Item({:d}, \'{}\', \'{}\')'.format(priority, node, previous)

    if start not in graph or finish not in graph:
        msg = f'No route possible bewteen {start.name()} and {finish.name()}'
        raise ValueError(msg)

    distances = {node: (maxsize, None) for node in graph.nodes}
    priority_queue = [Item(0, start, None)]

    while priority_queue:
        # pop the first node with the smallest distance
        distance, node, previous = heappop(priority_queue)

        # only visit vertices we haven't seen yet
        if first(distances[node]) != maxsize:
            continue

        # visit all unseen adjacent nodes and update their distance
        distances[node] = (distance, previous)

        # we've found a shortest path
        if node == finish:
            break

        for neighbor in graph.neighbors(node):
            if first(distances[neighbor]) == maxsize:
                heappush(priority_queue, Item(distance + 1, neighbor, node))

    # Backtrack through the `previous` list to build the path
    path = deque()
    while last(distances[finish]):
        path.appendleft(finish)
        finish = last(distances[finish])
    if path:
        path.appendleft(finish)

    return list(path)
