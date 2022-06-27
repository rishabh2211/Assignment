# -*- coding: utf-8 -*-

""" Defines the API for a stop """

import json
from typing import List
import requests

from .functional import (fmap, length)

__URL = "https://api-v3.mbta.com"
"""URL of the request"""

class Stop:
    """
    A Stop is a location at which one may embark/disembark a public
    transportation vehicle
    """
    #pylint: disable=redefined-builtin
    def __init__(self, id, name):
        self.__id = id
        self.__name = name

    def __hash__(self):
        return hash(self.__id)

    def __eq__(self, rhs):
        return self.__id == rhs.id()

    def __repr__(self):
        return 'Stop(\'{}\', \'{}\')'.format(self.__id, self.__name)

    def id(self) -> str:
        """Get the unique id of this stop"""
        #pylint: disable=invalid-name
        return self.__id

    def name(self) -> str:
        """Get the name of this stop"""
        return self.__name

class Route:
    """
    A Route is a named a list of subway Stops
    """
    #pylint: disable=redefined-builtin
    def __init__(self, id, name, stops):
        self.__id = id
        self.__name = name
        self.__stops = stops

    def __eq__(self, another):
        return self.__id == another.id()

    def __hash__(self):
        return hash(self.__id)

    def __repr__(self):
        return "Route(\'{}\', \'{}\')".format(self.__id, self.__name)

    def id(self) -> str:
        """Get the unique id of this stop"""
        #pylint: disable=invalid-name
        return self.__id

    def name(self) -> str:
        """Get the name of this Route"""
        return self.__name

    def stops(self) -> List[Stop]:
        """Get a list of Stops in this Route"""
        return self.__stops

def __on_bad_response(response):
    spec = "Received {code:d} from mbda: {detail}"
    msg = spec.format(code=response.status_code, detail=response.reason)
    raise RuntimeError(msg)

def __mbta_data_request(query):
    #pylint: disable=no-member
    response = requests.get(__URL + query)
    if response.status_code != requests.codes.ok:
        __on_bad_response(response)

    payload = json.loads(response.text)
    return payload["data"]

def __get_attribute(route, attr):
    return route["attributes"][attr]

def __id(json_element):
    return json_element['id']

def __make_stop_from_json(json_stop):
    return Stop(__id(json_stop), __get_attribute(json_stop, 'name'))

def __load_stops_for_route(json_route):
    query = '/stops?filter[route]={}'.format(__id(json_route))
    stops = __mbta_data_request(query)
    return fmap(__make_stop_from_json, stops)

def __make_route_from_json(json_route):
    return Route(__id(json_route),
                 __get_attribute(json_route, 'long_name'),
                 __load_stops_for_route(json_route))

def load_routes() -> List[Route]:
    """Query the mbta api for all type 0 and 1 routes"""
    # Request that the server filter the results to limit the amount of
    # data that gets sent back.
    json_routes = __mbta_data_request('/routes?filter[type]=0,1')
    return fmap(__make_route_from_json, json_routes)

def num_stops(route) -> int:
    """Get the number of stops in the route"""
    return length(route.stops())
