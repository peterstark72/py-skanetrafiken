#!/usr/bin/env python3
# encoding: utf-8
"""
Skanetrafiken API Python 3 module
av Peter Stark <peterstark72@gmail.com>

Repo på <https://github.com/peterstark72/skanetrafiken>

För API dokumentation, se <http://www.labs.skanetrafiken.se/api.asp>

Exempel:

>>> import skanetrafiken
>>> sk.querystation("Malmö C")
>>> sk.resultspage("next", "Malmö C|80000|0", "landskrona|82000|0")

"""
from urllib.parse import urlencode
from urllib.request import urlopen
from lxml import etree
import logging
import urllib

__version__ = "2.1"

# XML namespace
XMLNS = u"{{http://www.etis.fskab.se/v1.0/ETISws}}{}"

API_SERVER_URL = "http://www.labs.skanetrafiken.se/v2.2/{}.asp"


def boolean(x):
    if x == "True":
        return True


def stringify(element):
    '''Concatenates all text in the subelements into one string'''
    return u"".join([x for x in element.itertext()]).strip()


class SkanetrafikenException(Exception):
    pass

POINTTYPE = ("STOP_AREA", "ADDRESS", "POI", "UNKNOWN")
POINT = 'Point',\
    {'Id': str, 'Name': str, 'Type': str, 'X': int, 'Y': int}
NEARESTSTOPAREA = 'NearestStopArea', \
    {'Id': str, 'Name': str, 'X': int, 'Y': int, 'Distance': int}
REALTIMEINFO = 'RealTimeInfo', \
    {'DepTimeDeviation': int, 'DepDeviationAffect': str}
LINE = 'Line', \
    {'Name': str, 'No': str, 'JourneyDateTime': str,
     'LineTypeName': str, 'Towards': str, 'RealTime': REALTIMEINFO}
LINES = 'Lines', {'Line': LINE}
TO = 'To', {'Id': str, 'Name': str}
FROM = 'From', {'Id': str, 'Name': str}
TRANSPORTMODE = 'TransportMode', \
    {'Id': int, 'Name': str, 'DefaultChecked': boolean}
LINETYPE = 'LineType', \
    {'Id': int, 'Name': str, 'DefaultChecked': boolean}
ROUTELINK = 'RouteLink',\
    {'RouteLinkKey': str, 'DepDateTime': str,
     'DepIsTimingPoint': boolean, 'ArrDateTime': str,
     'ArrIsTimingPoint': boolean, 'From': FROM, 'To': TO, 'Line': LINE}
JOURNEY = 'Journey', \
    {'SequenceNo': int, 'DepDateTime': str, 'ArrDateTime': str,
     'DepWalkDist': int, 'ArrWalkDist': int, 'NoOfChanges': int,
     'Guaranteed': boolean, 'CO2factor': int, 'NoOfZones': int,
     'JourneyKey': str, 'FareType': str, 'Distance': int,
     'CO2value': str, 'RouteLinks': ROUTELINK}
GETJOURNEYPATHRESULT = 'GetJourneyPathResult',\
    {'Code': int, 'Message': str, 'ResultXML': str}
GETJOURNEYRESULT = 'GetJourneyResult', \
    {'Code': int, 'Message': str, 'JourneyResultKey': str,
     'Journeys': JOURNEY}
GETSTARTENDPOINTRESULT = 'GetStartEndPointResult',\
    {'Code': int, 'Message': str, 'StartPoints': POINT,
     'EndPoints': POINT}
GETNEARESTSTOPAREARESULT = 'GetNearestStopAreaResult', \
    {'Code': int, 'Message': str, 'NearestStopAreas': NEARESTSTOPAREA}
GETDEPARTUREARRIVALRESULT = 'GetDepartureArrivalResult',\
    {'Code': int, 'Message': str, 'Lines': LINE}
GETMEANSOFTRANSPORTRESULT = 'GetMeansOfTransportResult', \
    {'Code': int, 'Message': str, 'TransportModes': TRANSPORTMODE,
     'LineTypes': LINETYPE}


SKANETRAFIKEN_METHODS = {
    'querystation': {
        'returns': GETSTARTENDPOINTRESULT,
        'listtypes': ['StartPoints', 'EndPoints']
    },
    'neareststation': {
        'returns': GETNEARESTSTOPAREARESULT,
        'listtypes': ['NearestStopAreas']
    },
    'stationresults': {
        'returns': GETDEPARTUREARRIVALRESULT,
        'listtypes': ['Lines']
    },
    'trafficmeans': {
        'returns': GETMEANSOFTRANSPORTRESULT,
        'listtypes': ['LineTypes', 'TransportModes']
    },
    'resultspage': {
        'returns': GETJOURNEYRESULT,
        'listtypes': ['Journeys', 'RouteLinks']
    },
    'querypage': {
        'returns': GETSTARTENDPOINTRESULT,
        'listtypes': ['StartPoints', 'EndPoints']
    },
    'journeypath': {
        'returns': GETJOURNEYPATHRESULT,
        'listtypes': []
    }
}


