from v1.app import app
import pytest
import json
import time

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_heartbeat(client):
    response = client.get('/heartbeat')
    assert response.status_code == 200


def test_get_tasks(client):
    resp1 = client.get('/v1/tasks')
    resp2 = client.get('/v1/tasks/1')
    assert resp1.status_code == 200
    assert resp2.status_code == 200


def test_create_tasks(client):
    url = '/v1/tasks'
    d1 = {
        'schedule_time': '2022-01-01T00:00:00',
        'lines': 'victoria'
    }
    d2 = {'lines': 'victoria'}
    d3 = {'schedule_time': '2022-01-01T00:00:00'}
    d4 = {'schedule_time': '2021'}
    assert client.post(url, data=d1).status_code == 200
    time.sleep(1)
    assert client.post(url, data=d2).status_code == 200
    assert client.post(url, data=d3).status_code == 400
    assert client.post(url, data=d4).status_code == 400
    assert client.post(url).status_code == 400

def test_delete_task(client):
    url = '/v1/tasks'
    d1 = {
        'schedule_time': '2022-01-01T00:00:00',
        'lines': 'victoria'
    }
    time.sleep(1)
    task_id = eval(client.post(url, data=d1).data.decode('utf-8'))['task_id']

    url = f"/v1/tasks/{task_id}"
    assert client.delete(url).status_code == 200
