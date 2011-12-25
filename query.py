#!/usr/bin/env python
# encoding: utf-8
"""
query.py

Created by Familjen Stark-Wihlney on 2011-08-21.
Copyright (c) 2011 . All rights reserved.
"""

from skanetrafiken import BusStop, NAME_ID_DIC
from pprint import pprint

def main():
		
	#Tygelsjö till Malmö
	print u"Nästa buss mot Malmö"
	for s in ['80421', '80440']:
		a_stop = BusStop(s)
		a_stop.update()
		print a_stop.get_name()
		print a_stop.get_next_departure_for_line_towards("150", u"Malmö")

	#Malmä till Tygelsjö
	print u"Nästa buss mot Tygelsjö"
	for s in ['80134','80116','80000'] :
		a_stop = BusStop(s)
		a_stop.update()
		print a_stop.get_name()
		print a_stop.get_next_departure_for_line_towards("150", u"Vellinge")
		

if __name__ == '__main__':
	main()