def neareststation(x, y, R):
    '''
    X   x coordinate, RT 90 system
    Y   y coordinate, RT 90 system
    R   radius in meters
    '''
    return call_method('neareststation', **locals())


def trafficmeans():
    '''Returns current traffic means'''
    return call_method('trafficmeans', **locals())


def querypage(inpPointFr, inpPointTo):
    '''Search start and end point'''
    return call_method('querypage', **locals())


def querystation(inpPointFr):
    '''Search stop area'''
    return call_method('querystation', **locals())


def resultspage(selPointFr, selPointTo, cmdAction="next",
                inpTime=None, inpDate=None, transportMode=None,
                LastStart=None, FirstStart=None):
    '''
    inpTime       [Optional] time for journey
    inpDate       [Optional] journey  date
    selPointFr    departure point name|id|type
    selPointTo    destination point name|id|type
    NoOf          [Optional] No of journeys in result
    transportMode [Optional] Sum of linetype ids retrieved
                    from trafficmeans method
    cmdAction     search/next/previous set of journeys
    LastStart     [Optional] date&time of last journey in previous results
                    (used in conjunction with cmdAction = next)
    FirstStart    [Optional] date&time of first journey in previous results
                    (used in conjunction with cmdAction = previous)
    '''
    return call_method('resultspage', **locals())


def journeypath(cf, id):
    '''
    cf     JourneyKey retrieved in response from resultspage method
    id     SequenceNo of journey retrieved in response from resultspage method
    '''
    return call_method('journeypath', **locals())


def stationresults(selPointFrKey, inpDate=None,
                   inpTime=None, selDirection=None):
    '''
    selPointFrKey   Stop Area id
    inpDate         [Optional] date for departure
    inpTime         [Optional] time for departure
    selDirection    [Optional] 0 = departures, 1 = arrivals
    '''
    return call_method('stationresults', **locals())


def build_map(target_node, conversions, list_types):

    data = {}

    for key, conversion in conversions.items():
        key_element = target_node.find(XMLNS.format(key))
        if (key_element is not None):

            if (isinstance(conversion, tuple)):
                #We have a complex type
                complex_key, complex_conversion = conversion

                if (key in list_types):
                    #We have a list of complex type
                    data[key] = []
                    complex_nodes = \
                        key_element.findall(XMLNS.format(complex_key))
                    for conode in complex_nodes:
                        data[key].append(build_map(conode,
                                         complex_conversion, list_types))
                else:
                    #We have one complex type
                    data[key] = build_map(key_element, complex_conversion,
                                          list_types)
            else:
                data[key] = conversion(stringify(key_element))

    return data


def build_return(doc, meta):

    element, conversions = meta['returns']

    #Get the target element
    e = doc.find(".//"+XMLNS.format(element))

    #Return empty if no top element is found
    if(e is None):
        raise SkanetrafikenException("No result")

    code = e.find(XMLNS.format("Code"))
    msg = e.find(XMLNS.format("Message"))
    if code.text != "0":
        raise SkanetrafikenException(msg.text)

    #Start building
    return build_map(e, conversions, meta['listtypes'])


def call_method(method, **kw):

    # UTF-8 encode all arguments
    data = {}
    for k in [k for k in kw if kw[k] is not None]:
        data[k] = str(kw[k]).encode("utf-8")
    encoded_args = urlencode(data)

    # Build URL
    url = API_SERVER_URL.format(method) + "?" + encoded_args

    try:
        response = urlopen(url)
        result = response.read()
        doc = etree.fromstring(result)
    except:
        raise SkanetrafikenException("Could not connect to server")
    finally:
        logging.info("GET: {}".format(url))

    return build_return(doc, SKANETRAFIKEN_METHODS[method])


if __name__ == '__main__':

    print(querystation("Tygelsjö"))

'''
    print querypage(u"Tygelsjö", u"Göteborg")
    print stationresults(80421)

    try:
        r = resultspage(u"Malmö|80000|0", u"landskrona|82000|0")
        cf = r.get("JourneyResultKey")
        print journeypath(cf, 1)
    except SkanetrafikenException as e:
        print e
'''

