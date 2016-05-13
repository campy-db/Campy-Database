import datetime

from Scripts.tripleWriters.labTM import LAB as ltm
from Scripts.tripleWriters.campyTM import CAMPY as ctm
from Scripts.TripleMaker import TripleMaker as tm
NOW = datetime.datetime.now()

def createDAddedTriple(isoTitle):
    triple = ctm.propTriple(isoTitle, {"hasDayAdded":str(NOW.day),
                                       "hasMonthAdded":str(NOW.month),
                                       "hasYearAdded":str(NOW.year)})
    return triple


