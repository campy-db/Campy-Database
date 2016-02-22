#######################################################################################################
# Triple Maker
#######################################################################################################

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
			raise "Uri must be a string. <> are not to be in uri. uri must end in # or /"
	
	###################################################################################################
    # Utility methods
	###################################################################################################
	def errMsg_str():
		return "Must be string"

	def errMsg_dict():
		return "Must be dictionary"

	# Appends title to the user's uri
	def addUri(self,title):
		return "<"+self.uri+title+">"

	# Appends title to the reifiedLiteral URI
	def addrLitUri(self,title):
		return "<"+self.rLitUri+title+">"

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

	def createRliteral(self,props):
		r=""
		for p in props:
			if type(props[p])!=list:
				r+=self.addUri("tag_"+props[p])+" "
				r+=self.addrLitUri("hasLiteralValue")+" "+props[p]+" .\n"
			else:
				for v in props[p]:
					r+=self.addUri("tag_"+v)+" "
					r+=self.addrLitUri("hasLiteralValue")+" "+v+" .\n"
		return r

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
	def subClass(self,sup,sub):
		if type(sup)==str and type(sub)==str:
			return self.addUri(sup)+" rdf:type owl:Class ; rdfs:subClassOf "+self.addUri(sub)+" ."
		else:
			raise self.errMsg_str()

	######################################################################################################
	#
	######################################################################################################
	def hasName(self,title,name):
		return self.propTriple(title,{"hasName":"\""+name+"\""},True)
		
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
			raise self.errMsg_str()

		if class_:
			if type(class_)==str:
				r+=", "+self.addUri(class_)+" "
			else:
				raise self.errMsg_str()
		return r+".\n"

	###################################################################################################	
	# propTriple
	# 	Create a triple for defining the properties of an individual
	# 	NOTE - The individual should be defined already, but it doesn't always have to be due to all 
	#		   the domains and ranges we've defined.
	# 		   Literal string values have to be passed in with quotation marks. 
	#	       EG {"hasName":"\"billy\""}
	# 
	# 	title - A string. The title of the individual, like its uri I mean, just without the whole www 
	#			part.
	# 	props - A dictionary with the property name as the key and the property value as the value. The
	#           property value can be a list or just a single value. Even if the property value is a 
	#			literal number value, still pass it in as a string.
	# 	isLiteral - True if ALL properties are literal properties, false otherwise.
	###################################################################################################
	def propTriple(self,title,props,isLiteral,rLiteral=None):
		if type(title)==str:
			r=self.addUri(title)+" "
		else:
			raise self.errMsg_str()

		if type(props)==dict:
			i=1
			# Add all the properties to the individual's definition
			for p in props:
				r+=self.addUri(p)+" "
				if type(props[p])!=list:
					if isLiteral:
						if rLiteral:
							r+=self.addUri("tag_"+props[p])+" "
						else:
							r+=props[p]+" "
					else:
						r+=self.addUri(props[p])+" "
				else:
					j=1
					for v in props[p]:
						if isLiteral:
							if rLiteral:
								r+=self.addUri("tag_"+v)+" "
							else:
								r+=v+" "
						else:
							r+=self.addUri(v)+" "
						if j!=len(props[p]):
							r+=","
						j+=1
				
				if i!=len(props):
					r+="; "
				i+=1
			r+=".\n"
			if rLiteral and isLiteral:
				r+=self.createRliteral(props)
		else:
			raise self.errMsg_dict()
		return r


###################################################################################################
# Main. Just for testing purposes.
###################################################################################################
import TripleMaker as t
def main():
	trip=t.TripleMaker("https://github.com/samuel-peers/campyOntology/blob/master/CampyOntology2.0.owl#")
	print trip.propTriple("sam",{"hasName":"\"sam\""},True,True)


if __name__=="__main__":
	main()
	
