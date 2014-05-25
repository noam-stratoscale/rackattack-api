import os
from rackattack.tcp import client


_VAR_NAME = "RACKATTACK_PROVIDER"


def factory():
    if _VAR_NAME not in os.environ:
        raise Exception(
            "The environment variable '%s' must be defined properly" % _VAR_NAME)
    return client.Client(connectTo=os.environ[_VAR_NAME])
