import logging
import json
from urllib import request


def head(list):
    return list[0] if list else None


def make_request(url, **kwargs):
    req = request.Request(url=url, **kwargs)
    response = request.urlopen(req)
    data = response.read().decode("utf-8")
    result = json.loads(data)
    code = result.get("errcode")
    message = result.get("errmsg")
    if code and code != 0:
        raise ValueError(message)
    return result


def getLogger(name="main", level="DEBUG"):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    fmt = logging.Formatter("%(levelname)s:%(name)s:%(message)s")

    stream_handler = logging.StreamHandler()
    logger.addHandler(stream_handler)
    stream_handler.setFormatter(fmt)
    return logger
