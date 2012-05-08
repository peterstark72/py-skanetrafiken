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


import logging
import string
import urllib
import datetime
import pprint

from xml.dom import minidom


#URLs from http://www.labs.skanetrafiken.se/api.asp
XMLNS = u"http://www.etis.fskab.se/v1.0/ETISws"

API_VERSION = "v2.2"
API_SERVER = "http://www.labs.skanetrafiken.se"

API_URL_TEMPLATE = string.Template('${server}/' + API_VERSION + '/${method}.asp')

ERROR_EXCEPTION = string.Template('Error: ${status}.')

string = lambda s : s.encode('utf-8')
integer = lambda n : int(n)
date = lambda d : datetime.datetime.strptime(d,'%Y-%m-%dT%H:%M:%S')
boolean = lambda b : True if b=='true' else False 

POINT = 'Point', {
	'Id' : string,
	'Name': string,
	'Type' : string,
	'X' : integer,
	'Y' : integer
} 

NEARESTSTOPAREA = 'NearestStopArea', {
	'Id' : string,
	'Name' : string, 
	'X' : integer, 
	'Y' : integer, 
	'Distance' : integer 
}

REALTIMEINFO = 'RealTimeInfo' , {
	'DepTimeDeviation' : integer,
	'DepDeviationAffect' : string
}

LINE = 'Line', {
	'Name' : string,
	'No' : string,
	'JourneyDateTime' : date,
	'LineTypeName' : string,
	'Towards' : string,
	'RealTime' : REALTIMEINFO
}

TRANSPORTMODE = 'TransportMode', {
	'Id' : integer,
	'Name' : string,
	'DefaultChecked' : boolean
}

LINETYPE = 'LineType', {
	'Id' : integer,
	'Name' : string,
	'DefaultChecked' : boolean
}

JOURNEY = 'Journey' , {
	'SequenceNo' : integer,
	'DepDateTime' : date,
	'ArrDateTime' : date,
	'DepWalkDist' : integer,
	'ArrWalkDist' : integer,
	'NoOfChanges' : integer,
	'Guaranteed' : boolean,
	'CO2factor' : integer,
	'NoOfZones' : integer,
	'JourneyKey' : string,
	'FareType' : string,
	'Distance' : integer,
	'CO2value' : string
}

GETJOURNEYPATHRESULT = 'GetJourneyPathResult' , {
	'Code' : integer,
	'Message' : string,
	'ResultXML' : string
}

GETJOURNEYRESULT = 'GetJourneyResult', {
	'Code' : integer,
	'Message' : string,
	'JourneyResultKey' : string,
	'Journeys' : JOURNEY
}

GETSTARTENDPOINTRESULT = 'GetStartEndPointResult' , {
	'Code' : integer,
	'Message' : string,
	'StartPoints' : POINT,
	'EndPoints': POINT
} 

GETNEARESTSTOPAREARESULT = 'GetNearestStopAreaResult' , {
	'Code' : integer,
	'Message' : string,
	'NearestStopAreas' : NEARESTSTOPAREA
}

GETDEPARTUREARRIVALRESULT = 'GetDepartureArrivalResult' , {
	'Code' : integer,
	'Message' : string,
	'Lines' : LINE
}

GETMEANSOFTRANSPORTRESULT = 'GetMeansOfTransportResult' , {
	'Code' : integer,
	'Message' : string,
	'TransportModes' : TRANSPORTMODE,
	'LineTypes' : LINETYPE
}


