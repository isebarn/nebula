import sys, inspect
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
from humps import decamelize
from uuid import uuid1
from os import environ

config = Config()
config.max_connection_pool_size = 10
connection_pool = ConnectionPool()
ok = connection_pool.init([("127.0.0.1", 9669)], config)


def execute(command):
    space = environ.get("SPACE") if environ.get("SPACE") else "data"
    with connection_pool.session_context("root", "nebula") as session:
        session.execute("USE {}".format(space))
        return session.execute(command)


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

        return self


class Vertex(Nebula):
    _fetch = "fetch prop on {} '{}' yield properties(vertex)"
    _insert = "insert vertex {}({}) values '{}':({});"
    vid = None

    def get(self):
        result = execute(self._fetch.format(self._name(), self.vid))
        if not result.is_empty():
            item = next(result.__iter__()).get_value(0).as_map()
            [
                setattr(self, k, v.as_int() if v.is_int() else v.as_string())
                for k, v in item.items()
            ]
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


def configure(clsmembers):
    spaces = [x for x in execute("show spaces").__iter__()]
    spaces = [x.get_value(0).as_string() for x in spaces.__iter__()]
    space = environ.get("SPACE") if environ.get("SPACE") else "data"

    # create space
    if space not in spaces:
        execute(
            "CREATE SPACE {}(partition_num=15, replica_factor=1, vid_type=fixed_string(30));".format(
                space
            )
        )

    execute("USE {}".format(space))
    # clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    for item in clsmembers:
        name = decamelize(item[0])

        target = None
        if issubclass(item[1], Vertex) and item[0] != "Vertex":
            target = "tag"

        elif issubclass(item[1], Edge) and item[0] != "Edge":
            target = "edge"

        if target:
            result = execute("describe {} {}".format(target, name))

            if result.is_empty():
                create = ",".join(
                    ["{} {}".format(k, v) for k, v in item[1]().values().items()]
                )

                create = "CREATE {} {}({});".format(target, name, create)
                execute(create)


# config()

# session.release()
