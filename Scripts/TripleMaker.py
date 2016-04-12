"""
 Triple Maker
"""

from . import cleanCSV as cn

class TripleMaker(object):

    ################################################################################################
    # Constructor
    #
    # uri - The uri that the user has defined for their database. Must have # or / at the end.
    #       And < > are not to be included
    #
    # rLiteral - A boolean. True if the ontology using this is using reified literals.
    #
    # NOTE - For reified literals, the URI will be
    #        http://www.essepuntato.it/2010/06/literalreification/
    ################################################################################################
    def __init__(self, uri):

        if isinstance(uri, str) and uri[len(uri) - 1] in ("#", "/") and uri[0] != "<":
            self.uri = uri
            self.rlit_uri = "http://www.essepuntato.it/2010/06/literalreification/"
        else:
            raise Exception("Uri must be a string. <> are not to be in uri. uri must end in # or /")


    ################################################################################################
    # STATIC & CLASS METHODS
    ################################################################################################

    ################################################################################################
    # staticAddURI
    ################################################################################################
    @staticmethod
    def staticAddURI(title, uri):
        return "<{}{}>".format(uri, cn.cleanString(title))

    ################################################################################################
    # multiURI
    ################################################################################################
    @staticmethod
    def multiURI(triple, uris, isLiteral=None):

        l = 2 if isLiteral else 3

        result = " ".join([TripleMaker.staticAddURI(triple[x], uris[x]) for x in range(l)])

        result += " {}".format(triple[2]) if isLiteral else ""

        return "{} .\n".format(result)

    @classmethod
    def errMsg_str(cls, s=None):

        msg = "{} must be a string".format(s) if s else "Arguments must be strings"
        return Exception(msg)

    @classmethod
    def errMsg_dict(cls):
        return Exception("Argument must be dictionary")

    @classmethod
    def errMsg_empty(cls, s=None):

        msg = "{} should not be empty".format(s) if s else "Value should not be empty"
        return Exception(msg)

    @classmethod
    def errMsg(cls):
        return Exception("Invalid type for argument")

    @classmethod
    def addDataRange(cls, range_):
        return "rdfs:range xsd:{}".format(range_)

    ################################################################################################
    # rlTag
    ################################################################################################
    @classmethod
    def rlTag(cls, v):

        v = str(v).lower() if isinstance(v, bool) else v
        return "tag_{}".format(v)

    ################################################################################################
    # OBJECT METHODS
    ################################################################################################

    # Appends title to the user's uri
    def addURI(self, title):
        return "<{}>".format(self.uri+cn.cleanString(title))

    # Appends title to the reifiedLiteral URI
    def addrlitURI(self, title):
        return "<{}>".format(self.rlit_uri+cn.cleanString(title))

    # Returns a domain declaration.
    # Note that only classes can be the domain of a property
    def addDomain(self, domain):
        return "rdfs:domain {}".format(self.addURI(domain))

    # Returns an object range declaration for an objectProperty
    def addObjRange(self, range_):
        return "rdfs:range {}".format(self.addURI(range_))


    ################################################################################################
    # objProp
    # Returns a triple that creates a new object property. All args must be strings
    #
    # title  - The name of the new property
    # domain - The domain of the property.
    # range  - You guessed it, the range of the property.
    ################################################################################################
    def objProp(self, title, domain, range_):

        if isinstance(title, str) and isinstance(domain, str) and isinstance(range_, str):

            title = self.addURI(title)

            r = self.addObjRange(range_)

            d = self.addDomain(domain)

            return "{} rdf:type owl:ObjectProperty ; {} ; {} .\n".format(title, r, d)

        else:
            raise self.errMsg()


    ################################################################################################
    # dataProp
    # Returns a triple that creates a new data property. All args must be strings
    #
    # title  - The name of the new property
    # domain - The domain of the property.
    # range  - The range of the property.
    ################################################################################################
    def dataProp(self, title, domain, range_):

        if isinstance(title, str) and isinstance(domain, str) and isinstance(range_, str):

            title = self.addURI(title)

            r = self.addDataRange(range_)

            d = self.addDomain(domain)

            return "{} rdf:type owl:DatatypeProperty ; {} ; {} .\n".format(title, r, d)

        else:
            raise self.errMsg_str()


    ################################################################################################
    # superClass
    # Returns a triple that creates a new class that is not a sublcass of any class.
    #
    # sup - The name of the new class. Must be string
    ################################################################################################
    def superClass(self, sup):

        if isinstance(sup, str):
            return self.addURI(sup)+" rdf:type owl:Class ."
        else:
            raise self.errMsg_str()

    ################################################################################################
    # subClass
    # Returns a triple that creates a new subclass. All args must be strings
    #
    # sub - The name of the new class
    # sup - The name of the super class of sub
    ################################################################################################
    def subClass(self, sub, sup):

        if isinstance(sup, str) and isinstance(sub, str):

            sub = sub[0].upper()+sub[1:]
            sup = sup[0].upper()+sup[1:]

            return self.addURI(sub)+" rdf:type owl:Class ; rdfs:subClassOf "+\
                   self.addURI(sup)+" ."
        else:
            raise self.errMsg_str()


    ################################################################################################
    # indTriple
    # Returns a triple creating an individual that belongs to some class, or no class.
    #
    # title  - The name of the individual. Must be string
    # class_ - The class that the individual belongs to. Must be string. Can be absent.
    ################################################################################################
    def indTriple(self, title, class_=None):

        if title == "":
            raise self.errMsg_empty("title")

        if isinstance(title, str):
            r = self.addURI(title)+" rdf:type owl:NamedIndividual "
        else:
            raise self.errMsg_str("title")

        if class_:
            if isinstance(class_, str):

                class_ = class_[0].upper() + class_[1:]

                r += ", "+self.addURI(class_)+" "
            else:
                raise self.errMsg_str("class_")

        return r+".\n"


    ################################################################################################
    # propTriple
    # Create a triple for defining the properties of an individual
    #
    # title - A string. The title of the individual.
    #
    # props - A dictionary with the property name as the key and the property value as the value.The
    #         property value can be a list or just a single value. Even if the property value is a
    #		  literal number value, still pass it in as a string.
    #
    # isLiteral - True if the ALL the property values are literals. False or None otherwise.
    #
    # rLiteral - True if the ALL property values are to be reified literals. False or None otherwise
    #
    ################################################################################################
    def propTriple(self, title, props, isLiteral=None, rLiteral=None):

        if not isinstance(title, str):
            raise self.errMsg_str("title")

        if not isinstance(props, dict):
            raise self.errMsg_dict()

        def edit(v):

            if v == "" or v is None:
                raise self.errMsg_empty("Property value")

            litType = type(v)

            v = str(v).lower() if litType == bool else v # booleans in rdf are lower case

            v = self.rlTag(v) if rLiteral else v

            v = "\"{}\"".format(cn.cleanName(v))\
                 if litType == str and not rLiteral else v

            v = str(v) # Integers and so forth need to be strings

            v = self.addURI(v) if not isLiteral or rLiteral else v

            return v

        def makeProp(p):

            props[p] = [props[p]] if not isinstance(props[p], list) else props[p]

            vals = ", ".join([edit(v) for v in props[p]])

            uri_p = self.addURI(p) if p != "hasLiteralValue" else self.addrlitURI(p)

            return "{} {}".format(uri_p, vals)

        result = self.createRliterals(props) if rLiteral else ""

        props = "; ".join([makeProp(p) for p in props])

        result += "{} {} .\n".format(self.addURI(title), props)

        return result

    ################################################################################################
    # createRliteral
    # Called in propTriple. Used to create triples that define reified literals.
    #
    # props - A dictionary of properties as defined in propTriple definition.
    ################################################################################################
    def createRliterals(self, props):

        def makeProp(p):

            props[p] = [props[p]] if not isinstance(props[p], list) else props[p]

            return "".join([self.propTriple(self.rlTag(v), {"hasLiteralValue":v}, True)\
                            for v in props[p]])

        return "".join([makeProp(p) for p in props])


###################################################################################################
# MAIN
# Just for testing.
###################################################################################################
def main():
    t = TripleMaker("www.example.com/sam#")
    print t.addDataRange("ran")

if __name__ == "__main__":
    main()
