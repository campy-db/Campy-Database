import sys
sys.path.append("/home/student/Campy/CampyDatabase/WebApp/app")

from sparql import queries as q

animals = [ a.lower() for a in q.getSubClasses("Animal") ]

gen_animals = [ a.lower() for a in q.getHighestClasses("Animal") ]

spec_animals = [ a.lower() for a in q.getLowestClasses("Animal") ]

sample_types = q.getLowestClasses("Food") + q.getLowestClasses("By_product") + q.getLowestClasses("Faecal") 

sample_types = [ s.lower() for s in sample_types ]