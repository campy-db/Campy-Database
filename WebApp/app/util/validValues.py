import sys
sys.path.append("/home/student/Campy/CampyDatabase/WebApp/app")

from sparql import queries as q

animals = [ a.lower() for a in q.getSubClasses("Animal") ]

gen_animals = [ a.lower() for a in q.getHighestClasses("Animal") ]

spec_animals = [ a.lower() for a in q.getLowestClasses("Animal") ]

sample_types = q.getSubClasses("FoodType") + q.getSubClasses("ByProduct") + q.getSubClasses("FaecalType") 