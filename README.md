Skanetrafiken API Python Module
===============================

A Python module to access Skånetrafiken Open API. 

Documentation is here <http://www.labs.skanetrafiken.se/api.asp>

# Installation

```pip install skanetrafiken```


# Examples

```python
import skanetrafiken as sk
sk.querystation("Malmö C")
sk.resultspage("next", u"Malmö C|80000|0", "landskrona|82000|0")
```