Skanetrafiken API Python module
av Peter Stark <peterstark72@gmail.com>
(Inspirerad av Steve Marshalls Fire Eagle API.)


Repo på <https://github.com/peterstark72/skanetrafiken>

För API dokumentation, se <http://www.labs.skanetrafiken.se/api.asp>

Exempel:

>>> import skanetrafiken
>>> sk = skanetrafiken.Skanetrafiken()
>>> sk.querystation(u"Malmö C")
>>> sk.resultspage("next", u"Malmö C|80000|0", u"landskrona|82000|0")