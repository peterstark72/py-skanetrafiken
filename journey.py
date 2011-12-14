#!/usr/bin/env python
# encoding: utf-8
"""
query.py

Created by Familjen Stark-Wihlney on 2011-08-21.
Copyright (c) 2011 . All rights reserved.
"""

import skanetrafiken
import json
import datetime
import sys

from pprint import pprint

def main():
	
	point2 = u"Malmö Spångatan"
	point1 = u"Tygelsjö Laavägen"
	
	station1 = skanetrafiken.query_station (point1)
	pprint(station1)
	
	station2 = skanetrafiken.query_station (point2)
	pprint(station2)
	
	journeys = skanetrafiken.get_journey(station1, station2)	
	pprint (journeys)
		

if __name__ == '__main__':
	main()