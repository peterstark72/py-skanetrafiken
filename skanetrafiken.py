#!/usr/bin/env python
# encoding: utf-8
"""
skanetrafiken.py

Created by Peter Stark.
Copyright (c) 2011 . All rights reserved.
"""
import logging
import urllib
import urllib2
import datetime
import xml.etree.ElementTree as ET

from google.appengine.api import urlfetch


#URLs from http://www.labs.skanetrafiken.se/api.asp
URL_SKANETRAFIKEN = u"http://www.labs.skanetrafiken.se/v2.2/"
GET_DEPARTURE_ARRIVALS_URL = URL_SKANETRAFIKEN + u"stationresults.asp?"
JOURNEYS_URL = URL_SKANETRAFIKEN + u"resultspage.asp?"
XMLNS = u"http://www.etis.fskab.se/v1.0/ETISws"


StopAreas = {
u"Falsterbo Strandbad" : (33029, (55.394098,12.851268)),
u"Gessie By" : (33001, (55.502196,12.995125)), 
u"Hököpinge Snickarevägen" : (33002,(55.493622,13.001292)),
u"Hököpinge Sockervägen" : (33003, (55.488366,13.008819)),
u"Malmö C" : (80000, (55.609458,13.000905)),
u"Malmö Drakagatan" : (80048, (55.551896,12.982937)),
u"Malmö Hyllie" : (80040, (55.562771,12.975839)),	
u"Malmö Konserthuset" : (80118, (55.599585,13.008459)),
u"Malmö Mobilia Öster" : (80544, (55.579874,13.005483)),
u"Malmö Spångatan" : (80134, (55.595568,13.008840)),
u"Malmö Studentgatan" : (80116, (55.603252,13.004579)),
u"Stamhem" : (80427, (55.508528,12.993423)),
u"Tygelsjö Fogsvansgatan" : (80424, (55.514941,12.997589)),
u"Tygelsjö Gullkragegatan" : (80440, (55.517846,12.998079)),
u"Tygelsjö Laavägen" : (80421, (55.519919,12.997947)),
u"V Klagstorps Kyrka" : (80450, (55.528000,12.995739))	
}



