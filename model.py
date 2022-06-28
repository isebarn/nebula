import sys, inspect
from Nebula import Vertex
from Nebula import Edge
from Nebula import configure


class Player(Vertex):
    name = "string"
    age = "int"


class Follow(Edge):
    degree = "string"


clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
configure(clsmembers)

# a = Follow(start="A", stop="B", degree="asd")
# a.save()
