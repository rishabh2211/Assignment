# -*- coding: utf-8 -*-

"""Defines solutions to the challenge questions"""

from typing import (Dict, List, Set, Tuple)
from networkx import MultiGraph

from .algorithm import dijkstras_shortest_path
from .functional import (compose, fmap, first, length, last, tail, zip_with)
from .routes import (Stop, Route, load_routes, num_stops)

def __print_route_info(route):
    print("{}, {:d} stops".format(route.name(), num_stops(route)))

def __print_connection_info(stop, routes):
    print("{}, {}".format(stop, routes))

def find_connecting_stops(routes) -> List[Tuple[Stop, List[Route]]]:
    """
    Find all stops that connect more than one route.
    Return [Stop, [Route]]
    """
    stops = {}
    for route in sorted(routes, key=Route.name):
        for stop in route.stops():
            id_ = stop.id()
            if id_ not in stops:
                stops[id_] = (stop, [])

            last(stops[id_]).append(route)

    return list(filter(lambda p: length(last(p)) > 1, stops.values()))

def make_stop_lookup_table(routes) -> Dict[str, Set[Stop]]:
    """
    Build a dictionary to look up the stop given the name in lower-case
    """
    stops = {}
    for route in routes:
        for stop in route.stops():
            name_ = stop.name().lower()
            if name_ not in stops:
                stops[name_] = set()
            stops[name_].add(stop)

    return stops

def __make_route_graph(routes):
    graph = MultiGraph()
    for route in routes:
        # assume each segment has weight 1 -  we could estimate edge weight via
        # distance bewteen stops (we have location information), but we have
        # no information to tell us how fast any particular service is.
        make_route_segment = lambda src, dst: (src, dst, {'route': route})
        segments = zip_with(make_route_segment, route.stops(), tail(route.stops()))
        graph.add_edges_from(segments)
    return graph

def __get_possible_route_segments(graph, path):
    """Get the set of possible routes we could take to go between stops"""
    edge_data = lambda a, b: graph.get_edge_data(a, b).values()
    routes_between = lambda a, b: map(lambda x: x['route'], edge_data(a, b))
    make_journey_segment = lambda a, b: (a, set(routes_between(a, b)))
    return zip_with(make_journey_segment, path, tail(path))

def __print_change(stop, route):
    print("{} ({})".format(stop.name(), route.name() if route else ""))

def make_itinerary(routes, start, finish) -> List[Tuple[Stop, Route]]:
    """
    Compute a path from start to finish and return a list of Changes
    """
    graph = __make_route_graph(routes)

    # I'm not sure dijkstra is really what we want here. I don't think people
    # mind a few extra stops for a direct service. A nicer algorithm would be
    # minimize the number of changes within some journey time
    path = dijkstras_shortest_path(graph, start, finish)

    if length(path) == 0:
        __on_no_such_route(start, finish)

    segments = __get_possible_route_segments(graph, path)
    current = None
    itinerary = []

    for stop, choices in segments:
        if current not in choices:
            current = first(choices)
            itinerary.append((stop, current))

    itinerary.append((finish, None))
    return itinerary

def __on_unknown_stop(name):
    raise ValueError('Unknown stop "{}"'.format(name))

def __on_no_such_route(start, finish):
    msg = f'Cannot find path between "{start.name()}" and "{finish.name()}"'
    raise ValueError(msg)

def __on_unknown_route_name(name):
    raise ValueError(f'No such route name: "{name}"')

def __on_ambiguous_stop(name):
    print('Warning: duplicate stop detected: "{}"'.format(name))
    print('Journey planner may be inaccurate')

def list_routes():
    """Question 1: List the long names of all routes"""
    for name in sorted(map(Route.name, load_routes())):
        print(name)

def print_route(descriptor):
    """
    Print the name of the route described by descriptor, along with the number
    of stops. Valid descriptor are "longest" or "shortest"
    """
    routes = sorted(load_routes(), key=num_stops)
    selector = last if descriptor == "longest" else first
    __print_route_info(selector(routes))

def list_connections():
    """
    Print all stops that connect two or more routes along with the relevant
    route names for each of 'those stops'
    """
    connections = find_connecting_stops(load_routes())
    for stop, routes in sorted(connections, key=compose(Stop.name, first)):
        __print_connection_info(stop.name(), fmap(Route.name, routes))

def remove_route(routes, route_name):
    if not route_name:
        return routes

    if route_name.lower() not in map(compose(str.lower, Route.name), routes):
        __on_unknown_route_name(route_name)

    return [item for item in routes if item.name().lower() != route_name.lower()]

def plan_route(start, finish, avoid = ''):
    """print the required routes to take to get from start to finish"""
    routes = load_routes()
    stop_names = make_stop_lookup_table(routes)

    def validate(name):
        if name.lower() not in stop_names:
            __on_unknown_stop(name)

        stops = stop_names[name.lower()]
        if length(stops) > 1:
            __on_ambiguous_stop(name)

        return first(stops)

    # hard code removal of the red line
    routes = remove_route(routes, avoid)
    for stop, route in make_itinerary(routes, validate(start), validate(finish)):
        __print_change(stop, route)
