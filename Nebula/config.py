import inspect
import sys
from os import environ


# from Nebula.models import Vertex
# from Nebula.models import Edge


def configure(connection_pool):
    session = connection_pool.get_session("root", "nebula")
    execute = session.execute
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

    clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)

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

    return execute, session
