#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by Peter o Kristina on 2012-06-05.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import pprint

import skanetrafiken


def main():

	sk = skanetrafiken.Skanetrafiken()
	
	try:
		pprint.pprint( sk.querypage(u"Malmö", u"Ystad"))
	
		resval = sk.resultspage("next", u"Malmö C|80000|1", u"landskrona|82000|0")
		if (resval[0]['Code'] == 0):
			cf = resval[0]['JourneyResultKey']
			pprint.pprint( sk.journeypath(cf,1))
		
		pprint.pprint( sk.querystation(u"Tygelsjö Laavägen"))
		pprint.pprint( sk.neareststation(6167930,1323215,1000))
		pprint.pprint( sk.stationresults(80000))
		pprint.pprint( sk.trafficmeans())

	except SkanetrafikenException as e:
		print e
	except Exception as e:
		print e
	
	
	#print sk.querystation(u"Malmö")
	



if __name__ == '__main__':
	main()

