"""
 BatchUploader.py
"""
import pandas as pd
from .shared.tripleWriters import *
from .shared.extractValue import getAnimal, getEnviro, getPerson, getType, getTypeProp
from .shared.shared_validators import validSource, checkGenAnimal, checkGenType
from Scripts.endpoint import update

################################################################################################
# A list for storing warning and error messages. Of the form
# [('warning','you should change this..'), ('error','you must change this..')]
################################################################################################
class EWlist(object):

    WARNING = "warning"
    ERROR = "error"

    def __init__(self):
        self.ew_list = []
        self.contains_errors = False

    def addError(self, msg):

        if not isinstance(msg, str):
            raise Exception("The message must be a string")

        err = EWlist.ERROR
        self.ew_list.append((err, msg))

    def addWarning(self, msg):

        if not isinstance(msg, str):
            raise Exception("The message must be a string")

        warn = EWlist.WARNING
        self.ew_list.append((warn, msg))
        self.contains_warnings = True

    # This tells us whether there are any errors or warnings in our list
    def isEmpty(self):
        return self.ew_list == []

####################################################################################################
# Takes in data from a csv, checks if the column names are good, uses shared_validators.py to make
# sure the values are correct, then uses clean_triple_writers to make triples from the data.
####################################################################################################
class BatchUploader(object):

    def __init__(self, fname):

        dir_ = r"/home/student/Campy/CampyDatabase/WebApp/app/uploads/{}".format(fname)
        self.filename = fname
        self.data_frame = pd.read_csv(dir_)
        self.max_rows = len(self.data_frame.index)
        self.last_animal = None
        self.last_type = None

        self.ew_list = EWlist()

    ################################################################################################
    # Return False if the data frame does not contain have key as a column name, True otherwise
    ################################################################################################
    def tryKey(self, key):

        try:
            self.data_frame[key][0]
            return True
        except KeyError:
            return False

    def getEW(self):
        return self.ew_list.ew_list

    @staticmethod
    def getMessage(col_name, row_num, msg):
        row_num += 2 # The indexes are off by 2
        return "In the '{}' column, row {}, {}".format(col_name, row_num, msg)

    ################################################################################################
    # Create all the triples from the csv data. Calls the functions in clean_triple_writers to
    # do the actual triple making. So really here we just make sure the data is correctly formatted
    # and choose which triples to make
    ################################################################################################
    def createTriples(self, last_values):

        def createEPItriple(row, row_num):

            epi_triple = ""
            valid = True

            # Check if there is a key named Source
            source_key = "Source"
            if not self.tryKey(source_key):

                self.ew_list.addError("Your spreadsheet requires a column named Source")
                valid = False
                # Don't keep going if there is no Source column

            else: # Source key is good

                source = row["Source"]

                # Check if the source is valid
                valid_s, msg_s = validSource(source)
                if not valid_s:

                    msg = BatchUploader.getMessage("Source", row_num, msg_s)
                    self.ew_list.addError(msg)
                    valid = False
                    #Don't keep going if the source it invalid

                else:

                    # Use the extractValues module to grab the animal, enviro, or human
                    animal = getAnimal(source)
                    enviro = getEnviro(source)
                    human = getPerson(source)

                    if animal:

                        type_ = getType(source)

                        # Check if there are other warnings and/or errors. Need this for checking
                        # general values, ie checkGenAnimal and checkGenType
                        other_ew = not self.ew_list.isEmpty()

                        valid_a, msg_a =\
                        checkGenAnimal(animal, last_values["animal"], other_ew)

                        valid_t, msg_t =\
                        checkGenType(type_, last_values["type"], other_ew)

                        if not valid_a:
                            msg = BatchUploader.getMessage("Source", row_num, msg_a)
                            self.ew_list.addWarning(msg)
                            last_values["animal"] = animal

                        if not valid_t:
                            msg = BatchUploader.getMessage("Source", row_num, msg_t)
                            self.ew_list.addWarning(msg)
                            last_values["type"] = type_

                        type_prop = getTypeProp(source)
                        data = {"animal":animal,
                                "type":type_,
                                "type_prop":type_prop,
                                "aID":"",
                                "locale":"",
                                "sex":"",
                                "age":""}

                        if valid_a and valid_t and iso_title:
                            epi_triple = createAnimalTriple(data, iso_title)
                        else:
                            valid = False

                    # if enviro
                    # if human

            return epi_triple, valid

        triple = []
        valid = True

        if last_values is None:
            last_values = {}
            last_values["animal"] = None
            last_values["type"] = None

        name_key = "Strain Name"

        if not self.tryKey(name_key):
            self.ew_list.addError("Your spreadsheet requires a column named Strain Name")
            iso_title = None
            valid = False
        else:
            iso_title = str(self.data_frame[name_key][0])
            triple.append(createIsolateTriple(iso_title, ""))

        # We do keep going even if there is no Strain Name column because we want to return any
        # other errors in the sheet to the user

        for r in range(self.max_rows):

            row = self.data_frame.loc[r]

            epi_triple, valid = createEPItriple(row, r)

            triple.append(epi_triple)

        if valid:
            #print update("insert data{{{}}}".format(triple))
            print "".join(triple)

        return valid, last_values
