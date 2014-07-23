#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import skanetrafiken
import unittest


class TestSkanetrafikenOpenApi(unittest.TestCase):

    def setUp(self):
        self.sk = skanetrafiken.Skanetrafiken()

    def test_querypage(self):
        r = self.sk.querypage(inpPointFr="lund", inpPointTo="ystad")
        self.assertIsNotNone(r)

    def test_querystation(self):
        r = self.sk.querystation(u"Tygelsjö")
        self.assertIsNotNone(r)

    def test_resultpage(self):
        r = self.sk.resultspage("next", u"Malmö C|80000|0",
                                u"landskrona|82000|0")
        self.assertIsNotNone(r)

    def test_neareststation(self):
        r = self.sk.neareststation(x=6167930, y=1323215, R=1000)
        self.assertIsNotNone(r)

    def test_stationresults(self):
        r = self.sk.stationresults(selPointFrKey=80000)
        self.assertIsNotNone(r)

    def test_trafficmeans(self):
        r = self.sk.trafficmeans()
        self.assertIsNotNone(r)


if __name__ == '__main__':
    unittest.main()
