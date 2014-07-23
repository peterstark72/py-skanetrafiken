#!/usr/bin/env python
# encoding: utf-8
"""
Skanetrafiken API Python module
av Peter Stark <peterstark72@gmail.com>
(Inspirerad av Steve Marshalls Fire Eagle API.)


Repo på <https://github.com/peterstark72/skanetrafiken>

För API dokumentation, se <http://www.labs.skanetrafiken.se/api.asp>

Exempel:

>>> import skanetrafiken
>>> sk = skanetrafiken.Skanetrafiken()
>>> sk.querystation(u"Malmö C")
>>> sk.resultspage("next", u"Malmö C|80000|0", u"landskrona|82000|0")


Copyright (c) 2012, Peter Stark
All rights reserved.

Unless otherwise specified, redistribution and use of this software in
source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * The name of the author nor the names of any contributors may be
      used to endorse or promote products derived from this software without
      specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from lxml import etree
import urllib


#URLs from http://www.labs.skanetrafiken.se/api.asp
XMLNS = u"{{http://www.etis.fskab.se/v1.0/ETISws}}{}"

API_SERVER_URL = "http://www.labs.skanetrafiken.se/v2.2/{}.asp"


def boolean(x):
    if x == "True":
        return True


def stringify(element):
    '''Concatenates all text in the subelements into one string'''
    return u"".join([x for x in element.itertext()]).strip()


POINT = 'Point',\
    {'Id': unicode, 'Name': unicode, 'Type': unicode, 'X': int, 'Y': int}
NEARESTSTOPAREA = 'NearestStopArea', \
    {'Id': unicode, 'Name': unicode, 'X': int, 'Y': int, 'Distance': int}
REALTIMEINFO = 'RealTimeInfo', \
    {'DepTimeDeviation': int, 'DepDeviationAffect': unicode}
LINE = 'Line', \
    {'Name': unicode, 'No': unicode, 'JourneyDateTime': unicode,
     'LineTypeName': unicode, 'Towards': unicode, 'RealTime': REALTIMEINFO}
LINES = 'Lines', {'Line': LINE}
TO = 'To', {'Id': unicode, 'Name': unicode}
FROM = 'From', {'Id': unicode, 'Name': unicode}
TRANSPORTMODE = 'TransportMode', \
    {'Id': int, 'Name': unicode, 'DefaultChecked': boolean}
LINETYPE = 'LineType', \
    {'Id': int, 'Name': unicode, 'DefaultChecked': boolean}
ROUTELINK = 'RouteLink',\
    {'RouteLinkKey': unicode, 'DepDateTime': unicode,
     'DepIsTimingPoint': boolean, 'ArrDateTime': unicode,
     'ArrIsTimingPoint': boolean, 'From': FROM, 'To': TO, 'Line': LINE}
JOURNEY = 'Journey', \
    {'SequenceNo': int, 'DepDateTime': unicode, 'ArrDateTime': unicode,
     'DepWalkDist': int, 'ArrWalkDist': int, 'NoOfChanges': int,
     'Guaranteed': boolean, 'CO2factor': int, 'NoOfZones': int,
     'JourneyKey': unicode, 'FareType': unicode, 'Distance': int,
     'CO2value': unicode, 'RouteLinks': ROUTELINK}
GETJOURNEYPATHRESULT = 'GetJourneyPathResult',\
    {'Code': int, 'Message': unicode, 'ResultXML': unicode}
GETJOURNEYRESULT = 'GetJourneyResult', \
    {'Code': int, 'Message': unicode, 'JourneyResultKey': unicode,
     'Journeys': JOURNEY}
GETSTARTENDPOINTRESULT = 'GetStartEndPointResult',\
    {'Code': int, 'Message': unicode, 'StartPoints': POINT,
     'EndPoints': POINT}
GETNEARESTSTOPAREARESULT = 'GetNearestStopAreaResult', \
    {'Code': int, 'Message': unicode, 'NearestStopAreas': NEARESTSTOPAREA}
GETDEPARTUREARRIVALRESULT = 'GetDepartureArrivalResult',\
    {'Code': int, 'Message': unicode, 'Lines': LINE}
GETMEANSOFTRANSPORTRESULT = 'GetMeansOfTransportResult', \
    {'Code': int, 'Message': unicode, 'TransportModes': TRANSPORTMODE,
     'LineTypes': LINETYPE}


SKANETRAFIKEN_METHODS = {
    'querystation': {
        'required': ['inpPointFr'],
        'optional': ['inpPointTo'],
        'returns': GETSTARTENDPOINTRESULT,
        'listtypes': ['StartPoints', 'EndPoints'],
        'url_template': API_SERVER_URL
    },
    'neareststation': {
        'required': ['x', 'y'],
        'optional': ['R'],
        'returns': GETNEARESTSTOPAREARESULT,
        'listtypes': ['NearestStopAreas'],
        'url_template': API_SERVER_URL
    },
    'stationresults': {
        'required': ['selPointFrKey'],
        'optional': [],
        'returns': GETDEPARTUREARRIVALRESULT,
        'listtypes': ['Lines'],
        'url_template': API_SERVER_URL
    },
    'trafficmeans': {
        'required': [],
        'optional': [],
        'returns': GETMEANSOFTRANSPORTRESULT,
        'listtypes': ['LineTypes', 'TransportModes'],
        'url_template': API_SERVER_URL
    },
    'resultspage': {
        'required': ['cmdaction', 'selPointFr', 'selPointTo'],
        'optional': ['inpTime', 'inpDate', 'LastStart',
                                'FirstStart', 'NoOf', 'transportMode'],
        'returns': GETJOURNEYRESULT,
        'listtypes': ['Journeys', 'RouteLinks'],
        'url_template': API_SERVER_URL
    },
    'querypage': {
        'required': ['inpPointFr', 'inpPointTo'],
        'optional': [],
        'returns': GETSTARTENDPOINTRESULT,
        'listtypes': ['StartPoints', 'EndPoints'],
        'url_template': API_SERVER_URL
    },
    'journeypath': {
        'required': ['cf', 'id'],
        'optional': [],
        'returns': GETJOURNEYPATHRESULT,
        'listtypes': [],
        'url_template': API_SERVER_URL
    }
}


class SkanetrafikenException(Exception):
    pass


class SkanetrafikenAccumulator:
    def __init__(self, skanetrafiken_obj, name):
        self.skanetrafiken_obj = skanetrafiken_obj
        self.name = name

    def __repr__(self):
        return self.name

    def __call__(self, *args, **kw):
        return self.skanetrafiken_obj.call_method(self.name, *args, **kw)


class Skanetrafiken(object):
    '''Looks up times and stops from skanetrafiken.se '''

    def __init__(self):

        for method, _ in SKANETRAFIKEN_METHODS.items():
            if not hasattr(self, method):
                setattr(self, method, SkanetrafikenAccumulator(self, method))

    def build_map(self, target_node, conversions, list_types):

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
                            data[key].append(self.build_map(conode,
                                             complex_conversion, list_types))
                    else:
                        #We have one complex type
                        data[key] = self.build_map(key_element,
                                                   complex_conversion,
                                                   list_types)
                else:
                    data[key] = conversion(stringify(key_element))

        return data

    def build_return(self, doc, target_element, conversions, list_types):

        result = {}

        #Get the target element
        e = doc.find(".//"+XMLNS.format(target_element))

        #Return empty if no top element is found
        if(e is None):
            return result

        #Start building
        result = self.build_map(e, conversions, list_types)

        return result

    def call_method(self, method, *args, **kw):

        meta = SKANETRAFIKEN_METHODS[method]

        if args:
            names = meta['required'] + meta['optional']
            for i in range(len(args)):
                kw[names[i]] = unicode(args[i]).encode('utf-8')

        # Check we have all required parameters
        if (len(set(meta['required']) - set(kw.keys())) > 0):
            raise SkanetrafikenException('Missing parameters')

        encoded_args = urllib.urlencode(kw)
        url = meta['url_template'].format(method)
        response = urllib.urlopen(url=url, data=encoded_args)

        element, conversions = meta['returns']
        doc = etree.parse(response)

        results = self.build_return(doc,
                                    element,
                                    conversions,
                                    meta['listtypes'])

        return results


if __name__ == '__main__':
    sk = Skanetrafiken()
    print sk.querystation(u"Tygelsjö")


