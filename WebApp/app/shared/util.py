#from .extractValue import getSpecies
#from .shared_validators import validSpecies

def popVals(my_dict):
    return {x:y for x, y in my_dict.iteritems() if y != ""}

#def isValidSpecies(name):
#    spec, subspec, un_spec= getSpecies(name)
#    valid, message = validSpecies(spec, subspec, un_spec)
#    return valid

    