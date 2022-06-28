from Nebula import Vertex
from Nebula import session


class Player(Vertex):

    name = str
    age = int


from pprint import pprint

pprint(Player("player122").get().to_json())
session.release()
