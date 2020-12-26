from pprint import pprint
from openap import prop

ac = prop.aircraft("A320")

pprint(ac)

eng = prop.engine("CFM56-5B4")

pprint(eng)
