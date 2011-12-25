#!/usr/bin/env python
# encoding: utf-8
"""
skanetrafiken.py

Created by Peter Stark.
Copyright (c) 2011 . All rights reserved.
"""

import urllib
import urllib2
import datetime
from xml.etree import ElementTree

GET_DEPARTURE_ARRIVALS_URL = u"http://www.labs.skanetrafiken.se/v2.2/stationresults.asp?"
JOURNEYS_URL = u"http://www.labs.skanetrafiken.se/v2.2/resultspage.asp?"
XMLNS = "{http://www.etis.fskab.se/v1.0/ETISws}"
NAME_ID_DIC = {
	'80421' : u"Laavägen",
	'80000' : u"Malmö C",
	'80120' : u"Malmö Södervärn",
	'80440' : u"Tygelsjö Gullkragegatan",
	'80134' : u"Malmö Spångatan",
	'80116' : u"Malmö Studentgatan"
	}


class BusStop (object):	
		
	def __init__(self, id_arg):
		self.name = NAME_ID_DIC[id_arg]
		self.id = id_arg
		self.lines = []	
			
	
	def update(self):

		query_args = {
			u'selDirection': u'0',
			u'selPointFrKey' : self.id
			}
		encoded_args = urllib.urlencode(query_args)		
		url = GET_DEPARTURE_ARRIVALS_URL + encoded_args
				
		try:
			fp = urllib2.urlopen(url)			
		except IOError, e:
			return False
			
		tree = ElementTree.parse(fp)
		if (tree == None):
			return False
			
		for node in list(tree.getiterator(XMLNS + 'Line')):
			line = {}
			journey_date_time = node.findtext(XMLNS + 'JourneyDateTime')
			line['when'] = datetime.datetime.strptime(journey_date_time,'%Y-%m-%dT%H:%M:%S')			
			line['name'] = node.findtext(XMLNS + 'Name')
			line['towards'] = node.findtext(XMLNS + 'Towards')			
			line['dep_time_deviation']	= node.findtext('./' + XMLNS +'RealTime/' +  XMLNS + 'RealTimeInfo/' + XMLNS + 'DepTimeDeviation')						
			self.lines.append(line)

		return True
	
	
	def get_next_departure(self):
		if (len(self.lines) > 0):		
			return self.lines[0]
		else:
			return None
			

	def get_next_departure_for_line_towards(self, name, towards):
	
		lines = self.get_departures_for_line_towards(name, towards)
	
		if (len(lines) > 0):		
			return lines[0]
		else:
			return None

		
		
	def get_name(self):
		return self.name


	def get_all_departures(self):
		return self.lines

		
	def get_departures_for_line(self, name):
		if (name == None):
			return None
		else:
			return [line for line in self.lines if line['name'] == name]
		
			
	def get_departures_for_line_towards(self, name, towards):
		if (name == None or towards == None):
			return None
		else:
			return [line for line in self.lines if towards in line['towards'] and line['name'] == name]



class JourneyPlanner (object):
	

	def get_journey(self, fr, to, max_changes=0):


		sel_point_fr = NAME_ID_DIC[fr] + "|" + fr + "|0"
		sel_point_to = NAME_ID_DIC[to] + "|" + to + "|0"		
		query_args = {"cmdaction" : "next", "selPointFr": sel_point_fr.encode('utf-8'), "selPointTo" : sel_point_to.encode('utf-8')}		
		encoded_args = urllib.urlencode(query_args)
		
		url = JOURNEYS_URL + encoded_args

		fp = urllib.urlopen(url)	
		tree = ElementTree.parse(fp)
	
		journeys = []	
		for node in list(tree.getiterator('{http://www.etis.fskab.se/v1.0/ETISws}Journey')):
			
			journey = {}
			journey['no_of_changes'] = int ( node.findtext('{http://www.etis.fskab.se/v1.0/ETISws}NoOfChanges'))
			datetime.datetime.strptime(node.findtext('{http://www.etis.fskab.se/v1.0/ETISws}DepDateTime'),'%Y-%m-%dT%H:%M:%S')			
			journey['dep_date_time'] = datetime.datetime.strptime(node.findtext('{http://www.etis.fskab.se/v1.0/ETISws}DepDateTime'),'%Y-%m-%dT%H:%M:%S')			
			journey['arr_date_time'] = datetime.datetime.strptime(node.findtext('{http://www.etis.fskab.se/v1.0/ETISws}ArrDateTime'),'%Y-%m-%dT%H:%M:%S')			
			journey['duration'] = journey['arr_date_time'] - journey['dep_date_time']

			journey['route_links'] = []
			for route in list(node.getiterator('{http://www.etis.fskab.se/v1.0/ETISws}RouteLink')):
				route_link = {}
				route_link['from'] = route.findtext('./{http://www.etis.fskab.se/v1.0/ETISws}From/{http://www.etis.fskab.se/v1.0/ETISws}Name')
				route_link['to'] = route.findtext('./{http://www.etis.fskab.se/v1.0/ETISws}To/{http://www.etis.fskab.se/v1.0/ETISws}Name')
				route_link['name']  = route.findtext('./{http://www.etis.fskab.se/v1.0/ETISws}Line/{http://www.etis.fskab.se/v1.0/ETISws}Name')
				route_link['towards']  = route.findtext('./{http://www.etis.fskab.se/v1.0/ETISws}Line/{http://www.etis.fskab.se/v1.0/ETISws}Towards')
				journey['route_links'].append(route_link)			
				
			journeys.append(journey)
	
		journeys = [j for j in journeys if j['no_of_changes'] <= max_changes]	
		
		return journeys			










