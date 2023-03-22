import pytest
from multiprocessing import Process
from a2wsgi.wsgi import WSGIMiddleware
from httpx import AsyncClient
from uvicorn import Server, Config

from main import application

ASGI_APP = WSGIMiddleware(application)


@pytest.mark.asyncio
async def test_server_is_running():
    async with AsyncClient(app=ASGI_APP, base_url="http://localhost") as ac:
        response = await ac.get("/notfound")
        assert response.status_code == 200
        assert response.text == "Not Found"