class Planner(object):
	'''Looks up times and stops from skanetrafiken.se '''
	def __init__(self):
		pass
		
	def _open_request(self, method, arguments):
		
		encoded_args = urllib.urlencode(arguments)		
		query_url = URL_SKANETRAFIKEN + method + u"?" + encoded_args	
		logging.info("Sends request to %s", query_url)
		
		try:
			fp = urlfetch.fetch(url=query_url, method = urlfetch.GET)
			#fp = urllib.urlopen(query_url)		
		except Exception as e:			
			logging.error("Error when requesting from SK: %s", str(e))
			return 0
			
		return fp.content
		
		
	def _parse_point(self, e):
		'Parses <Point> element'
		point = dict()
		point['id'] = e.findtext('{%s}Id' % XMLNS)
		point['name'] = e.findtext('{%s}Name' % XMLNS)
		point['type'] = e.findtext('{%s}Type' % XMLNS)		
		return point
		
	
		
	def get_start_end_points(self, fr_arg, to_arg):
		'Returns dictinary with start and end points'

		method = u"querypage.asp"
		arguments = {
			u'inpPointFr': fr_arg.encode('utf-8'),
			u'inpPointTo' : to_arg.encode('utf-8')
		}
				
		fp = self._open_request(method, arguments)
		if (fp == 0):
			return None
		
		result = {
			'start_points' : [], 
			'end_points' : []
			}
					
		try: 
			tree = ET.parse(fp)	
		except Exception as e:
			logging.error("Error when parsing: %s", str(e))	

				
		points_e = tree.find('.//{%s}StartPoints' % XMLNS)		
		for p in points_e.findall('{%s}Point' % XMLNS):
				result['start_points'].append(self._parse_point(p))
		
		points_e = tree.find('.//{%s}EndPoints' % XMLNS)		
		for p in points_e.findall('{%s}Point' % XMLNS):
				result['end_points'].append(self._parse_point(p))
		
		return result
	
			
	def get_journey(self, fr_arg, to_arg, cmd='next'):
		'resvalssökning'
		method = u"resultspage.asp"
		arguments = {
			'cmdaction' : cmd,
			'selPointFr': fr_arg.encode('utf-8'),
			'selPointTo' : to_arg.encode('utf-8')
		}
				
		fp = self._open_request(method, arguments)
		if (fp == 0):
			return None

		try: 
			tree = ET.fromstring(fp)	
		except Exception as e:
			logging.error("Error when parsing: %s", str(e))	
				
		journeys = []
		journeys_e = tree.find('.//{%s}Journeys' % XMLNS)
		for j in journeys_e.findall('{%s}Journey' % XMLNS):
			journey = dict()
			t = j.findtext('{%s}DepDateTime' % XMLNS)
			journey['dep_date_time'] = datetime.datetime.strptime(t,'%Y-%m-%dT%H:%M:%S')			
			t = j.findtext('{%s}ArrDateTime' % XMLNS)
			journey['arr_date_time'] = datetime.datetime.strptime(t,'%Y-%m-%dT%H:%M:%S')
			journey['no_of_changes'] = j.findtext('{%s}NoOfChanges' % XMLNS)
			
			journey['distance'] = j.findtext('{%s}Distance' % XMLNS)
			
			journey['links'] = []
			route_links = j.find('{%s}RouteLinks' % XMLNS)
			for r in route_links.findall('{%s}RouteLink' % XMLNS): 
				link = dict()

				link['dep_date_time'] = r.findtext('{%s}DepDateTime' % XMLNS)
				link['arr_date_time'] = r.findtext('{%s}ArrDateTime' % XMLNS)				

				link['from'] = dict()				
				link['from']['id'] = r.findtext('{%s}From/{%s}Id' % (XMLNS, XMLNS))				
				link['from']['name'] = r.findtext('{%s}From/{%s}Name' % (XMLNS, XMLNS))				
				
				link['to'] = dict()
				link['to']['id'] =  r.findtext('{%s}To/{%s}Id' % (XMLNS, XMLNS))				
				link['to']['name'] =  r.findtext('{%s}To/{%s}Name' % (XMLNS, XMLNS))				

				link['line'] = dict()
				link['line']['name'] = r.findtext('{%s}Line/{%s}Name' % (XMLNS, XMLNS))				
				link['line']['no'] = r.findtext('{%s}Line/{%s}No' % (XMLNS, XMLNS))				
				link['line']['towards'] = r.findtext('{%s}Line/{%s}Towards' % (XMLNS, XMLNS))				
				
				journey['links'].append(link)			 
								
			journeys.append(journey)	
			
		
		return journeys	


	def get_departures(self, fr_arg):
		'''
		Stationresults
		Gets departures from stop		
		'''	
		method = u"stationresults.asp"
		arguments = {
			'selPointFrKey': fr_arg
		}	
	
				
		fp = self._open_request(method, arguments)
		if (fp == 0):
			return None
	
		try: 			
			tree = ET.fromstring(fp)			
		except Exception as e:
			logging.error("Error when parsing: %s", str(e))	
			return None

		departures = list()
		for node in tree.iter('{%s}Line' % XMLNS):
			line = dict()
		
			journey_date_time = node.findtext('{%s}JourneyDateTime' % XMLNS)
			
			t = datetime.datetime.strptime(journey_date_time,'%Y-%m-%dT%H:%M:%S')			
			line['day'] = t.day				
			line['hour'] = str(t.hour)
			line['minute'] = str(t.minute)
						
			line['name'] = node.findtext('{%s}Name' % XMLNS)		
			line['towards'] = line['name'] + " " + node.findtext('{%s}Towards' % XMLNS) 
		
			line['dep_time_deviation']	= node.findtext('./{%s}RealTime/{%s}RealTimeInfo/{%s}DepTimeDeviation' % (XMLNS,XMLNS,XMLNS))						
			if (line['dep_time_deviation'] == None):
				line['dep_time_deviation'] = 0
		
			departures.append(line)
	
		return 	departures	
		
			
	def get_nearest(self,x,y):
		"Gets nearest station"
		method = u"neareststation.asp"
		arguments = {
			'X': x,
			'Y': y			
		}			
		fp = self._open_request(method, arguments)
		if (fp == 0):
			return None
	
		try: 			
			tree = ET.fromstring(fp)			
		except Exception as e:
			logging.error("Error when parsing: %s", str(e))	
			return None

		nearest_stops = list()
		for node in tree.iter('{%s}NearestStopArea' % XMLNS):
			s = dict()
			s['name'] = node.findtext('{%s}Name' % XMLNS)
			s['distance'] = node.findtext('{%s}Distance' % XMLNS)
			s['id'] = node.findtext('{%s}Id' % XMLNS)
			nearest_stops.append(s)
			
		return nearest_stops
	
		
	def query_station(self, fr_arg):

		method = u"querystation.asp"
		arguments = {
			'inpPointfr': fr_arg.encode('utf-8')
		}			

		fp = self._open_request(method,arguments)
		if (fp == 0):
			return None			

		try: 			
			tree = ET.fromstring(fp)			
		except Exception as e:
			logging.error("Error when parsing: %s", str(e))	
			return None
		
		stops = list()
		start_points = tree.find(".//{%s}StartPoints" % XMLNS)
		for point in start_points.findall("{%s}Point" % XMLNS):
			stop = dict()
			stop['name'] = point.findtext("{%s}Name" % XMLNS)
			stop['id'] = point.findtext("{%s}Id" % XMLNS)
			stop['x'] = float(point.findtext("{%s}X" % XMLNS))
			stop['y'] = float(point.findtext("{%s}Y" % XMLNS))
			stops.append(stop)
		
		return stops
		
		

def main():
	p = Planner()
	#print p.query_station(u"Malmö")	
	#print p.get_departures(80421)	
	#print p.get_nearest(x=6158063,y=1322703)
	
	
	for d in StopAreas:
		print StopAreas[d][1][0],StopAreas[d][1][1] 
			

if __name__ == '__main__':
	main()		
		












