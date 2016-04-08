"""
 data_queries.py

 Specific sparql queries for retrieving a set of data
"""

import sys
sys.path.append("/home/student/Campy/CampyDatabase")

from Scripts import endpoint as e
from Scripts import TripleMaker as tm
from Scripts.tripleWriters.campyTM import CAMPY as ctm
from Scripts.tripleWriters.labTM import LAB as ltm

def trimResult(r, v):

    l = []
    for b in r["results"]["bindings"]:
        l.append(b[v]["value"])

    return l

def get_epi_data(iso):

    q = """
        select ?e
        where {{
            {iso} a {isolate} .
            {iso} {hasEPIprop} ?e .
        }}
        """.format(iso=ctm.addURI(iso),
                   isolate=ctm.addURI("Isolate"),
                   hasEPIprop=ctm.addURI("hasEPIproperty"))

    result = trimResult(e.query(q), "e")

    q = """
        select ?sn
        where {{
            {iso} {hasSource} ?s.
            ?s {hasName} ?sn
        }}
        """.format(iso=ctm.addURI(iso),
                   hasSource=ctm.addURI("hasSampleSource"),
                   hasName=ctm.addURI("hasName"))

    result = trimResult(e.query(q), "sn")

    print result
