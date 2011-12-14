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

stops = [
		(u"Laavägen", u"80421"),
		(u"Malmö C", u"80000"),
		(u"Malmö Södervärn", u"80120"),
		(u"Tygelsjö Gullkragegatan", u"80440"),
		(u"Malmö Spångatan", u"80134"),
		(u"Malmö Studentgatan", u"80116")
		]

current_time = datetime.datetime.now(); #+ datetime.timedelta(hours=1)


def query_station(inpPointfr):	
	
	station = None
		
	for s in stops:
		if inpPointfr in s[0]:
			station = {} 
			station['name'] = s[0]
			station['id'] = s[1]
	
	if station == None:	
	
		query_args = {u'inpPointfr': inpPointfr.encode('utf-8')}
		encoded_args = urllib.urlencode(query_args)		
		url = u"http://www.labs.skanetrafiken.se/v2.2/querystation.asp?" +  encoded_args
	
		fp = urllib2.urlopen(url)	
		tree = ElementTree.parse(fp)	

		for node in list(tree.getiterator('{http://www.etis.fskab.se/v1.0/ETISws}Point')):
			name = node.findtext('{http://www.etis.fskab.se/v1.0/ETISws}Name')
			if inpPointfr in name:
				station = {} 
				station['id'] =  node.findtext('{http://www.etis.fskab.se/v1.0/ETISws}Id')
				station['name'] =  name
				break
		
	return station
		
	
def get_departure_arrivals(point_from, name = "", towards = ""):
	
	url = u"http://www.labs.skanetrafiken.se/v2.2/stationresults.asp?selPointFrKey=" +  point_from['id'] + "&selDirection=0"

	fp = urllib2.urlopen(url)	
	tree = ElementTree.parse(fp)
		
	bus_stop = {}
	bus_stop['name'] = point_from['name'] 
	bus_stop['current_time'] = current_time
	
	bus_stop['lines'] = []
	for node in list(tree.getiterator('{http://www.etis.fskab.se/v1.0/ETISws}Line')):
		bus_stop['lines'].append(parse_line(node))
	
	if (name != ""):
		bus_stop['lines'] =  [line for line in bus_stop['lines'] if line['name'] == name]
		
	if (towards != ""):
		bus_stop['lines'] =  [line for line in bus_stop['lines'] if towards in line['towards']]
	
	return bus_stop
		

def get_journey(point_from, point_to, max_changes=0):


	sel_point_fr = point_from['name'] + "|" + point_from['id'] + "|0"
	sel_point_to = point_to['name'] + "|" + point_to['id'] + "|0"
	query_args = {"cmdaction" : "next", "selPointFr": sel_point_fr.encode('utf-8'), "selPointTo" : sel_point_to.encode('utf-8')}		
	encoded_args = urllib.urlencode(query_args)
	url = "http://www.labs.skanetrafiken.se/v2.2/resultspage.asp?" + encoded_args


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


def parse_line (line_node):

	line = {}
	journey_date_time 			= line_node.findtext('{http://www.etis.fskab.se/v1.0/ETISws}JourneyDateTime')
	line['when'] 				= datetime.datetime.strptime(journey_date_time,'%Y-%m-%dT%H:%M:%S')			
	if line['when'] > current_time:
		line['timeuntil'] = int ((line['when'] - current_time).seconds / 60)	
	else:
		line['timeuntil'] = - int ((current_time - line['when']).seconds / 60)			
	line['name'] 				= line_node.findtext('{http://www.etis.fskab.se/v1.0/ETISws}Name')
	line['towards'] 			= line_node.findtext('{http://www.etis.fskab.se/v1.0/ETISws}Towards')
	line['dep_time_deviation']			= line_node.findtext('./{http://www.etis.fskab.se/v1.0/ETISws}RealTime/{http://www.etis.fskab.se/v1.0/ETISws}RealTimeInfo/{http://www.etis.fskab.se/v1.0/ETISws}DepTimeDeviation')
	line['dep_affect']			= line_node.findtext('./{http://www.etis.fskab.se/v1.0/ETISws}RealTime/{http://www.etis.fskab.se/v1.0/ETISws}RealTimeInfo/{http://www.etis.fskab.se/v1.0/ETISws}DepDeviationAffect')

	return line








