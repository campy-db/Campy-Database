import sys
sys.path.append("/home/student/Campy/CampyDatabase/WebApp/app")

from sparql import queries as q

animals = [ a.lower() for a in q.getSubClasses("Animal") ]

gen_animals = [ a.lower() for a in q.getHighestClasses("Animal") ]

sample_types = [ st.lower() for st in q.getSubClasses("Animal_sample")]

gen_sample_types = [ st.lower() for st in q.getHighestClasses("Animal_sample") ]

