#!/usr/bin/env python
# encoding: utf-8
"""
skanetrafiken.py

Created by Peter Stark.
Copyright (c) 2011 . All rights reserved.
"""
import logging
import string
import urllib
import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom


#URLs from http://www.labs.skanetrafiken.se/api.asp
XMLNS = u"http://www.etis.fskab.se/v1.0/ETISws"

API_VERSION = "v2.2"
API_SERVER = "http://www.labs.skanetrafiken.se"

API_URL_TEMPLATE = string.Template('${server}/' + API_VERSION + '/${method}.asp')

string = lambda s : s.encode('utf-8')
integer = lambda n : int(n)
date = lambda d : datetime.datetime.strptime(d,'%Y-%m-%dT%H:%M:%S')

POINT = 'Point', {
	'Id' : string,
	'Name': string,
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

LINE = 'Line', {
	'Name' : string,
	'No' : string,
	'JourneyDateTime' : date,
	'DepTimeDeviation' : integer, 
	'Towards' : string
}

SKANETRAFIKEN_METHODS = {
	'querystation' : {
		'required' : ['inpPointFr'],
		'optional' : ['inpPointTo'],
		'returns' : POINT,
		'url_template' : API_URL_TEMPLATE 
	},
	'neareststation' : {	
		'required' : ['x', 'y'],
		'optional' : ['R'],
		'returns' : NEARESTSTOPAREA,
		'url_template' : API_URL_TEMPLATE 
	},
	'stationresults' : {	
		'required' : ['selPointFrKey'],
		'optional' : [],
		'returns' : LINE,
		'url_template' : API_URL_TEMPLATE 
	}
}

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
		for node in dom_element.getElementsByTagName(target_element_name):
			data = dict()			
			for key,conversion in conversions.items():
				data_element = node.getElementsByTagName(key)
				if (len(data_element) > 0):
					data[key] = conversion(data_element[0].firstChild.data)
			results.append(data)
					
		return results 	
				
	
	def call_method(self, method, *args, **kw):
		
		meta = SKANETRAFIKEN_METHODS[method]
		
		if args:
			names = meta['required'] + meta['optional']				
			for i in range(len(args)):
				kw[names[i]] = unicode(args[i]).encode('utf-8')		
		encoded_args = urllib.urlencode(kw)	
		url = meta['url_template'].substitute(method=method,server=self.api_server ) + "?" + encoded_args
		response = urllib.urlopen(url)
		
	  	element, conversions = meta['returns']
		response_dom = minidom.parse( response )
		results = self.build_return(response_dom, element, conversions )
		
		return results
		


def main():
	sk = Skanetrafiken()
	print sk.querystation(u"Tygelsjö")
	print sk.stationresults("80421")
	print sk.neareststation("6158063", "1322703")
	

if __name__ == '__main__':
	main()		
		












