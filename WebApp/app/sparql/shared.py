"""
 shared.py

 Functions that all of our query modules need

"""

####################################################################################################
# GLOBAL VARIABLES
####################################################################################################
CPREFIX =\
"prefix :<https://github.com/campy-db/Campy-Database/blob/master/Ontologies/CampyOntology.owl#>"
LITPREFIX = "prefix lit:<http://www.essepuntato.it/2010/06/literalreification/>"

####################################################################################################
# Write a triple to the database running on blazegraph. Blazegraph server must be running for this
# to work.
#
# t - The triple to be inserted.
####################################################################################################
def writeToBG(t):
    print "insert data{{{}}}".format(t)

####################################################################################################
# Returns a list of lists, where the lists are all the bindings for the vars in the query. EG if we
# do "select ?a ?b ?c ?d ..." then we'll have a list that looks like:
# [[a1, b1, c1, d1], [a2, b2, c2, d2], ..., [ak, bk, ck, dk]], where a# is the binding for ?a, same
# deal for the other letters.
#
# Returns a list if there is only one var in the query, IE if each list in the list has length 1. EG
# if after the for loop, l = [[a], [a1], ..., [ak]], then we return [a, a1, ..., ak].
#
# Returns a list of values if after the for loop, the outer list contains one list. EG if
# l = [[a, b, c]], then return [a, b, c].
#
# Returns a single string if the result is one single value in a single inner list. EG if after the
# for loop, l = [["someval"]], we return "someval"
#
# Returns an empty string if there are no results.
####################################################################################################
def trimResult(r):

    result = []
    vars_ = r["head"]["vars"]
    for b in r["results"]["bindings"]:
        triple = []
        for v in vars_:
            triple.append(b[v]["value"])
        result.append(triple)

    if len(vars_) == 1:
        result = ["".join(v) for v in result]

    if len(result) == 1:
        result = result[0]

    if not result:
        return ""

    return result
