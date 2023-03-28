from dotenv import load_dotenv

# load env
load_dotenv(override=True)

from os import getenv
from urllib.parse import parse_qs
from a2wsgi.wsgi import WSGIMiddleware

from util import getLogger
from route_handler import wx as wx_handler, chatgpt as chatgpt_handler

logger = getLogger()
port = int(getenv("Port"))


def application(environ, start_response):
    url = environ.get("PATH_INFO")
    method = environ.get("REQUEST_METHOD")
    qs = parse_qs(environ.get("QUERY_STRING"))
    length = environ.get("CONTENT_LENGTH", "0")
    length = 0 if length == "" else int(length)
    data = environ["wsgi.input"].read(length)

    status = "200 OK"
    # defafult headers
    headers = [
        ("Content-type", "application/json; charset=utf-8"),
        ("Access-Control-Allow-Origin", "*"),
    ]

    try:
        if url == "/wx":
            start_response(status, headers)
            return wx_handler(method, data, qs)
        elif url == "/chatgpt":
            headers = [
                ("Content-type", "text/event-stream;charset=utf-8"),
                ("Access-Control-Allow-Origin", "*"),
            ]
            start_response(status, headers)
            return chatgpt_handler(method, qs)
        else:
            start_response(status, headers)
            return ["Not Found".encode("utf-8")]
    except Exception as e:
        err = f"{e}"
        logger.error(err)
        return [err.encode("utf-8")]


app = WSGIMiddleware(application)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app=app, host="0.0.0.0", port=port, log_level="info")
