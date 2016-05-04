#popVal
def popVals(my_dict):
    return {x:y for x, y in my_dict.iteritems() if y != ""}
#isNumber