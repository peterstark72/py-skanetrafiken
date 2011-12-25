#!/usr/bin/env python
# encoding: utf-8
"""
query.py

Created by Familjen Stark-Wihlney on 2011-08-21.
Copyright (c) 2011 . All rights reserved.
"""

from skanetrafiken import JourneyPlanner
import json
import datetime
import sys

from pprint import pprint

def main():
	
	planner = JourneyPlanner()
	
	journey = planner.get_journey('80421','80000')
	
	pprint (journey)
		

if __name__ == '__main__':
	main()