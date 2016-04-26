"""
 BatchUploader.py
"""
import pandas as pd
from .shared.clean_triple_writers import createAnimalTriple
from .shared.extractValue import getAnimal, getEnviro, getPerson, getType, getTypeProp
from .shared.shared_validators import validSource
from Scripts.endpoint import update

class BatchUploader(object):

    def __init__(self, fname):
        dir_ = r"/home/student/Campy/CampyDatabase/WebApp/app/uploads/{}".format(fname)
        self.filename = fname
        self.data_frame = pd.read_csv(dir_)
        self.max_rows = len(self.data_frame.index)

    def createTriples(self):

        def createEPItriples(row):

            epi_triple = []

            try:
                source = row["Source"]
                valid, message = validSource(source)
                if not valid:
                    print message
                else:
                    animal = getAnimal(source)
                    enviro = getEnviro(source)
                    human = getPerson(source)

                    if animal:
                        type_ = getType(source)
                        type_prop = getTypeProp(source)
                        data = {"animal":animal,
                                "type":type_,
                                "type_prop":type_prop,
                                "aID":"",
                                "locale":"",
                                "sex":"",
                                "age":""}
                        print data
                        epi_triple.append(createAnimalTriple(data, iso_title))

            except KeyError:
                print "error"

            print "".join(epi_triple)

        iso_title = str(self.data_frame["Strain Name"][0])

        for r in range(self.max_rows):

            row = self.data_frame.loc[r]

            triple = createEPItriples(row)

            #print update("insert data{{{}}}".format(triple))
            print triple
