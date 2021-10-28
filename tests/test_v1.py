from v1 import app
import pytest

@pytest.fixture
def app():
    yield app


@pytest.fixture
def client(app):
    return app.test_client()

def test_heartbeat():
    response = client.get('/heartbeat')
    assert response.get_data == 'OK'
    assert response.status == 200


def test_get_tasks():
    resp1 = client.get('tasks')
    resp2 = client.get('tasks/1')
    assert resp1.status == 200
    assert resp2.status == 200

