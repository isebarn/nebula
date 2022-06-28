from humps import decamelize
from Nebula import execute
from uuid import uuid1


class Nebula:
    _saved = False

    def __init__(self, *args, **kwargs):
        [setattr(self, k, v) for k, v in kwargs.items()]

    @classmethod
    def _name(cls):
        return decamelize(cls.__name__)

    def to_json(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    @classmethod
    def properties(cls):
        return list(set(cls.__dict__) - set(cls.__bases__[0].__dict__.keys()))

    def values(self):
        return {k: getattr(self, k) for k in self.properties()}

    def save(self):
        if isinstance(self, Vertex):
            self.vid = self.vid if self.vid else str(uuid1())

        insert = self._insert.format(
            self._name(),
            ",".join(self.properties()),
            self.identifier(),
            ",".join(
                [
                    "'{}'".format(x) if isinstance(x, str) else str(x)
                    for x in self.values().values()
                ]
            ),
        )

        execute(insert)
        self._saved = True


class Vertex(Nebula):
    _fetch = "fetch prop on {} '{}' yield properties(vertex)"
    _insert = "insert vertex {}({}) values '{}':({});"
    vid = None

    def get(self):
        result = execute(self._fetch.format(self._name(), self.vid))
        if not result.is_empty():
            item = next(result.__iter__()).get_value(0).as_map()
            [setattr(self, k, v) for k, v in item.items()]
            self._saved = True

        return self

    def identifier(self):
        return self.vid


class Edge(Nebula):
    _insert = "insert edge {}({}) values {}:({});"
    start = None
    stop = None

    def identifier(self):
        return "'{}' -> '{}'".format(self.start, self.stop)
