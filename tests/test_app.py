import pytest
from leafspy import flask_server
from flask import jsonify


@pytest.fixture
def client():
    return flask_server.app.test_client()


def test_import(client):
    pass


def test_base_route_that_does_not_exist(client):
    url = '/'
    response = client.get(url)
    assert response.get_data() == b'This page does not exist'
    assert response.status_code == 404


def test_upload_file_get(client):
    url = '/upload_file'

    response = client.get(url)
    assert b"Upload" in response.get_data()
    assert response.status_code == 200


def test_upload_file_post_no_file(client):
    url = '/upload_file'
    message = {
        "test_type": "some-test",
        "test_type_subcategory": "details",
        "instrument": "tester",
        "instrument_brand": "audi",
    }

    response = client.post(url, data=message)
    j = response.get_json()

    assert j["Code"] == 1
    assert j["Message"] == "No file attached"
    assert response.status_code == 200
