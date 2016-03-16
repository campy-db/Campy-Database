#######################################################################################################
# Triple Maker
#######################################################################################################
import clean as cn

class TripleMaker:

	###################################################################################################
	# Constructor
	# uri - The uri that the user has defined for their database. Must have # or / at the end. And < > 
	#       are not to be included
	# rLiteral - A boolean. True if the ontology using this is using reified literals.
	# NOTE - For reified literals, the URI will be http://www.essepuntato.it/2010/06/literalreification/
	###################################################################################################
	def __init__(self,uri):
		if type(uri)==str and (uri[len(uri)-1]=="#" or uri[len(uri)-1]=="/") and uri[0]!="<":
			self.uri=uri
			self.rLitUri="http://www.essepuntato.it/2010/06/literalreification/" 
		else:
			raise Exception("Uri must be a string. <> are not to be in uri. uri must end in # or /")
	
	###################################################################################################
    # Utility methods
	###################################################################################################
	def errMsg_str(self,s=None):
		if s:
			result=Exception(s+" must be a string")
		else:
			result=Exception("Arguments must be strings")
		return result

	def errMsg_dict(self):
		return Exception("Argument must be dictionary")

	# Appends title to the user's uri
	def addUri(self,title):
		return "<"+self.uri+cn.cleanString(title)+">"

	# Appends title to the reifiedLiteral URI
	def addrLitUri(self,title):
		return "<"+self.rLitUri+cn.cleanString(title)+">"

	# Returns a domain declaration.
	# Note that only classes can be the domain of a property	
	def addDomain(self,domain):
		return "rdfs:domain "+self.addUri(domain)

	# Returns an object range declaration for an objectProperty	
	def addObjRange(self,range_):
		return "rdfs:range "+self.addUri(range_)	

	# Returns a datatype range declaration for a datatypeProperty	
	def addDataRange(self,range_):
		return "rdfs:range xsd:"+range_


	###################################################################################################
    # Methods
	###################################################################################################

	###################################################################################################
    # createRliteral
    #	Creates reified literals.
	###################################################################################################
	def createRliteral(self,litType,props):
		result=""

		for p in props:
			length=1
			# If the value for the property is a list, we must add the URI to each value
			isList=type(props[p])==list
			if isList: 
				length=len(props[p])

			for j in range(length):
				if isList:
					val=props[p][j]
				else:
					val=props[p]

				result+=self.addUri("tag_"+val)+" "

				val=cn.cleanName(val)

				if litType=="string":
					val="\"%s\"" %(val)

				result+=self.addrLitUri("hasLiteralValue")+" "+val+" .\n"

		return result

	###################################################################################################
	# objProp 
	#	Returns a triple that creates a new object property. All args must be strings
	#	title  - The name of the new property
	#	domain - The domain of the property.
	#	range  - You guessed it, the range of the property.
	###################################################################################################	
	def objProp(self,title,domain,range_):
		if type(title)==str and type(domain)==str and type(range_)==str:
			return self.addUri(title)+" rdf:type owl:ObjectProperty ;"+self.addObjRange(range_)+" ;"\
			+self.addDomain(domain)+" ."
		else:
			raise self.errMsg()

	###################################################################################################
	# dataProp
	# 	Returns a triple that creates a new data property. All args must be strings
	#	title  - The name of the new property
	#	domain - The domain of the property. 
	#	range  - The range of the property. 
	###################################################################################################
	def dataProp(self,title,domain,range_):
		if type(title)==str and type(domain)==str and type(range_)==str:
			return self.addUri(title)+" rdf:type owl:DatatypeProperty ;"+self.addDataRange(range_)+" ;"\
			+self.addDomain(domain)+" ."
		else:
			raise self.errMsg_str()

	###################################################################################################
	# superClass
	# 	Returns a triple that creates a new class that is not a sublcass of any class.
	#	sup - The name of the new class. Must be string
	###################################################################################################
	def superClass(self,sup):
		if type(sup)==str:
			return self.addUri(sup)+" rdf:type owl:Class ."
		else:
			raise self.errMsg_str()

	###################################################################################################
	# subClass
	# 	Returns a triple that creates a new subclass. All args must be strings
	#	sub - The name of the new class
	#	sup - The name of the super class of sub
	###################################################################################################
	def subClass(self,sub,sup):
		if type(sup)==str and type(sub)==str:
			sub=sub[0].upper()+sub[1:]
			sup=sup[0].upper()+sup[1:]

			return self.addUri(sub)+" rdf:type owl:Class ; rdfs:subClassOf "+\
				   self.addUri(sup)+" ."
		else:
			raise self.errMsg_str()
		
	###################################################################################################
	# indTriple
	# 	Returns a triple creating an individual that belongs to some class, or no class.
	#	Can create a new triple, or add properties to an existing.
	#	Note this isn't totally necessary as the class that an individual is part of is usually 
	#	inferred by the properties attached to it (because of all the domains and ranges), but this is
	#	not always the case. EG :iso17 :hasAnimal :chicken. It'll be inferred that iso17 is an isoalte,
	#	but it will not be inferred that chicken is a chicken (he he), just that it is an animal.
	#	title  - The name of the individual. Must be string
	#	class_ - The class that the individual belongs to. Must be string. Can be absent though as you
	###################################################################################################
	def indTriple(self,title,class_=None):
		if type(title)==str:
			r=self.addUri(title)+" rdf:type owl:NamedIndividual " 
		else:
			raise self.errMsg_str("title")

		if class_:
			if type(class_)==str:
				class_=class_[0].upper()+class_[1:] # title() can't be used as sometimes the class
													# is camelCase, and title() will put everything
													# to lower case except the first letter
				r+=", "+self.addUri(class_)+" "
			else:
				raise self.errMsg_str("class_")
		return r+".\n"

	###################################################################################################	
	# propTriple
	# 	Create a triple for defining the properties of an individual
	# 
	# 	title - A string. The title of the individual, like its uri I mean, just without the whole www 
	#			part, we add that here.
	# 	props - A dictionary with the property name as the key and the property value as the value. The
	#           property value can be a list or just a single value. Even if the property value is a 
	#			literal number value, still pass it in as a string. If it's not a number and not a 
	#			an rdf boolean (true, false), we have to add quotations to the value.
	# 	litType - The type of literal the prop vals are. Since all literal prop values have to be 
	#			  passed in as strings, we explicity say what type they are. If its 'string', we add
	#			  quotations to the value. Note that we originally had it so we just check if the value 
	#			  is a number or a boolean and add quoatations if they aren't, but some of the numbers
	#			  in the ontology have to be a string, specifically hex numbers. There is not hex type
	#			  in rdf. Also, in the future we may need to append literal types, 
	#             eg "Sam"^^xsd:string.
	#			  
	#   rLiteral - True if the ALL property values are reified literals, false otherwise
	###################################################################################################
	def propTriple(self,title,props,litType=None,rLiteral=None):
		if type(title)==str:
			result=self.addUri(title)+" "
		else:
			raise self.errMsg_str("title")

		if type(props)==dict:
			i=1
			# Add all the properties to the individual's definition
			for p in props: # p=The name of the property

				result+=self.addProp(p,props,litType,rLiteral)
		
				if i!=len(props):
					result+="; " # There's more than one property name
				i+=1
			result+=".\n"

			# If the property values are literals, and we're using reified literals,
			# create literal object and attach literal value to it
			if rLiteral and litType: # The literal type must be defined if your making reified literals
				result+=self.createRliteral(litType,props)

		else: # Props has to be a dictionary
			raise self.errMsg_dict()
		return result


	###################################################################################################
	# addProp
	# 	Just to make propTriple more readable.
	###################################################################################################
	def addProp(self,p,props,litType=None,rLiteral=None):
		result=""
		result+=self.addUri(p)+" " # Add the URI to the property name
				
		length=1
		# If the value for the property is a list, we must add the URI to each value
		isList=type(props[p])==list
		if isList: 
			length=len(props[p])

		for j in range(length):
			if isList:
				val=props[p][j]
			else:
				val=props[p]

			if litType:
				if rLiteral:
					result+=self.addUri("tag_"+val)+" "
				else:
					# Most weird characters that we remove when we add the URI are allowed
					# to be in literal values, but some are not.
					val=cn.cleanName(val)

					# Check if the value is a string literal
					if litType=="string":
						val="\"%s\"" %(val)

					result+=val+" "
			else:
				result+=self.addUri(val)+" "

			if j!=len(props[p])-1 and isList:
				result+=","

		return result


###################################################################################################
# Main. Just for testing.
###################################################################################################
import TripleMaker as t
def main():
	trip=t.TripleMaker("https://github.com/samuel-peers/campyOntology/blob/master/CampyOntology2.0.owl#")
	print trip.propTriple("Sam",{"hasName":["bill","jone"],"iscool":"444466"},"string",True)



if __name__=="__main__":
	main()
	