SKANETRAFIKEN_METHODS = {
	'querystation' : {
		'required' : ['inpPointFr'],
		'optional' : ['inpPointTo'],
		'returns' : GETSTARTENDPOINTRESULT,
		'url_template' : API_URL_TEMPLATE 
	},
	'neareststation' : {	
		'required' : ['x', 'y'],
		'optional' : ['R'],
		'returns' : GETNEARESTSTOPAREARESULT,
		'url_template' : API_URL_TEMPLATE 
	},
	'stationresults' : {	
		'required' : ['selPointFrKey'],
		'optional' : [],
		'returns' : LINE,
		'url_template' : API_URL_TEMPLATE 
	},
	'trafficmeans' : {	
		'required' : [],
		'optional' : [],
		'returns' : GETMEANSOFTRANSPORTRESULT,
		'url_template' : API_URL_TEMPLATE 
	},
	'resultspage'  : {	
		'required' : ['cmdaction','selPointFr', 'selPointTo'],
		'optional' : ['inpTime','inpDate','LastStart', 'FirstStart','NoOf','transportMode'],
		'returns' : GETJOURNEYRESULT,
		'url_template' : API_URL_TEMPLATE 
	},	
	'querypage'  : {	
			'required' : ['inpPointFr','inpPointTo'],
			'optional' : [],
			'returns' : GETSTARTENDPOINTRESULT,
			'url_template' : API_URL_TEMPLATE 
		},
	'journeypath'  : {	
			'required' : ['cf','id'],
			'optional' : [],
			'returns' : GETJOURNEYPATHRESULT,
			'url_template' : API_URL_TEMPLATE 
		}	
}


class SkanetrafikenException( Exception ):
    pass


class SkanetrafikenAccumulator:
    def __init__( self, skanetrafiken_obj, name ):
        self.skanetrafiken_obj = skanetrafiken_obj
        self.name          = name
    
    def __repr__( self ):
        return self.name
    
    def __call__( self, *args, **kw ):
        return self.skanetrafiken_obj.call_method( self.name, *args, **kw )



class Skanetrafiken(object):
	'''Looks up times and stops from skanetrafiken.se '''

	def __init__(self):
	
		self.api_server = API_SERVER
		
		for method, _ in SKANETRAFIKEN_METHODS.items():
			if not hasattr( self, method ):
				setattr( self, method, SkanetrafikenAccumulator( self, method ))
		
		
		
	def build_return(self,dom_element, target_element_name, conversions):

		results = list()
		
		node_list = dom_element.getElementsByTagName(target_element_name)
		for node in node_list:
			data = dict()
			for key, conversion in conversions.items():
			
				if isinstance(conversion, tuple):
					child_key, child_conversion = conversion
					data[key] = self.build_return (node, child_key, child_conversion)						
				else:
					data_element = node.getElementsByTagName(key)
					if (len(data_element) > 0):
						element_child = data_element[0].firstChild
						if (element_child != None):
							if (element_child.nodeType == node.TEXT_NODE):
								data[key] = conversion(element_child.data)
			results.append(data)
		
		return results
	
	
	
	def call_method(self, method, *args, **kw):
		
		meta = SKANETRAFIKEN_METHODS[method]
		
		if args:
			names = meta['required'] + meta['optional']				
			for i in range(len(args)):
				kw[names[i]] = unicode(args[i]).encode('utf-8')		
		
		#check we have all required parameters
		if (len(set(meta['required']) - set(kw.keys())) > 0):
			raise SkanetrafikenException, ERROR_EXCEPTION.substitute(status = 'missing parameters')				
		
		encoded_args = urllib.urlencode(kw)	
		url = meta['url_template'].substitute(method=method,server=self.api_server ) + "?" + encoded_args		
		response = urllib.urlopen(url)
		
	  	element, conversions = meta['returns']
		response_dom = minidom.parse( response )
		results = self.build_return(response_dom, element, conversions )
		
		return results
		


def main():

	sk = Skanetrafiken()
	
	try:
		pprint.pprint( sk.querypage(u"Malmö", u"Ystad"))
		
		resval = sk.resultspage("next", u"Malmö C|80000|1", u"landskrona|82000|0")
		if (resval[0]['Code'] == 0):
			cf = resval[0]['JourneyResultKey']
			pprint.pprint( sk.journeypath(cf,1))
		
		#pprint.pprint( sk.querystation(u"Tygelsjö Laavägen"))
		#pprint.pprint( sk.neareststation(6167930,1323215,1000))
		#pprint.pprint( sk.stationresults(80000))
		#pprint.pprint( sk.trafficmeans())

	except SkanetrafikenException as e:
		print e
	except Exception as e:
		print e
	
	
	#print sk.querystation(u"Malmö")
	
	

if __name__ == '__main__':
	main()		
		












