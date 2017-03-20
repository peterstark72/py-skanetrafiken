#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import skanetrafiken as sk
import unittest


class TestSkanetrafikenOpenApi(unittest.TestCase):

    def test_querypage(self):
        r = sk.querypage(inpPointFr="lund", inpPointTo="ystad")
        self.assertIsNotNone(r)

    def test_querystation(self):
        r = sk.querystation("Tygelsjö")
        self.assertIsNotNone(r)

    def test_resultspage(self):
        r = sk.resultspage(selPointFr="Malmö C|80000|0",
                           selPointTo="Landskrona|82000|0")
        self.assertIsNotNone(r)

    def test_neareststation(self):
        r = sk.neareststation(x=6167930, y=1323215, R=1000)
        self.assertIsNotNone(r)

    def test_stationresults(self):
        r = sk.stationresults(selPointFrKey=80000)
        self.assertIsNotNone(r)

    def test_trafficmeans(self):
        r = sk.trafficmeans()
        self.assertIsNotNone(r)


if __name__ == '__main__':
    unittest.main()
