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
	
	query = u"Malmö Mobilia Öster"
	
	station = skanetrafiken.query_station (query)
	if station:
		pprint (station)
		dep_arr = skanetrafiken.get_departure_arrivals (station)
		pprint (dep_arr)
	

if __name__ == '__main__':
	main()

